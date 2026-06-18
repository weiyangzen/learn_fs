<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-gen1.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-gen1.c

## Purpose
Implements common VFE generation-1 streaming and buffer handling used by older Qualcomm CAMSS VFE hardware families such as 4.1/4.7/4.8. It bridges the generic VFE line and video-node code to generation-specific register operations supplied through `struct vfe_hw_ops_gen1`.

## Important APIs, Types, And Functions
- Exports `vfe_gen1_enable()`, `vfe_gen1_disable()`, `vfe_gen1_halt()`, `vfe_word_per_line()`, `vfe_isr_ops_gen1`, and `vfe_video_ops_gen1`.
- Uses `struct vfe_line`, `struct vfe_output`, `struct vfe_device`, and `struct camss_buffer` from the shared CAMSS VFE/video layers.
- Key helpers reserve write masters, initialize ping/pong addresses, program frame-drop patterns, update active buffers, and translate hardware interrupts into VB2 buffer completion.

## Control Flow
Stream-on increments `vfe->stream_count`, enables common IRQ/write-interface state on the first stream, reserves one or more write masters depending on pixel format, primes up to two buffers, configures RDI or PIX blocks, and triggers a register update. Stream-off waits for a next SOF and register-update acknowledgement, disables write masters, disconnects RDI or stops CAMIF for PIX, releases output resources, and disables the write interface when the last stream stops. Interrupt flow is split through `vfe_isr_ops_gen1`: SOF completes pending shutdown waits, register-update completes synchronization or restarts queued captures after stopping, WM-done advances ping/pong buffers and calls `vb2_buffer_done()`, and composite-done routes PIX completion.

## State And Persistence
All state is in-memory driver state: `stream_count`, `output->state`, pending buffer lists, ping/pong slots, `last_buffer`, frame-drop update index, `sequence`, and completion objects. No persistent storage is touched. Concurrency is protected with `stream_lock` and `output_lock`; completion waits synchronize with ISR callbacks.

## Dependencies And Integration Points
Depends on V4L2 media graph sensor discovery for frame-skip information, VB2 for buffer lifecycle, and hardware-specific Gen1 callbacks for bus, CAMIF, WM, IRQ, scaler/crop, and QoS programming. It is selected by SoC VFE resource tables in `camss.c` through `vfe_ops_4_1`, `vfe_ops_4_7`, or `vfe_ops_4_8` implementations.

## Risks And Edge Cases
Timeouts on SOF, register update, or halt indicate stuck hardware and only log or return errors depending on path. Buffer starvation drives frame-drop patterns and delayed `last_buffer` completion, so state transitions around `STOPPING`, `SINGLE`, and `CONTINUOUS` are sensitive. Multi-plane formats depend on correct WM count and address indexing. The disabled `active_buf` mismatch check (`&& 0`) hides a potential hardware/status inconsistency.

## Test Signals
Useful signals are successful stream-on/off on RDI and PIX lines, correct frame sequence/timestamps, no missing-buffer or unmapped-WM ratelimited errors, no SOF/reg-update/halt timeouts, and VB2 buffers returning `DONE` or expected error states under queue starvation and stream stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-gen1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-gen1.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-gen1.h

## Purpose
Declares the generation-1 VFE abstraction layer used by older CAMSS hardware. It separates common Gen1 streaming logic from per-revision register programming.

## Important APIs, Types, And Functions
- Defines `struct vfe_hw_ops_gen1`, a large callback table for bus connect/disconnect, write-interface control, IRQ control, CAMIF control, module/scaler/crop/demux programming, QoS, xbar setup, UB configuration, ping/pong addresses, frame-drop control, and WM enable/status.
- Provides `vfe_calc_interp_reso()` for scaler interpolation mode selection.
- Declares `vfe_gen1_enable()`, `vfe_gen1_disable()`, `vfe_gen1_halt()`, `vfe_word_per_line()`, `vfe_isr_ops_gen1`, and `vfe_video_ops_gen1`.

## Control Flow
The header has no runtime control flow, but it defines the required callback contract consumed by `camss-vfe-gen1.c`. SoC-specific VFE files populate these callbacks, the shared VFE resource table stores them in `vfe->ops_gen1`, and stream enable/disable paths invoke them in hardware-programming order.

## State And Persistence
No state is owned here. The declarations operate on `struct vfe_device`, `struct vfe_line`, and `struct vfe_output` instances owned by `camss-vfe.h` and initialized by `camss-vfe.c`.

## Dependencies And Integration Points
Includes `camss-vfe.h` and relies on V4L2 pixel format types through callback signatures. Its exported declarations are the integration point between generic VFE code and revision-specific register files such as VFE 4.x implementations.

## Risks And Edge Cases
The callback table is broad and has no capability flags, so every Gen1 hardware implementation must provide semantically compatible functions. Mismatched UB sizing, WM status semantics, or PIX/RDI IRQ wiring can cause dropped frames or stalled shutdowns. The comment above `vfe_gen1_halt()` says `vfe_gen1_enable`, which is a documentation typo.

## Test Signals
Build coverage verifies all Gen1 ops tables satisfy the callback signatures. Runtime signals are the Gen1 stream and interrupt tests covered by `camss-vfe-gen1.c`, especially RDI/PIX enable, halt completion, and address update behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-gen1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-gen3.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-gen3.c

## Purpose
Implements the VFE hardware ops for newer CAMSS Gen3-style IFE/VFE blocks used by platforms such as SM8550, SM8650, QCS8300, and SA8775P. It programs RDI write-master bus registers and delegates generic queueing to the shared VFE v2 helpers.

## Important APIs, Types, And Functions
- Exports `const struct vfe_hw_ops vfe_ops_gen3`.
- Implements `vfe_wm_start()`, `vfe_wm_stop()`, `vfe_wm_update()`, `vfe_reg_update()`, `vfe_reg_update_clear()`, `vfe_subdev_init()`, `vfe_global_reset()`, `vfe_isr()`, and `vfe_halt()`.
- Uses SoC-version and lite/full VFE macros to choose BUS register bases and RDI write-master indices.

## Control Flow
On VFE subdevice init, the file installs Gen3 video ops that call `vfe_queue_buffer_v2()` and `vfe_flush_buffers()`. Stream enable from common code reserves a logical WM, then `vfe_wm_start()` maps it to the correct hardware RDI client, sets bus clock-gating override, frame increment, image config defaults, optional top-core downscaling disable for VFE 690 platforms, frame-drop/subsample settings, MMU prefetch, and WM enable. Buffer updates write the image address, with address shifting for non-690 hardware. Register updates are routed to the CSID wrapper via `camss_reg_update()`.

## State And Persistence
No persistent state is stored. The file writes MMIO registers through `vfe->base` and relies on common `vfe_output` state for active buffers and stream counts. Gen3 reset and ISR handling are minimal: global reset completes immediately through `vfe_isr_reset_ack()`, the ISR is a no-op, and halt relies on common output disable.

## Dependencies And Integration Points
Depends on Linux MMIO helpers, the common CAMSS VFE v2 helpers, CSID register-update integration, and SoC resource version/lite metadata from `camss.c`. The actual buffers come from `camss-video.c` and are advanced by `vfe_buf_done()` callbacks.

## Risks And Edge Cases
Register offsets and RDI mappings differ between VFE 690 and 780 families and between lite/full blocks; incorrect version metadata will program wrong clients. The no-op ISR means completion must come through CSID/buffer-done paths, so missing external interrupt routing can silently stall. Address shifting for non-690 hardware assumes the hardware expects 256-byte granularity.

## Test Signals
Expected signals are successful RDI capture on full and lite Gen3 VFEs, correct address programming in debug logs, no buffer starvation under `vfe_queue_buffer_v2()`, and correct operation on both VFE 690 and 780 register-layout families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-gen3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-vbif.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-vbif.c

## Purpose
Provides a tiny helper layer for programming the VFE VBIF bus interface on CAMSS platforms that expose a separate VBIF register region.

## Important APIs, Types, And Functions
- `vfe_vbif_write_reg()` writes a value to a VBIF offset relative to `vfe->vbif_base`.
- `vfe_vbif_apply_settings()` programs fixed sort enable and select registers with hard-coded values.

## Control Flow
Callers first map `vfe->vbif_base` during VFE subdevice initialization when `has_vbif` is set in resources. A hardware-specific VFE path can then call `vfe_vbif_apply_settings()`, which writes `VBIF_FIXED_SORT_EN` and `VBIF_FIXED_SORT_SEL0` and returns success.

## State And Persistence
The only state change is MMIO register state in the VBIF block. There is no cached software state and no persistent storage.

## Dependencies And Integration Points
Depends on `struct vfe_device` from the VFE core and `writel_relaxed()` from Linux I/O APIs. Resource metadata in `camss.c` controls whether the VBIF region is mapped.

## Risks And Edge Cases
The settings are unconditional and hard-coded, so they assume the VBIF layout and desired sorting policy match all callers. There is no guard against a NULL or invalid `vbif_base`; correct use depends on resource setup. The helper returns `0` without readback or error detection.

## Test Signals
Boot/probe should map the named VBIF resource on platforms that set `has_vbif`. Runtime capture should show no bus ordering or memory write issues after applying settings; hardware debug or trace readback can verify the programmed registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-vbif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-vbif.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-vbif.h

## Purpose
Declares the VBIF helper interface used by VFE hardware code that needs to program a separate VFE bus interface block.

## Important APIs, Types, And Functions
- Declares `vfe_vbif_write_reg(struct vfe_device *vfe, u32 reg, u32 val)`.
- Declares `vfe_vbif_apply_settings(struct vfe_device *vfe)`.
- Includes `camss-vfe.h` for the `struct vfe_device` definition.

## Control Flow
No runtime logic is implemented here. The header exposes the write and apply helpers to hardware-specific VFE source files.

## State And Persistence
No owned state. Functions declared here operate on the `vbif_base` MMIO mapping stored in `struct vfe_device`.

## Dependencies And Integration Points
Integrated with VFE initialization in `camss-vfe.c`, which maps the VBIF resource when the SoC resource table advertises `has_vbif`. Hardware-specific VFE modules include this header when they apply VBIF policy.

## Risks And Edge Cases
Because the header exposes raw register writes, callers must provide valid offsets and ensure the hardware block is powered and mapped. There is no type-level separation between VBIF register offsets and other VFE offsets.

## Test Signals
Compile coverage ensures callers include the correct declarations. Runtime test signals mirror `camss-vfe-vbif.c`: successful probe with VBIF resources and stable streaming after settings are applied.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-vbif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe.c

## Purpose
Implements the shared VFE subdevice, format negotiation, power/clock management, entity registration, and generic v2 buffer flow for Qualcomm CAMSS. It is the central glue between SoC resource tables, hardware-specific VFE ops, media-controller subdevs, and the video capture nodes.

## Important APIs, Types, And Functions
- Exports format tables `vfe_formats_*`, lifecycle APIs `msm_vfe_subdev_init()`, `msm_vfe_register_entities()`, `msm_vfe_unregister_entities()`, `vfe_get()`, `vfe_put()`, `vfe_reset()`, `vfe_disable()`, `vfe_enable_v2()`, `vfe_queue_buffer_v2()`, `vfe_buf_done()`, `vfe_flush_buffers()`, WM reservation helpers, and ISR helpers.
- Implements V4L2 subdev core/video/pad ops for power, stream, mbus code/frame-size enumeration, get/set format, and PIX compose/crop selections.
- Owns supported RDI and PIX media-bus/pixel-format tables for old and newer SoCs.

## Control Flow
Initialization maps VFE and optional VBIF registers, attaches power domains, requests IRQs, acquires clocks and clock-rate tables, initializes locks/completions, and configures per-line format tables. Registration creates one V4L2 subdev and one video node per VFE line, then links each subdev source pad to its video sink. Power-on calls optional VFE power-domain ops, resumes runtime PM, computes clock rates from connected sensor pixel clocks, enables clocks, resets hardware, clears output maps, initializes output state, and logs hardware version. Stream-on sets the line output reserved and dispatches to hardware `vfe_enable`; stream-off dispatches to hardware `vfe_disable`. The v2 path uses one WM per line, primes up to two buffers, updates addresses, and completes buffers in `vfe_buf_done()`.

## State And Persistence
State is in `struct vfe_device` and `struct vfe_line`: power and stream reference counts, clock arrays, power-domain links, WM-to-line maps, output state, pending buffers, active buffer slots, completions, and active pad formats/selections. No durable persistence exists. `power_lock`, `stream_lock`, and `output_lock` guard concurrent state transitions.

## Dependencies And Integration Points
Depends on Linux clocks, PM runtime, generic PM domains, platform resources, IRQs, media-controller/V4L2 subdev APIs, VB2, and helper functions from `camss.c` for sensor lookup, pixel clocks, clock margin, and CSID register updates. Hardware-specific ops come from Gen1, Titan/IFE, and Gen3 VFE implementations selected by SoC resources.

## Risks And Edge Cases
Clock-rate selection depends on sensor `V4L2_CID_PIXEL_RATE`; absent controls force fallback behavior and can mask underclocking. Format and crop constraints differ for RDI and PIX; invalid propagation can lead to `-EPIPE` at video start. Power-count or stream-count imbalance can leave clocks/domains on or trigger errors. The generic v2 output mapping notes that line-to-WM identity will not work for PIX streams. Register-reset and halt paths are timeout-sensitive.

## Test Signals
Probe/register/unregister should succeed for each compatible resource table. Media graph inspection should show CSID/ISPIF/VFE/video links. V4L2 compliance should cover mbus code enumeration, selection bounds, format propagation, stream-on/off, buffer completion, power cycling, and runtime PM/interconnect behavior across RDI and PIX lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe.h

## Purpose
Defines the shared VFE data model and public interfaces used by CAMSS core, hardware-specific VFE implementations, and video-node code.

## Important APIs, Types, And Functions
- Defines pad constants, write-master limits, halt/frame-drop constants, `enum vfe_output_state`, `enum vfe_line_id`, `struct vfe_output`, `struct vfe_line`, `struct vfe_hw_ops`, `struct vfe_isr_ops`, `struct vfe_subdev_resources`, and `struct vfe_device`.
- Declares VFE initialization/registration, power, reset, stream, buffer, WM, ISR, and helper APIs.
- Declares external format tables and hardware ops tables including Gen1, Titan/IFE generations, and Gen3.

## Control Flow
The header has no implementation, but it defines the contracts used by runtime flow. `camss.c` resource tables point each VFE instance at a `struct vfe_hw_ops`; `camss-vfe.c` calls those ops from power and stream paths; hardware-specific files call back into shared helpers for buffer queues and completions.

## State And Persistence
`struct vfe_device` holds the persistent in-memory state for a VFE instance while the driver is bound: MMIO bases, IRQ name/id, clocks, completions, locks, counters, output map, line array, ops pointers, video ops, and power-domain links. `struct vfe_output` tracks per-line buffer state and pending queues. No state survives driver unload or reboot.

## Dependencies And Integration Points
Includes Linux clock/spinlock types and media/V4L2 headers, plus `camss-video.h` and Gen1 declarations. It is included broadly by CAMSS core, VFE hardware files, VBIF helpers, and CSID parent integrations.

## Risks And Edge Cases
The ABI is internal but highly coupled: changes to enum values, line counts, WM limits, or union members affect several hardware generations. `to_vfe()` relies on array layout and line IDs matching array indices. The `vfe_hw_ops` table mixes optional and mandatory callbacks, so users must guard optional entries consistently.

## Test Signals
Compile coverage across all enabled SoC variants is the first signal. Runtime signals are successful VFE probe, stream, interrupt, power, and buffer tests using all ops tables that instantiate these structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-video.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-video.c

## Purpose
Implements the CAMSS V4L2 video capture node and VB2 queue operations. It exposes each VFE output line as a `video_device`, converts upstream media-bus formats to multi-planar pixel formats, validates the media pipeline, and forwards buffers to VFE output ops.

## Important APIs, Types, And Functions
- Exports `msm_video_register()` and `msm_video_unregister()`.
- Implements VB2 ops: queue setup, buffer init/prepare/queue, prepare/start/stop/unprepare streaming.
- Implements V4L2 ioctls for querycap, format enumeration, frame-size enumeration, get/set/try format, buffer ioctls, stream ioctls, and a single camera input.

## Control Flow
Registration initializes a DMA-SG VB2 queue, media sink pad, mutexes, default active format, V4L2 device fields, and registers the video node. Userspace format setting is rejected while the queue is busy and otherwise normalized through `__video_try_fmt()`. Buffer init records DMA addresses from SG tables and synthesizes chroma-plane addresses for semi-planar NV formats. Stream start powers the pipeline, starts media pipeline tracking, verifies the active video format against the remote subdev format, then walks upstream through sink pads calling `s_stream(1)`. Stop walks the same path calling `s_stream(0)`, stops the pipeline, and flushes buffers with error state.

## State And Persistence
State is per `struct camss_video`: active format, VB2 queue, media pad, media pipeline, locks, format table, alignment, and line-based flag. Buffers store DMA addresses and queue nodes in `struct camss_buffer`. No persistent storage is used.

## Dependencies And Integration Points
Depends on V4L2 ioctl/file helpers, media-controller links, `videobuf2-dma-sg`, and VFE-provided `camss_video_ops` for queueing and flushing. It expects a remote VFE subdev connected to its sink pad and format tables inherited from the VFE line.

## Risks And Edge Cases
Streaming fails with `-EPIPE` if the video node format diverges from the remote subdev active format. Line-based mode preserves user bytesperline/sizeimage constraints but must clamp carefully to avoid undersized buffers. NV12/NV21/NV16/NV61 address derivation assumes contiguous luma/chroma layout in the same DMA allocation. Stop returns early on upstream stream-off error, which can skip pipeline stop and buffer flush.

## Test Signals
V4L2 compliance should cover format enumeration, TRY/S_FMT clamping, busy queue rejection, MMAP/DMABUF/READ io modes, stream-on format mismatch failures, DMA address setup, clean stream-off buffer flushing, and media-pipeline power balancing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-video.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-video.h

## Purpose
Defines the CAMSS video-node structures and operations shared between VFE output code and the V4L2/VB2 video implementation.

## Important APIs, Types, And Functions
- `struct camss_buffer` wraps `vb2_v4l2_buffer`, up to three DMA addresses, and a list node for VFE queues.
- `struct camss_video_ops` provides VFE-specific `queue_buffer` and `flush_buffers` callbacks.
- `struct camss_video` stores the VB2 queue, video device, media pad, active format, pipeline object, locks, alignment/line-based flags, and supported format table.
- Declares `msm_video_register()` and `msm_video_unregister()`.

## Control Flow
The header defines data passed through runtime flow: VFE registration fills `struct camss_video`, `msm_video_register()` initializes the video node, VB2 queueing calls `camss_video_ops.queue_buffer`, and stream stop calls `flush_buffers`.

## State And Persistence
All state is in-memory per video node and per queued buffer. `active_fmt` is the authoritative userspace-visible capture format until changed with S_FMT. No durable persistence exists.

## Dependencies And Integration Points
Includes Linux mutex and V4L2/media/VB2 headers. It is used by `camss-vfe.c`, `camss-vfe-gen1.c`, shared VFE v2 helpers, and `camss-video.c`.

## Risks And Edge Cases
`addr[3]` assumes no supported format needs more than three planes. Callback pointers must be installed before registration or buffer queueing would dereference invalid ops. Queue locking is split between `lock` and `q_lock`, so implementation changes must preserve V4L2/VB2 lock ordering.

## Test Signals
Compile coverage verifies the callback and structure contracts. Runtime signals are successful video node registration, buffer queue/dequeue, and flushing through each installed VFE video ops table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-video.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss.c

## Purpose
Implements the Qualcomm CAMSS platform driver: SoC resource descriptions, probe/remove, media/V4L2 registration, async sensor binding, power-domain/interconnect management, and media graph construction across CSIPHY, CSID, optional ISPIF, VFE, and video nodes.

## Important APIs, Types, And Functions
- Defines static `camss_subdev_resources` arrays for many compatibles, mapping regulators, clocks/rates, register names, interrupts, hardware ops, line counts, lite/full flags, VBIF/power-domain names, format tables, and interconnect paths.
- Core helpers include `camss_add_clock_margin()`, `camss_enable_clocks()`, `camss_disable_clocks()`, `camss_find_sensor_pad()`, `camss_get_link_freq()`, `camss_get_pixel_clock()`, `camss_pm_domain_on/off()`, `camss_reg_update()`, and `camss_buf_done()`.
- Driver flow is in `camss_probe()`, `camss_remove()`, notifier callbacks, runtime PM callbacks, and the `qcom_camss_driver` platform driver.

## Control Flow
Probe allocates the CAMSS object and per-block arrays from matched resource data, gets interconnect paths, configures top-level power domains, initializes CSIPHY/VFE/CSID/ISPIF subdevices, sets the DMA mask, registers media and V4L2 devices, initializes the async notifier, parses fwnode endpoints, registers internal entities, creates internal media links, registers the media device, and waits for external sensor subdevs. Bound sensors attach CSI lane config to the target CSIPHY; notifier completion links sensor source pads to CSIPHY sinks and registers subdev nodes. Runtime resume programs interconnect bandwidth; suspend clears it. Remove unregisters notifier and entities, deletes media/V4L2 state when video references are gone, and detaches power domains.

## State And Persistence
State is the bound `struct camss`: resource pointer, arrays of subdevices, media/v4l2 devices, notifier, device pointer, top-level and VFE power-domain links, interconnect paths, CSID wrapper base, and a video-node reference count. No persistent storage is written.

## Dependencies And Integration Points
Depends on platform OF matching, fwnode graph endpoints, V4L2 async/media-controller frameworks, runtime PM, generic PM domains, interconnect framework, DMA masks, and all CAMSS block-specific modules. Device-tree compatible strings select exact resource tables.

## Risks And Edge Cases
Resource tables are large and tightly coupled to DT names; any clock/reg/interrupt/power-domain mismatch breaks probe. Some platforms use legacy power-domain index assumptions. Async endpoint parsing only supports CSI2 D-PHY, rejecting C-PHY. Link creation builds broad crossbar-style links, so wrong pad counts or line counts can create invalid graphs. `camss_remove()` defers full delete while video references remain, making ref-count correctness important.

## Test Signals
Probe should succeed for each compatible with matching DT, media graph topology should show expected sensors and internal links, runtime PM should set/clear interconnect bandwidth, stream tests should exercise `camss_reg_update()`/`camss_buf_done()` routing, and remove/unbind should clean up without leaked entities or power-domain links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss.h

## Purpose
Defines the CAMSS core data structures, resource descriptors, supported SoC versions, and cross-module helper APIs used by the Qualcomm camera subsystem driver.

## Important APIs, Types, And Functions
- Defines `struct camss_subdev_resources`, `struct resources_icc`, `struct resources_wrapper`, `enum pm_domain`, `enum camss_version`, `struct camss_resources`, `struct camss`, `struct camss_camera_interface`, `struct camss_async_subdev`, `struct camss_clock`, and `struct parent_dev_ops`.
- Declares helpers for clocks, sensor discovery, link frequency/pixel clock, PM domains, VFE parent access, deletion, buffer done, and register update.
- Provides container macros for resolving parent `struct camss` or `struct device` from module arrays.

## Control Flow
No implementation is present, but this header defines the contracts used throughout probe, async binding, stream setup, and hardware interrupt handling. `camss.c` fills `struct camss_resources`, block init functions consume `struct camss_subdev_resources`, and CSID/VFE modules call back through parent helpers.

## State And Persistence
`struct camss` is the top-level in-memory state for a bound platform device. Resource structures are static descriptors. Async subdev structures retain parsed CSI lane configuration for external sensors while the notifier is active. No persistent storage is represented.

## Dependencies And Integration Points
Includes Linux device/types and V4L2/media headers plus CAMSS block headers. It is the primary integration header for CSIPHY, CSID, ISPIF, VFE, format handling, and core platform code.

## Risks And Edge Cases
Array sizes are capped by `CAMSS_RES_MAX`; resource tables must remain within those limits and null-terminate variable arrays. Container macros rely on module arrays and indices matching resource order. Adding a SoC version requires synchronized updates across resource tables, format/ops support, and version-specific conditionals.

## Test Signals
Build coverage across all CAMSS source files validates type contracts. Runtime test signals are successful probe, async sensor binding, media graph construction, VFE parent get/put behavior, clock programming, and buffer/register update routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/Kconfig

## Purpose
Adds the Kconfig entry for the Qualcomm Iris V4L2 stateless video decoder driver.

## Important APIs, Types, And Functions
- Defines `config VIDEO_QCOM_IRIS` as a tristate option named "Qualcomm Iris V4L2 decoder driver".
- Depends on `VIDEO_DEV` and either `ARCH_QCOM` or `COMPILE_TEST`.
- Selects `V4L2_MEM2MEM_DEV`, `QCOM_MDT_LOADER`, `QCOM_SCM`, and `VIDEOBUF2_DMA_CONTIG`.

## Control Flow
Kconfig evaluation exposes the option only when dependencies are met. Selecting it as built-in or module controls whether the Iris objects listed in the Makefile are linked into the kernel or module.

## State And Persistence
No runtime state. The selected value persists only in kernel configuration files such as `.config`.

## Dependencies And Integration Points
Integrates the Iris decoder with the media platform driver menu and ensures required V4L2 mem2mem, VB2 DMA-contiguous, Qualcomm MDT firmware loading, and SCM interfaces are available.

## Risks And Edge Cases
Dependency omissions can allow invalid builds; overly strict dependencies can hide compile-test coverage. Selecting DMA-contiguous constrains expected memory allocation behavior for the driver.

## Test Signals
Kernel `olddefconfig`/menuconfig visibility, `allyesconfig`/`allmodconfig`, module builds, and compile-test builds on non-Qualcomm architectures are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/Makefile

## Purpose
Defines the object composition for the Qualcomm Iris V4L2 decoder driver module.

## Important APIs, Types, And Functions
- Builds `qcom-iris.o` when `CONFIG_VIDEO_QCOM_IRIS` is enabled.
- Aggregates Iris source objects for buffer management, core/platform setup, firmware, HFI command/packet/response handling, instance state, control handling, power management, V4L2 file/ioctl paths, VB2 integration, and VPU buffer handling.
- Adds `iris_platform_gen1.o` only when `CONFIG_VIDEO_QCOM_VENUS` is unset.

## Control Flow
Kbuild expands `qcom-iris-objs` into the ordered object list for the composite `qcom-iris.o` target. The final object is linked built-in or as a module according to the Kconfig tristate.

## State And Persistence
No runtime state is stored in the Makefile. Build outputs are generated under the kernel build tree and are not source persistence.

## Dependencies And Integration Points
Depends on the matching Kconfig symbol and the listed Iris C files. It integrates the Iris driver into the kernel media platform Qualcomm build directory.

## Risks And Edge Cases
Missing an object can produce unresolved symbols or silently omit functionality. Stale object names break builds when source files are renamed. Object ordering can matter for initcall/linker-section behavior, though normal C symbol resolution is order-insensitive within this composite object.

## Test Signals
`make M=drivers/media/platform/qcom/iris` or full kernel builds with `CONFIG_VIDEO_QCOM_IRIS=m/y` should produce `qcom-iris.o` without missing object or unresolved symbol errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/Makefile -->
