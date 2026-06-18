# Research: subset-b-004165

This grouped report covers Samsung CAMIF, S5P/Exynos G2D, and S5P/Exynos JPEG media driver files under `sources/distributed-fs/ceph-client/drivers/media/platform/samsung/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s3c-camif/camif-capture.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s3c-camif/camif-capture.c

Purpose: implements the V4L2 capture video nodes and the CAMIF subdevice pad/control operations for the Samsung S3C24xx/S3C64xx camera interface. It connects the sensor-facing media subdevice to two capture video paths, codec and preview, and owns buffer queuing, stream start/stop, IRQ buffer rotation, format negotiation, crop/compose controls, and default path setup.

Important APIs and functions: `s3c_camif_register_video_node()` creates one capture node per path with vb2 DMA-contig queues, media pads, H/V flip controls, and `s3c_camif_ioctl_ops`. `s3c_camif_create_subdev()` creates the CAMIF media subdevice with sink/source pads and test-pattern/color-effect controls. `start_streaming()`, `stop_streaming()`, `buffer_queue()`, and `s3c_camif_irq_handler()` are the capture lifecycle core. Format and geometry entry points are `s3c_camif_vidioc_try_fmt()`, `s3c_camif_vidioc_s_fmt()`, `s3c_camif_subdev_set_fmt()`, `s3c_camif_subdev_set_selection()`, and `s3c_camif_s_selection()`. `camif_reinitialize()` is the common recovery/cleanup path for stop and error cases.

Control flow: open resumes runtime PM and powers the sensor; close stops capture for the owning file, releases vb2 queues, powers down the sensor, and drops PM. `STREAMON` starts the media pipeline, validates the remote sensor format against `camif->mbus_fmt`, then delegates to vb2. `start_streaming()` resets/configures global CAMIF when no other path is running, or configures only the video path when another path already owns the frontend. Queued buffers are split between two active hardware slots and a pending queue. IRQs clear status, handle overflow/abort state, retire the just-filled active buffer, program the next pending buffer into two hardware address slots, and apply deferred `ST_VP_CONFIG` register updates.

State and persistence: persistent runtime state lives in `struct camif_dev` and `struct camif_vp`: frontend bus format/crop, per-path output format, payload, scaler, composition rect, owner, vb2 queue, pending/active lists, frame sequence, and state bits (`ST_VP_PENDING`, `RUNNING`, `STREAMING`, `SENSOR_STREAMING`, `ABORTING`, `LASTIRQ`, `CONFIG`). Sensor power/stream reference counts are kept in `camif->sensor`. No on-disk persistence exists.

Dependencies and integration: uses V4L2 core, media controller links, v4l2-subdev pad ops, vb2 DMA-contig, runtime PM, platform sensor data from `media/drv-intf/s3c_camif.h`, and register helpers from `camif-regs.c`. It assumes an I2C sensor subdevice and immutable media links created by `camif-core.c`.

Risks: buffer-slot logic depends on CAMIF frame-count semantics and can mis-deliver frames if index handling is wrong. Stop waits for a last IRQ and falls back to forced disable after `CAMIF_STOP_TIMEOUT`, so hardware that misses interrupts may return error buffers. `sensor_set_power()` and `sensor_set_streaming()` use reference counts and must stay balanced across open/close and error paths. Several geometry paths are partial or SoC-specific, especially S3C64xx composition and S3C244x scaler direction limits.

Test signals: exercise `v4l2-compliance` capture, media graph setup, sensor format mismatch rejection, minimum buffer count enforcement, `STREAMON/OFF` with both codec and preview nodes, H/V flip controls, test-pattern/color-effect controls, crop changes while streaming, stop timeout/error-buffer behavior, and IRQ frame sequence/payload correctness with DMA-contig buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s3c-camif/camif-capture.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s3c-camif/camif-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s3c-camif/camif-core.c

Purpose: platform-driver and shared core for the S3C CAMIF driver. It defines supported pixel formats, scaler factor calculation, sensor/media registration, clocks, IRQ registration, probe/remove, runtime PM, and per-SoC variant data.

Important APIs and functions: `s3c_camif_find_format()` filters `camif_formats[]` by fourcc/index and per-path SoC flags. `s3c_camif_get_scaler_config()` computes prescaler/main-scaler ratios and scale-up bits from frontend crop and output frame. `s3c_camif_probe()` allocates `camif_dev`, validates platform data, maps registers, requests both path IRQs, initializes subdev/video/media entities, registers the sensor, and enables PM. Runtime PM is implemented by `s3c_camif_runtime_resume()` and `s3c_camif_runtime_suspend()`.

Control flow: probe copies platform data, selects `s3c244x_camif_variant` or `s3c6410_camif_variant` from the platform id, maps MMIO, registers IRQs via `s3c_camif_irq_handler()`, acquires platform GPIOs, creates the CAMIF subdev, prepares clocks, sets the external sensor clock rate, initializes default formats, resumes the hardware, registers the media device and sensor, creates links, registers both video nodes, then drops runtime PM. Remove unwinds media/video/sensor registrations, disables runtime PM, releases clocks, unregisters the subdev, and returns GPIOs.

State and persistence: `camif_dev` is device-private in platform drvdata. Format catalog and SoC variant tables are static read-only state. `stream_count` and path state are owned by capture/register code but initialized here. Runtime PM state is in kernel PM core; no durable persistence exists.

Dependencies and integration: depends on platform data for GPIO hooks and sensor I2C board info, `clk_get()` names `camif` and `camera`, `platform_get_irq()` for two path IRQs, V4L2/media device registration, and helper entry points implemented in `camif-capture.c`.

Risks: the driver is platform-data based rather than DT-first, so missing or stale board data fails probe. Error unwind order is subtle because media device cleanup, V4L2 unregister, sensor unregister, clock release, and GPIO release interact. Scaler math rejects ratios at or above 64:1 and relies on crop/output values being sanitized before streaming.

Test signals: probe/remove on both platform IDs, clock and GPIO error injection, sensor absent/deferred probe, media graph inspection, scaler ratio boundary tests, runtime PM resume/suspend balancing, and capture tests that verify variant-specific output width/height limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s3c-camif/camif-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s3c-camif/camif-core.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s3c-camif/camif-core.h

Purpose: central shared contract for the CAMIF driver. It declares constants, pixel format metadata, frame/scaler structs, device/path state structs, buffer/address structs, path ids, state bits, and cross-file function prototypes.

Important APIs and types: `struct camif_dev` aggregates the media device, V4L2 root device, CAMIF subdev, frontend bus format/crop, sensor subdev state, media pipeline, subdev controls, two `camif_vp` paths, variant data, platform data, clocks, locks, and MMIO base. `struct camif_vp` represents one capture path with IRQ queue, video device, control handler, owner, vb2 queue, pending/active buffer lists, scaler, output format/frame, sequence, state bits, path id, flip/rotation, and register offset. `struct camif_fmt`, `camif_frame`, `camif_scaler`, `s3c_camif_variant`, and `camif_buffer` describe formats, geometry, SoC limits, and DMA buffers.

Control flow role: the header is included by core, capture, and register files to keep shared state layout identical. Inline helpers `camif_active_queue_add/pop/peek()` and `camif_pending_queue_add/pop()` are used by capture and IRQ code to transfer buffers between software queues and hardware slots.

State and persistence: state flags are bitfields stored in `camif_vp::state`; active buffer count and buffer indices reflect hardware scheduling. `camif_dev::sensor.power_count` and `stream_count` hold runtime reference counts. The structures are in-memory only.

Dependencies and integration: includes Linux platform/IRQ/spinlock/V4L2 headers, media entity/control/device headers, vb2 V4L2 headers, and `media/drv-intf/s3c_camif.h` platform definitions. It declares register helper functions via `camif-regs.h` separately.

Risks: queue helpers assume callers hold appropriate locks and that lists are non-empty. `camif_active_queue_peek()` removes by hardware index and returns `NULL` if no matching buffer is found, so caller correctness depends on buffer index bookkeeping. Any struct layout change affects all CAMIF files.

Test signals: compile coverage for all CAMIF translation units, lockdep around queue helpers, stress tests with rapid QBUF/DQBUF/STREAMOFF, and tests that validate state bit transitions under both normal and aborting IRQ flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s3c-camif/camif-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s3c-camif/camif-regs.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s3c-camif/camif-regs.c

Purpose: MMIO programming layer for S3C CAMIF. It translates driver state into register writes for reset, source format, crop, bus polarity, output DMA addresses/sizes, scaler, target format, flip, image effects, test pattern, capture enable/disable, interrupt clearing, and register dumps.

Important APIs: exported helpers include `camif_hw_reset()`, `camif_hw_set_source_format()`, `camif_hw_set_camera_crop()`, `camif_hw_set_camera_bus()`, `camif_hw_set_output_addr()`, `camif_hw_set_output_dma()`, `camif_hw_set_target_format()`, `camif_hw_set_scaler()`, `camif_hw_enable_scaler()`, `camif_hw_enable_capture()`, `camif_hw_disable_capture()`, `camif_hw_set_lastirq()`, `camif_hw_clear_pending_irq()`, and `camif_hw_dump_regs()`.

Control flow: capture initialization calls reset and global setup, then per-path configuration programs target format, scaler, flip, output DMA sizing, and initial buffer addresses. IRQ and stop paths clear pending IRQs, clear FIFO overflow, enable last-IRQ mode, and disable capture/scaler. Capture enable increments `camif->stream_count`; capture disable decrements it and disables global `IMGCPTEN` when the last path stops.

State and persistence: this file does not own durable state. It reads `camif_dev`, `camif_vp`, `camif_frame`, and `camif_scaler` and commits their current values to volatile hardware registers. The hardware register state persists only while the device is powered and not reset.

Dependencies and integration: depends on `camif-regs.h` register macros and `camif-core.h` data structures. It uses `readl/writel`, delays for reset timing, and V4L2 color-effect/media-bus constants. Variant checks split S3C244x from S3C6410 behavior.

Risks: many fields are encoded with fixed masks and shifts; wrong alignment or unsupported format state can silently program invalid hardware. `camif_get_dma_burst()` warns but leaves burst outputs zero if width/ybpp are invalid, so upstream format validation is essential. Stream count underflow is guarded with `WARN_ON` but still indicates lifecycle imbalance.

Test signals: register trace/dump comparison against hardware manuals for both variants, capture start/stop with both paths, scaler ratio tests, crop offset tests, planar Y/Cb/Cr DMA address tests, color effect/test pattern validation, and overflow IRQ handling on S3C244x.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s3c-camif/camif-regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s3c-camif/camif-regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s3c-camif/camif-regs.h

Purpose: CAMIF register map and hardware helper declarations. It defines register offsets, field masks, bit constructors, status decoders, DMA address formulas, scaler/control bits, image effect bits, and prototypes for the MMIO helper functions implemented in `camif-regs.c`.

Important APIs and constants: register macros cover global source/offset/control registers (`CISRCFMT`, `CIWDOFST`, `CIGCTRL`), DMA output addresses (`CIYSA`, `CICBSA`, `CICRSA`), path target/scaler/control/status registers (`CITRGFMT`, `CICTRL`, `CISCPRERATIO`, `CISCPREDST`, `CISCCTRL`, `CISTATUS`), capture control (`CIIMGCPT`), image effects, memory input DMA, and scan-line offsets. `CISTATUS_FRAMECNT()` is central to IRQ buffer-slot selection.

Control flow role: capture and register code use these macros to program SoC-specific paths without duplicating numeric offsets. `_offs` and `id` parameters allow one macro family to address codec and preview paths and S3C6410 register offsets.

State and persistence: the header itself owns no runtime state, but the bit definitions encode the hardware state model: capture enable, scaler enable, overflow flags, frame count, last IRQ, bus polarity, test pattern, input/output format, and DMA offsets.

Dependencies and integration: includes `linux/bitops.h`, `camif-core.h`, and Samsung platform bus definitions. The prototypes form the MMIO layer consumed by `camif-capture.c`.

Risks: macro correctness is critical because a wrong offset or mask corrupts hardware programming. Some comments note SoC-specific differences and disabled bits, so future changes must verify variant behavior rather than applying one register interpretation globally.

Test signals: compile checks for macro use, hardware register dump sanity after stream start, tests across codec/preview ids, and specific verification that `CISTATUS_FRAMECNT()` maps to the buffer index expected by IRQ rotation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s3c-camif/camif-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-g2d/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-g2d/Kconfig

Purpose: build configuration for the Samsung S5P/Exynos G2D 2D graphics accelerator V4L2 mem2mem driver.

Important declarations: `config VIDEO_SAMSUNG_S5P_G2D` is a tristate option. It depends on `V4L_MEM2MEM_DRIVERS`, `VIDEO_DEV`, and either `ARCH_S5PV210`, `ARCH_EXYNOS`, or `COMPILE_TEST`. It selects `VIDEOBUF2_DMA_CONTIG` and `V4L2_MEM2MEM_DEV`.

Control flow and integration: enabling this option causes the Makefile to build the `s5p-g2d` module/object from `g2d.o` and `g2d-hw.o`. The selected dependencies ensure V4L2 mem2mem and contiguous DMA buffer support are present for queueing and hardware DMA.

State and persistence: no runtime state; this is kernel build metadata.

Risks: missing architecture or mem2mem dependencies will hide the option. Selecting DMA-contig implies the runtime driver expects physically contiguous buffers or IOMMU-compatible contiguous DMA mappings.

Test signals: Kconfig visibility under Exynos/S5PV210 and `COMPILE_TEST`, module build with `CONFIG_VIDEO_SAMSUNG_S5P_G2D=m`, and dependency closure in allmodconfig-style builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-g2d/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-g2d/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-g2d/Makefile

Purpose: build recipe for the Samsung G2D V4L2 mem2mem driver.

Important declarations: `s5p-g2d-objs := g2d.o g2d-hw.o` links the core V4L2/mem2mem driver with the hardware register helper file. `obj-$(CONFIG_VIDEO_SAMSUNG_S5P_G2D) += s5p-g2d.o` connects the aggregate object to the Kconfig option.

Control flow and integration: when the option is built-in or modular, Kbuild compiles both source files and links them into one driver object that registers the platform driver from `g2d.c`.

State and persistence: no runtime state.

Risks: adding new G2D helper files requires updating this object list. A mismatch between Kconfig symbol and object name would break builds.

Test signals: incremental build with the symbol enabled as `y` and `m`, and symbol-disabled build confirming no objects are compiled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-g2d/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-g2d/g2d-hw.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-g2d/g2d-hw.c

Purpose: low-level MMIO helper layer for Samsung G2D BitBLT hardware. It writes source/destination geometry, base addresses, color modes, ROP, flip, scaling, command, start, reset, and interrupt-clear registers.

Important APIs: `g2d_reset()`, `g2d_set_src_size()`, `g2d_set_src_addr()`, `g2d_set_dst_size()`, `g2d_set_dst_addr()`, `g2d_set_rop4()`, `g2d_set_flip()`, `g2d_set_v41_stretch()`, `g2d_set_cmd()`, `g2d_start()`, and `g2d_clear_int()`.

Control flow: `device_run()` in `g2d.c` enables the clock gate, resets hardware, programs source and destination frames plus DMA addresses, applies current controls, optionally configures stretch scaling, writes command bits, and calls `g2d_start()`. The ISR calls `g2d_clear_int()` after completion.

State and persistence: the helpers only project `struct g2d_frame` and `struct g2d_dev` state into volatile registers. Hardware state is reset per mem2mem job.

Dependencies and integration: includes `g2d.h` for device/frame structures and `g2d-regs.h` for register offsets and constants. Uses `readl/writel` only; locking and clock management are handled by `g2d.c`.

Risks: `g2d_set_v41_stretch()` divides by destination crop dimensions, so prior selection validation must prevent zero width/height. Register fields mask dimensions to 12 or 16 bits, relying on upper-layer clamping to `MAX_WIDTH/MAX_HEIGHT`. Revision-specific behavior differs for cache clear and scaling command bits.

Test signals: mem2mem copy, invert, H/V flip, stretch on v3 and v4 hardware, IRQ completion, and register programming tests that compare frame offsets/strides/right-bottom coordinates against requested crop/compose rectangles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-g2d/g2d-hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-g2d/g2d-regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-g2d/g2d-regs.h

Purpose: register and constant definitions for the Samsung G2D BitBLT engine.

Important constants: defines general, command, rotate/direct, source, destination, pattern, mask, clip, ROP/alpha, color, and color-key register offsets. It also defines pixel color mode encodings via `COLOR_MODE(order, mode)`, common ROP4 values (`ROP4_COPY`, `ROP4_INVERT`), hardware limits (`MAX_WIDTH`, `MAX_HEIGHT`), defaults, timeout, scaling defaults, and v3 stretch command bit.

Control flow role: consumed by `g2d-hw.c` to translate `g2d_frame` and control state into MMIO writes, and by `g2d.c` for format hardware values and validation limits.

State and persistence: no runtime state; describes volatile hardware register layout and supported value encodings.

Dependencies and integration: standalone header used inside the G2D driver. Its limits feed V4L2 format validation, while mode macros feed the `formats[]` table in `g2d.c`.

Risks: hardware limit constants and mode encodings must match SoC revision behavior. The 12-bit coordinate writes in the helper layer make it important that these limits and validation stay in sync.

Test signals: compile tests, format enumeration/try_fmt validation, and hardware smoke tests for every listed RGB format and ROP value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-g2d/g2d-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-g2d/g2d.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-g2d/g2d.c

Purpose: V4L2 mem2mem driver for Samsung S5P/Exynos G2D 2D accelerator. It exposes one mem2mem video node that copies, flips, inverts, crops/composes, and scales RGB buffers using the G2D hardware.

Important APIs and functions: `g2d_open()` allocates a per-file `g2d_ctx`, initializes source/destination vb2 queues, controls, and default frames. `vidioc_try_fmt()`, `vidioc_s_fmt()`, `vidioc_g_selection()`, and `vidioc_s_selection()` implement format and crop/compose negotiation. `device_run()` programs a job using `g2d-hw.c`; `g2d_isr()` completes source/destination buffers and the mem2mem job. `g2d_probe()` maps MMIO, prepares clocks, requests IRQ, registers V4L2/mem2mem/video devices, and selects v3/v4 variant data from OF match.

Control flow: userspace opens the node, configures source/output formats and selections, queues one source and one destination buffer, then V4L2 mem2mem calls `device_run()`. The driver enables the gate clock for the job, resets the engine, programs geometry and DMA addresses, applies ROP/flip controls under `ctrl_lock`, starts hardware, and waits for IRQ. The ISR clears the interrupt, disables the gate clock, removes both buffers, copies timestamp metadata, marks both done, finishes the job, and clears `dev->curr`.

State and persistence: global state is `struct g2d_dev` with V4L2/m2m devices, locks, clocks, MMIO, current context, and variant. Per-file state is `struct g2d_ctx` containing input/output `g2d_frame`s, controls, ROP, and flip flags. No persistent storage exists.

Dependencies and integration: V4L2 mem2mem core, vb2 DMA-contig, OF platform matching (`samsung,s5pv210-g2d`, `samsung,exynos4212-g2d`), `sclk_fimg2d` and `fimg2d` clocks, one IRQ, and hardware helpers from `g2d-hw.c`.

Risks: `vidioc_s_selection()` does not visibly clamp rectangles to frame bounds or nonzero dimensions beyond negative offset checks, so invalid crop/compose sizes can reach hardware and scaling division. `g2d_s_ctrl()` handles `V4L2_CID_HFLIP` cluster updates but has no explicit `V4L2_CID_VFLIP` case, relying on clustered HFLIP callback behavior. The ISR uses `BUG_ON()` for missing context/buffers, which can panic on unexpected IRQ or state corruption.

Test signals: `v4l2-compliance` mem2mem, RGB32/RGB565/RGB555/RGB444/RGB24 formats, crop/compose bounds including zero/oversize rectangles, negative effect control, H/V flip cluster, scaling on both hardware variants, IRQ storm/unexpected IRQ handling, and clock prepare/enable failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-g2d/g2d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-g2d/g2d.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-g2d/g2d.h

Purpose: shared private interface for the Samsung G2D driver. It defines device, context, frame, format, variant structures and prototypes for hardware helper functions.

Important types: `struct g2d_dev` owns V4L2/mem2mem devices, video node, mutex, control spinlock, current context, MMIO registers, clocks, IRQ, and hardware variant. `struct g2d_ctx` is per file handle and stores input/output frames, V4L2 controls, ROP, and flip state. `struct g2d_frame` stores full dimensions, crop dimensions, offsets, format, stride, bottom/right coordinates, and buffer size. `struct g2d_fmt` maps V4L2 fourcc to depth and hardware color mode. `struct g2d_variant` stores hardware revision.

Control flow role: included by `g2d.c` and `g2d-hw.c` so the high-level V4L2 code and low-level register code share the same frame and device layout.

State and persistence: all structures are in-memory runtime state. `dev->curr` bridges mem2mem job submission and IRQ completion.

Dependencies and integration: includes Linux platform and V4L2 device/control headers. Declares hardware helper API consumed by `device_run()` and ISR.

Risks: fields such as `right`, `bottom`, `stride`, and `size` are cached derivatives that must be updated every time formats or selections change. `dev->curr` must be valid exactly while hardware is active.

Test signals: compile coverage, format/selection tests that verify cached fields, concurrent opens/contexts, and IRQ completion validating `dev->curr` lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-g2d/g2d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/Kconfig

Purpose: build configuration for the Samsung S5P/Exynos JPEG codec V4L2 mem2mem driver.

Important declarations: `config VIDEO_SAMSUNG_S5P_JPEG` is a tristate option depending on `V4L_MEM2MEM_DRIVERS`, `VIDEO_DEV`, and `ARCH_S5PV210 || ARCH_EXYNOS || COMPILE_TEST`. It selects `VIDEOBUF2_DMA_CONTIG` and `V4L2_MEM2MEM_DEV`.

Control flow and integration: enabling the symbol builds the `s5p-jpeg` aggregate object, which registers encoder and decoder mem2mem video nodes from `jpeg-core.c`.

State and persistence: no runtime state; build metadata only.

Risks: missing selected dependencies would break vb2/mem2mem use. Architecture gating controls driver visibility for non-Samsung builds except compile-test coverage.

Test signals: Kconfig visibility and build as built-in/module across Exynos, S5PV210, and `COMPILE_TEST` configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/Makefile

Purpose: Kbuild recipe for the Samsung JPEG codec driver.

Important declarations: `s5p-jpeg-objs := jpeg-core.o jpeg-hw-exynos3250.o jpeg-hw-exynos4.o jpeg-hw-s5p.o` links the common V4L2/mem2mem core with all supported hardware register backends. `obj-$(CONFIG_VIDEO_SAMSUNG_S5P_JPEG) += s5p-jpeg.o` ties the aggregate object to Kconfig.

Control flow and integration: regardless of selected runtime variant, all helper backends are compiled into the driver object so OF/platform matching can choose behavior at probe time.

State and persistence: no runtime state.

Risks: new JPEG backend files or symbol renames must be reflected here. Because all backends are linked, compile errors in any variant break the whole driver.

Test signals: module and built-in builds with the Kconfig symbol enabled; disabled-symbol build should omit the aggregate object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/jpeg-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/jpeg-core.c

Purpose: common V4L2 mem2mem JPEG codec driver for S5P, Exynos3250-compatible, Exynos4-compatible, Exynos5420, and Exynos5433 JPEG IP. It exposes separate encoder and decoder video nodes, negotiates raw/JPEG formats, parses JPEG headers for decode jobs, programs variant-specific hardware through helper files, handles controls, queueing, PM, IRQ completion, and OF matching.

Important APIs and functions: `s5p_jpeg_open()` chooses encode/decode mode by video node and creates per-file controls and m2m queues. `s5p_jpeg_find_format()`, `s5p_jpeg_try_fmt_vid_cap/out()`, and `s5p_jpeg_s_fmt()` implement variant- and direction-aware format negotiation. `s5p_jpeg_parse_hdr()` extracts width, height, SOS, DHT, DQT, SOF, and subsampling from queued JPEG input. `s5p_jpeg_device_run()`, `exynos4_jpeg_device_run()`, and `exynos3250_jpeg_device_run()` program hardware by variant. IRQ handlers `s5p_jpeg_irq()`, `exynos4_jpeg_irq()`, and `exynos3250_jpeg_irq()` complete mem2mem jobs. Probe/remove and PM are in `s5p_jpeg_probe()`, `s5p_jpeg_remove()`, `s5p_jpeg_runtime_resume()`, and `s5p_jpeg_runtime_suspend()`.

Control flow: probe selects variant data, maps MMIO, requests the variant IRQ handler, gets clocks, registers V4L2 and mem2mem devices, then registers encoder and decoder nodes. For encoding, userspace configures raw output and JPEG capture, queues buffers, runtime PM enables clocks, `device_run` writes dimensions, DMA addresses, quantization/Huffman tables, controls, and starts hardware; IRQ sets JPEG payload size and returns buffers. For decoding, output QBUF parses the JPEG header before scheduling. A resolution change queues `V4L2_EVENT_SOURCE_CHANGE`; capture queue data is updated immediately if not streaming or on capture STREAMOFF acknowledgement.

State and persistence: `struct s5p_jpeg` holds global locks, V4L2 devices, two video nodes, m2m device, registers, IRQ, clocks, variant, and aggregate IRQ status. `struct s5p_jpeg_ctx` holds mode, quality, restart interval, subsampling, output/capture queue metadata, decode scale factor, crop rectangle, header-parsed flag, crop alteration flag, controls, and resolution-change state. No durable storage exists.

Dependencies and integration: V4L2 mem2mem, vb2 DMA-contig, V4L2 controls/events, runtime PM, OF matching, clocks, IRQs, and variant helper headers. The raw format table binds fourcc support to direction, variant, alignment, plane count, depth, and subsampling.

Risks: JPEG header parsing runs on mapped user-provided buffers and must avoid overreads; it returns false on malformed markers and restricts marker counts. Decode job readiness depends on `hdr_parsed`, so missing or stale parse state blocks jobs. Format/subsampling adjustment is highly variant-specific, with known Exynos4 and Exynos3250 workarounds for subsampling, odd widths, downscale, and padding. IRQ handlers assume current mem2mem context and remove buffers once terminal status is seen; partial/multi-stage Exynos3250 interrupts accumulate in `irq_status`.

Test signals: `v4l2-compliance` for both nodes, encode/decode smoke tests across all supported raw formats, malformed JPEG headers, resolution-change event flow, streamoff acknowledgement, compression quality/restart/subsampling controls, Exynos4 odd-width and subsampling downgrades, Exynos3250 downscale/crop behavior, PM clock balance, IRQ error/status handling, and payload size correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/jpeg-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/jpeg-core.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/jpeg-core.h

Purpose: shared private definitions for the Samsung JPEG codec driver.

Important types and constants: declares driver name, clock count, compression quality range, RGB-to-YCbCr coefficients, IRQ timeout, format flags, encode/decode modes, queue type ids, subsampling ids, marker limits, and version enums. `struct s5p_jpeg` is the global device abstraction. `struct s5p_jpeg_variant` stores version, format flag, compatibility quirks, m2m ops, IRQ handler, and clock names. `struct s5p_jpeg_fmt` describes fourcc, depth, plane counts, alignment, subsampling, and direction/variant flags. `struct s5p_jpeg_q_data` stores queue format, dimensions, JPEG marker offsets, and buffer size. `struct s5p_jpeg_ctx` is per-file codec state.

Control flow role: included by the common core and all hardware helpers so they share variant IDs, mode constants, address structure, and context/device layouts.

State and persistence: defines in-memory state only. Header parsing results persist in `s5p_jpeg_q_data` for the lifetime of a context or until the next output format/header update.

Dependencies and integration: includes Linux interrupt, media JPEG marker definitions, V4L2 device/file-handle/control headers. Hardware helper headers consume `struct s5p_jpeg_addr` and mode/version constants.

Risks: format flags control which formats userspace can request for each variant and direction; mistakes expose unsupported hardware combinations. `S5P_JPEG_MAX_MARKER` limits stored DHT/DQT marker segments and can reject complex JPEGs.

Test signals: compile coverage across all helper files, format enumeration per variant, control defaults per encode/decode mode, and header parser tests that validate marker storage limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/jpeg-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/jpeg-hw-exynos3250.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/jpeg-hw-exynos3250.c

Purpose: MMIO helper backend for Exynos3250-compatible JPEG hardware, also reused by Exynos5420 variant data. It programs reset, power, DMA issue counts, clock mode, raw input/output formats, dimensions, quant/Huffman table selectors, stride/offset, DMA addresses, coefficients, scaling, timer, interrupts, and start/restart.

Important APIs: `exynos3250_jpeg_reset()`, `exynos3250_jpeg_input_raw_fmt()`, `exynos3250_jpeg_output_raw_fmt()`, `exynos3250_jpeg_proc_mode()`, `exynos3250_jpeg_subsampling_mode()`, `exynos3250_jpeg_imgadr()`, `exynos3250_jpeg_stride()`, `exynos3250_jpeg_offset()`, `exynos3250_jpeg_dec_scaling_ratio()`, `exynos3250_jpeg_interrupts_enable()`, `exynos3250_jpeg_get_int_status()`, and `exynos3250_jpeg_compressed_size()`.

Control flow: `exynos3250_jpeg_device_run()` in `jpeg-core.c` resets and powers the block, configures DMA/clock/proc mode, then calls these helpers according to encode or decode mode. The IRQ path reads timer and JPEG interrupt status with these helpers, clears statuses, may restart after header interrupt, and reads compressed size/subsampling at completion.

State and persistence: no software-owned state. The helpers write volatile registers based on `s5p_jpeg_ctx` state supplied by the core.

Dependencies and integration: includes `jpeg-core.h`, `jpeg-regs.h`, and its public header. It maps V4L2 fourcc values to Exynos3250 register encodings for RGB/YUV packed and planar/semi-planar formats.

Risks: reset polls with fixed retry counts; failure is not returned to callers. Stride/offset calculations must match buffer layout and crop/downscale rules in the core. Unsupported fourcc falls through to zero encodings, relying on core format filtering.

Test signals: encode/decode for each Exynos3250 format, downscale ratios 1/2/4/8, crop offsets, RGB byte-swap variants, timer timeout handling, header interrupt restart, and Exynos5420 stream-error path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/jpeg-hw-exynos3250.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/jpeg-hw-exynos3250.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/jpeg-hw-exynos3250.h

Purpose: public helper declarations for the Exynos3250-compatible JPEG register backend.

Important APIs: declares reset/power/DMA/clock helpers, raw input/output format setters, Y16 mode, proc mode, subsampling get/set, restart interval, quant/Huffman selector helpers, dimension setters, interrupt/timer helpers, stream bounds, DMA address/stride/offset helpers, coefficient setup, start/restart, compressed size, decode stream size, and decode scaling ratio.

Control flow role: consumed by `jpeg-core.c` when the selected variant uses `exynos3250_jpeg_m2m_ops` and `exynos3250_jpeg_irq()`.

State and persistence: no state; function prototypes operate on a passed MMIO base and immediate values.

Dependencies and integration: includes `linux/io.h`, `linux/videodev2.h`, and `jpeg-regs.h`; depends on `struct s5p_jpeg_addr` from the shared core header through include ordering in users.

Risks: declarations must stay synchronized with the implementation and variant core calls. Because all helpers accept raw register bases, caller locking and PM enablement are external responsibilities.

Test signals: build coverage with `jpeg-core.c`, sparse/prototype checks, and variant-specific smoke tests that touch every declared helper through encode/decode paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/jpeg-hw-exynos3250.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/jpeg-hw-exynos4.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/jpeg-hw-exynos4.c

Purpose: MMIO helper backend for Exynos4x12-style JPEG hardware and Exynos5433-compatible differences. It controls reset, encode/decode mode, image and encoded output formats, interrupts, Huffman-table enable, stream/frame buffer addresses, image size, table selection, decode table component selection, stream size, bitstream size, and decoded frame format.

Important APIs: `exynos4_jpeg_sw_reset()`, `exynos4_jpeg_set_enc_dec_mode()`, `__exynos4_jpeg_set_img_fmt()`, `__exynos4_jpeg_set_enc_out_fmt()`, `exynos4_jpeg_set_interrupt()`, `exynos4_jpeg_set_huf_table_enable()`, `exynos4_jpeg_set_sys_int_enable()`, address/size setters, `exynos4_jpeg_set_encode_tbl_select()`, decode Q/H table selectors, `exynos4_jpeg_get_stream_size()`, and `exynos4_jpeg_get_frame_fmt()`.

Control flow: `exynos4_jpeg_device_run()` uses these helpers to reset and program encode or decode jobs. Exynos5433 decode additionally parses JPEG Huffman/quantization markers in the core and uses selector helpers before enabling tables. The IRQ path disables system interrupts, reads status, maps it to result codes, completes buffers, disables mode, and reads decoded subsampling for Exynos4.

State and persistence: no software-owned state; writes volatile registers. Some register fields differ by version, handled by version parameters in internal format helpers.

Dependencies and integration: includes shared JPEG core, Exynos4 helper header, and `jpeg-regs.h`. Maps many V4L2 raw formats to Exynos4/Exynos5433 register encodings and chroma swap bits.

Risks: unsupported formats fall through without error in helper switches, depending on the core to filter. Version-specific masks and swap bits must be kept correct for Exynos4 vs Exynos5433. Table selection programming is tightly coupled to header parsing and default table setup.

Test signals: Exynos4 and Exynos5433 encode/decode, all supported YUV/RGB/GREY formats, decoded subsampling readback, JPEGs with custom DHT/DQT tables on Exynos5433, interrupt status error mapping, and bitstream size/payload reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/jpeg-hw-exynos4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/jpeg-hw-exynos4.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/jpeg-hw-exynos4.h

Purpose: public declarations for Exynos4/Exynos5433 JPEG MMIO helpers.

Important APIs: declares reset, mode setting, image format and encoded output format setters, table setup/selection helpers, interrupt/status helpers, stream/frame address and size setters, Huffman enable, system interrupt enable, stream-size readback, decode bitstream size, and decoded frame format readback.

Control flow role: used by `jpeg-core.c` for variants whose m2m ops are `exynos4_jpeg_m2m_ops`.

State and persistence: no runtime state in the header; all helpers operate on a register base supplied by the caller.

Dependencies and integration: relies on shared JPEG core types/enums such as `struct s5p_jpeg_addr` and `enum exynos4_jpeg_img_quality_level` through include order.

Risks: because declarations are low-level and unguarded, core code must ensure clocks are enabled, spinlocks held, and formats validated before calling.

Test signals: compile/prototype checks and full encode/decode paths on Exynos4-compatible variant data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/jpeg-hw-exynos4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/jpeg-hw-s5p.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/jpeg-hw-s5p.c

Purpose: MMIO helper backend for original S5P JPEG hardware. It handles reset, power, raw input/output mode, encode/decode mode, subsampling, restart interval, quant/Huffman selectors, dimensions, decode interrupts, timer/stream status, DMA addresses, color conversion coefficients, start, completion status, interrupt clear, and compressed-size readback.

Important APIs: `s5p_jpeg_reset()`, `s5p_jpeg_poweron()`, `s5p_jpeg_input_raw_mode()`, `s5p_jpeg_proc_mode()`, `s5p_jpeg_subsampling_mode()`, `s5p_jpeg_dri()`, `s5p_jpeg_qtbl()`, `s5p_jpeg_htbl_ac/dc()`, `s5p_jpeg_x/y()`, interrupt enable/status helpers, `s5p_jpeg_jpgadr()`, `s5p_jpeg_imgadr()`, `s5p_jpeg_coef()`, `s5p_jpeg_start()`, and `s5p_jpeg_compressed_size()`.

Control flow: `s5p_jpeg_device_run()` calls these helpers to configure legacy S5P encode/decode jobs. The legacy IRQ handler checks stream-bound, timer, result, and stream status through these helpers, clears relevant status, sets capture payload for encode, updates subsampling, clears the interrupt, and finishes the mem2mem job.

State and persistence: no software-owned state; all effects are volatile register writes/reads.

Dependencies and integration: includes shared core definitions, `jpeg-regs.h`, and `jpeg-hw-s5p.h`. It supports a narrower raw format set than newer helpers: RGB565 and YUV422 input for encode, YUV422/YUV420 output for decode.

Risks: `s5p_jpeg_reset()` busy-waits indefinitely until reset clears, unlike Exynos3250's bounded loops. Status clearing sequences depend on documented read/write side effects. Compressed size is assembled from three byte registers and must match hardware counter semantics.

Test signals: legacy S5P encode/decode, reset behavior, timeout and stream-bound error handling, interrupt clear sequencing, compressed payload size, RGB565/YUV422 input mode, and decode YUV420/YUV422 output mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/jpeg-hw-s5p.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/jpeg-hw-s5p.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/jpeg-hw-s5p.h

Purpose: public declarations and limits for the original S5P JPEG register backend.

Important APIs and constants: defines min/max dimensions, raw input/output mode ids, and declarations for reset, power, mode/subsampling/restart/table/dimension/interrupt/address/coefficient/start/status/compressed-size helpers.

Control flow role: consumed by `jpeg-core.c` for the `SJPEG_S5P` variant and by `jpeg-hw-s5p.c` implementation.

State and persistence: no runtime state; all helpers are stateless operations on a passed MMIO base.

Dependencies and integration: includes `linux/io.h`, `linux/videodev2.h`, and `jpeg-regs.h`. The core uses its constants for legacy S5P format programming.

Risks: declared width/height limits are broad; actual alignment and buffer-size constraints are enforced in the core. Caller must provide valid clocks/register mapping and serialized access.

Test signals: build/prototype checks and legacy variant encode/decode paths that exercise every declaration reachable from `s5p_jpeg_device_run()` and `s5p_jpeg_irq()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/jpeg-hw-s5p.h -->
