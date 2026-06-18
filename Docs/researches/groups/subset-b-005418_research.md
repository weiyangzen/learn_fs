# subset-b-005418 Research

Grouped source research for the IPU3 staging ImgU V4L2/PCI glue and the IPU7 staging driver boot, bus, firmware ABI, DMA, buttress, CPD, ISYS firmware, and CSI PHY layers. Each source file has a separate marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-tables.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-tables.h

## Purpose

This header declares static tuning tables and default image-processing configuration used by the IPU3 CSS parameter code. It is a compile-time contract between `ipu3-tables.c`, `ipu3-css-params.c`, and the UAPI/ABI structures that are copied into firmware parameter buffers.

## Important APIs, Types, and Functions

Key constants describe scaler and lookup dimensions: `IMGU_BDS_CONFIG_LEN`, `IMGU_SCALER_DOWNSCALE_4TAPS_LEN`, `IMGU_SCALER_DOWNSCALE_2TAPS_LEN`, `IMGU_GDC_LUT_LEN`, and `IMGU_XNR3_VMEM_LUT_LEN`. `struct imgu_css_bds_config` holds horizontal/vertical phase arrays, pattern array, sample length, and enable flags for bayer-domain scaling. `struct imgu_css_xnr3_vmem_defaults` carries XNR3 LUT vectors. Externs expose BDS configs, scaler taps, GDC LUTs, XNR3 defaults, and default blocks for BNR, demosaic, CCM, gamma, CSC, CDS, shading, IEFD, YDS, CHNR, edge/noise reduction, TCC, ANR, AWB, AE, AF, and related UAPI objects.

## Control Flow

There is no runtime control flow. The declared tables are selected and copied by the CSS parameter/configuration path when formats, rectangles, and processing parameters are prepared.

## State and Persistence Behavior

The file owns no mutable state. Its extern data is read-only driver state compiled into the module and persists for module lifetime.

## Dependencies and Integration Points

It includes `ipu3-abi.h` and depends on `linux/bitops.h` for `BIT()`. Its declarations are consumed by IPU3 CSS format/parameter setup and must match IPU3 UAPI and firmware ABI layout.

## Risks and Edge Cases

Array length, fixed-point, or default structure drift can break firmware programming without compiler errors if the consumer assumes a different table shape. The BDS granularity and scaler tap constants are hardware-facing.

## Test Signals

Useful signals are IPU3 module build coverage, format negotiation that exercises BDS/GDC/scaler paths, parameter-buffer ABI size checks, and image-quality regressions on raw-to-NV12 capture using default parameter sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-tables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-v4l2.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-v4l2.c

## Purpose

This file exposes the IPU3 ImgU processing block as V4L2 media-controller entities: per-pipe subdevices, video nodes for input/output/viewfinder, metadata nodes for parameters and 3A statistics, controls, pad links, vb2 queues, and ioctl operations.

## Important APIs, Types, and Functions

Important entry points are `imgu_v4l2_register()`, `imgu_v4l2_unregister()`, and `imgu_v4l2_buffer_done()`. Subdevice operations include `imgu_subdev_open()`, `imgu_subdev_s_stream()`, format get/set, and selection get/set. Media links are handled by `imgu_link_setup()`. vb2 operations are `imgu_vb2_buf_init()`, `imgu_vb2_buf_cleanup()`, `imgu_vb2_buf_queue()`, `imgu_vb2_queue_setup()`, `imgu_vb2_start_streaming()`, and `imgu_vb2_stop_streaming()`. Format helpers include `find_format()`, `imgu_try_fmt()`, `imgu_fmt()`, and metadata format handlers. Registration helpers create subdevices and nodes for every pipe.

## Control Flow

Registration builds a media device, V4L2 device, one ImgU subdevice per CSS pipe, five video/meta nodes per pipe, pad links, subdev nodes, and then registers the media device. During setup, link enable toggles `node.enabled` and the input link toggles the corresponding CSS pipe bit. `STREAMON` starts an individual vb2 queue; only once all enabled nodes across enabled pipes are streaming does the file call each subdevice `s_stream(1)` and then `imgu_s_stream(true)`. `STREAMOFF` reverses that order once for the whole pipeline, then stops the individual node and returns queued buffers. `QBUF` maps or validates the buffer, links it to the node list, sets payload, and asks `imgu_queue_buffers()` to feed CSS if the device is already streaming.

## State and Persistence Behavior

Persistent state lives in `struct imgu_video_device`, `struct imgu_v4l2_subdev`, and `struct imgu_media_pipe`: enabled links, active subdevice state, running mode, formats, rectangles, vb2 queues, buffer lists, sequence counters, and media pipeline objects. Global streaming state is protected by `imgu->streaming_lock`; queue/list state is protected by `imgu->lock` and per-node queue locks.

## Dependencies and Integration Points

The file integrates V4L2 core, media controller, videobuf2 DMA-SG, IPU3 CSS format/metadata helpers, and IPU3 DMA mapping. It calls into `ipu3.c` through `imgu_s_stream()` and `imgu_queue_buffers()`, and into CSS helpers through `imgu_css_fmt_try()`, `imgu_css_fmt_set()`, and `imgu_css_meta_fmt_set()`.

## Risks and Edge Cases

Pipeline start depends on every enabled node streaming; a missing queue can leave stream setup staged but not started. Parameters are metadata output and are not DMA-mapped like image buffers. `imgu_fmt()` allocates temporary format copies during TRY format and must free all non-target queues. Stop streaming intentionally avoids multiple `s_stream(0)` calls because newer V4L2 call helpers warn on repeated calls. Enabled-link state and CSS enabled pipe bits must stay synchronized.

## Test Signals

Exercise media graph enumeration, link enable/disable, `VIDIOC_TRY_FMT`/`S_FMT` on raw input and NV12 outputs, metadata params/stat nodes, multi-pipe stream-on ordering, stream-off from different nodes, buffer queueing before and during streaming, and suspend/stop error paths that return queued buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-v4l2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3.c

## Purpose

This is the IPU3 ImgU PCI driver core. It probes the PCI device, powers and initializes CSS/MMU/DMA/V4L2 layers, handles interrupts, feeds and drains firmware CSS queues, manages dummy buffers for optional nodes, and implements runtime/system power transitions.

## Important APIs, Types, and Functions

Exported internal functions are `imgu_node_to_queue()`, `imgu_map_node()`, `imgu_queue_buffers()`, and `imgu_s_stream()`. Probe/remove flow is `imgu_pci_probe()` and `imgu_pci_remove()`. Interrupt flow uses `imgu_isr()` and `imgu_isr_threaded()`. Dummy buffer helpers include preallocate/init/get/check/cleanup functions. Power helpers are `imgu_powerup()` and `imgu_powerdown()`. PM callbacks are `imgu_suspend()`, `imgu_resume()`, and runtime dummy callbacks.

## Control Flow

Probe enables PCI/MMIO/MSI, sets a 39-bit DMA mask, initializes locks and drain waitqueue, powers CSS enough to initialize MMU/DMA/CSS, registers V4L2 nodes, requests a threaded IRQ, and enables runtime PM. Streaming-on resumes runtime PM, powers up CSS at 200 or 450 MHz depending on enabled pipe input size, starts CSS streaming, initializes per-pipe dummy buffers, and queues initial buffer sets. `imgu_queue_buffers()` only feeds CSS when the input master queue has a real buffer; other enabled queues can use user buffers or dummy buffers. The threaded IRQ dequeues finished CSS buffers, timestamps/sequences output-side buffers, completes user buffers, wakes drain waiters when CSS is empty, and queues more work unless `qbuf_barrier` is set.

## State and Persistence Behavior

`struct imgu_device` persists PCI/MMIO, V4L2/media devices, MMU, IOVA domain, CSS state, per-pipe node state, locks, streaming flags, suspend flag, qbuf barrier, and drain waitqueue. Per-pipe dummy DMA maps persist across node lifetime and are resized at stream start to match active formats. CSS buffer state distinguishes new, queued, done, and error states.

## Dependencies and Integration Points

The file integrates Linux PCI, MSI IRQs, runtime PM, `ipu3-css`, `ipu3-css-fw`, `ipu3-dmamap`, `ipu3-mmu`, and the V4L2 layer in `ipu3-v4l2.c`. Firmware requirements are declared through `MODULE_FIRMWARE()`.

## Risks and Edge Cases

Dummy buffers avoid requiring userspace to queue every optional output, but the master input queue never uses dummies. Queueing failure after streaming can complete all unqueued user buffers with error. Suspend sets `qbuf_barrier`, synchronizes the IRQ, waits up to one second for CSS queue drain, then stops and powers down. Error unwinding in probe must unwind CSS, DMA, MMU, power, and locks in strict reverse order.

## Test Signals

Signals include PCI probe/remove with firmware present and missing, IRQ dequeue under continuous streaming, stream-on with optional VF/stat nodes disabled, stream-on with params metadata, high-resolution input forcing 450 MHz, system suspend/resume while streaming, runtime PM transitions, and error injection in CSS queueing/dummy buffer allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3.h

## Purpose

This header defines the shared IPU3 ImgU driver model used by PCI, V4L2, CSS, DMA, and MMU code. It names queue/node topology, supported size limits, buffer wrappers, media-pipe structures, and driver-wide device state.

## Important APIs, Types, and Functions

Important constants include `IMGU_QUEUE_MASTER`, `IMGU_NODE_*`, `IMGU_NODE_NUM`, input/output min/max dimensions, and queue depth. Key structures are `imgu_vb2_buffer`, `imgu_buffer`, `imgu_node_mapping`, `imgu_video_device`, `imgu_v4l2_subdev`, `imgu_media_pipe`, and `imgu_device`. Prototypes expose node/queue mapping, buffer queueing, V4L2 registration, buffer completion, and stream control. `imgu_bytesperline()` calculates NV12 or RAW packed line stride.

## Control Flow

There is no executable flow beyond `imgu_bytesperline()`. The type layout shapes flows implemented in `ipu3.c` and `ipu3-v4l2.c`: video nodes own vb2 queues and buffer lists; media pipes own per-node state plus CSS dummy buffers; `imgu_device` owns the global CSS/MMU/V4L2/PM state.

## State and Persistence Behavior

The header defines persistent in-memory state for the lifetime of the PCI device and its registered media graph. Buffer wrappers bind vb2 buffers to CSS buffers and DMA maps. Per-pipe state tracks enabled queues, dummy buffers, media pipeline, subdevice rectangles, controls, and running mode.

## Dependencies and Integration Points

It includes Linux IOVA/PCI, V4L2 controls/devices, vb2 DMA-SG, and `ipu3-css.h`. It is the central integration header for `ipu3.c`, `ipu3-v4l2.c`, and support modules.

## Risks and Edge Cases

Several structures rely on first-member embedding for `container_of()` conversions. Node IDs, CSS queue IDs, and enabled pipe bits must remain aligned. The stride helper encodes hardware-specific raw packing assumptions.

## Test Signals

Compile coverage is the main header signal. Runtime signals include format setup across all nodes, queue/node mapping, vb2 buffer completion, and RAW/NV12 stride correctness across edge widths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/Kconfig

## Purpose

This Kconfig entry exposes the Intel IPU7 staging driver as `VIDEO_INTEL_IPU7`, covering the base `intel_ipu7` module and the `intel_ipu7_isys` module used for camera sensor capture.

## Important APIs, Types, and Functions

The config is a tristate and selects required infrastructure: `AUXILIARY_BUS`, `IOMMU_IOVA`, `VIDEO_V4L2_SUBDEV_API`, `MEDIA_CONTROLLER`, `VIDEOBUF2_DMA_SG`, and `V4L2_FWNODE`.

## Control Flow

There is no runtime control flow. At build configuration time it gates compilation of IPU7 modules.

## State and Persistence Behavior

No runtime state is defined. The selected symbol determines whether objects are built-in, modular, or omitted.

## Dependencies and Integration Points

Dependencies require ACPI or compile-test, video device support, x86 with DMA, PCI, and the IPU bridge compatibility expression. The selected symbols line up with the auxiliary-bus split between base and ISYS drivers.

## Risks and Edge Cases

Dependency drift can make the module buildable without a subsystem it assumes at runtime, especially media-controller, fwnode, vb2, auxiliary bus, or IOVA support.

## Test Signals

Build-test with `m`, `y`, and disabled configurations, plus `COMPILE_TEST` where supported, verifies that the Kconfig dependencies match source includes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/Makefile -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/Makefile

## Purpose

This Makefile defines the IPU7 object split: a base PCI/bus/boot/DMA/MMU/buttress/CPD/syscom module and a separate ISYS media capture module.

## Important APIs, Types, and Functions

`intel-ipu7-objs` contains `ipu7.o`, bus, DMA, MMU, buttress, CPD, syscom, and boot objects. `intel-ipu7-isys-objs` contains ISYS, CSI2, CSI PHY, firmware ISYS, video, queue, and subdevice objects. Both modules are built from `CONFIG_VIDEO_INTEL_IPU7`.

## Control Flow

There is no runtime flow; object lists define link composition and symbol ownership.

## State and Persistence Behavior

No runtime state is owned here. Build output creates two modules that cooperate through exported `INTEL_IPU7` namespace symbols.

## Dependencies and Integration Points

The base module provides infrastructure used by the ISYS module: bus devices, DMA helpers, boot, syscom, and buttress controls. The ISYS module depends on these exports to initialize firmware and media entities.

## Risks and Edge Cases

Missing an object can lead to unresolved namespace exports or runtime feature absence. Because both modules key off one Kconfig symbol, load ordering and symbol namespaces matter.

## Test Signals

Module build/link tests and `modpost` namespace checks are the primary signals, followed by loading `intel_ipu7` and `intel_ipu7_isys` together.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/abi/ipu7_fw_boot_abi.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/abi/ipu7_fw_boot_abi.h

## Purpose

This header defines the packed firmware boot ABI shared between host driver and GOFO/IPU firmware. It describes logger configuration, boot parameter register IDs, boot config layout, secondary boot config layout, frequency units, and boot-state/error constants.

## Important APIs, Types, and Functions

Key types are `struct ia_gofo_logger_config`, `struct ia_gofo_boot_config`, and `struct ia_gofo_secondary_boot_config`. Enums include `ia_gofo_buttress_reg_id`, `ia_gofo_boot_uc_tile_frequency_units`, and `ia_gofo_boot_state`. Constants define boot-param register offsets, reserved sizes, logger severity and channel bits, critical error values, and `IA_GOFO_FW_BOOT_STATE_IS_CRITICAL()`.

## Control Flow

The header has no executable flow, but `ipu7-boot.c` follows this state machine: write boot config DMA address and UNINIT state, start uC, poll until READY or critical, later write SHUTDOWN_CMD and poll INACTIVE.

## State and Persistence Behavior

The packed structs are DMA-visible boot memory. Firmware writes boot state, queue indices address, and messaging version back through buttress boot parameter registers.

## Dependencies and Integration Points

It includes `ipu7_fw_common_abi.h` and `ipu7_fw_syscom_abi.h`. It is consumed by boot setup, ISYS firmware setup, and buttress diagnostics.

## Risks and Edge Cases

Every packed field is firmware ABI. Incorrect length, version, queue config offset, or reserved size can prevent firmware boot. Critical states in the `0xdead****` range must be treated as terminal.

## Test Signals

Boot tests should observe UNINIT-to-READY transitions, critical state logging, shutdown to INACTIVE, and queue index/message version register publication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/abi/ipu7_fw_boot_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/abi/ipu7_fw_common_abi.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/abi/ipu7_fw_common_abi.h

## Purpose

This header defines common GOFO firmware ABI primitives used by boot, ISYS, PSYS, and message protocols: address type, version structures, TLV headers/lists, error records, generic message headers, indirect/log messages, and common queue IDs.

## Important APIs, Types, and Functions

Important definitions include `ia_gofo_addr_t`, `struct ia_gofo_version_s`, `IA_GOFO_MSG_VERSION_INIT`, `struct ia_gofo_msg_version_list`, `struct ia_gofo_tlv_header`, `struct ia_gofo_tlv_list`, `struct ia_gofo_msg_err`, `struct ia_gofo_msg_header`, `struct ia_gofo_msg_header_ack`, `struct ia_gofo_msg_indirect`, and log message types. Queue IDs include ACK, LOG, and device input queues.

## Control Flow

No runtime control flow is implemented. Other ABI headers embed these common structs at the head of command, ack, log, graph, task, and stream messages.

## State and Persistence Behavior

The packed structures describe DMA/message queue tokens and payloads persisted only while firmware communication buffers are valid.

## Dependencies and Integration Points

It includes Linux fixed-width types. It is foundational for `ipu7_fw_boot_abi.h`, `ipu7_fw_msg_abi.h`, and `ipu7_fw_isys_abi.h`.

## Risks and Edge Cases

Packed TLV layout, alignment constants, and header embedding must match firmware parsers. The macro typo `IA_GOFO_MSG_ERR_UNSPECIFED` is ABI-visible naming but not behavioral. Error group/code checks should use `IA_GOFO_MSG_ERR_IS_OK()`.

## Test Signals

Compile ABI users, validate message sizes/offsets against firmware documentation, and test non-OK firmware errors through ack structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/abi/ipu7_fw_common_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/abi/ipu7_fw_config_abi.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/abi/ipu7_fw_config_abi.h

## Purpose

This small ABI header defines common firmware configuration values for watchdog and command timers.

## Important APIs, Types, and Functions

It defines `IPU_CONFIG_ABI_WDT_TIMER_DISABLED`, `IPU_CONFIG_ABI_CMD_TIMER_DISABLED`, and `struct ipu7_wdt_abi` with `wdt_timer1_us` and `wdt_timer2_us`.

## Control Flow

No runtime control flow is present. Subsystem config structures embed `ipu7_wdt_abi`, and setup code fills the fields before synchronizing DMA-visible config memory.

## State and Persistence Behavior

The watchdog fields become part of DMA-visible subsystem configuration passed to firmware at boot.

## Dependencies and Integration Points

It includes Linux types and is included by ISYS/PSYS config ABI headers.

## Risks and Edge Cases

Zero disables watchdog timers in current users. Changing defaults can alter firmware hang detection and recovery behavior.

## Test Signals

Boot firmware with disabled and non-disabled watchdog values where supported; inspect config DMA buffer before boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/abi/ipu7_fw_config_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/abi/ipu7_fw_insys_config_abi.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/abi/ipu7_fw_insys_config_abi.h

## Purpose

This header defines the ISYS firmware subsystem configuration block passed in boot config to the input-system firmware.

## Important APIs, Types, and Functions

`struct ipu7_insys_config` contains `timeout_val_ms`, `ia_gofo_logger_config`, and `ipu7_wdt_abi`. It includes boot, common config, and ISYS ABI headers.

## Control Flow

No executable flow. `ipu7_fw_isys_init()` allocates this structure through IPU7 DMA, zeros it, configures syscom logging and watchdogs, syncs it, and passes its DMA address to `ipu7_boot_init_boot_config()`.

## State and Persistence Behavior

The structure is persistent DMA memory while ISYS firmware is initialized and is freed by `ipu7_fw_isys_release()`.

## Dependencies and Integration Points

It bridges boot config and ISYS firmware command queues, specifically logger and watchdog setup.

## Risks and Edge Cases

Firmware interprets exact field layout. The current driver leaves timeout and watchdogs disabled/zeroed, so firmware-side timeout behavior depends on firmware defaults or disabled watchdog policy.

## Test Signals

ISYS boot with syscom logging enabled, DMA sync verification, and firmware log queue output are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/abi/ipu7_fw_insys_config_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/abi/ipu7_fw_isys_abi.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/abi/ipu7_fw_isys_abi.h

## Purpose

This packed ABI header defines the IPU7 ISYS firmware command/response protocol: queue layout, stream open/capture/close commands, MIPI identifiers, frame formats, stream and frame message maps, stream configuration, buffer sets, responses, send tokens, and error codes.

## Important APIs, Types, and Functions

Important constants define output queues, input queues, stream limit, output pin limit, and queue IDs. Enums define response types, send types, MIPI VC/port values, frame formats, DPCM, output destinations, and token flags. Main packed structs are `ipu7_insys_resolution`, `ipu7_insys_capture_output_pin_payload`, `ipu7_insys_output_link`, `ipu7_insys_output_pin`, `ipu7_insys_input_pin`, `ipu7_insys_stream_cfg`, `ipu7_insys_buffset`, `ipu7_insys_resp`, `ipu7_insys_resp_queue_token`, and `ipu7_insys_send_queue_token`.

## Control Flow

The ABI is used by `ipu7-fw-isys.c` and video code: stream configuration buffers are sent with `STREAM_OPEN`, buffer sets are sent with start/capture commands, firmware writes response tokens to output queues, and host code consumes responses from syscom.

## State and Persistence Behavior

State is queue-token and payload memory shared by host and firmware. Stream IDs, frame IDs, user tokens, DMA addresses, and error records tie firmware responses back to V4L2 streams and buffers.

## Dependencies and Integration Points

It includes common ABI and is used by ISYS video/queue/CSI code. It depends on syscom queue sizing and boot configuration from the base module.

## Risks and Edge Cases

The file self-includes its own guard path, which is harmless due to include guards but unusual. Packed layout and queue IDs are firmware ABI. Max stream, input pin, output pin, and frame format limits must match video code. Error groups distinguish general, stream, and capture failures.

## Test Signals

Test stream open/start/capture/flush/abort/close, response parsing for SOF/EOF/pin-ready, all supported raw/YUV formats, stream ID bounds, and firmware error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/abi/ipu7_fw_isys_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/abi/ipu7_fw_msg_abi.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/abi/ipu7_fw_msg_abi.h

## Purpose

This packed ABI header defines a broader IPU firmware graph/task messaging protocol, mainly for processing-system style graph execution: device open/close, graph open/close, task request/done, terminals, links, compression options, profiles, and error codes.

## Important APIs, Types, and Functions

Key enums define message types, node/profile/link/term types, device/graph/task states, and error groups. Key structs include `ipu7_msg_node_profile`, `ipu7_msg_cb_profile`, `ipu7_msg_node`, `ipu7_msg_link_cmprs_option`, `ipu7_msg_link`, `ipu7_msg_task`, `ipu7_msg_task_done`, `ipu7_msg_term`, `ipu7_msg_term_event`, `ipu7_msg_dev_open`, `ipu7_msg_dev_close`, `ipu7_msg_graph_open`, and graph ack/close structs. Queue constants define FWPS input/output queue counts and message size caps.

## Control Flow

The header itself has no control flow. Consumers construct TLV-backed device/graph/task messages, enqueue them to firmware, then parse ack/done/event responses with embedded common ack headers.

## State and Persistence Behavior

State is message-payload memory shared with firmware. Device, graph, and task states are protocol-visible state machines rather than host-owned globals.

## Dependencies and Integration Points

It includes common GOFO ABI types and reuses common message header/error structures. It is part of the IPU7 firmware ABI family and aligns with syscom queue IDs.

## Risks and Edge Cases

TLV lists, compression option sizing, bitmap dimensions, max terminal count, and queue ID ranges are ABI-sensitive. Graph open errors have many memory/resource failure modes, so host diagnostics must retain error group/code/detail.

## Test Signals

ABI compile checks, struct size/offset verification, graph open/close with compression options, invalid graph/task IDs, and firmware ack error propagation are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/abi/ipu7_fw_msg_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/abi/ipu7_fw_psys_config_abi.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/abi/ipu7_fw_psys_config_abi.h

## Purpose

This header defines the processing-system firmware configuration block.

## Important APIs, Types, and Functions

`struct ipu7_psys_config` contains debug manifest selection, timeout, compression support, logger config, watchdog config, a PSYS debug bitmask, and padding.

## Control Flow

No executable flow. A PSYS boot path would allocate/fill this config and pass its DMA address through the common boot config mechanism.

## State and Persistence Behavior

The structure is DMA-visible firmware configuration state for PSYS boot lifetime.

## Dependencies and Integration Points

It includes boot and common config ABI headers. Its fields align with firmware logging, watchdog, compression, and debug-manifest behavior.

## Risks and Edge Cases

Compression and debug flags alter firmware behavior. Packed layout and padding must remain stable.

## Test Signals

PSYS firmware boot with default and debug/compression configurations, plus boot config size and DMA sync checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/abi/ipu7_fw_psys_config_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/abi/ipu7_fw_syscom_abi.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/abi/ipu7_fw_syscom_abi.h

## Purpose

This header defines the firmware ABI for syscom queue configuration and queue indices.

## Important APIs, Types, and Functions

`struct syscom_queue_params_config` describes a queue token array address, token size, and maximum capacity. `struct syscom_config_s` carries output and input queue counts. Inline helpers `syscom_config_get_queue_configs()` and `_const()` locate the variable-length queue config array immediately after `syscom_config_s`. `struct syscom_queue_indices_s` holds firmware read/write indices.

## Control Flow

No direct runtime flow. Boot code embeds queue parameters after the boot config syscom context and firmware publishes queue index memory location after boot.

## State and Persistence Behavior

Queue config and indices are shared state between host and firmware. Host-owned queue token memory persists until boot config release.

## Dependencies and Integration Points

It includes common ABI address type and is consumed by boot setup and syscom token helpers.

## Risks and Edge Cases

The variable-length layout relies on `&config[1]`; allocation sizes must include all queue configs. Queue capacity must be at least firmware-supported minimum when queues are active.

## Test Signals

Boot queue initialization, syscom token enqueue/dequeue, queue full/empty handling, and queue index address publication after firmware READY.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/abi/ipu7_fw_syscom_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-boot.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-boot.c

## Purpose

This file implements firmware boot/shutdown for IPU7 ISYS and PSYS microcontrollers, including boot config allocation, syscom queue memory setup, uC reset/start/stop, boot parameter register programming, and boot-state polling.

## Important APIs, Types, and Functions

Exported APIs are `ipu7_boot_init_boot_config()`, `ipu7_boot_release_boot_config()`, `ipu7_boot_start_fw()`, `ipu7_boot_stop_fw()`, and `ipu7_boot_get_boot_state()`. Internal helpers manage boot parameter register addresses, uC cell reset/start/stop/init, and common boot config initialization.

## Control Flow

`ipu7_boot_init_boot_config()` allocates DMA-visible boot config and queue memory, initializes version/frequency/syscom fields, aligns queue memory to 64 bytes, and fills host and firmware queue config views. `ipu7_boot_start_fw()` resets the uC, writes UNINIT/zero diagnostic registers/config DMA address, starts the cell, polls boot state until READY or critical, then records firmware queue-index MMIO address and message version. `ipu7_boot_stop_fw()` verifies READY, writes SHUTDOWN_CMD, polls INACTIVE or critical, and resets/stops the uC.

## State and Persistence Behavior

State is held on `struct ipu7_bus_device`: boot config CPU/DMA pointer, size, firmware entry, syscom queue memory, and queue indices pointer. These allocations persist between init and release.

## Dependencies and Integration Points

It integrates buttress registers, platform DMEM offsets, IPU7 DMA allocation/sync, syscom queue config, and firmware error logging.

## Risks and Edge Cases

If queue memory allocation fails after boot config allocation, callers rely on release cleanup. Boot and stop polling timeouts are finite. Critical boot states dump firmware logs and return errors. Boot register offsets differ by subsystem. DMA address truncation would be dangerous because boot registers are 32-bit firmware ABI addresses.

## Test Signals

Test boot READY path, critical state handling, boot timeout, shutdown INACTIVE path, queue index publication, queue memory alignment, and release cleanup after partial initialization failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-boot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-boot.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-boot.h

## Purpose

This header declares the IPU7 firmware boot API used by subsystem drivers.

## Important APIs, Types, and Functions

It declares `FW_QUEUE_CONFIG_SIZE()`, `ipu7_boot_init_boot_config()`, `ipu7_boot_release_boot_config()`, `ipu7_boot_start_fw()`, `ipu7_boot_stop_fw()`, and `ipu7_boot_get_boot_state()`.

## Control Flow

No implementation flow. Callers initialize queue/subsystem config, call start to boot firmware, use syscom queues, stop firmware, then release boot config.

## State and Persistence Behavior

The API operates on `struct ipu7_bus_device` boot and syscom fields and DMA-visible queue/config allocations.

## Dependencies and Integration Points

It forward-declares `ipu7_bus_device` and `syscom_queue_config` and includes Linux types. ISYS firmware glue uses these calls directly.

## Risks and Edge Cases

Call order matters: release before stop or start before init leaves `ipu7_bus_device` fields invalid. Queue count and config array sizing must match `FW_QUEUE_CONFIG_SIZE()`.

## Test Signals

Compile namespace users and run firmware init/open/close/release sequencing tests, including failure unwinds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-boot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-bus.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-bus.c

## Purpose

This file implements the IPU7 auxiliary bus device layer and runtime PM domain used to split the base PCI driver into ISYS/PSYS child devices.

## Important APIs, Types, and Functions

Public APIs are `ipu7_bus_initialize_device()`, `ipu7_bus_add_device()`, and `ipu7_bus_del_devices()`. Runtime PM callbacks are `bus_pm_runtime_suspend()` and `bus_pm_runtime_resume()`. `ipu7_bus_release()` frees per-device private data and the bus device.

## Control Flow

Initialization allocates an `ipu7_bus_device`, binds it to the PCI parent/IPU device/control data, initializes an auxiliary device, attaches a PM domain, forbids runtime PM, then enables PM. Adding the device calls `auxiliary_device_add()`, links it into `isp->devices` under a mutex, and allows runtime PM. Deletion disables runtime PM, removes from the list, deletes the auxiliary device, and uninitializes it. Runtime resume powers up the buttress-controlled subsystem before generic resume; suspend runs generic suspend then powers down.

## State and Persistence Behavior

Each child holds auxiliary device state, driver data, subsystem ID, pdata, MMU/syscom/firmware fields, DMA mask, firmware SGT, and boot config fields. A global mutex protects the device list.

## Dependencies and Integration Points

It depends on Linux auxiliary bus, PM domains/runtime PM, PCI, and the buttress power API. It is the handoff layer between `ipu7.c` and subsystem modules such as ISYS.

## Risks and Edge Cases

Powerdown failure attempts generic resume and returns busy/I/O error. Device release frees `pdata`, so ownership must be clear. Runtime PM is initially forbidden until the auxiliary device is added.

## Test Signals

Auxiliary probe/remove, runtime PM resume/suspend, failure of buttress powerup/powerdown, and unloading modules with live child devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-bus.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-bus.h

## Purpose

This header defines the IPU7 auxiliary bus device model shared by the base PCI driver and subsystem drivers.

## Important APIs, Types, and Functions

`enum ipu7_subsys` identifies IS and PS. `struct ipu7_bus_device` embeds `auxiliary_device` and stores subsystem, pdata, MMU, parent IPU device, buttress control, firmware SGT/entry, syscom, and boot config fields. `struct ipu7_auxdrv_data` provides ISR callbacks and threaded-IRQ wake policy. Conversion macros map between devices and bus devices.

## Control Flow

No implementation flow. The structs support bus creation, IRQ demux, firmware boot, DMA, and subsystem driver binding.

## State and Persistence Behavior

State persists for each auxiliary child lifetime. The bus device is also the anchor for subsystem DMA/syscom/boot allocations.

## Dependencies and Integration Points

It includes auxiliary bus, device/list/scatterlist/types, firmware boot ABI, and syscom declarations. Buttress IRQ code uses `auxdrv_data`.

## Risks and Edge Cases

Fields are shared across modules, so initialization order is critical. `auxdrv_data` must be valid before buttress IRQ dispatch. DMA mask and firmware SGT must match MMU setup.

## Test Signals

Compile users, auxiliary driver binding, IRQ dispatch with and without threaded handlers, and firmware boot using bus-device fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-bus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-buttress-regs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-buttress-regs.h

## Purpose

This register header maps the IPU7/IPU8 buttress, power bridge, firmware boot parameter, security, IPC, power, clock, CSI PHY, and interrupt register space.

## Important APIs, Types, and Functions

It defines register offsets for IRQ status/enable/clear/mask, TSC/PB timestamps, workpoint and power status, sleep/clock overrides, firmware control/security/source registers, access blockers, boot parameter entries, memory ECC status, IPC registers, PB error logs, and CSI PHY offsets. It also defines interrupt bits, power state masks, IPC command/response constants, frequency ratios, security masks, D2D/NDE fields, UCX control bits, and PB config offsets.

## Control Flow

No code flow exists. `ipu7-buttress.c`, `ipu7-boot.c`, and `ipu7-isys-csi-phy.c` use these offsets and masks to program hardware state machines.

## State and Persistence Behavior

The file describes MMIO state owned by hardware. Some values, such as idle watchdog, boot params, and IRQ masks, are cached/restored by the driver.

## Dependencies and Integration Points

It is the central register contract for buttress power/auth/IPC, firmware boot, and CSI PHY configuration.

## Risks and Edge Cases

Incorrect offsets or masks can corrupt hardware control state. Some registers are generation-specific (`IPU7_` vs `IPU8_`, PTL/PB timestamp paths). A typo-like macro `BUTTRESS_REG_PS_AB_REGION_MAX_ADDRESS0` references `i` in its replacement and should be handled cautiously by consumers.

## Test Signals

Hardware smoke tests for IRQ clear/enable, runtime power up/down, CSE IPC, firmware boot params, TSC sync, and CSI PHY bring-up validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-buttress-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-buttress.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-buttress.c

## Purpose

This file controls the IPU7 buttress hardware block: secure CSE IPC, firmware authentication, IRQ demultiplexing, ISYS/PSYS power and clock transitions, D2D/NDE setup, timestamp sync/readout, wakeups, and buttress initialization/restoration.

## Important APIs, Types, and Functions

Public APIs include `ipu_buttress_ipc_reset()`, `ipu_buttress_powerup()`, `ipu_buttress_powerdown()`, `ipu_buttress_get_secure_mode()`, `ipu_buttress_authenticate()`, `ipu_buttress_reset_authentication()`, `ipu_buttress_auth_done()`, frequency getters, TSC sync/read/convert helpers, `ipu_buttress_wakeup_is_uc()`, `ipu_buttress_wakeup_ps_uc()`, `ipu_buttress_isr()`, `ipu_buttress_isr_threaded()`, `ipu_buttress_init()`, `ipu_buttress_restore()`, and `ipu_buttress_exit()`.

## Control Flow

Initialization sets mutexes/completions, CSE IPC register offsets/NACK mask, secure mode, WDT cache/ref clock, PB/buttress setup, and retries CSE IPC reset. IRQ handling obtains runtime PM if active, clears PB and buttress IRQs, dispatches IS/PS IRQ bits to auxiliary driver callbacks, handles CSE send/receive completions, disables IRQ bits that need threaded handling, and re-enables them after threaded callbacks. Powerup/down choose IPU7 or IPU8 paths, manage D2D/NDE for ISYS, request/release clock ownership or PS PLL as needed, program workpoint ratios, and poll power status. Authentication sends BOOT_LOAD and AUTH_RUN IPC commands and polls security/bootloader status.

## State and Persistence Behavior

`struct ipu_buttress` stores power/auth/console/IPC mutexes, CSE IPC completions and register addresses, cached WDT value, PSYS frequency fields, force flags, and reference clock. Hardware state persists in buttress MMIO registers and is restored by `ipu_buttress_restore()`.

## Dependencies and Integration Points

The file depends on PCI/runtime PM, firmware DMA state, auxiliary bus children, buttress register definitions, CPU model matching, and exported symbols for ISYS/PSYS modules. Authentication uses `isp->cpd_fw` and `psys->fw_sgt`.

## Risks and Edge Cases

CSE IPC has multiple timeout/retry paths and secure-mode bypasses. IRQ handling must avoid touching powered-down hardware; it uses `pm_runtime_get_if_active()`. Power transitions are generation-specific and polling-based. Authentication assumes firmware source registers point at the CPD package. TSC sync differs across IPU7/IPU7.5/IPU8.

## Test Signals

Signals include secure and non-secure boot, CSE reset/auth success and timeout/NACK failures, ISYS/PSYS runtime PM cycling, IRQ demux to child drivers, PB error logging, TSC sync/read conversion, suspend/resume restore, and IPU7/IPU7.5/IPU8 hardware variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-buttress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-buttress.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-buttress.h

## Purpose

This header declares the buttress control API and state structures for IPU7 platform power, IPC, authentication, IRQ, and timestamp services.

## Important APIs, Types, and Functions

`struct ipu_buttress_ctrl` describes subsystem power/frequency/status bits and clock ownership masks. `struct ipu_buttress_ipc` stores CSE IPC completions, NACK data, receive data, and register offsets. `struct ipu_buttress` stores locks, IPC state, cached WDT, frequency knobs, and reference clock. Function prototypes expose power, authentication, frequency, TSC, IRQ, init/exit/restore, CSI port config, and uC wakeup services.

## Control Flow

No implementation flow. The prototypes define the sequence used by bus runtime PM, PCI probe, firmware boot, and ISYS command paths.

## State and Persistence Behavior

The declared structs are embedded in `struct ipu7_device` and persist for the PCI device lifetime.

## Dependencies and Integration Points

It includes completion, IRQ, list, and mutex infrastructure and forward-declares IPU7/device objects. Consumers include bus PM, boot, firmware command, and main PCI code.

## Risks and Edge Cases

Control descriptors must match hardware generation and subsystem. IPC completions and mutexes must be initialized before IRQs can complete them.

## Test Signals

Compile coverage and runtime tests for power/auth/TSC/IRQ helper calls through base and subsystem modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-buttress.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-cpd.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-cpd.c

## Purpose

This file validates and extracts IPU7 CPD firmware package contents. CPD packages contain manifest, metadata, and binary entries for ISYS and PSYS firmware.

## Important APIs, Types, and Functions

Public APIs are `ipu7_cpd_validate_cpd_file()` and `ipu7_cpd_copy_binary()`. Internal packed types model CPD header, entries, metadata attribute, IPL metadata, and combined metadata. Helpers locate entries, manifest, and per-binary metadata.

## Control Flow

Validation checks CPD marker, entry count, header/entry bounds, each entry bounds, manifest maximum size, and metadata type/length for both binaries. It then parses the last 128 bytes of each binary into six newline-delimited metadata lines and logs name/version/timestamp/commit. Copying searches binary entries by 12-byte name, copies the binary into the code region at the IPL load offset, and returns the entry point from IPL metadata.

## State and Persistence Behavior

No persistent driver state is owned. It reads firmware package memory and writes caller-provided code region memory.

## Dependencies and Integration Points

It integrates with the main IPU7 firmware request/load path and buttress authentication/boot code. It uses `struct ipu7_device` for logging.

## Risks and Edge Cases

Validation does not verify CRC or cryptographic signature; secure-mode authentication is separate. Version metadata parsing is best-effort and continues on malformed online metadata. Copying trusts validated offsets and metadata load offsets.

## Test Signals

Test malformed marker, entry count, entry bounds, oversized manifest, bad metadata type/length, missing binary name, valid copy offset/entry, and malformed trailing online metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-cpd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-cpd.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-cpd.h

## Purpose

This header declares CPD firmware package validation and binary extraction helpers.

## Important APIs, Types, and Functions

It forward-declares `struct ipu7_device` and declares `ipu7_cpd_validate_cpd_file()` plus `ipu7_cpd_copy_binary()`.

## Control Flow

No implementation flow. Callers validate a CPD package before copying named firmware binaries into the uC code region.

## State and Persistence Behavior

No state is owned. Functions operate on caller-provided firmware memory and code-region buffers.

## Dependencies and Integration Points

The header is used by the base IPU7 firmware load path and indirectly by boot/authentication.

## Risks and Edge Cases

Callers must validate before copy and provide a code region large enough for metadata offsets and binary sizes.

## Test Signals

Compile users and firmware-load tests with valid and invalid CPD packages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-cpd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-dma.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-dma.c

## Purpose

This file implements IPU7 DMA/IOMMU helpers that allocate coherent-ish shared buffers, map scatterlists into the IPU IOVA space, synchronize caches, mmap allocated buffers to userspace, and free/unmap IOVAs.

## Important APIs, Types, and Functions

Public APIs are `ipu7_dma_alloc()`, `ipu7_dma_free()`, `ipu7_dma_mmap()`, `ipu7_dma_map_sg()`, `ipu7_dma_unmap_sg()`, sgtable wrappers, and cache sync helpers. Internal `struct vm_info` tracks allocated pages, IPU IOVA, virtual mapping, and size. Helpers allocate/free page arrays and locate `vm_info` by IOVA.

## Control Flow

Allocation reserves an IOVA, allocates/splits pages, zeroes and optionally flushes them, maps each page for PCI DMA, maps PCI DMA addresses into IPU MMU, vmaps pages, records `vm_info`, and returns CPU virtual address plus IPU DMA handle. Free reverses the process: find IOVA/vm info, remove list entry, vunmap, unmap PCI DMA and IPU MMU, clear/free pages, invalidate TLB, free IOVA, and free metadata. SG mapping validates zero offsets, counts pages, allocates or reserves an IOVA region, maps each SG DMA address into IPU MMU, then rewrites SG DMA addresses to IPU IOVAs; unmap restores PCI DMA addresses from MMU translations before unmapping.

## State and Persistence Behavior

Allocated buffers persist in `mmu->vma_list` until freed. IOVAs are allocated from `mmu->dmap->iovad`; IPU MMU mappings persist until explicit unmap and TLB invalidation.

## Dependencies and Integration Points

It depends on Linux DMA mapping, IOVA allocator, scatterlists, vmalloc/vmap, cache flushing, and IPU7 MMU helpers. Boot/syscom and ISYS config use `ipu7_dma_alloc()`; video queues use SG mapping.

## Risks and Edge Cases

Manual page/IOVA bookkeeping is delicate. Several invalid-state `WARN_ON()` paths return early in free and can leak if state is inconsistent. SG entries with non-zero offsets are unsupported. `ipu7_dma_map_sg()` returns `0` for allocation failure, following DMA map convention but requiring callers to treat zero as failure. Reserved firmware code region mapping is special.

## Test Signals

Stress allocate/free, partial allocation failure, mmap, SG map/unmap with multi-page buffers, non-zero offset rejection, reserved firmware region mapping, TLB invalidation, and cache sync visibility to firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-dma.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-dma.h

## Purpose

This header declares IPU7 DMA allocation, synchronization, mmap, and scatterlist mapping APIs.

## Important APIs, Types, and Functions

It defines `DMA_ATTR_RESERVE_REGION`, `struct ipu7_dma_mapping`, and prototypes for single/SG cache sync, allocate/free, mmap, SG map/unmap, and sgtable map/unmap helpers.

## Control Flow

No implementation flow. The API is used by firmware boot/config code and buffer queues to obtain IPU-visible IOVA mappings.

## State and Persistence Behavior

`struct ipu7_dma_mapping` stores MMU info and an IOVA domain. Allocated mappings are tracked by the implementation on the MMU.

## Dependencies and Integration Points

It includes Linux DMA map ops, DMA mapping, IOVA, scatterlist, and IPU7 bus definitions.

## Risks and Edge Cases

Callers must match map/unmap and alloc/free, pass the correct `ipu7_bus_device`, and handle the special reserve-region attribute.

## Test Signals

Compile coverage and allocation/map/unmap tests through boot config, firmware queues, and V4L2 capture buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-fw-isys.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-fw-isys.c

## Purpose

This file provides ISYS firmware glue: syscom queue sizing, ISYS subsystem config allocation, boot-config initialization, firmware open/close wrappers, command token submission, response access, and debug dumps for stream/buffer payloads.

## Important APIs, Types, and Functions

Public functions include `ipu7_fw_isys_init()`, `ipu7_fw_isys_release()`, `ipu7_fw_isys_open()`, `ipu7_fw_isys_close()`, `ipu7_fw_isys_simple_cmd()`, `ipu7_fw_isys_complex_cmd()`, `ipu7_fw_isys_get_resp()`, `ipu7_fw_isys_put_resp()`, `ipu7_fw_isys_dump_stream_cfg()`, and `ipu7_fw_isys_dump_frame_buff_set()`.

## Control Flow

Initialization allocates `ipu7_syscom_context`, creates queue configs for ISYS output message/log/reserved queues and input device/per-stream queues, allocates DMA-visible `ipu7_insys_config`, enables syscom logger channel, disables watchdog timers, reads current ISYS frequency through buttress, syncs config, selects message major version by hardware generation, and initializes boot config. Complex command submission optionally flushes payload cache, obtains a syscom token for `stream_handle + IPU_INSYS_INPUT_MSG_QUEUE`, fills address/handle/type/stream/flag, puts the token, and wakes IS uC. Response access gets/puts tokens from the output message queue.

## State and Persistence Behavior

`isys->subsys_config` and `adev->syscom` persist from init to release. Queue token state is shared with firmware through boot-created syscom memory.

## Dependencies and Integration Points

It depends on ISYS ABI/config ABI, IPU7 boot, DMA, syscom, buttress frequency/wakeup, and ISYS stream/video code.

## Risks and Edge Cases

Queue selection relies on stream handle bounds. `ipu7_syscom_get_token()` returning NULL maps to `-EBUSY`. Payload cache flushing is manual. Init failure must release boot/subsystem allocations. Message major version differs between IPU8 and earlier hardware.

## Test Signals

Test init/release leaks, boot open/close, queue full command failure, stream open/capture/close commands, response token parsing, and debug dump coverage for multi-pin stream configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-fw-isys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-fw-isys.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-fw-isys.h

## Purpose

This header declares the host-side ISYS firmware interface used by ISYS video/queue code.

## Important APIs, Types, and Functions

It declares init/release/open/close, dump helpers, simple/complex command submission, and response get/put APIs. It includes `ipu7_fw_isys_abi.h` and forward-declares ISYS structures.

## Control Flow

No implementation flow. Callers initialize firmware support, open booted firmware, send stream/buffer commands, consume responses, and close/release firmware support.

## State and Persistence Behavior

The APIs operate on `struct ipu7_isys` state, including subsystem config DMA memory and syscom queues.

## Dependencies and Integration Points

It is the bridge between V4L2 stream management and firmware syscom/boot layers.

## Risks and Edge Cases

Command callers must provide CPU and DMA pointers for complex payloads and respect stream handle/queue limits.

## Test Signals

Compile ISYS users and run stream open/capture/close command sequences with response draining.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-fw-isys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-csi-phy.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-csi-phy.c

## Purpose

This file programs the IPU7/IPU8 CSI-2 DWC controller and C/D-PHY register blocks for camera sensor links, including reset, data-ID filters, DPHY/CPHY tuning tables, lane aggregation, readiness polling, and powerdown.

## Important APIs, Types, and Functions

Public APIs are `ipu7_isys_csi_phy_powerup()` and `ipu7_isys_csi_phy_powerdown()`. Internal helpers read/write PHY, CSI, and GPREG registers; apply bit masks; configure CSI controller interrupts/lanes/mode; reset PHY; configure data IDs from remote subdev frame descriptors; poll PHY readiness; calculate table-driven DPHY/CPHY parameters; and configure a PHY based on link frequency, lane count, mode, and aggregation.

## Control Flow

Powerup remaps non-IPU7 port-A links with more than two lanes into aggregation mode, resets the primary PHY, programs lane force/control and mode, optionally resets/programs port B for aggregation, configures the CSI controller and data ID monitors, configures DPHY or CPHY from remote link frequency, releases reset/shutdown, waits for ready, clears force controls, and repeats configuration/readiness for port B in aggregation mode. Powerdown resets the active port and also port B when aggregation was used.

## State and Persistence Behavior

Register programming persists in ISYS MMIO/PHY hardware until reset or powerdown. A static bitmap `data_ids` tracks use of eight DWC data-ID monitor slots, and `isys->phy_rext_cal` caches calibration from PHY0 for reuse on other PHYs.

## Dependencies and Integration Points

It depends on media controller remote-pad lookup, V4L2 subdev frame descriptors, CSI2 register definitions, platform register bases, IPU hardware-version helpers, and CSI2 link-frequency helpers.

## Risks and Edge Cases

The global `data_ids` bitmap is not keyed per controller and is not cleared in this file on powerdown, so repeated configurations may exhaust monitors unless reset elsewhere. Link frequency lookup failure aborts PHY config. Hardware-generation and port-specific lane mappings are subtle. Many tuning writes are table-driven and sensitive to mbps range boundaries.

## Test Signals

Exercise DPHY and CPHY links, 1/2/4 lane modes, IPU7 vs IPU7.5/IPU8 variants, port-A aggregation, multiple VCs/data types, repeated stream start/stop, link-frequency failure handling, PHY ready timeout, and sensor frame descriptor validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-csi-phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-csi-phy.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-csi-phy.h

## Purpose

This header declares CSI PHY power control for IPU7 ISYS CSI2 ports.

## Important APIs, Types, and Functions

It defines `PHY_MODE_DPHY`, `PHY_MODE_CPHY`, and declares `ipu7_isys_csi_phy_powerup()` plus `ipu7_isys_csi_phy_powerdown()`.

## Control Flow

No implementation flow. CSI2 stream enable code calls powerup before enabling capture and powerdown during teardown.

## State and Persistence Behavior

The functions operate on `struct ipu7_isys_csi2` state such as port, lane count, PHY mode, and parent ISYS.

## Dependencies and Integration Points

It forward-declares ISYS and references `struct ipu7_isys_csi2` without a forward declaration in this header, relying on include order from consumers.

## Risks and Edge Cases

The missing explicit `struct ipu7_isys_csi2` forward declaration can make include-order changes fragile. PHY mode values must match firmware/hardware expectations.

## Test Signals

Compile include-order tests and runtime DPHY/CPHY stream start/stop through CSI2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-csi-phy.h -->
