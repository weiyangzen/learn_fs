# Research: subset-b-005400

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_compat_css20.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_compat_css20.c

## Purpose
This file is the main AtomISP CSS 2.x compatibility layer. It adapts the Linux/V4L2-facing atomisp driver to the Intel IA CSS firmware API, including firmware loading, MMIO callbacks, CSS pipe and stream creation, ISP parameter propagation, video/stat/metadata buffer queueing, event dispatch, and allocation/freeing of CSS-owned statistics data. It is the central runtime bridge between `atomisp_sub_device` state and the firmware's `ia_css_*` interfaces.

## Important APIs and Functions
- MMIO callbacks: `atomisp_css2_hw_store_8/16/32`, `atomisp_css2_hw_load_8/16/32`, `atomisp_css2_hw_store`, and `atomisp_css2_hw_load` serialize ISP register access through `mmio_lock` and are installed into `ia_css_env.hw_access_env` by `atomisp_css_load_firmware()`.
- Firmware/CSS lifecycle: `atomisp_css_load_firmware()`, `atomisp_css_init()`, and `atomisp_css_uninit()` set CSS firmware pointers, MMU base, print hooks, and `isp->css_initialized`.
- Pipe/stream lifecycle: `atomisp_create_pipes_stream()`, `atomisp_destroy_pipes_stream()`, `atomisp_css_update_stream()`, `atomisp_css_start()`, and `atomisp_css_stop()` create, destroy, start, and reset CSS pipe/stream objects stored under `asd->stream_env[]`.
- Configuration mutators: functions such as `atomisp_css_input_set_resolution()`, `atomisp_css_input_set_format()`, `atomisp_css_video_configure_output()`, `atomisp_css_capture_configure_pp_input()`, `atomisp_css_input_configure_port()`, and `atomisp_css_video_set_dis_envelope()` update `ia_css_stream_config`, `ia_css_pipe_config`, and `ia_css_pipe_extra_config`.
- Buffer APIs: `atomisp_q_video_buffer_to_css()`, `atomisp_q_metadata_buffer_to_css()`, `atomisp_q_s3a_buffer_to_css()`, `atomisp_q_dis_buffer_to_css()`, `atomisp_css_dequeue_buffer()`, and `atomisp_css_queue_buffer()` wrap `ia_css_pipe_enqueue_buffer()` and `ia_css_pipe_dequeue_buffer()`.
- Statistics and metadata allocation: `atomisp_css_allocate_stat_buffers()`, `atomisp_css_free_stat_buffers()`, `atomisp_alloc_3a_output_buf()`, `atomisp_alloc_dis_coef_buf()`, and `atomisp_alloc_metadata_output_buf()` allocate IA CSS 3A, DVS/DIS, and metadata buffers, often mapping CSS/HMM memory into CPU address space.
- Event handling: `atomisp_css_isr_thread()` drains CSS psys events and routes frame/stat/metadata completions to `atomisp_buf_done()`, while FW assert events queue `isp->assert_recovery_work`.
- ISP parameter get/set wrappers: many `atomisp_css_get_*_config()` and `atomisp_css_set_*()` functions translate between AtomISP public structs and IA CSS config objects.

## Control Flow
Firmware setup starts with `atomisp_css_load_firmware()`, which installs the hardware access callbacks and calls `ia_css_load_firmware()`. `atomisp_css_init()` then gets the HMM/MMU page directory base and calls `ia_css_init()`. Per-open or format setup initializes stream/pipe defaults with `atomisp_css_init_struct()` and mutates them through subdev/ioctl helpers. Before streaming, `atomisp_create_pipes_stream()` calls `__create_pipes()` for run-mode-valid pipe IDs and then `__create_streams()` to bind those pipes into IA CSS streams. `atomisp_css_start()` starts the SP and every created CSS stream. During streaming, vb2 code queues output frames and side buffers into CSS, and the IRQ thread translates CSS completion events back into atomisp buffer completion and V4L2 events. Stream-off calls `atomisp_css_stop()`, which destroys streams/pipes before `ia_css_stop_sp()` because the CSS API requires that ordering, resets raw-buffer tracking, moves in-CSS stats buffers back to free lists, frees queued parameters, and optionally resets CSS config defaults.

## State and Persistence
Persistent runtime state lives in `struct atomisp_sub_device`: `stream_env[]` contains IA CSS stream pointers, pipe pointers, configs, stream state, channel IDs, ISYS configs, and update flags; `params` contains active CSS parameter blobs, grid info, metadata user buffers, DVS state, and update flags. `struct atomisp_device` contributes global CSS firmware/env, MMIO base, HMM/MMU integration, hardware revision, and `css_initialized`. The file also relies on the global `atomisp_dev` to find the active device from MMIO callbacks and on the global `dbg_func` for CSS debug print behavior. In-memory lists for 3A, DIS, and metadata buffers are persistent across streaming until explicitly freed.

## Dependencies and Integration Points
This code depends heavily on Intel IA CSS headers and runtime (`ia_css_*`, `sh_css_*`, `ia_css_isys_*`), the AtomISP command layer (`atomisp_cmd.h`), buffer/file operations (`atomisp_fops.h`), ioctls (`atomisp_ioctl.h`), HMM (`hmm_*`), and MMU glue (`sh_mmu_mrfld`). It is called by `atomisp_fops.c` for vb2 queueing, by `atomisp_ioctl.c` for stream start/stop and parameter application, and by `atomisp_subdev.c` for media bus format/selection changes. CSI timing code in `atomisp_csi2.c` also uses exported MMIO store helpers.

## Risks
- MMIO callbacks dereference global `atomisp_dev`; incorrect driver data or multi-device assumptions would be fragile.
- CSS object lifetime is complex: failure paths destroy and recreate streams/pipes, and the API requires specific ordering around `ia_css_stop_sp()`.
- Many functions assume caller-side serialization through `isp->mutex`; missing lock coverage would corrupt stream or buffer queues.
- Several paths use legacy workarounds and FIXME comments, including copy-mode ISP parameter updates, pipe ID translation, hard-coded MIPI buffer fallbacks, and disabled/limited firmware features.
- User-copy-heavy DIS coefficient/stat paths must match current grid dimensions and buffer byte counts; stale grid information returns `-EAGAIN`, but misuse can still surface as `-EFAULT` or invalid statistics.
- Stats and metadata lists are manually spliced between free, in-CSS, and ready states, making leak/double-free regressions likely if event paths change.

## Test Signals
Useful signals include successful firmware load/init, successful `atomisp_create_pipes_stream()` for preview/video/capture/copy modes, `ia_css_pipe_get_info()` returning expected frame sizes after format changes, vb2 queue/dequeue under sustained streaming, CSS event processing for output, 3A, DIS, and metadata buffers, FW assert recovery work scheduling, stream-off followed by stream-on after the reset workaround, and fault-injection on CSS allocation and stream creation rollback paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_compat_css20.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_compat_css20.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_compat_css20.h

## Purpose
This header defines the CSS 2.x compatibility contract shared by the AtomISP driver. It exposes CSS stream state, stream environment, firmware environment, CSS event/buffer wrappers, and statistics buffer types used by the implementation in `atomisp_compat_css20.c` and by other AtomISP modules.

## Important APIs and Types
- Constants such as `ATOMISP_CSS2_PIPE_MAX`, continuous-frame defaults, DVS frame delay, MIPI buffer fallback sizes, and `MAX_STREAMS_PER_CHANNEL` encode CSS 2.x behavior.
- `enum atomisp_css_stream_state` tracks stream lifecycle: uninitialized, created, started, and stopped.
- `struct atomisp_css_isys_config_info` records input-format and dimensions for multi-stream ISYS configurations on one virtual channel.
- `struct atomisp_stream_env` is the key per-input-stream state container: IA CSS stream pointer, stream config/info, pipe arrays, pipe configs, extra configs, update flags, ACC stream state, virtual channel ID, and per-channel ISYS info.
- `struct atomisp_css_env` wraps IA CSS firmware and environment structures.
- `struct atomisp_s3a_buf`, `struct atomisp_dis_buf`, `struct atomisp_css_buffer`, and `struct atomisp_css_event` are driver-side wrappers around IA CSS buffer/event objects.
- The header declares CSS parameter setters, debug helpers, firmware loading, DVS grid access, and debug function controls.

## Control Flow
This header does not implement control flow directly; it defines the data structures that drive CSS lifecycle control in the C file. Code in subdev and ioctl layers populates `atomisp_stream_env` config fields, then the compatibility layer creates IA CSS pipes/streams from those fields. The declared setter APIs update pending `asd->params.config` fields, which are later applied to the running CSS stream or to a specific pipe.

## State and Persistence
`atomisp_stream_env` instances persist inside `atomisp_sub_device` across open/format/stream operations. Pipe configs and update flags persist until stream stop or reinitialization resets them. Statistics buffer wrapper structures are list nodes whose ownership moves between free, CSS-owned, and ready lists. `atomisp_css_env` persists inside `atomisp_device` for the lifetime of firmware/CSS initialization.

## Dependencies and Integration Points
The header includes V4L2 media bus definitions and IA CSS headers (`ia_css.h`, `ia_css_types.h`, `ia_css_acc_types.h`, `sh_css_legacy.h`). It forward-declares AtomISP device/subdevice types to avoid pulling the full internal header into every caller. It integrates with `atomisp_fops.c`, `atomisp_ioctl.c`, `atomisp_subdev.c`, and the command layer through its shared CSS configuration and setter declarations.

## Risks
The structures expose raw IA CSS pointers and fixed-size arrays indexed by IA CSS enum values, so enum drift or out-of-range pipe/stream IDs can corrupt state. The header only declares a subset of functions implemented in the C file; additional prototypes likely live in `atomisp_compat.h`, so maintainers must check both interfaces when changing CSS glue. State fields such as `stream_state`, `update_pipe[]`, and `isys_info[]` are not self-synchronizing and depend on higher-level locking.

## Test Signals
Compile coverage is important because this header binds many IA CSS types. Runtime validation should confirm stream state transitions, pipe-array indexing, ACC stream isolation, multi-ISYS configuration defaults, and statistics buffer list ownership under stream start/stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_compat_css20.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_csi2.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_csi2.c

## Purpose
This file implements AtomISP's MIPI CSI-2 V4L2 subdevice entities and receiver timing setup. Each CSI2 port is represented as a V4L2 subdev with sink/source pads that bridge camera sensors to the Atom ISP subdev.

## Important APIs and Functions
- `atomisp_csi2_set_ffmt()` validates and applies media-bus formats, clamps dimensions, and mirrors the sink format to the source pad.
- `csi2_enum_mbus_code()`, `csi2_get_format()`, and `csi2_set_format()` provide V4L2 pad operations.
- `mipi_csi2_init_entities()` initializes each CSI2 subdev, pads, media entity function, and default formats.
- `atomisp_mipi_csi2_register_entities()` and `atomisp_mipi_csi2_unregister_entities()` handle V4L2/media registration cleanup.
- `atomisp_csi2_configure()` conditionally calls `atomisp_csi2_configure_isp2401()` to program ISP2401 CSI receiver delay registers.
- `atomisp_mipi_csi2_init()` initializes the firmware/software-node bridge and all CSI2 port entities.

## Control Flow
Initialization starts with `atomisp_mipi_csi2_init()`, which calls `atomisp_csi2_bridge_init()` to create firmware graph data, then loops over `ATOMISP_CAMERA_NR_PORTS` and initializes each `isp->csi2_port[i]`. Format setting on the sink pad resolves the requested media-bus code through `atomisp_find_in_fmt_conv()`, clamps width/height to AtomISP limits, stores field information, and recursively updates the source pad. Source-pad set always mirrors the sink pad, with a FIXME for DPCM decompression. When streaming starts, `atomisp_csi2_configure()` calculates per-lane timing values from the sensor's `V4L2_CID_LINK_FREQ` and writes CSI2 delay registers through the CSS MMIO store helper.

## State and Persistence
Each `struct atomisp_mipi_csi2_device` stores two pad formats and a back-pointer to `atomisp_device`. Formats persist in `csi2->formats[]` for active state, while try formats live in `v4l2_subdev_state`. CSI receiver timing is programmed into hardware registers at stream start and is not represented as persistent driver state beyond sensor link frequency and current input port.

## Dependencies and Integration Points
This file depends on `atomisp_subdev.c` for input format conversion tables, `atomisp_internal.h` for device state and hardware-revision checks, `atomisp-regs.h` for CSI register offsets, and `atomisp_compat_css20.c` for `atomisp_css2_hw_store_32()`. It integrates into the media graph as a bridge between sensor subdevs and the Atom ISP processing subdev.

## Risks
The source format always mirrors the sink format, so compressed DPCM input is not decompressed despite the FIXME. `atomisp_csi2_configure_isp2401()` assumes valid `asd->input_curr`, sensor control handler, and port index; missing link-frequency controls fall back to default timing. Port and lane tables are fixed and must match hardware. The cleanup function is empty, so resource ownership remains in registration/unregistration paths.

## Test Signals
Test by enumerating CSI2 mbus codes, setting sink/source pad formats in active and try states, verifying media graph links, streaming on ISP2401 sensors with and without `V4L2_CID_LINK_FREQ`, and reading back or tracing writes to CSI2 delay registers for primary/secondary/tertiary ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_csi2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_csi2.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_csi2.h

## Purpose
This header declares the AtomISP CSI2 subdevice interface, including pad indices, the per-port device structure, entity lifecycle functions, ACPI/software-node bridge entry points, and receiver configuration hooks.

## Important APIs and Types
- Pad constants `CSI2_PAD_SINK`, `CSI2_PAD_SOURCE`, and `CSI2_PADS_NUM` define the media entity topology.
- `struct atomisp_mipi_csi2_device` embeds `struct v4l2_subdev`, two media pads, active pad formats, a V4L2 control handler, and an `atomisp_device` back-pointer.
- Exported functions cover format setting, init/cleanup, entity register/unregister, bridge init/firmware parse, and stream-time CSI2 configuration.

## Control Flow
The header is consumed by AtomISP PCI setup and internal code. Driver probe initializes CSI2 bridge and entities through `atomisp_mipi_csi2_init()`, firmware parsing registers async sensor matches through `atomisp_csi2_bridge_parse_firmware()`, media graph registration calls `atomisp_mipi_csi2_register_entities()`, and stream start calls `atomisp_csi2_configure()`.

## State and Persistence
CSI2 state is per `atomisp_mipi_csi2_device`. The embedded V4L2 subdev and media pads persist while the AtomISP device is registered. Active pad formats persist in the `formats` array; try-state formats are separate V4L2 framework state.

## Dependencies and Integration Points
The header includes GPIO/property and V4L2 subdev/control headers, plus AtomISP UAPI definitions. It is included by `atomisp_internal.h` so `struct atomisp_device` can embed `csi2_port[]`, and by CSI2 bridge/entity implementation files.

## Risks
Because `atomisp_device` embeds a fixed array of CSI2 devices, `ATOMISP_CAMERA_NR_PORTS` and pad constants must stay consistent with hardware and firmware graph parsing. Any new CSI2 controls must be reflected in the control handler lifetime and registration paths.

## Test Signals
Compile-time inclusion through `atomisp_internal.h`, media entity pad count checks, successful subdev registration for every port, and correct async sensor-to-port matching are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_csi2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_csi2_bridge.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_csi2_bridge.c

## Purpose
This file builds the firmware/software-node camera graph for AtomISP2 sensors described by ACPI and wires sensors into the V4L2 async notifier. It replaces missing or incomplete firmware graph data with software nodes, GPIO mappings, clock defaults, port/lane configuration, and optional VCM information.

## Important APIs and Functions
- `atomisp_csi2_bridge_init()` invokes `ipu_bridge_init()` with AtomISP-specific sensor parsing and deliberately leaves successful bridge nodes attached across module unload/reload.
- `atomisp_csi2_parse_sensor_fwnode()` derives per-sensor CSI port, lane count, mclk, orientation, GPIO mapping, and optional VCM type.
- `gmin_cfg_get_dsm()`, `gmin_cfg_get_dmi_override()`, `gmin_cfg_get()`, and `gmin_cfg_get_int()` read Intel DSM strings with DMI override support.
- `atomisp_csi2_get_pmc_clk_nr_from_acpi_pr0()` parses ACPI `_PR0` clock resources.
- `atomisp_csi2_set_pmc_clk_freq()` forces PMC platform clocks to 19.2 MHz where needed.
- `atomisp_csi2_add_gpio_mappings()` reuses INT3472 discrete GPIO parsing by constructing a faux `int3472_discrete_device`.
- Async notifier callbacks bind/unbind sensor subdevs and complete by calling `atomisp_register_device_nodes()`.
- `atomisp_csi2_bridge_parse_firmware()` parses graph endpoints, records lane counts, and registers remote fwnode async connections.

## Control Flow
`atomisp_csi2_bridge_init()` runs early during CSI2 init. If the AtomISP device already has a secondary fwnode it exits, otherwise `ipu_bridge_init()` scans sensors and calls `atomisp_csi2_parse_sensor_fwnode()` for each. Sensor parsing starts with HID defaults, obtains a PMC clock number from `_PR0`, sets the clock rate, derives or overrides CSI port, reads or defaults lanes, installs GPIO mappings, sets mclk/orientation, and optionally reads VCM type from a DSM. Later `atomisp_csi2_bridge_parse_firmware()` initializes `isp->notifier`, iterates fwnode graph endpoints by port ID, parses CSI2 endpoints, stores lane counts into `isp->sensor_lanes[mipi_port]`, and adds async remote fwnode matches. When every sensor is bound, `.complete()` registers AtomISP device nodes.

## State and Persistence
Bridge-created software nodes and faux INT3472 mappings are intentionally leaked on successful setup because they are intended to remain valid for the boot lifetime. Sensor binding state persists in `isp->sensor_subdevs[port]`, lane counts persist in `isp->sensor_lanes[]`, and async connection objects are owned by the V4L2 notifier. DMI override tables are static and immutable.

## Dependencies and Integration Points
This file depends on ACPI, DMI, common clock framework, INT3472 GPIO helpers, `ipu_bridge`, V4L2 fwnode parsing, and AtomISP internals. It integrates with `atomisp_mipi_csi2_init()`, `atomisp_register_device_nodes()`, and the media graph setup that later selects sensor inputs.

## Risks
The code contains platform-specific quirks for devices with incorrect DSM data; missing quirks may select the wrong CSI port or lane count. Successful bridge allocation is intentionally leaked, so repeated partial failures must be checked for cleanup behavior. GPIO mapping via faux INT3472 state depends on ACPI CRS semantics. The VCM path is disabled for some known sensors due to stream-start failures. `atomisp_csi2_bridge_parse_firmware()` returns immediately on a parse error and must release endpoint handles on every path.

## Test Signals
Signals include boot-time bridge creation on ACPI systems lacking native graph data, correct DMI override selection on Lenovo Miix 310 and Xiaomi Mipad2, PMC clock rate set to 19.2 MHz, GPIO mappings visible to sensor drivers, async notifier binding one sensor per port, lane counts matching endpoint data, and successful `atomisp_register_device_nodes()` after notifier completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_csi2_bridge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_dfs_tables.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_dfs_tables.h

## Purpose
This header defines the data model for AtomISP dynamic frequency scaling tables. It describes when the ISP should run at a given frequency based on image size, frame rate, and run mode.

## Important APIs and Types
- `struct atomisp_freq_scaling_rule` contains width, height, fps, ISP frequency, and run mode fields.
- `struct atomisp_dfs_config` names the low, max-at-voltage-minimum, and highest frequencies and points to a rule table plus table size.
- `dfs_config_cht_soc` is declared as the Cherry Trail SoC DFS configuration exported elsewhere.

## Control Flow
This file does not implement logic. Runtime DFS users, such as stream start/stop in `atomisp_ioctl.c`, consult the `atomisp_device::dfs` configuration and call frequency-scaling code to select `ATOMISP_DFS_MODE_AUTO`, low, or max operating points.

## State and Persistence
DFS config is immutable table data. `atomisp_device` stores a pointer to the chosen `atomisp_dfs_config`, plus current hardware frequency state in fields such as `running_freq` and `hpll_freq` declared in `atomisp_internal.h`.

## Dependencies and Integration Points
The header only includes `<linux/kernel.h>` and is included by AtomISP internals. It integrates with platform/PCI setup that chooses a DFS table and with stream start/stop paths that request frequency changes.

## Risks
Incorrect table entries can underclock the ISP for a resolution/fps/run-mode combination, causing dropped frames or CSS timeouts, or overclock it unnecessarily. The type uses plain unsigned integers without units encoded in names, so maintainers must preserve conventions.

## Test Signals
Validate by checking selected frequency during preview, video, and still capture at representative resolutions/fps, confirming stop-stream returns to low mode, and verifying CHT-specific configurations match hardware limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_dfs_tables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_fops.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_fops.c

## Purpose
This file implements AtomISP V4L2 file operations and videobuf2 queue operations for the capture video node. It owns open/release behavior, vb2 buffer setup/mapping/cleanup, and the path that moves queued userspace buffers and statistics side buffers into CSS.

## Important APIs and Functions
- `atomisp_queue_setup()` derives CSS frame information, falls back to a default format if needed, allocates CSS stat buffers, and sets a single plane size.
- `atomisp_buf_init()` initializes an IA CSS frame from `pipe->frame_info` and maps the vb2 vmalloc buffer into HMM memory with `hmm_create_from_vmalloc_buf()`.
- `atomisp_buf_queue()` validates pipe state, handles cache flushing, places frames on active or parameter-waiting queues, and queues to CSS if streaming.
- `atomisp_qbuffers_to_css()` selects the CSS pipe based on copy mode, VFPP, and run mode, then queues output frames.
- `atomisp_q_video_buffers_to_css()` moves frames from `activeq` to `buffers_in_css`, applies per-frame parameters, enqueues CSS output buffers, and opportunistically queues 3A, metadata, and DIS buffers.
- `atomisp_open()` enforces single-open, powers up the ISP through runtime PM, and reinitializes device/subdevice state.
- `atomisp_release()` releases vb2, frees CSS/internal buffers, powers down the sensor, destroys CSS streams/pipes, and runtime-suspends the ISP.
- `atomisp_vb2_ops` and `atomisp_fops` export the vb2 and V4L2 operation tables.

## Control Flow
Opening a video node calls `v4l2_fh_open()`, validates that cameras are attached, rejects a second user, resumes runtime PM, resets device/subdevice fields, and increments the pipe user count. Buffer allocation calls `queue_setup`, which ensures CSS frame info exists. Each buffer init maps the userspace-visible plane into an IA CSS frame. `buf_queue` either marks invalid buffers done on pipe errors or appends them to an active queue, then, if streaming, handles parameter pairing and queues into CSS. CSS queueing repeatedly fills available CSS queue depth from active frames and side-buffer pools. Release tears down the user, buffer queues, CSS/stat/internal buffers, sensor power, CSS pipes/streams, and runtime PM.

## State and Persistence
Persistent pipe state includes `users`, `frame_info`, `pix`, vb2 queue, active/in-CSS/waiting lists, per-frame parameter arrays, and per-buffer config IDs. CSS stat buffer pools live on `asd` lists and counters. `atomisp_dev_init_struct()` resets fatal-error and frequency state; `atomisp_subdev_init_struct()` resets CSS params, feature defaults, mode flags, and invokes `atomisp_css_init_struct()`.

## Dependencies and Integration Points
The code depends on V4L2, vb2-vmalloc, HMM memory mapping, AtomISP command helpers, CSS compatibility APIs, ioctl stream start/stop, and subdev state. `atomisp_ioctl.c` uses `atomisp_start_streaming()`/`atomisp_stop_streaming()` through the vb2 ops table. CSS completion events later return frames from `buffers_in_css` through command-layer helpers.

## Risks
Single-open enforcement is per pipe and may affect applications expecting multiple handles. `wbinvd()` cache flushing is broad and expensive. Per-frame parameter pairing uses legacy fields and queues, with comments noting original buffer-handling ugliness. Error handling around CSS queueing must move frames back to `activeq` to avoid lost buffers. HMM mapping must be freed exactly once in `buf_cleanup()`. The code often assumes `isp->mutex` and pipe spinlocks are used in the right order.

## Test Signals
Test open/release with no sensor, one sensor, and double-open attempts; vb2 `REQBUFS` before `S_FMT`; buffer init/cleanup leak checks; queue/dequeue with and without per-frame parameters; queue-depth behavior; 3A/DIS/metadata side-buffer queueing; and stream-off release cleanup under active buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_fops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_fops.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_fops.h

## Purpose
This header exposes AtomISP file-operation and vb2-operation entry points to the rest of the PCI driver.

## Important APIs and Types
- `atomisp_qbuffers_to_css()` queues pending video buffers into the active CSS pipe selected by current run mode.
- `atomisp_vb2_ops` is the vb2 operation table used by `atomisp_subdev.c` when initializing video queues.
- `atomisp_fops` is the V4L2 file operations table used by the video device.

## Control Flow
The header participates in video-node setup: `atomisp_subdev.c` installs `atomisp_vb2_ops` into `pipe->vb_queue`, while `atomisp_video_init()`/video-device setup use `atomisp_fops` for open, release, mmap, poll, and ioctl handling. During streaming, other paths may call `atomisp_qbuffers_to_css()` after buffers or parameters become available.

## State and Persistence
No state is defined here. The declared objects operate on `struct atomisp_sub_device`, `struct atomisp_video_pipe`, and vb2 queue state defined elsewhere.

## Dependencies and Integration Points
The header includes `atomisp_subdev.h` for subdevice/pipe type definitions and is included by file operations, ioctl, and CSS compatibility code.

## Risks
Because the header exports operation tables, any signature or ownership changes in vb2/V4L2 paths must remain synchronized with queue initialization and video registration code. `atomisp_qbuffers_to_css()` assumes the caller has prepared CSS streams and locking correctly.

## Test Signals
Compile-time linkage for `atomisp_vb2_ops` and `atomisp_fops`, video-node registration, successful vb2 queue initialization, and runtime queueing after `buf_queue` or parameter handling are the primary validation points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_fops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_gmin_platform.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_gmin_platform.c

## Purpose
This file provides legacy ACPI/EFI/DMI platform glue for AtomISP sensors on Intel "gmin" systems. It discovers or synthesizes sensor platform data, controls sensor GPIOs, clocks, and power rails, registers sensor subdevices with AtomISP, and applies board-specific quirks for missing or wrong firmware data.

## Important APIs and Functions
- `atomisp_platform_get_subdevs()` returns the legacy platform subdevice table.
- `atomisp_register_i2c_module()` registers a gmin-managed sensor subdev, disables ACPI power resources, and records CSI port/lane data.
- `atomisp_gmin_remove_subdev()` and `atomisp_unregister_subdev()` remove sensor entries and release associated GPIO/regulator/hostdata resources.
- `gmin_camera_platform_data()` allocates a `gmin_subdev` slot, detects PMIC type, initializes clock/power metadata, and returns either PMIC-backed or ACPI-backed platform callbacks.
- Power callbacks include `gmin_gpio0_ctrl()`, `gmin_gpio1_ctrl()`, `gmin_v1p2_ctrl()`, `gmin_v1p8_ctrl()`, `gmin_v2p8_ctrl()`, `gmin_flisclk_ctrl()`, and `gmin_acpi_pm_ctrl()`.
- `gmin_subdev_add()` reads ACPI/DSM/EFI/DMI configuration, obtains PMC clocks, GPIOs, regulators, and PMIC-specific register settings.
- `gmin_get_var_int()` reads a typed configuration variable through DMI overrides, sensor `_DSM`, or EFI variable fallback.
- `atomisp_register_sensor_no_gmin()` supports non-gmin sensor registration while still honoring ACPI-derived port/lane overrides.
- `isp_pm_cap_fixup()` disables broken PCI runtime PM capability on BYT ISP hardware.

## Control Flow
Sensor drivers call `gmin_camera_platform_data()` during probe to obtain callback tables. That path detects PMIC, reserves a global `gmin_subdev` slot, stores CSI format/bayer metadata, and calls `gmin_subdev_add()`. `gmin_subdev_add()` derives clock source, ACPI `_PR0` clock, default CSI port, lane count, GPIO descriptors, ACPI power-management viability, PMC clock handle, regulator handles, and PMIC-specific register defaults. The returned platform callbacks let sensor drivers power rails and clocks and allocate CSI hostdata through `gmin_csi_cfg()`. When the sensor registers with AtomISP, `atomisp_register_i2c_module()` records it in `pdata_subdevs[]`; removal drops table entries and frees resources.

## State and Persistence
Global state includes `gmin_subdevs[MAX_SUBDEVS]`, `pdata_subdevs[MAX_SUBDEVS + 1]`, global `pmic_id`, shared PMIC I2C address, shared regulator enable counts for 1.8V and 2.8V rails, and a global PMC clock-name buffer. Each `gmin_subdev` persists per sensor and tracks subdev pointer, clock, GPIOs, regulator handles, CSI metadata, on/off booleans, PMIC address, and AXP register overrides. DMI quirk tables and PMIC register definitions are static.

## Dependencies and Integration Points
This code depends on Linux I2C, ACPI, EFI runtime variables, DMI matching, common clock framework, regulator framework, GPIO descriptors, Intel SoC PMIC helpers, and AtomISP platform headers. It exports symbols used by sensor drivers and AtomISP platform discovery. It overlaps with newer `atomisp_csi2_bridge.c` parsing, and a comment notes that duplication can disappear once sensors move to V4L2 async probing.

## Risks
The file is highly platform-specific and uses global arrays with a fixed `MAX_SUBDEVS` limit. Shared regulator counters must remain balanced across sensors and error paths. Some PMIC writes go through Intel PMIC opregion helpers rather than ordinary I2C transfers. Firmware sources can conflict: DMI overrides win, `_DSM` may be ignored for `CamClk`, and EFI fallback may be stale. ACPI power-resource handling is intentionally disabled in `atomisp_register_i2c_module()`, which can surprise generic PM assumptions. `gmin_camera_platform_data()` assumes a free slot exists and does not robustly handle `find_free_gmin_subdev_slot()` failure.

## Test Signals
Validate on representative BYT/CHT tablets: DMI override selection, `_DSM` and EFI fallback parsing, PMIC detection for AXP/TI/Crystal Cove/regulator cases, balanced rail enable counts with two sensors, clock rate selection and enable/disable, GPIO acquisition, CSI hostdata allocation/free, fixed-table overflow behavior, and BYT PCI PM-cap fixup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_gmin_platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_internal.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_internal.h

## Purpose
This header defines AtomISP's central internal device model, hardware constants, timeout/queue sizing values, input descriptors, saved register state, DFS mode, and `struct atomisp_device`.

## Important APIs and Types
- Hardware IDs and revision macros identify BYT, Merrifield variants, Anniedale, and Cherry Trail devices and expose `IS_HWREVISION()`.
- Size and timing constants define image dimension limits, queue depths, event counts, timeout durations, raw-frame counts, metadata/stat queue depths, and ISR latency QoS.
- `struct atomisp_input_subdev` records a sensor input: logical port, mbus code, crop/binning support, power state, sensor/csi subdev pointers, remote source, native/active crop rectangles, and try-state storage.
- `enum atomisp_dfs_mode` names automatic, low, and max frequency scaling modes.
- `struct atomisp_regs` stores PCI and I-unit/CSI register values for save/restore/reset sequences.
- `struct atomisp_device` embeds V4L2/media devices, one AtomISP subdevice, async notifier, firmware/CSS env, PM/QoS state, CSI2 port array, mutex/spinlock, sensor lane/input tables, saved regs, DFS data, and fatal/CSS init state.
- `v4l2_dev_to_atomisp_device()` provides container conversion from V4L2 device.

## Control Flow
The header does not implement behavior but shapes most control flow. Probe and initialization fill `atomisp_device`, initialize CSI2 ports and the ISP subdev, load firmware, parse sensors, and register media/video nodes. File operations, ioctls, CSI2 bridge, CSS glue, and command helpers all pass `atomisp_device` and `atomisp_sub_device` around as their shared context.

## State and Persistence
`atomisp_device` is the persistent per-PCI-device state for the driver. It owns the long-lived media graph, firmware pointer, MMIO base, notifier, current sensor inputs, CSS environment, saved register snapshot, fatal-error status, work item for assert recovery, and CSS initialization flag. Sensor input state tracks current discovered sensors and per-port lane counts. The mutex serializes CSS API and device state operations; the spinlock protects `asd.streaming`.

## Dependencies and Integration Points
The header includes AtomISP platform definitions, V4L2 media/async/subdev APIs, IA CSS types, CSI2/subdev/compat headers, GP device and IRQ headers, firmware, PM QoS, IDR, and vmalloc. It is included widely across the PCI driver and is the shared contract for almost every file in this work item.

## Risks
Because this header includes many subsystem headers and embeds concrete types, small changes can trigger broad rebuild and cross-module coupling. The single embedded `struct atomisp_sub_device asd` means current code is shaped around one ISP processing subdev. `ATOM_ISP_MAX_WIDTH/HEIGHT` use `UINT_MAX`, so practical bounds must be enforced elsewhere. Many queue-depth and timeout constants are firmware assumptions; changing them affects CSS behavior.

## Test Signals
Build coverage across the AtomISP tree, probe on each supported PCI ID/revision, media-device registration, async notifier setup, PM/QoS behavior, saved-register reset paths, and lockdep around mutex/spinlock-protected fields are key validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_ioctl.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_ioctl.c

## Purpose
This file implements the AtomISP V4L2 ioctl table, supported output formats, input selection, format/frame enumeration, control get/set paths, vb2 qbuf/dqbuf wrappers, and streaming start/stop orchestration.

## Important APIs and Functions
- `atomisp_output_fmts[]`, `atomisp_get_format_bridge()`, and `atomisp_get_format_bridge_from_mbus()` map V4L2 pixel formats and mbus codes to IA CSS frame formats.
- `atomisp_pipe_check()` rejects operations after fatal errors and prevents settings changes while the vb2 queue is busy.
- Standard ioctls include querycap, enum/g/s input, enum framesizes/intervals, enum/try/g/s capture format, req/query/q/dq/expbuf, streamon/off, g/s parameters, and extended controls.
- `atomisp_alloc_css_stat_bufs()` allocates 3A, DIS, and metadata CSS buffers based on current CSS grid/stream info.
- `atomisp_qbuf_wrapper()` and `atomisp_dqbuf_wrapper()` preserve legacy per-frame config IDs and exposure IDs through `reserved` and `reserved2`.
- `atomisp_start_streaming()` and `atomisp_stop_streaming()` are vb2 stream operations and coordinate media pipeline, CSS, CSI, DFS, hardware workarounds, and sensor `s_stream`.
- `atomisp_stop_stream()` is the internal teardown path used for normal stop and start-failure rollback.

## Control Flow
Userspace uses the ioctl table on the capture video node. Format and frame enumeration consult the current input sensor and AtomISP format tables. `S_INPUT` locks the media graph and selects a new input only when not busy. `S_PARM` either forwards frame interval to the sensor or changes AtomISP run mode. `QBUF` records legacy per-frame setting IDs before delegating to vb2; `DQBUF` returns exposure and config IDs after vb2 dequeues. Stream start locks `isp->mutex`, validates the pipe, repairs media links, starts the media pipeline, configures DMA burst length, flushes caches, applies pending CSS parameters, starts CSS, marks streaming true, resets sequence counters, queues pending parameter/buffer work, enables SOF IRQs when valid, configures CSI2 timing, switches DFS to auto, sets the CSI-ready PCI bit on newer ISP2401 steppings, and finally starts the sensor. On sensor start failure it stops CSS without calling sensor stop. Stream stop clears streaming, disables CSS SOF IRQ, stops CSS, drains pending events, optionally stops the sensor, clears CSI-ready, lowers DFS, resets the ISP, flushes video buffers, recreates CSS streams, and stops the media pipeline.

## State and Persistence
The file reads and mutates `pipe->pix`, `pipe->frame_request_config_id[]`, `pipe->frame_config_id[]`, `asd->input_curr`, `asd->run_mode`, `asd->high_speed_mode`, `asd->params`, streaming flags, sequence counters, and exposure ID fields. It uses `isp->saved_regs` for PCI CSI/I-control workarounds and `isp->running_freq` indirectly through frequency-scaling calls.

## Dependencies and Integration Points
Dependencies include V4L2 ioctl/event APIs, PCI config access, AtomISP command helpers, file ops, internal state, CSS compatibility, and hardware register definitions. It coordinates with `atomisp_subdev.c` for formats/selection, `atomisp_fops.c` for vb2 operations, `atomisp_csi2.c` for receiver configuration, and sensor subdevs through V4L2 calls.

## Risks
`atomisp_vidioc_default()` currently returns `-EINVAL` for any nonzero private command before its legacy switch, effectively disabling all private AtomISP ioctls despite dead code below. Legacy use of `v4l2_buffer.reserved/reserved2` is explicitly called out as an abuse. Stream start has many side effects and requires careful rollback ordering. Cache flushing via `wbinvd()` is global. Frame enumeration uses global padding variables and sensor active state; crop/binning logic must match sensor capabilities. Error paths must keep media pipeline, CSS streams, sensor stream state, and vb2 buffers coherent.

## Test Signals
Run v4l2-compliance for standard ioctls, enumerate formats/sizes/intervals for crop and non-crop sensors, exercise `S_INPUT` while streaming, qbuf/dqbuf legacy IDs, stream start/stop/restart, sensor-start failure rollback, CSI-ready bit handling on ISP2401 B0/K0, DFS transitions, and private ioctl behavior returning `-EINVAL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_ioctl.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_ioctl.h

## Purpose
This header exposes the AtomISP ioctl-layer public interface used by video setup, file operations, and CSS/buffer code.

## Important APIs and Types
- `atomisp_output_fmts[]` is the exported V4L2-to-CSS format bridge table.
- `atomisp_get_format_bridge()` and `atomisp_get_format_bridge_from_mbus()` resolve V4L2 pixel formats and media-bus codes.
- `atomisp_pipe_check()` validates pipe state and optionally rejects settings changes while busy.
- `atomisp_alloc_css_stat_bufs()` allocates CSS statistics/metadata buffers for a stream.
- `atomisp_start_streaming()` and `atomisp_stop_streaming()` are the vb2 stream control callbacks.
- `atomisp_ioctl_ops` is the V4L2 ioctl operation table for the capture node.

## Control Flow
`atomisp_subdev.c` and video initialization attach `atomisp_ioctl_ops` to the video device. `atomisp_fops.c` calls `atomisp_pipe_check()` from buffer queueing and uses start/stop through `atomisp_vb2_ops`. Queue setup calls `atomisp_alloc_css_stat_bufs()` after CSS frame info is available.

## State and Persistence
No standalone state is defined here. The declared functions operate on `atomisp_device`, `atomisp_video_pipe`, `atomisp_sub_device`, and vb2 queue state.

## Dependencies and Integration Points
The header includes `ia_css.h` for CSS types and forward-declares core AtomISP structs. It is a key edge between ioctl, file-op, CSS, and video-node modules.

## Risks
Callers of `atomisp_pipe_check()` must hold `pipe->isp->mutex`, as asserted by the implementation. Start/stop prototypes bind vb2 directly to AtomISP stream logic, so signature changes in vb2 require coordinated updates.

## Test Signals
Build/link validation, v4l2 ioctl table registration, vb2 stream callbacks firing, queue setup allocating stat buffers, and settings-change rejection while buffers are busy validate this header's integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_subdev.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_subdev.c

## Purpose
This file implements the Atom ISP processing V4L2 subdevice, its media pads, format conversion tables, selection/crop/compose behavior, V4L2 controls, event subscription, video pipe initialization, and subdev registration/cleanup.

## Important APIs and Functions
- `atomisp_in_fmt_conv[]`, `atomisp_find_in_fmt_conv()`, and `atomisp_find_in_fmt_conv_by_atomisp_in_fmt()` map media-bus codes to AtomISP input formats, bit depth, and bayer order.
- `atomisp_subdev_uncompressed_code()` and `atomisp_subdev_is_compressed()` handle DPCM-compressed raw code relationships.
- `atomisp_subdev_format_conversion()` detects raw-to-non-raw ISP conversion between sink and source pads.
- `atomisp_subdev_get_rect()` and `atomisp_subdev_get_ffmt()` retrieve active or try-state pad rectangles/formats.
- `atomisp_subdev_set_selection()` implements sink crop and source compose rules, updates CSS effective resolution and DVS envelopes, and propagates sink crop to source compose unless told to keep config.
- `atomisp_subdev_set_ffmt()` applies media-bus formats and pushes active sink format details into CSS input config.
- `atomisp_link_setup()` handles media-link enable/disable, powers off sensors on link disable, and selects the input matching the enabled CSI receiver.
- `atomisp_init_subdev_pipe()` creates the vb2 queue and video pipe lists.
- `isp_subdev_init_entities()` initializes the ISP subdev media entity, video node, and custom V4L2 controls.
- Cleanup helpers unregister subdev/video entities and drain pending V4L2 events.

## Control Flow
`atomisp_subdev_init()` attaches the parent `atomisp_device`, initializes stats/metadata lists, initializes the ISP media entity, creates the capture video pipe, initializes the video device, and creates run-mode/VFPP/continuous/raw-lock/disable-DZ controls. During media negotiation, pad `set_fmt` on the sink validates input code, updates selection, and writes CSS input resolution, binning, bayer order, input format, and default ISYS configuration. Selection changes round dimensions to AtomISP steps, account for padding and DVS slack, choose crop/compose dimensions, set CSS DVS envelope, and update effective input resolution based on aspect ratio. Link setup chooses the current input when a CSI source link is enabled.

## State and Persistence
Subdev state persists in `isp->asd`: active pad formats/rectangles, control handler and controls, video pipe and vb2 queue, stats/metadata list heads, DIS lock, raw buffer bitmap lock, current parameters, and media pads. Try-state formats and rectangles are owned by V4L2 subdev state. Event subscriptions live on the subdev devnode file-handle list.

## Dependencies and Integration Points
This file depends on V4L2 subdev/media/vb2 APIs, AtomISP command helpers, CSS compatibility functions, file and ioctl operation tables, internal state, and video-node helpers. It integrates the CSI2 receiver source pads to the ISP sink pad and the ISP source pad to the capture video node.

## Risks
Selection math is intricate and mixes DVS, padding, aspect-ratio crop, VFPP modes, and run modes; regressions can produce CSS effective resolutions that differ from media graph expectations. Source-pad format handling only changes code and derives dimensions from compose. Event subscription rejects frame-sync when CSS SOF is invalid, which depends on stream input mode. Cleanup assumes devnode and file-handle lists exist when draining events. Control handler capacity is initialized with `1` but many controls are added; V4L2 can grow allocations, but errors must be checked.

## Test Signals
Use media-ctl to enable/disable links and verify input selection and sensor power, exercise try and active `set_fmt`/`get_fmt`, crop/compose with video/still/preview run modes and DVS on/off, raw-to-YUV conversion, compressed raw code helpers, event subscription for supported events, vb2 queue initialization, and unregister cleanup with pending events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_subdev.c -->
