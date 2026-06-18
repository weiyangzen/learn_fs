# Research: subset-b-004119

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-queue.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-queue.c

## Purpose
`ipu6-isys-queue.c` implements the videobuf2 queue side of Intel IPU6 ISYS capture. It owns buffer allocation validation, DMA mapping, incoming/active buffer lists, multi-output buffer set assembly, streaming start/stop coordination, and completion of buffers when firmware reports pin data ready.

## Important APIs, Types, And Functions
The file implements `vb2_ops` through `ipu6_isys_queue_ops`: queue setup, buffer init/prepare/cleanup, start/stop streaming, and buffer queueing. Public helpers include `ipu6_isys_buffer_list_queue()`, `ipu6_isys_buf_to_fw_frame_buf()`, `ipu6_isys_queue_buf_ready()`, and `ipu6_isys_queue_init()`. It uses `struct ipu6_isys_queue` incoming/active lists, `struct ipu6_isys_buffer_list` as a per-frame multi-queue bundle, and `struct ipu6_isys_video_buffer` for the vb2 buffer plus IPU6 DMA address.

## Control Flow
`ipu6_isys_buf_init()` maps the first vb2 DMA-SG plane with `ipu6_dma_map_sgtable()` and caches the IOVA. `buf_queue()` appends the buffer to `aq->incoming`; once all queues in the shared firmware stream are streaming, it calls `buffer_list_get()` to remove one buffer from every queue, converts that list to `ipu6_fw_isys_frame_buff_set_abi`, moves buffers to active, and sends `STREAM_CAPTURE` to firmware.

`start_streaming()` walks the media graph from the video node to the CSI-2 subdev and external source, calls `ipu6_isys_setup_video()`, validates link format, opens firmware, prepares the stream for the first queue, and when every queue in the pipeline is ready sends `STREAM_START_AND_CAPTURE` through `ipu6_isys_stream_start()`. `stop_streaming()` stops firmware if this was the last queue, removes the queue from the stream, returns all remaining buffers as errors, and closes firmware.

## State And Persistence
All state is transient kernel memory. Incoming buffers are waiting for a complete multi-queue frame set; active buffers have been given to firmware. `stream->sequence` and the recent SOF timestamp ring are used to stamp completed buffers. If active buffers remain during cleanup, `isys->need_reset` is set so later opens fail until runtime power cycling clears the condition.

## Dependencies And Integration Points
This file integrates V4L2 vb2, media-controller pipelines, IPU6 firmware commands, IPU6 DMA mapping, CSI-2 SOF/EOF timestamping, and runtime firmware open/close in `ipu6-isys-video.c`. It expects `ipu6_isys_get_*()` format helpers and `ipu6_isys_setup_video()` to be valid for the video node.

## Risks And Test Signals
The highest-risk behavior is synchronization across multiple capture queues: a frame request is valid only when every queue has an incoming buffer. Error paths must avoid losing buffers if firmware stream open/start fails. `ipu6_isys_stream_start()` can return `-ENOMEM` after taking buffers if `ipu6_get_fw_msg_buf()` fails in its post-start loop, so stress with low memory and multiple queues matters. Tests should cover stream-on with missing buffers, multi-output capture, metadata capture, firmware timeouts, STR2MMIO errors, stream-off with active buffers, link-format mismatch, and repeated runtime PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-queue.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-queue.h

## Purpose
This header defines the queue and buffer objects used by IPU6 ISYS video nodes and declares the queue/firmware conversion entry points implemented in `ipu6-isys-queue.c`.

## Important APIs, Types, And Data
`struct ipu6_isys_queue` wraps a `vb2_queue`, a media-stream list node, spinlock-protected `active` and `incoming` buffer lists, and the firmware output pin index. `struct ipu6_isys_buffer` is the list node embedded in capture buffers plus an atomic STR2MMIO error flag. `struct ipu6_isys_video_buffer` embeds `vb2_v4l2_buffer`, the ISYS buffer node, and the mapped DMA address. `struct ipu6_isys_buffer_list` is a temporary list of one buffer from each queue. The two flags, `IPU6_ISYS_BUFFER_LIST_FL_INCOMING` and `_ACTIVE`, select where a bundle is returned.

The declared APIs are `ipu6_isys_buffer_list_queue()`, `ipu6_isys_buf_to_fw_frame_buf()`, `ipu6_isys_queue_buf_ready()`, and `ipu6_isys_queue_init()`.

## Control Flow
The header supports a two-list queueing model. User buffers enter `incoming`, are bundled across all queues in a stream, then move to `active` just before firmware receives the frame-buffer-set command. Firmware completion later removes the matching active buffer and completes the vb2 buffer.

## State And Persistence
The structures store only live queue state for the current device lifetime. DMA addresses are set during vb2 buffer initialization and cleared on cleanup. No persistent storage is used.

## Dependencies And Integration Points
The header depends on vb2 V4L2 types and IPU6 firmware ABI structures. It is included by video and queue code and forward-declares `struct ipu6_isys_stream` to avoid a deeper include cycle.

## Risks And Test Signals
The conversion macros assume the exact embedding layout of queue and buffer structures. Tests should exercise all vb2 paths that use these macros: queue setup, buffer prepare, stream start/stop, capture completion, and error completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-subdev.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-subdev.c

## Purpose
`ipu6-isys-subdev.c` provides common V4L2 subdevice helpers for IPU6 ISYS bridge entities, especially CSI-2 receiver subdevices. It centralizes media-bus code handling, Bayer-order conversion, format propagation, stream routing setup, and common subdevice initialization/cleanup.

## Important APIs, Types, And Functions
Public helpers include `ipu6_isys_mbus_code_to_bpp()`, `ipu6_isys_mbus_code_to_mipi()`, `ipu6_isys_is_bayer_format()`, `ipu6_isys_convert_bayer_order()`, `ipu6_isys_subdev_set_fmt()`, `ipu6_isys_subdev_enum_mbus_code()`, `ipu6_isys_get_src_stream_by_src_pad()`, `ipu6_isys_subdev_set_routing()`, `ipu6_isys_subdev_init()`, and `ipu6_isys_subdev_cleanup()`. The implementation uses `struct ipu6_isys_subdev` from the companion header and V4L2 active-state routing APIs.

## Control Flow
Media-bus conversion helpers map V4L2 media-bus codes to bit depth and MIPI CSI-2 data types. Unsupported codes warn and return conservative defaults. `ipu6_isys_subdev_set_fmt()` clamps width/height to ISYS limits, picks a supported bus code, stores the format, and for sink pads propagates the same format to the opposite routed source stream while resetting crop to the full frame. Source-pad set-format requests are effectively read-only for bridge subdevices with more than one pad.

Routing is initialized to a default active 1:1 route from sink pad 0 stream 0 to source pad 1 stream 0 with a 4096x3072 SGRBG10 format. `ipu6_isys_subdev_set_routing()` validates `V4L2_SUBDEV_ROUTING_ONLY_1_TO_1` and applies routing with the same default format.

## State And Persistence
State lives in V4L2 subdev active/try state and the in-memory `ipu6_isys_subdev`. Crops are reset when a sink format changes. `asd->source` is initialized to `-1` and later used by CSI-2 code as the firmware stream source.

## Dependencies And Integration Points
This file integrates with media entity pads, V4L2 subdev streams/routing, V4L2 controls, and MIPI CSI-2 data type definitions. CSI-2 subdevice code reuses it to expose bridge entities consistently to `ipu6-isys-video.c`.

## Risks And Test Signals
Defaulting unsupported media-bus codes to 8-bit or invalid MIPI type can hide caller mistakes after only a warning. Routing currently supports only simple 1:1 routes, so multi-stream graph changes must be validated carefully. Test signals include V4L2 subdev routing tests, format propagation on sink pads, Bayer order conversion under odd crop offsets, unsupported code handling, and media graph validation before stream-on.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-subdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-subdev.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-subdev.h

## Purpose
This header declares the common IPU6 ISYS subdevice wrapper and helper API used by CSI-2 receiver subdevices and video setup code.

## Important APIs, Types, And Data
`struct ipu6_isys_subdev` embeds a `v4l2_subdev`, back-pointer to `struct ipu6_isys`, supported media-bus code table, pad array, optional control handler, optional `ctrl_init` callback, and `source` identifier used for firmware stream source selection. Conversion macros include `to_ipu6_isys_subdev()`.

Declared helpers cover media-bus depth and MIPI data type mapping, Bayer detection/order conversion, common set-format and enum-code ops, source-stream lookup by source pad, routing updates, and lifecycle init/cleanup.

## Control Flow
Callers initialize the wrapper with `ipu6_isys_subdev_init()`, providing subdev ops, expected controls, and sink/source pad counts. The subdevice then participates in V4L2 routing and stream enable/disable flows used by ISYS capture.

## State And Persistence
The header-defined state is per-device and per-subdevice only. `source` is initialized by implementation code and later read during stream preparation; no file or firmware persistence is represented here.

## Dependencies And Integration Points
It depends on V4L2 controls/subdevs and media entities. It is part of the internal contract between the ISYS core, CSI-2 receiver implementation, and video-node setup.

## Risks And Test Signals
The `supported_codes` pointer is expected to be a zero-terminated array. Bad table termination would cause enumeration and format matching to walk past bounds. Tests should cover subdevice init failure unwinding, pad flags for sink/source counts, and source-stream lookup after routing changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-subdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-video.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-video.c

## Purpose
`ipu6-isys-video.c` implements IPU6 ISYS V4L2 capture video nodes and the firmware stream lifecycle behind them. It exposes video and metadata capture formats, validates media links, computes DMA buffer sizes, configures firmware stream pins, starts/stops upstream subdev streams, manages stream handles, and contributes per-stream data-rate information for iWake watermark programming.

## Important APIs, Types, And Functions
The exported format table `ipu6_isys_pfmts[]` maps V4L2 pixel/meta formats to media-bus codes, packed/unpacked bit depths, firmware frame formats, and metadata flags. Major functions are `ipu6_isys_get_isys_format()`, `ipu6_isys_video_prepare_stream()`, `ipu6_isys_video_set_streaming()`, `ipu6_isys_fw_open()`, `ipu6_isys_fw_close()`, `ipu6_isys_setup_video()`, `ipu6_isys_video_init()`, `ipu6_isys_video_cleanup()`, stream lookup helpers, watermark helpers, and getters for current format/size/stride/dimensions.

## Control Flow
VIDIOC format calls clamp dimensions to ISYS limits, align bytes-per-line to 64 bytes, and over-allocate `sizeimage` by at least one line or the platform DMA overshoot value to avoid hardware DMA overrun. `ipu6_isys_setup_video()` finds the active route on the remote CSI-2 subdev, determines source stream, gets CSI-2 frame descriptor data when available, starts the media pipeline, and reserves or shares a firmware stream based on CSI source and virtual channel.

Streaming starts in `ipu6_isys_video_set_streaming()`. It maps the video pad route back to the sink stream, opens/configures firmware with `start_stream_firmware()`, then enables V4L2 subdev streams with the pipeline stream mask. Firmware open builds `ipu6_fw_isys_stream_cfg_data_abi` by adding input/output pins for every queue in the shared stream; optional first buffers are sent with `STREAM_START_AND_CAPTURE`. Stop sends firmware flush, disables upstream streams, closes firmware, and releases the stream-open count.

## State And Persistence
Video node state includes current video/meta formats, selected stream pointer, source stream, virtual channel/data type, and watermark parameters. ISYS firmware communication is reference counted in `isys->ref_count`; the first open configures SPC and initializes firmware communication, while the last close tears it down or marks `need_reset` if firmware context remains.

## Dependencies And Integration Points
This file ties together V4L2 file/ioctl APIs, vb2 queues, media pipelines, V4L2 subdev streams, CSI-2 frame descriptors, IPU6 CPD/SPC firmware setup, IPU6 firmware ABI commands, runtime PM, and iWake watermark calculation in `ipu6-isys.c`.

## Risks And Test Signals
Risk centers on graph/route assumptions and firmware sequencing. `ipu6_isys_fw_pin_cfg()` assumes locked active state and valid remote pads; bad route state can propagate to firmware pin counts. Stream sharing by virtual channel and subdevice must release refcounts exactly. `video_open()` blocks when `need_reset` is set, so tests need recovery through runtime suspend. Test media graphs with multiple CSI source pads, metadata capture, frame descriptors absent/present, unsupported mbus codes, format changes while queues are busy, stream-on failure after firmware open, and iWake data-rate calculations for sensors without link-frequency controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-video.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-video.h

## Purpose
This header defines the IPU6 ISYS video-node, firmware-stream, pixel-format, and watermark data structures used by queue, video, and ISYS core code.

## Important APIs, Types, And Data
`IPU6_ISYS_OUTPUT_PINS` is 11, and `IPU6_ISYS_MAX_PARALLEL_SOF` is 2. `struct ipu6_isys_pixelformat` stores V4L2 fourcc, bit depth, packed bit depth, media-bus code, firmware CSS format, and metadata flag. `struct ipu6_isys_stream` mirrors a firmware stream: mutex, sequence counter, recent SOF ring, source/handle, output pin count, owning subdevice, queue counts, streaming state, completions for open/close/start/stop, queue list, output pin to queue map, error, and CSI virtual channel. `struct ipu6_isys_video` owns the vb2 queue, mutex, media pad, video device, current video/meta formats, stream pointer, CSI link, watermark data, source stream, VC, and DT.

## Control Flow
Video nodes use the declarations here to allocate streams, prepare firmware pin configuration, open/close firmware, and query active format parameters for queue sizing. Watermark fields are populated before streaming and linked into the ISYS global watermark list while the stream is active.

## State And Persistence
The structures contain live driver state only. Completions and counters are reset around each firmware command sequence; format state persists until the video device is closed or reconfigured.

## Dependencies And Integration Points
The header depends on media entities, V4L2 devices, completion/mutex/list primitives, and `ipu6-isys-queue.h`. It is the central contract among ISYS video, queue, CSI-2, and ISYS core files.

## Risks And Test Signals
The `output_pins_queue` array is bounded by firmware pin IDs; firmware responses with out-of-range pins must be ignored safely. Tests should cover shared streams, stream refcounting, multiple SOFs before data-ready, and cleanup after failed firmware completions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-video.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys.c

## Purpose
`ipu6-isys.c` is the auxiliary driver for the IPU6 input system. It registers the ISYS media device, V4L2 device, CSI-2 receiver subdevices, capture video nodes, async sensor notifier, runtime PM handlers, firmware message buffers, ISR path, and iWake watermark programming.

## Important APIs, Types, And Functions
Key routines include `isys_probe()`, `isys_remove()`, runtime PM resume/suspend, `isys_register_devices()`, `isys_notifier_init()`, `isys_isr()`, `isys_isr_one()`, `ipu6_get_fw_msg_buf()`, `ipu6_put_fw_msg_buf()`, `ipu6_cleanup_fw_msg_bufs()`, and exported `update_watermark_setting()`. It uses `struct ipu6_isys`, `struct isys_fw_msgs`, `struct isys_iwake_watermark`, and `struct ltr_did`.

## Control Flow
Probe defers until the PCI parent marks the bus ready, allocates ISYS state and CSI-2 receivers, initializes locks/lists/streams, maps firmware in non-secure mode, allocates firmware command buffers, selects the PHY power callback by hardware version, and registers media/V4L2/video/CSI/notifier devices. Firmware message buffers are preallocated and moved between free and firmware-owned lists.

Runtime resume initializes the IPU6 MMU hardware, raises CPU latency QoS, starts TSC sync, marks ISYS powered, programs interrupt registers/CDC thresholds, and sets LTR/DID for ISYS-on. Runtime suspend clears power, resets `need_reset`, drops QoS, restores off LTR/DID, and marks MMU not ready.

The top-level ISR masks non-SW ISYS IRQs while draining CSI and firmware responses. CSI sync IRQs translate FS/FE by virtual channel into SOF/EOF events. Firmware responses complete stream command completions, return firmware message buffers on `PIN_DATA_READY`, complete vb2 buffers, update stream error state, and record SOF timestamps/sequences.

## State And Persistence
State persists only while the auxiliary device is bound. `power` protects ISR access, `need_reset` blocks later opens after firmware/HW cleanup anomalies, `stream_opened` blocks system suspend, and the watermark list tracks active stream data rates. No disk persistence exists.

## Dependencies And Integration Points
The driver integrates the IPU6 auxiliary bus, buttress/TSC, CPD firmware package directory, custom IPU6 DMA/MMU, IPU6 firmware ISYS ABI, media controller, V4L2 async sensor binding, `ipu_bridge` ACPI/fwnode sensor discovery, and CSI-2 PHY implementations.

## Risks And Test Signals
`isys_iwake_watermark_cleanup()` calls `list_del()` on the list head itself, which is unusual and worth static-analysis attention. `isys_remove()` unregisters devices before notifier cleanup, while probe error paths differ; teardown ordering should be stress-tested. Firmware response handling depends on valid stream handles and refcounts. Tests should include probe/remove, async sensor binding with invalid ports, runtime PM cycles, firmware timeouts/errors, CSI receiver error IRQs, suspend while streams are open, and iWake behavior with multiple active streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys.h

## Purpose
This header defines the central IPU6 ISYS device state, platform limits, firmware message buffer wrapper, async sensor data, CSI-2 configuration, iWake watermark state, and exported ISYS helper declarations.

## Important APIs, Types, And Data
Constants define entity naming, maximum firmware streams, firmware queue sizes, ISYS frame dimension limits, SRAM granularity/size by generation, and IPU6EP iWake LTR/mem-open defaults. `struct ipu6_isys` owns the media/V4L2 devices, auxiliary device, power state, stream tables/refcounts, firmware communication pointer, locks, platform data, PHY power callback, CSI-2 receivers, PM QoS request, firmware message buffer lists, async notifier, and watermark state. `struct isys_fw_msgs` is the DMA-visible union for frame-buffer-set and stream-config firmware messages.

## Control Flow
Consumers use this header to access shared ISYS state from video, queue, CSI-2, and core files. Runtime PM and firmware paths operate through fields such as `fwcom`, `need_reset`, `streams`, `framebuflist`, and `iwake_watermark`.

## State And Persistence
All fields are in-memory device-lifetime state. The stream array supports up to 16 firmware streams. `need_reset`, `power`, `ref_count`, and `stream_opened` are central state gates for open, runtime PM, and suspend behavior.

## Dependencies And Integration Points
The header depends on Linux mutex/spinlock/PM QoS/list types, media and V4L2 async/device types, IPU6 platform state, firmware ABI, CSI-2 receiver definitions, and video definitions. It exports PHY power functions and firmware message helpers across ISYS submodules.

## Risks And Test Signals
Because this is a shared state contract, field lifetime and locking are critical. Test signals include lockdep coverage for `streams_lock`, `power_lock`, `stream_mutex`, and watermark mutex; firmware buffer list leak checks; and stream refcount validation across multi-node capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-mmu.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-mmu.c

## Purpose
`ipu6-mmu.c` implements the IPU6 internal MMU page-table manager and hardware programming layer used by ISYS and PSYS auxiliary devices. It builds a two-level 32-bit IOVA page table, maps/unmaps pages for the custom IPU6 DMA layer, initializes hardware TLB stream registers, invalidates TLBs, and allocates a trash buffer used by MMU v2 invalidation workarounds.

## Important APIs, Types, And Functions
Exported APIs are `ipu6_mmu_init()`, `ipu6_mmu_cleanup()`, `ipu6_mmu_hw_init()`, `ipu6_mmu_hw_cleanup()`, `ipu6_mmu_map()`, `ipu6_mmu_unmap()`, and `ipu6_mmu_iova_to_phys()`. Internal helpers allocate dummy pages/L2 tables/L1 tables, map L2 pages, unmap ranges, invalidate TLBs, and allocate/destroy the trash-buffer IOVA range.

## Control Flow
`ipu6_mmu_init()` copies hardware variant descriptors, assigns register bases, creates `struct ipu6_mmu`, allocates the shared DMA mapping object, and builds dummy page-table state. `ipu6_mmu_hw_init()` writes the L1 page-table base and info bits into each MMU hardware block, configures L1/L2 stream block start registers, allocates the trash page/range if needed, and marks the MMU ready. `ipu6_mmu_map()` validates alignment and calls `l2_map()`, which allocates an L2 page table on first use, maps it for DMA, installs it in L1, fills L2 PTEs, and flushes cache lines. Unmap replaces entries with the dummy-page PTE. Hardware cleanup marks the MMU not ready; full cleanup unmaps/free tables and IOVA metadata.

## State And Persistence
The page table, dummy page, dummy L2 table, trash-page mapping, and IOVA allocator are in-memory and device-lifetime only. `ready_lock` guards whether invalidation can hit hardware; `mmu_info->lock` serializes table updates.

## Dependencies And Integration Points
The code depends on DMA mapping, Linux IOVA allocator, IPU6 hardware variant data from `ipu6.c`, register offsets from `ipu6-platform-regs.h`, and `ipu6-dma` users that call map/unmap.

## Risks And Test Signals
`l2_unmap()` logs unmapped L1 entries but continues without reducing `size`, which could loop through later L1 entries and end with a size warning; invalid unmap callers deserve testing. `ipu6_mmu_iova_to_phys()` assumes the L2 table pointer exists and can fault for dummy L1 regions. Cleanup manually frees `dummy_l2_pt` without `free_dummy_l2_pt()`, so DMA unmap symmetry should be checked. Tests should cover aligned/unaligned map/unmap, cross-L1 mappings, low-memory L2 allocation failures, trash-buffer allocation failure unwind, repeated runtime PM hardware init/cleanup, and DMA API debug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-mmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-mmu.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-mmu.h

## Purpose
This header defines the IPU6 MMU public data structures and function prototypes used by the PCI parent and auxiliary ISYS/PSYS devices.

## Important APIs, Types, And Data
`ISYS_MMID` and `PSYS_MMID` identify the input and processing system MMUs. `struct ipu6_mmu_info` stores the software page tables, dummy mappings, aperture, page-size bitmap, spinlock, and back-pointer to the DMA mapping. `struct ipu6_mmu` stores hardware block descriptors, MMU id, page-table base, owning device, DMA mapping, VMA list, trash page/IOVAs, ready state, ready lock, and invalidate callback.

Declared APIs initialize/cleanup the MMU object, initialize/cleanup hardware, map/unmap ranges, and translate IOVA to physical address.

## Control Flow
The PCI parent creates MMU objects before auxiliary devices are added. Runtime PM resume calls hardware init; runtime suspend calls hardware cleanup. DMA allocation/mapping paths call `ipu6_mmu_map()` and `ipu6_mmu_unmap()`.

## State And Persistence
MMU state persists while the parent PCI device is bound. The hardware-ready flag is separate from allocated page-table state so runtime PM can stop hardware without destroying mappings.

## Dependencies And Integration Points
This header is consumed by IPU6 PCI, ISYS, and DMA code. It relies on hardware variant descriptors declared elsewhere and Linux spinlock/list/page types.

## Risks And Test Signals
Callers must not use `ipu6_mmu_iova_to_phys()` on unmapped ranges. Tests should validate lifetime ordering: no DMA map calls after cleanup, no hardware invalidation after suspend, and no leaks in probe error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-platform-buttress-regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-platform-buttress-regs.h

## Purpose
This header provides IPU6 buttress register offsets, bit definitions, power-state encodings, firmware-security IPC constants, interrupt masks, TSC controls, and default frequency-control values.

## Important APIs, Types, And Data
The file defines ISYS/PSYS frequency control registers and default ratios, power-state masks and FSM values, BTRS control bits, firmware reset/security registers, firmware source address registers, ISR status/enable/clear registers, CSE/ISH IPC doorbell/data/CSR definitions, fabric commands, TSC registers, and aggregate masks `BUTTRESS_IRQS` and `BUTTRESS_EVENT`.

## Control Flow
This is definition-only code. Consumers in buttress and PCI code use the constants to power domains, authenticate firmware, service IPC interrupts, configure arbitration, synchronize TSC, and react to fatal/non-fatal hardware events.

## State And Persistence
No runtime state is defined here. The macros describe memory-mapped hardware state in the IPU6 PCI BAR.

## Dependencies And Integration Points
It depends on Linux `BIT()` and `GENMASK()`. It is included by the PCI parent and ISYS files and supports integration with CSE/ISH firmware authentication and interrupt handling.

## Risks And Test Signals
Register definitions are hardware contracts. Wrong masks or offsets cause power/authentication/interrupt failures. Tests are hardware bring-up oriented: firmware auth, runtime PM transitions, ISR clearing, watchdog/fatal error reporting, TSC reads, and secure/non-secure boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-platform-buttress-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-platform-isys-csi2-reg.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-platform-isys-csi2-reg.h

## Purpose
This header defines IPU6 ISYS CSI-2 receiver register offsets, interrupt register layouts, PPI/CSI front-end controls, hub controls, generation-specific top IRQ registers, and DPHY timing/control registers.

## Important APIs, Types, And Data
Macros cover per-port base address calculation, port reset/control registers, four IRQ groups per port, error IRQ masks for IPU6 and IPU6SE, FS/FE virtual-channel IRQ bits, PPI2CSI enable/configuration, CSI front-end mode/mux/sync controls, hub reset/access registers, top-level IRQ registers for IPU6 and IPU6V6/MTL, `IPU6_ISYS_UNISPART_IRQ_CSI2(port)`, and SIP/port DPHY timing offsets.

## Control Flow
This file is definition-only. CSI-2 receiver code and ISYS setup use the definitions to initialize receivers, clear/mask/enable interrupts, calculate per-port MMIO bases, and program DPHY timings.

## State And Persistence
No software state is stored here. It describes hardware registers and bit encodings.

## Dependencies And Integration Points
It depends on Linux bit helpers and is included by the IPU6 PCI/ISYS/CSI-2 paths. It must align with the hardware-generation data chosen in `ipu6_internal_pdata_init()`.

## Risks And Test Signals
The IRQ mapping and generation-specific offsets are risk areas: MTL uses different top IRQ addresses and firmware-access offsets. Test signals include CSI receiver probe on each hardware generation, FS/FE IRQ delivery per virtual channel, receiver error reporting, and DPHY timing programming for 2-lane and 4-lane sensors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-platform-isys-csi2-reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-platform-regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-platform-regs.h

## Purpose
This header defines shared IPU6 platform register offsets for ISYS/PSYS MMUs, SPC/DMEM regions, ISYS/PSYS interrupts, DMA/CD C thresholds, package directory placement, SPC status/control bits, info segment flags, pixel remapping constants, address-burst groups, and PSYS firmware IRQs.

## Important APIs, Types, And Data
Important definitions include unified offsets, ISYS/PSYS IOMMU offsets and stream-id register offsets, SPC/DMEM offsets, ISYS UNISPART/CSI-related IRQ registers, CDC threshold registers, CSI port counts, SPC status bits for start/run/ready/cache behavior, IPU information flags, pixel remapping no-op constants, address-burst group registers and target enums, NCI access mode enum, and PSYS GPDEV/FW IRQ offsets.

## Control Flow
The file has no executable flow. PCI, MMU, ISYS, PSYS, and firmware setup code use the constants to program hardware blocks and construct platform data.

## State And Persistence
There is no software state. Values describe memory-mapped hardware state.

## Dependencies And Integration Points
It depends on Linux bit helpers. It is one of the main hardware-contract headers used by `ipu6.c`, `ipu6-isys.c`, and `ipu6-mmu.c`.

## Risks And Test Signals
Hardware-generation assumptions are important. Wrong offsets can break firmware boot, MMU page-table programming, interrupts, or DMA routing. Tests should include firmware SPC boot, MMU init on ISYS and PSYS, ISYS CSI interrupts, PSYS firmware IRQs, and DMA capture integrity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-platform-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6.c

## Purpose
`ipu6.c` is the PCI parent driver for Intel IPU6 hardware. It identifies the hardware generation, loads and authenticates firmware, initializes buttress power/security state, creates ISYS and PSYS auxiliary devices, instantiates their MMUs and platform data, configures SPC firmware boot data, handles PCI/runtime PM, and cleans up all child devices on removal.

## Important APIs, Types, And Functions
The file defines generation-specific `isys_ipdata` and `psys_ipdata`, buttress control descriptors, `struct ipu6_cell_program`, exported `ipu6_configure_spc()`, and the PCI driver callbacks. Major functions include `ipu6_internal_pdata_init()`, `ipu6_isys_init()`, `ipu6_psys_init()`, `ipu6_pci_config_setup()`, `ipu6_configure_vc_mechanism()`, `ipu6_pci_probe()`, `ipu6_pci_remove()`, reset prepare/done handlers, and PM callbacks.

## Control Flow
Probe enables the PCI device, maps BAR0, sets the DMA mask, selects firmware and hardware version from PCI ID, fills internal platform data for the generation, initializes buttress, requests and validates CPD firmware, creates ISYS and PSYS auxiliary devices plus MMUs, powers PSYS enough to initialize its MMU, maps firmware and creates package directory, requests the shared IRQ, authenticates firmware, powers PSYS back down, configures VC arbitration, logs SKU/version, enables runtime PM, and finally marks the bus ready for auxiliary probes.

`ipu6_configure_spc()` invalidates SPC icache and either writes the secure-mode package directory IMR offset or parses the CPD package directory/cell program to configure icache base, master, start PC, and DMEM package directory pointer.

## State And Persistence
`struct ipu6_device` persists for the PCI device lifetime. It stores child bus devices, firmware pointer/name, BAR mapping, secure mode flags, hardware version, and `bus_ready_to_probe`. Runtime PM restore paths reapply buttress state and IPC reset when needed.

## Dependencies And Integration Points
The driver integrates PCI IDs from `ipu6-pci-table`, IPU bridge ACPI sensor setup, CPD firmware parsing, buttress authentication/IPC/IRQ code, auxiliary-bus child devices, IPU6 MMU, and ISYS/PSYS platform data.

## Risks And Test Signals
Probe error unwinding spans many resources; failures after child creation must clean MMUs, package directories, firmware mappings, IRQs, and firmware references in the right order. MSI behavior differs for IPU6EP/MTL. Secure versus non-secure SPC setup changes firmware address handling. Test signals include probe on every PCI ID, missing/invalid firmware, secure and non-secure boot, suspend/resume with IPC reset, PCI reset recovery, IRQ sharing, and child auxiliary probe deferral until `bus_ready_to_probe` is true.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6.h

## Purpose
This header defines the core IPU6 device identity, firmware names, hardware-version helpers, DMA/MMU limits, arbitration constants, MMU v2 trash-buffer workaround geometry, and the `struct ipu6_device` shared by the PCI parent and auxiliary children.

## Important APIs, Types, And Data
`enum ipu6_version` covers IPU6, IPU6SE, IPU6EP, and IPU6EP MTL. Inline helpers identify each version. Firmware names select generation-specific CPD blobs. `struct ipu6_device` stores the PCI device, child device list, ISYS/PSYS bus devices, buttress state, CPD firmware metadata, BAR base, reset/security flags, hardware version, and bus readiness. The header also defines MMU address limits, stream-cache limits, IOSF arbitration constants, DMA overshoot minimum, GDA page constants, and trash-buffer range/block offsets for MMU v2 invalidation.

## Control Flow
The header has no executable flow beyond inline version predicates. It provides constants that `ipu6.c`, `ipu6-mmu.c`, and ISYS code use during probe, firmware setup, MMU setup, and platform data initialization.

## State And Persistence
`struct ipu6_device` is the central in-memory state for the PCI device lifetime. Firmware and child pointers remain valid until remove unwinds them.

## Dependencies And Integration Points
It depends on Linux PCI/list types and `ipu6-buttress.h`. It is the common include for the IPU6 PCI, MMU, ISYS, and related support files.

## Risks And Test Signals
The hardware-version predicates gate register offsets, firmware names, port counts, and PHY callbacks; any new PCI ID must map to a correct version. MMU trash-buffer geometry is a hardware workaround and should be validated with DMA corruption tests and TLB invalidation stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ivsc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ivsc/Kconfig

## Purpose
This Kconfig entry defines `CONFIG_INTEL_VSC`, the Intel Visual Sensing Controller driver option.

## Important APIs, Types, And Data
`INTEL_VSC` is a tristate option titled "Intel Visual Sensing Controller". It depends on `INTEL_MEI`, `ACPI`, and `VIDEO_DEV`, and has an `IPU_BRIDGE || !IPU_BRIDGE` dependency to allow optional bridge integration without forcing that symbol. It selects `MEDIA_CONTROLLER`, `VIDEO_V4L2_SUBDEV_API`, and `V4L2_FWNODE`.

## Control Flow
Selecting this option builds IVSC support split into ACE and CSI drivers. ACE controls sensor ownership between IVSC firmware and host CPU; CSI controls the CSI-2 link ownership, routing destination, and link configuration.

## State And Persistence
No runtime state exists in this build file. It controls module availability.

## Dependencies And Integration Points
The entry wires IVSC into MEI client devices, ACPI-described camera platforms, V4L2 subdev/media-controller infrastructure, and optional IPU bridge support.

## Risks And Test Signals
Misconfigured dependencies can build IVSC without required V4L2 fwnode/subdev support or hide it on valid platforms. Build tests should cover built-in and module configurations, with and without `IPU_BRIDGE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ivsc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ivsc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ivsc/Makefile

## Purpose
This Makefile builds the Intel IVSC MEI client drivers.

## Important APIs, Types, And Data
When `CONFIG_INTEL_VSC` is enabled, it builds two modules/objects: `ivsc-csi.o` from `mei_csi.o` and `ivsc-ace.o` from `mei_ace.o`.

## Control Flow
There is no runtime flow. The file maps the single Kconfig symbol to the two logical IVSC drivers described in Kconfig.

## State And Persistence
No state is represented.

## Dependencies And Integration Points
The module names align with Kconfig help text and MEI client driver registration inside the C files.

## Risks And Test Signals
Build tests should confirm both modules are produced for `m` and linked for `y`, and that module names match expected autoload behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ivsc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ivsc/mei_ace.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ivsc/mei_ace.c

## Purpose
`mei_ace.c` is the Intel IVSC ACE MEI client driver. It sends firmware IPC commands to get the ACE firmware id and switch camera sensor ownership between IVSC firmware and the host CPU. It also links runtime PM with the IVSC CSI MEI device and clears ACPI dependencies after switching ownership to the host.

## Important APIs, Types, And Functions
The file defines ACE command/notification bitfield structures, command IDs (`ACE_GET_FW_ID`, switch to host/IVSC), event types, and `struct mei_ace`. Key functions are `construct_command()`, `mei_ace_send()`, `ace_set_camera_owner()`, `ace_get_firmware_id()`, `mei_ace_rx()`, `mei_ace_setup_dev_link()`, `mei_ace_post_probe_work()`, probe/remove, and runtime suspend/resume.

## Control Flow
Probe allocates state, enables the MEI client, registers the receive callback, sends `ACE_GET_FW_ID`, enables runtime PM, finds the sibling CSI MEI client by UUID-derived child name, creates a PM runtime device link, and schedules work. The work switches camera ownership to the host and clears ACPI dependencies so sensor devices can probe.

`mei_ace_send()` serializes commands with a mutex and one completion. It waits first for an ACK, validates command id/status, and for ownership commands waits for a second command response. RX distinguishes ACK notifications from events, stores ACK/response data, updates firmware id on `GET_FW_ID`, and completes waiters.

Runtime suspend switches the camera back to IVSC; runtime resume switches it to host. Remove cancels work, drops the device link, disables PM, switches to IVSC, disables MEI, and destroys the mutex.

## State And Persistence
State is per MEI client: firmware id, latest ACK/response, completion, mutex, CSI device/link, and post-probe work. Sensor ownership is hardware/firmware state, not persistent storage.

## Dependencies And Integration Points
The driver depends on MEI client bus, ACPI, runtime PM, workqueues, and the IVSC CSI sibling UUID. It coordinates with camera sensor ACPI dependencies and with the CSI driver through a PM runtime device link.

## Risks And Test Signals
`mei_ace_setup_dev_link()` stores `ace->csi_dev = csi_dev` after `put_device(csi_dev)`, but the stored pointer is not later dereferenced except link deletion; still, pointer lifetime should be reviewed if future code uses it. Command ACK/response matching relies on one outstanding command. Tests should cover firmware timeout, killable waits, bad ACK command id/status, missing CSI sibling/fwnode deferral, runtime PM ownership flips, remove while work is pending, and sensor probe sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ivsc/mei_ace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ivsc/mei_csi.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ivsc/mei_csi.c

## Purpose
`mei_csi.c` is the Intel IVSC CSI MEI client and V4L2 bridge driver. It exposes a two-pad V4L2 subdevice between a sensor and the host IPU pipeline, sends MEI commands to assign CSI-2 link ownership and configure lane/frequency parameters, forwards stream-on/off to the remote sensor, and reports privacy state through a read-only V4L2 control.

## Important APIs, Types, And Functions
Important structures include `struct csi_link_cfg`, `struct csi_cmd`, `struct csi_notif`, and `struct mei_csi`. Key functions are `mei_csi_send()`, `csi_set_link_owner()`, `csi_set_link_cfg()`, `mei_csi_rx()`, `mei_csi_set_stream()`, `mei_csi_set_fmt()`, `mei_csi_get_mbus_config()`, async notifier bound/unbind callbacks, `mei_csi_init_controls()`, `mei_csi_parse_firmware()`, probe, and remove.

## Control Flow
Probe first finds any IPU6 PCI device and initializes IPU bridge sensor fwnodes, requires the MEI device to have fwnode data, enables MEI, registers RX, parses firmware graph endpoints, then initializes and registers the V4L2 subdev. Firmware parsing reads sink/source endpoints, requires matching CSI-2 lane counts, and registers an async notifier for the remote sensor. The bound callback links the remote sensor source pad to the IVSC CSI sink pad.

On stream-on from V4L2, the driver obtains the remote link frequency, switches CSI link ownership to host, sends lane/frequency configuration, waits an empirical 100 ms, then starts the remote sensor. Stream-off stops the remote sensor and switches link ownership back to IVSC. RX handles privacy notifications by updating `V4L2_CID_PRIVACY` and command responses by completing the command wait.

## State And Persistence
The driver stores current streaming state, lane count, link frequency, remote pad pointer, command response/completion, V4L2 controls, and active subdev state. No file persistence exists. Privacy state is cached in the V4L2 control.

## Dependencies And Integration Points
It depends on MEI, IPU bridge, IPU6 PCI ID table, V4L2 async/subdev/fwnode/control frameworks, media-controller links, and the remote sensor's link-frequency control and `s_stream` op.

## Risks And Test Signals
Probe calls `mei_csi_parse_firmware()` before `v4l2_subdev_init()`, but `v4l2_async_subdev_nf_init()` receives `&csi->subdev`; this ordering is worth verifying against V4L2 notifier expectations. `mei_csi_set_stream()` assumes `csi->remote` is bound before streaming. Command status `-1` is translated to privacy-on success, which should be documented in tests. Test invalid lane mismatch, missing endpoints, remote sensor unbind, link-frequency absence, command timeout, privacy notifications, stream-on error unwinding to IVSC ownership, and format propagation across both pads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ivsc/mei_csi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/Kconfig

## Purpose
This Kconfig file declares the ivtv PCI media driver family: MPEG encoder/decoder support, optional ALSA PCM capture, and optional framebuffer support for Conexant cx23415/cx23416 devices.

## Important APIs, Types, And Data
`VIDEO_IVTV` is the main tristate driver for cx23415/cx23416 PCI PVR cards. It depends on `VIDEO_DEV`, `PCI`, `I2C`, and `RC_CORE`, selects several tuner/video/audio decoder/encoder helper drivers, and builds the `ivtv` module. `VIDEO_IVTV_ALSA` depends on `VIDEO_IVTV` and `SND`, selects `SND_PCM`, and builds `ivtv-alsa`. `VIDEO_FB_IVTV` depends on `VIDEO_IVTV` and `FB`, selects framebuffer I/O memory helpers, and builds `ivtvfb`. `VIDEO_FB_IVTV_FORCE_PAT` optionally forces framebuffer init under x86 PAT.

## Control Flow
The Kconfig choices determine which ivtv companion modules are available. The ALSA option provides a PCM capture interface in addition to the V4L2 PCM stream.

## State And Persistence
No runtime state is represented here.

## Dependencies And Integration Points
The file integrates ivtv with V4L2, PCI, I2C, RC core, ALSA PCM, framebuffer support, tuner drivers, EEPROM support, and multiple analog video/audio subdevice drivers.

## Risks And Test Signals
The broad `select` list can force-build many helper drivers; configuration tests should cover modular and built-in combinations. ALSA must not be selectable without main ivtv and sound core. Framebuffer PAT behavior should be tested only on relevant x86 systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/Makefile

## Purpose
This Makefile assembles the ivtv driver objects and optional companion modules.

## Important APIs, Types, And Data
`ivtv-objs` includes routing, card tables, controls, driver core, file ops, firmware, GPIO, I2C, ioctl, IRQ, mailbox, queues, streams, UDMA, VBI, and YUV objects. `ivtv-alsa-objs` includes `ivtv-alsa-main.o` and `ivtv-alsa-pcm.o`. Object inclusion follows `CONFIG_VIDEO_IVTV`, `CONFIG_VIDEO_IVTV_ALSA`, and `CONFIG_VIDEO_FB_IVTV`. Additional include paths point to media tuners and DVB frontends.

## Control Flow
No runtime flow exists; this file controls build composition.

## State And Persistence
No state is represented.

## Dependencies And Integration Points
It maps Kconfig selections to module objects and includes tuner/frontend headers needed by ivtv source files.

## Risks And Test Signals
Build tests should verify that `ivtv-alsa` links only when ALSA support is enabled and that include paths remain valid after media tree moves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-alsa-main.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-alsa-main.c

## Purpose
`ivtv-alsa-main.c` registers an ALSA capture card for each ivtv device with an enabled PCM stream. It hooks into the ivtv extension init callback, creates `struct snd_ivtv_card`, creates the PCM device, registers the ALSA card, and tears cards down during module unload.

## Important APIs, Types, And Functions
The file defines module parameters `debug` and `index[]`, global `ivtv_alsa_debug`, and helper functions `snd_ivtv_card_create()`, `snd_ivtv_card_set_names()`, `snd_ivtv_init()`, `ivtv_alsa_load()`, `snd_ivtv_exit()`, and `ivtv_alsa_exit_callback()`. It uses `struct snd_ivtv_card` from `ivtv-alsa.h` and `snd_ivtv_pcm_create()` from `ivtv-alsa-pcm.c`.

## Control Flow
Module init sets `ivtv_ext_init` to `ivtv_alsa_load`, letting the main ivtv driver call into ALSA setup for each card. `ivtv_alsa_load()` skips disabled PCM streams and duplicate ALSA instances, then calls `snd_ivtv_init()`. Card initialization creates an ALSA card, attaches private data, sets driver/short/long names, creates the PCM capture device, stores `itv->alsa` before registration to avoid races, and registers the card.

Module exit finds the `ivtv` PCI driver, iterates devices, retrieves each V4L2 device's ALSA card, frees the ALSA card, clears `itv->alsa`, and clears `ivtv_ext_init`.

## State And Persistence
State is live module/device state only: `itv->alsa` links ivtv to ALSA private data, and ALSA card lifetime is managed by `snd_card_free()`. Module parameters persist only while loaded.

## Dependencies And Integration Points
The file integrates ivtv core, V4L2 device state, ALSA core, PCI driver iteration, and the PCM implementation.

## Risks And Test Signals
In `snd_ivtv_init()` error handling, `snd_card_free(sc)` will call private free after `snd_ivtv_card_create()`, then the code also `kfree(itvsc)`, creating a potential double free. Module exit calls `driver_find()` without checking for NULL before `driver_for_each_device()`. Tests should cover PCM-disabled cards, duplicate load, ALSA registration failure, module unload while cards exist, and KASAN/KFENCE around error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-alsa-main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-alsa-pcm.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-alsa-pcm.c

## Purpose
`ivtv-alsa-pcm.c` implements the ALSA PCM capture device that receives PCM audio packets from the ivtv encoder stream and copies them into the ALSA runtime ring buffer.

## Important APIs, Types, And Functions
The file defines `snd_ivtv_hw_capture` with fixed S16_LE, 48 kHz, stereo capture constraints, module parameter `pcm_debug`, callback `ivtv_alsa_announce_pcm_data()`, ALSA ops for open/close/prepare/trigger/pointer, and exported `snd_ivtv_pcm_create()`.

## Control Flow
`snd_ivtv_pcm_create()` creates one capture-only PCM device, initializes the card spinlock, installs capture ops, uses a vmalloc managed buffer, and names the PCM after the ivtv card. Opening the PCM serializes against ivtv V4L2 file operations, initializes hardware on first open, claims the ivtv PCM stream, assigns hardware constraints, stores the substream, installs `itv->pcm_announce_callback`, marks the stream as streaming, and starts the ivtv V4L2 encode stream. Closing stops the encode stream, clears streaming state, releases the stream, and removes the announce callback.

`ivtv_alsa_announce_pcm_data()` is called by ivtv when PCM bytes arrive. It validates the substream/runtime/dma area, converts byte count to frames, copies data into the ALSA ring buffer with wrap handling, updates hardware pointer and period accounting under ALSA stream lock, and calls `snd_pcm_period_elapsed()` when a period completes.

## State And Persistence
`struct snd_ivtv_card` stores the active capture substream, hardware pointer, and period-progress counter. State resets on prepare/open and is not persistent beyond module/device lifetime.

## Dependencies And Integration Points
The file integrates ALSA PCM core with ivtv stream claiming, stream start/stop, and the ivtv PCM announce callback. It relies on `snd_ivtv_lock()` using ivtv's serialize mutex.

## Risks And Test Signals
`ivtv_alsa_announce_pcm_data()` updates `hwptr_done_capture` under `snd_pcm_stream_lock()`, while `snd_ivtv_pcm_pointer()` reads it under `itvsc->slock`; these are different locks, so pointer reads can race. The trigger op is a no-op, so ALSA start/stop semantics are mostly handled at open/close. Tests should cover ring wrap, period elapsed cadence, concurrent pointer callback, stream already busy, close during packet delivery, and ALSA hw_params near min/max period settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-alsa-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-alsa-pcm.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-alsa-pcm.h

## Purpose
This small header declares the PCM creation entry point for the ivtv ALSA companion driver.

## Important APIs, Types, And Data
It forward-depends on `struct snd_ivtv_card` from `ivtv-alsa.h` and declares `int snd_ivtv_pcm_create(struct snd_ivtv_card *itvsc);`.

## Control Flow
`ivtv-alsa-main.c` calls `snd_ivtv_pcm_create()` while building the ALSA card. The implementation creates and configures the capture PCM device.

## State And Persistence
No state is stored in this header.

## Dependencies And Integration Points
It is the interface between the ALSA card setup file and the PCM implementation file.

## Risks And Test Signals
The declaration must remain synchronized with the implementation. Build tests catch signature drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-alsa-pcm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-alsa.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-alsa.h

## Purpose
This header defines the shared private state and logging/locking helpers for the ivtv ALSA companion module.

## Important APIs, Types, And Data
`struct snd_ivtv_card` stores the parent `v4l2_device`, ALSA `snd_card`, period progress, capture hardware pointer, active capture substream, and spinlock. It declares `ivtv_alsa_debug`, wraps ivtv's `serialize_lock` in `snd_ivtv_lock()`/`snd_ivtv_unlock()`, defines debug flag bits, and provides logging macros for warning/info/error output.

## Control Flow
ALSA card and PCM code use the structure as their shared context. PCM open/close take the ivtv serialize lock through the inline helpers before claiming/stopping the ivtv PCM stream.

## State And Persistence
The structure is allocated per ivtv ALSA card and persists until the ALSA card is freed. It stores only runtime counters and pointers.

## Dependencies And Integration Points
The header assumes `to_ivtv()` and ivtv core types are visible from including source files. It integrates ALSA private data with ivtv V4L2 device state and stream serialization.

## Risks And Test Signals
The logging macros reference a local `v4l2_dev` symbol, so callers must have that variable in scope. The spinlock in the structure should protect pointer/counter state consistently; current PCM code uses mixed locks. Tests should include sparse/build coverage and concurrency testing around PCM callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-alsa.h -->
