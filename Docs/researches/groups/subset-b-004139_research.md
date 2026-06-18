# subset-b-004139 Research

Grouped research for the requested media platform source files. Each section is source-tree aligned and uses the exact reconciliation markers required by the worker contract.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/imagination/e5010-mmu-regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/imagination/e5010-mmu-regs.h

## Purpose
This header is a generated-style register map for the Imagination E5010 JPEG encoder MMU block. It does not implement logic; it defines offsets, strides, entry counts, bit masks, shifts, repetition counts, and the byte size needed by the E5010 hardware code to program address translation, tiling, request policy, fault handling, statistics, and version discovery registers.

## Important APIs, Types, And Constants
There are no functions or types. The public surface is a collection of `MMU_*` macros. The key groups are directory base registers (`MMU_MMU_DIR_BASE_ADDR_*`), tile configuration and bounds (`MMU_MMU_TILE_CFG_*`, `MMU_MMU_TILE_MIN_ADDR_*`, `MMU_MMU_TILE_MAX_ADDR_*`), control registers (`MMU_MMU_CONTROL0_*`, `MMU_MMU_CONTROL1_*`), address mode (`MMU_MMU_ADDRESS_CONTROL_*`), hardware capability/status (`MMU_MMU_CONFIG0_*`, `MMU_MMU_CONFIG1_*`, `MMU_MMU_STATUS0_*`, `MMU_MMU_STATUS1_*`), request/protocol fault registers, bandwidth/stall/latency counters, statistics reset bits, version fields, and `MMU_BYTE_SIZE`.

## Control Flow And State
The file has no runtime control flow and no persistent software state. Its constants are consumed by MMIO read/write helpers elsewhere in the E5010 driver. The hardware state represented by the macros is persistent only in the device registers: MMU enable/bypass state, page directory addresses, tile windows, pause/reset/flush/invalidate commands, fault status, and performance counters.

## Dependencies And Integration Points
This header is intended to be included by E5010 JPEG encoder hardware code, alongside the core and encoder register headers in the same `imagination` platform directory. The only unusual symbol is `IMG_TRUE` in `MMU_MMU_ADDRESS_CONTROL_TRUSTED`, which must be provided by another included Imagination header or removed if unused. Register users must combine masks and shifts correctly and must respect array strides and entry counts for banks and tiles.

## Risks
Register maps are fragile: a wrong offset, bit mask, or shift silently programs hardware incorrectly. The repeated-bit fields on `CONTROL1`, `BANK_INDEX`, `REQUEST_PRIORITY_ENABLE`, and `MEM_REQ` expose array-like fields packed into one register, so callers must not assume a single bit. Fault clear, pause, flush, invalidate, and soft reset bits are write-command style fields and should be sequenced carefully to avoid losing diagnostic state.

## Test Signals
Build coverage should compile all E5010 files that include this header. Runtime validation should check that MMU enable/bypass configuration, directory base programming, cache invalidation/flush, and fault clear paths produce expected hardware behavior. Fault injection or malformed DMA address tests should verify that status and protocol fault fields decode correctly. Register dump tests can compare offsets against the E5010 hardware reference.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/imagination/e5010-mmu-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/intel/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/intel/Kconfig

## Purpose
This Kconfig file introduces the Intel media platform driver menu and the `VIDEO_PXA27x` configuration symbol for the PXA27x Quick Capture Interface V4L2 capture driver. It controls whether `pxa_camera.c` can be built and encodes the compile-time dependencies required by the driver.

## Important APIs, Types, And Functions
There are no C APIs. The important configuration symbol is `VIDEO_PXA27x`, a tristate option labelled "PXA27x Quick Capture Interface driver". It depends on the media platform driver class, `VIDEO_DEV`, and either `PXA27x` or `COMPILE_TEST`. It selects `VIDEOBUF2_DMA_SG`, `SG_SPLIT`, and `V4L2_FWNODE`.

## Control Flow And State
Kconfig state determines whether the PXA camera driver is not built, built-in, or built as a module. The selected dependencies are part of the build-time state that makes the vb2 DMA-SG buffer handling and scatterlist splitting paths available.

## Dependencies And Integration Points
The file is integrated from the parent media platform Kconfig hierarchy. Its `VIDEO_PXA27x` symbol is consumed by the adjacent Makefile, which adds `pxa_camera.o` when enabled. The dependency on `PXA27x || COMPILE_TEST` keeps the driver tied to the intended platform while still allowing cross-architecture compile coverage.

## Risks
If the selected vb2 and scatterlist helpers diverge from what `pxa_camera.c` actually uses, the driver can fail to compile under valid configurations. The symbol name contains `PXA27x` casing, so Makefiles and external config fragments must match exactly. Because the driver uses both platform data and firmware-node endpoints, weakening `V4L2_FWNODE` selection would break OF probing.

## Test Signals
Useful checks are `allyesconfig`/`allmodconfig` build coverage, `COMPILE_TEST` builds on non-PXA architectures, and a target PXA configuration that enables `VIDEO_PXA27x` as both built-in and module. Kconfig linting should confirm there are no unmet direct dependencies for `VIDEOBUF2_DMA_SG`, `SG_SPLIT`, or `V4L2_FWNODE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/intel/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/intel/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/intel/Makefile

## Purpose
This Makefile connects the Intel platform media Kconfig symbol to the PXA camera driver object. It is intentionally small: when `CONFIG_VIDEO_PXA27x` is enabled, `pxa_camera.o` is compiled into the media platform build.

## Important APIs, Types, And Functions
There are no APIs or functions. The relevant build rule is `obj-$(CONFIG_VIDEO_PXA27x) += pxa_camera.o`.

## Control Flow And State
The only state is build configuration state from Kconfig. The object is built as built-in or module according to the tristate value of `CONFIG_VIDEO_PXA27x`.

## Dependencies And Integration Points
This file depends on the parent kernel media build system including the directory. It maps directly to `drivers/media/platform/intel/pxa_camera.c` and to the `VIDEO_PXA27x` symbol defined in the adjacent Kconfig file.

## Risks
Because the driver is a single object, there are no local ordering risks. The main risk is symbol drift: if the Kconfig symbol or source filename changes, this Makefile must be updated with it. A typo here silently omits the driver from builds even if Kconfig is enabled.

## Test Signals
Run a configured kernel build with `CONFIG_VIDEO_PXA27x=m` and verify that `pxa_camera.ko` is produced. Built-in coverage should verify `pxa_camera.o` is linked when `CONFIG_VIDEO_PXA27x=y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/intel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/intel/pxa_camera.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/intel/pxa_camera.c

## Purpose
This file implements the V4L2 capture driver for the PXA27x Quick Capture Interface. It binds a single external camera sensor through V4L2 async subdevice discovery, configures the PXA camera interface registers, manages vb2 DMA-SG capture buffers, and delivers captured frames through a `/dev/video*` node.

## Important APIs, Types, And Functions
Important register macros cover CICR/CISR/CIFR/CITOR/CIBR registers and their control bits. Format modeling is handled by `struct pxa_mbus_pixelfmt`, `struct pxa_mbus_lookup`, and `struct pxa_camera_format_xlate`. Runtime state is held in `struct pxa_camera_dev`, which contains V4L2/vb2/notifier objects, the sensor subdev, DMA channels, locks, current format, register save state, and queued/active buffers. `struct pxa_buffer` embeds `vb2_v4l2_buffer` and stores DMA descriptors, cookies, scatterlists, plane sizes, and active-DMA bit state.

Key functions include `pxa_mbus_build_fmts_xlate()`, `pxa_camera_set_bus_param()`, `pxa_camera_setup_cicr()`, `pxa_buffer_init()`, vb2 callbacks `pxac_vb2_*`, DMA helpers `pxa_dma_add_tail_buf()`, `pxa_dma_start_channels()`, and `pxa_camera_dma_irq()`, V4L2 ioctl handlers `pxac_vidioc_*`, async sensor callbacks `pxa_camera_sensor_bound()` / `pxa_camera_sensor_unbind()`, PM hooks, DT parsing, and `pxa_camera_probe()` / `pxa_camera_remove()`.

## Control Flow
Probe allocates `pxa_camera_dev`, maps registers, registers a V4L2 device, gathers platform data or DT endpoint data, requests three DMA channels (`CI_Y`, `CI_U`, `CI_V`), configures DMA source addresses, activates the camera clock/register defaults, requests the QCI IRQ, and registers a V4L2 async notifier. When the sensor binds, the driver builds host/sensor format translations, sets a default 640x480 format, powers and configures the sensor, initializes vb2, and registers the video device.

Format setting validates hardware frame bounds, negotiates subdev media-bus format, computes bytesperline and image size, stores `current_fmt/current_pix`, and programs CICR registers. Streaming queues vb2 buffers, splits the single user plane into Y/U/V DMA scatterlists for planar mode, submits reusable DMA descriptors, and starts capture. EOF from the camera interrupt disables further EOF interrupts and schedules bottom-half work, which resets FIFOs, chooses the first queued buffer, marks active DMA channels, and issues pending DMA. DMA callbacks clear the completed channel bit; once all active planes for a buffer complete, `pxa_camera_wakeup()` timestamps, sequences, completes the vb2 buffer, and advances to the next queued buffer. FIFO overruns trigger capture stop, descriptor resubmission, and restart.

## State And Persistence
Persistent runtime state is in `pcdev`: current format, bus flags, clock rates, DMA channels, capture list, `active` buffer pointer, `buf_sequence`, and saved CICR registers for suspend/resume. No state is persisted beyond device lifetime. The driver saves CICR0-4 over suspend, powers the sensor down/up, and restarts capture if an active buffer existed.

## Dependencies And Integration Points
The driver depends on V4L2 core, V4L2 async/fwnode, vb2 DMA-SG, DMAengine, PXA DMA slave IDs, platform data in `linux/platform_data/media/camera-pxa.h`, OF graph endpoints, and camera subdevices implementing pad operations and optional `s_power` / `g_skip_top_lines`. It integrates with kernel PM through `dev_pm_ops`, with the media userspace ABI through standard video capture ioctls, and with optional `CONFIG_VIDEO_ADV_DEBUG` register access ioctls.

## Risks
The most sensitive code is the DMA hot-chaining path. The driver submits descriptors while DMA can already be running and compensates for missed links with `pxa_camera_check_link_miss()`. FIFO overrun recovery restarts the whole capture path and must not lose queued buffers. Format handling assumes one vb2 plane even for YUV422P and splits that memory into hardware planes; bad size calculations can corrupt memory or produce invalid planar layout. Locking spans spinlocks in IRQ/DMA contexts and a mutex for file/vb2 operations, so active-buffer races are a regression risk. The probe path initializes vb2 both before and after sensor bind, which should be watched when refactoring.

## Test Signals
Build with `CONFIG_VIDEO_PXA27x` and `COMPILE_TEST`. Runtime tests should cover sensor async bind/unbind, format enumeration and set/try for packed and planar formats, streaming with one and multiple buffers, FIFO overrun recovery, DMA callback completion for 1-plane and 3-channel modes, streamoff returning queued buffers as errors, suspend/resume during idle and active capture, and DT endpoint parsing for bus width and polarities. V4L2 compliance and media pipeline tests are important external signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/intel/pxa_camera.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/m2m-deinterlace.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/m2m-deinterlace.c

## Purpose
This file implements a V4L2 memory-to-memory deinterlacing driver backed by a DMAengine channel with interleaved-transfer support. It converts sequential-field input buffers into either interlaced output or progressive line-doubled output for YUV420 and YUYV formats.

## Important APIs, Types, And Functions
`struct deinterlace_fmt` declares supported fourccs and queue direction flags. `struct deinterlace_q_data` stores width, height, sizeimage, format, and field for a queue. `struct deinterlace_dev` owns the V4L2/video device, DMA channel, mutex, busy flag, and m2m device. `struct deinterlace_ctx` owns one file handle, m2m context, colorspace, DMA cookie, abort flag, and `dma_interleaved_template`.

The central functions are `deinterlace_job_ready()`, `deinterlace_device_run()`, `deinterlace_issue_dma()`, `dma_callback()`, format ioctls `vidioc_*`, vb2 callbacks `deinterlace_queue_setup()`, `deinterlace_buf_prepare()`, `deinterlace_buf_queue()`, queue creation `queue_init()`, file operations `deinterlace_open()` / `deinterlace_release()`, and platform probe/remove.

## Control Flow
Probe allocates the device, requests any DMA channel advertising `DMA_INTERLEAVE`, registers a V4L2 device, registers a video node, initializes the V4L2 mem2mem device, and stores driver data. Open allocates a context, initializes its V4L2 file handle and mem2mem queues, allocates one interleaved DMA template, and defaults colorspace. Userspace configures matching output/capture formats and compatible field conversion. `vidioc_streamon()` rejects mismatched fourccs and unsupported field-direction combinations before delegating to V4L2 m2m.

When both source and destination buffers are ready and the device is not busy, `deinterlace_device_run()` marks the device busy and submits a sequence of interleaved DMA operations. For YUV420 it submits separate Y, U, and V odd/even or line-doubling operations; for YUYV it submits odd/even or odd/doubled operations. Only the final operation in the sequence carries the callback. `dma_callback()` clears busy, removes source and destination buffers, copies timestamp/timecode metadata, marks both done, and finishes the m2m job.

## State And Persistence
Queue format state is held in a global static `q_data[2]`, not per context. Per-open state includes colorspace, abort flag, and DMA template. The driver has no persistent storage. Runtime state is the global DMA channel, `busy` atomic, and queued mem2mem buffers.

## Dependencies And Integration Points
The driver depends on V4L2 mem2mem, vb2 DMA-contig, DMAengine interleaved DMA, and the platform bus. It registers as a platform driver named `m2m-deinterlace` and exposes `V4L2_CAP_VIDEO_M2M | V4L2_CAP_STREAMING`. It does not use hardware-specific registers; the DMAengine provider supplies the actual copy engine.

## Risks
The global `q_data` means multiple opens can overwrite each other's negotiated formats, which is a serious multi-instance correctness risk. `queue_init()` appears to assign the destination default field into `q_data[V4L2_M2M_SRC].field`, leaving destination field initialization suspicious. If `deinterlace_issue_dma()` fails to acquire addresses, prepare, or submit a DMA descriptor, it returns without completing buffers or finishing the job, which can hang userspace. The code assumes the DMA template with one `data_chunk` is enough for all operations and reuses it across sequential submissions. Abort handling calls job finish but does not explicitly terminate in-flight DMA.

## Test Signals
Compile with DMAengine and V4L2 mem2mem enabled. Runtime tests should use two simultaneous file handles to expose global-format leakage, validate all four field conversion modes, stream YUV420 and YUYV with MMAP/DMABUF, inject DMA prep/submit failures, and run streamoff/close while a job is busy. V4L2 compliance should verify queue setup, field validation, and timestamp propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/m2m-deinterlace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/marvell/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/marvell/Kconfig

## Purpose
This Kconfig file declares Marvell media platform driver options for two camera controller integrations built on the shared MCAM core: the PCI-based Marvell 88ALP01 Cafe CCIC controller and the platform-device Armada 610/MMP camera controller.

## Important APIs, Types, And Functions
There are no C APIs. `VIDEO_CAFE_CCIC` is a tristate for the 88ALP01 Cafe controller and depends on media platform drivers, PCI, I2C, `VIDEO_DEV`, and `COMMON_CLK`. It selects V4L2 async support, optional OV7670 autoselection, and vb2 vmalloc, DMA-contig, and DMA-SG backends. `VIDEO_MMP_CAMERA` is a tristate for Marvell Armada 610/MMP camera controllers and depends on I2C, `VIDEO_DEV`, `ARCH_MMP || COMPILE_TEST`, and `COMMON_CLK`. It selects OV7670 autoselection, `I2C_GPIO`, V4L2 async, and the same vb2 memory backends.

## Control Flow And State
The file controls build inclusion only. The selected memory backends are important because `mcam-core.c` conditionally compiles support for vmalloc, contiguous DMA, and scatter-gather modes based on vb2 backend symbols.

## Dependencies And Integration Points
The adjacent Makefile uses `CONFIG_VIDEO_CAFE_CCIC` to build `cafe_ccic.o` plus `mcam-core.o`, and `CONFIG_VIDEO_MMP_CAMERA` to build `mmp_camera.o` plus `mcam-core.o`. Both drivers integrate with external OV7670 sensor support when media subdevice autoselection is enabled.

## Risks
Because the shared MCAM core conditionally compiles buffer modes from selected vb2 backends, changing selected symbols can remove runtime buffer modes. The Cafe driver is PCI/I2C-specific while MMP is platform/OF-specific, so dependency broadening under `COMPILE_TEST` must retain the support APIs they include. Selecting all three vb2 backends increases build coverage but also exposes code paths that platform defaults may not normally use.

## Test Signals
Build `VIDEO_CAFE_CCIC=m` and `VIDEO_MMP_CAMERA=m`, including `COMPILE_TEST` for MMP on non-MMP architectures. Check that `mcam-core.o` links correctly into each module and that OV7670 autoselection behaves as expected under media subdriver autoselect configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/marvell/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/marvell/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/marvell/Makefile

## Purpose
This Makefile builds the two Marvell camera controller modules and links both against the shared `mcam-core.o` implementation.

## Important APIs, Types, And Functions
There are no runtime APIs. `obj-$(CONFIG_VIDEO_CAFE_CCIC) += cafe_ccic.o mcam-core.o` builds the Cafe module support, with `cafe_ccic-y := cafe-driver.o`. `obj-$(CONFIG_VIDEO_MMP_CAMERA) += mmp_camera.o mcam-core.o` builds the MMP module support, with `mmp_camera-y := mmp-driver.o`.

## Control Flow And State
Build state follows the two Kconfig symbols. Both configurations compile `mcam-core.o`; if both are enabled, the build system must avoid duplicate symbol problems through normal kernel object/module handling.

## Dependencies And Integration Points
The Makefile is the bridge between Kconfig and `cafe-driver.c`, `mmp-driver.c`, and `mcam-core.c`. It reflects the architectural split: platform glue lives in the wrapper objects, while V4L2/vb2/register/IRQ frame logic lives in `mcam-core.o`.

## Risks
`mcam-core.c` exports `mccic_*` symbols and also contains module metadata, so incorrect object grouping can produce duplicate or missing symbol behavior. If the core is refactored into a library-like object, this Makefile must preserve the intended link ownership for both modules.

## Test Signals
Build Cafe only, MMP only, and both enabled. Verify that modules contain the expected driver aliases and that no duplicate `mccic_*` symbol or module metadata warnings appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/marvell/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/marvell/cafe-driver.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/marvell/cafe-driver.c

## Purpose
This file is the PCI/platform glue for the Marvell 88ALP01 "Cafe" CMOS Camera Controller, used by first-generation OLPC systems. It initializes PCI resources, exposes the controller's hardware SMBus block as a Linux I2C adapter for the OV7670 sensor, performs Cafe-specific power/reset sequencing, and delegates V4L2 capture behavior to `mcam-core.c`.

## Important APIs, Types, And Functions
`struct cafe_camera` wraps an `mcam_camera`, PCI device pointer, I2C adapter, wait queue, and a `registered` flag. Cafe-specific register definitions include GPIO/power registers (`REG_GPR`), TWSI/SMBus registers (`REG_TWSIC0`, `REG_TWSIC1`), and global control/interrupt/GPIO registers. SMBus functions include `cafe_smbus_write_data()`, `cafe_smbus_read_data()`, `cafe_smbus_xfer()`, `cafe_smbus_setup()`, and `cafe_smbus_shutdown()`. Controller hooks include `cafe_ctlr_init()`, `cafe_ctlr_power_up()`, and `cafe_ctlr_power_down()`. PCI lifecycle is handled by `cafe_pci_probe()`, `cafe_shutdown()`, remove, suspend, and resume.

## Control Flow
Module init registers a PCI driver for `PCI_DEVICE_ID_MARVELL_88ALP01_CCIC`. Probe allocates `cafe_camera`, initializes the embedded MCAM state for `MCAM_CAFE`, selects vmalloc buffer mode, enables PCI bus mastering, maps registers, requests a shared IRQ, initializes the controller/global registers, registers an SMBus adapter, registers V4L2, initializes an async notifier for an OV7670 client on the Cafe SMBus adapter, calls `mccic_register()`, creates an `xclk` clock lookup for the sensor, instantiates the OV7670 I2C client, and marks the device registered.

Interrupt handling reads `REG_IRQSTAT`, calls `mccic_irq()` for frame interrupts when the device is registered, clears TWSI interrupts, and wakes the SMBus wait queue. SMBus read/write operations program the hardware TWSI registers, wait for interrupt-driven completion with timeout fallback, and report controller error/status bits. Suspend calls `mccic_suspend()`. Resume reinitializes Cafe registers and calls `mccic_resume()`.

## State And Persistence
Cafe-specific state is limited to the PCI device, I2C adapter, wait queue, and the `registered` flag. Capture state, formats, buffers, and frame counters are owned by `mcam_camera`. Hardware state includes global reset/clock bits, GPIO sensor power/reset lines, TWSI command registers, and MCAM registers.

## Dependencies And Integration Points
The file depends on PCI, I2C, interrupt handling, clkdev, OV7670 platform data, and `mcam-core.h`. It supplies `plat_power_up` and `plat_power_down` callbacks used by the core. It integrates with the Linux I2C stack by implementing only byte-data SMBus transactions, which matches the OV7670 use case.

## Risks
The SMBus hardware has timing quirks: write completion needs a post-interrupt delay, reads/writes can hang or silently complete, and the code relies on timeout recovery. The global control registers are shared with other Cafe functions such as NAND/SD, so reset/clock changes may have cross-device effects. Probe has many ordered resources; error unwind must keep PCI IRQ, I/O mapping, V4L2, SMBus, and MCAM registration balanced. The hard-coded OV7670 client and OLPC wiring assumptions limit reuse.

## Test Signals
Test PCI probe/remove, SMBus byte read/write timeouts and TWSI interrupt wakeups, OV7670 client creation, capture streaming through MCAM vmalloc mode, suspend/resume, and error injection in each probe stage. On actual Cafe hardware, validate GPIO power/reset polarity and that global register initialization does not disturb sibling devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/marvell/cafe-driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/marvell/mcam-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/marvell/mcam-core.c

## Purpose
This file implements the shared Marvell CCIC camera core used by both Cafe and MMP platform wrappers. It owns V4L2 device behavior, async sensor binding, format negotiation, vb2 queue management, capture start/stop, frame interrupt processing, sensor clock control, power sequencing, and buffer handling across vmalloc, DMA-contiguous, and DMA scatter-gather modes.

## Important APIs, Types, And Functions
The exported platform-facing API is `mccic_register()`, `mccic_irq()`, `mccic_shutdown()`, `mccic_suspend()`, and `mccic_resume()`. Internal state is mostly `struct mcam_camera` from `mcam-core.h` plus `struct mcam_vb_buffer` and `struct mcam_dma_desc`. Format support is encoded in `mcam_formats[]`, mapping V4L2 fourccs to bytes-per-pixel, planar state, and media-bus codes.

Major internal functions include DMA setup/completion for vmalloc (`mcam_alloc_dma_bufs()`, `mcam_ctlr_dma_vmalloc()`, `mcam_frame_work()`), DMA-contig (`mcam_set_contig_buffer()`, `mcam_dma_contig_done()`), DMA-SG (`mcam_sg_next_buffer()`, `mcam_dma_sg_done()`, `mcam_sg_restart()`), hardware image configuration (`mcam_ctlr_image()`, `mcam_ctlr_configure()`), power and MIPI helpers, master clock `clk_ops`, vb2 callbacks, V4L2 ioctl handlers, file open/release, async notifier callbacks, and interrupt frame completion handling.

## Control Flow
`mccic_register()` validates or overrides the requested buffer mode, initializes mutex/state/default format, registers the async notifier, registers an `mclk` provider, and optionally preallocates vmalloc-mode coherent DMA buffers. When a sensor binds, `mccic_notify_bound()` resets/initializes the sensor, sets up vb2 according to buffer mode, clones the video-device template, and registers the video node.

Open powers the sensor and runtime PM, resets the camera, and marks hardware config needed. Format try/set delegates to the sensor pad format path, computes bytesperline/sizeimage, and marks controller configuration dirty. Streaming starts in `mcam_vb_start_streaming()`: if real buffers are not yet available for DMA modes it enters `S_BUFWAIT`; otherwise it resets counters and calls `mcam_read_setup()`. That function configures the sensor and controller if needed, enables or disables MIPI based on bus type, enables frame interrupts, sets `S_STREAMING`, and starts the controller unless SG restart is pending.

`mccic_irq()` is called by platform IRQ handlers with `dev_lock` held. It clears frame interrupts, records SOF bits, marks DMA active, stops the controller on SOF in SG mode, and completes frames only when EOF has a matching SOF. Completion updates sequence/frame counters and dispatches to the active buffer-mode completion callback. Stop streaming stops DMA with a long hardware settle wait and returns queued/active buffers as errors.

## State And Persistence
The core keeps a state machine (`S_NOTREADY`, `S_IDLE`, `S_FLAKED`, `S_STREAMING`, `S_BUFWAIT`), bit flags for valid frames, DMA active, config-needed, single-buffer fallback, SG restart, and SOF tracking, plus frame counters, vb2 buffer lists, active hardware buffers, default/current pix format, and current media-bus code. No state persists across module/device lifetime, but suspend/resume preserves logical streaming state and restarts if needed.

## Dependencies And Integration Points
The core depends on V4L2, V4L2 async, controls/events, vb2 memory backends, runtime PM, clock framework, and platform-supplied `mcam_camera` fields. Cafe and MMP wrappers supply register mapping, locks, device, chip ID, buffer mode, bus/MIPI parameters, IRQ calls, and optional platform power/DPHY callbacks. Sensor subdevices must support reset/init/power and pad format operations.

## Risks
The buffer-mode logic is complex. Vmalloc mode copies from internal coherent buffers in bottom-half work; DMA-contig reuses buffers when userspace underruns; SG mode must stop/restart the controller between frames and tracks `CF_SG_RESTART`. Frame completion relies on matching SOF/EOF bits; hardware that drops SOF or reports multiple frames can stress this logic. `mcam_ctlr_stop_dma()` uses a fixed 150 ms sleep and only logs if DMA remains active. Runtime PM is tied into the exported sensor clock, so clock consumers can power the controller unexpectedly. Error handling around `mcam_cam_configure()` adds return values and may mask which subdev operation failed.

## Test Signals
Build all vb2 backend combinations selected by Kconfig. Runtime coverage should exercise vmalloc, DMA-contig, and DMA-SG buffer modes; empty-buffer underrun behavior; SG restart after a later buffer arrives; format negotiation for packed, planar, RGB, and Bayer formats; read and streaming io modes; SOF/EOF interrupt ordering; stop streaming during active DMA; suspend/resume with open users and active streaming; and notifier bind/unbind. V4L2 compliance and stress streaming with low buffer counts are strong signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/marvell/mcam-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/marvell/mcam-core.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/marvell/mcam-core.h

## Purpose
This header defines the shared Marvell camera core contract, including platform-populated device state, buffer mode choices, exported core functions, register I/O helpers, and the CCIC register map used by Cafe and MMP wrappers plus `mcam-core.c`.

## Important APIs, Types, And Constants
Key enums are `enum mcam_state`, `enum mcam_buffer_mode`, and `enum mcam_chip_id`. `struct mcam_frame_state` tracks frames, single-buffer cases, and delivered frames. `struct mcam_camera` is the central device object: platform fields include register base/size, spinlock, device, chip ID, buffer mode, clock/MIPI settings, clock handles, and platform callbacks; private core fields include V4L2 objects, state flags, notifier/sensor, vb2 queue/list, DMA buffers, sequence counters, mode-specific callbacks, current pixel format, media-bus code, and mutex.

The exported functions are `mccic_register()`, `mccic_irq()`, `mccic_shutdown()`, `mccic_suspend()`, and `mccic_resume()`. Inline helpers `mcam_reg_write()`, `mcam_reg_read()`, `mcam_reg_write_mask()`, `mcam_reg_clear_bit()`, and `mcam_reg_set_bit()` centralize MMIO access.

## Control Flow And State
The header does not run code beyond inline register helpers. It describes runtime state ownership: platform code fills the top part of `struct mcam_camera` before calling `mccic_register()`, while the core owns the lower private fields after registration. Register definitions cover DMA BARs, MIPI CSI2 controls, image pitch/size/offset, IRQ status/mask/clear, controller format/control bits, clock control, Cafe upper address, and Armada descriptor registers.

## Dependencies And Integration Points
The header depends on Linux list/clock/workqueue and V4L2/vb2 headers. It is shared by `mcam-core.c`, `cafe-driver.c`, and `mmp-driver.c`. Its compile-time buffer mode macros mirror selected vb2 backends and hard-fail if no supported backend is configured.

## Risks
Because `struct mcam_camera` mixes platform-owned and core-private fields, platform drivers can accidentally modify core state if boundaries are not respected. Register helper callers must hold `dev_lock` when required by the comments. Buffer-mode availability is compile-time conditional, so code paths referenced by platform defaults must be present in Kconfig selections. Register defines are used for multiple chip generations; bits marked Cafe-only or Armada-only should not be applied blindly across variants.

## Test Signals
Compile both Cafe and MMP drivers with each selected backend. Static checks should catch missing vb2 mode symbols. Runtime register dump/debug tests should verify offsets and bit fields for each chip. API tests should ensure platform wrappers initialize all required public fields before `mccic_register()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/marvell/mcam-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/marvell/mmp-driver.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/marvell/mmp-driver.c

## Purpose
This file is the platform-device wrapper for Marvell MMP/Armada 610 camera controllers. It supplies MMP-specific clock handling, MIPI D-PHY calculation, OF sensor discovery, IRQ routing, runtime/system PM, and core registration around the shared MCAM V4L2 implementation.

## Important APIs, Types, And Functions
`struct mmp_camera` contains the platform device, embedded `mcam_camera`, list node, MIPI clock, and IRQ number. `mmpcam_calc_dphy()` computes CSI2 D-PHY register values from platform data and the MIPI clock. `mmpcam_irq()` reads `REG_IRQSTAT` and forwards it to `mccic_irq()`. `mcam_init_clk()` obtains the core clocks named `axi`, `func`, and `phy`. Lifecycle and PM are handled by `mmpcam_probe()`, `mmpcam_remove()`, `mmpcam_runtime_resume()`, `mmpcam_runtime_suspend()`, `mmpcam_suspend()`, and `mmpcam_resume()`.

## Control Flow
Probe allocates `mmp_camera`, initializes the embedded `mcam_camera`, copies platform data for clock source/divider, bus type, D-PHY values, and lane count when available, or falls back to historical parallel-bus defaults. For CSI2 it obtains the `mipi` clock unless an existing DPHY6 value makes it unnecessary. It sets chip ID `MCAM_ARMADA610`, default buffer mode `B_DMA_sg`, bus info, register mapping, and common clocks. It registers the V4L2 device, finds the first OF graph endpoint, creates a V4L2 async notifier connection to the remote sensor, calls `mccic_register()`, adds an OF clock provider for the sensor master clock, requests the shared IRQ, and enables runtime PM.

The IRQ handler holds `mcam.dev_lock`, reads pending CCIC interrupts, and lets the core process frame state. Runtime resume enables the three optional clocks in order; runtime suspend disables them in reverse. System suspend/resume delegates to `mccic_suspend()` / `mccic_resume()` when runtime PM has not already suspended the device.

## State And Persistence
Most capture state is in the embedded core object. Wrapper state includes obtained clocks, MIPI clock, IRQ number, platform D-PHY data, and runtime PM status. D-PHY registers are recalculated on MIPI enable through the core callback. No persistent storage exists.

## Dependencies And Integration Points
The wrapper depends on OF graph endpoints, platform resources, runtime PM, common clock framework, optional board platform data from `mmp-camera.h`, and `mcam-core.h`. It integrates with the core through the `calc_dphy` callback, bus/MIPI fields, clocks, IRQ forwarding, and `mccic_*` lifecycle API.

## Risks
The code assumes valid platform data for CSI2 paths: `mcam->dphy` is dereferenced when checking `mcam->dphy[2]`, so missing platform data for a CSI2 configuration would be dangerous unless DT never sets that path without pdata. Optional clocks are stored even when `devm_clk_get()` fails; PM paths must keep guarding `IS_ERR()`. `of_clk_add_provider()` is not explicitly removed in remove, which should be checked against devres/OF clock provider expectations. Error unwind after adding the clock provider and before PM enable calls `mccic_shutdown()` but does not appear to undo the provider.

## Test Signals
Build with `COMPILE_TEST` and on MMP configs. Runtime tests should cover probe with parallel bus DT, CSI2 platform data, missing optional clocks, absent endpoint, IRQ frame forwarding, runtime PM clock ordering, system suspend/resume while streaming, and MIPI lane/DPHY calculation. Device tree validation should check `clock-output-names`, graph endpoint, and clock names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/marvell/mmp-driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/Kconfig

## Purpose
This Kconfig file provides the MediaTek media platform driver menu and includes the sub-Kconfig files for the MediaTek JPEG, MDP, video codec, VPU, and MDP3 driver families.

## Important APIs, Types, And Functions
There are no C APIs. The file emits a menu comment and sources `drivers/media/platform/mediatek/jpeg/Kconfig`, `mdp/Kconfig`, `vcodec/Kconfig`, `vpu/Kconfig`, and `mdp3/Kconfig`.

## Control Flow And State
Kconfig inclusion order makes the nested MediaTek driver symbols visible under the media platform hierarchy. The state is entirely build-time configuration.

## Dependencies And Integration Points
This file is included by the parent media platform Kconfig. The adjacent Makefile mirrors this structure by descending into the same subdirectories. For this work item, the relevant child is `jpeg/Kconfig`, which defines `VIDEO_MEDIATEK_JPEG`.

## Risks
Path drift is the primary risk: if a subdirectory is renamed or removed, this Kconfig will break menu parsing. Inclusion order can matter if child symbols depend on symbols defined by earlier child files, so reordering should be deliberate.

## Test Signals
Run Kconfig parsing through normal kernel configuration targets and ensure all sourced child Kconfigs exist. Enable each child family independently to verify menu visibility and dependency reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/Makefile

## Purpose
This Makefile descends into MediaTek media platform subdirectories so their local Makefiles can add objects according to their own Kconfig symbols.

## Important APIs, Types, And Functions
There are no runtime APIs. The build rules are unconditional directory recursion entries: `obj-y += jpeg/`, `mdp/`, `vcodec/`, `vpu/`, and `mdp3/`.

## Control Flow And State
The parent media build always visits these subdirectories when this Makefile is included. Actual object inclusion remains controlled by each child Makefile's config symbols.

## Dependencies And Integration Points
The file mirrors `mediatek/Kconfig` source entries. For this work item, it routes the build to `mediatek/jpeg/Makefile`, where `CONFIG_VIDEO_MEDIATEK_JPEG` controls JPEG driver objects.

## Risks
Unconditional `obj-y` directory traversal requires all listed directories and Makefiles to exist. If a child Makefile has side effects or unconditional objects, they will be evaluated even when no child driver is selected.

## Test Signals
Run standard kernel builds with all MediaTek media symbols disabled and enabled. Confirm that disabling `VIDEO_MEDIATEK_JPEG` prevents JPEG objects from building despite directory traversal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/Kconfig

## Purpose
This Kconfig file declares the MediaTek JPEG codec driver option. The driver exposes hardware JPEG decode and encode functionality through the V4L2 mem2mem API.

## Important APIs, Types, And Functions
There are no C APIs. `VIDEO_MEDIATEK_JPEG` is a tristate labelled "Mediatek JPEG Codec driver". It depends on V4L2 mem2mem drivers, MediaTek IOMMU support or `COMPILE_TEST`, `VIDEO_DEV`, MediaTek architecture or `COMPILE_TEST`, and MediaTek SMI support or a compile-test case with SMI disabled. It selects `VIDEOBUF2_DMA_CONTIG` and `V4L2_MEM2MEM_DEV`.

## Control Flow And State
The symbol controls whether the objects in `mediatek/jpeg/Makefile` are built. Selected symbols guarantee the mem2mem framework and contiguous DMA allocator used by `mtk_jpeg_core.c`.

## Dependencies And Integration Points
The driver needs DMA-contiguous buffers and V4L2 mem2mem support. Its platform integration relies on OF matches in the core and child hardware files. The module name advertised to users is `mtk-jpeg`.

## Risks
The dependency expression around `MTK_SMI` allows compile testing when SMI is disabled, but real hardware paths may require SMI and IOMMU integration. If new SoC variants need additional clocks, IOMMU, or power-domain symbols, this Kconfig must reflect them to prevent runtime probe failures.

## Test Signals
Build as module and built-in under MediaTek SoC configs and under `COMPILE_TEST`. Check that `VIDEOBUF2_DMA_CONTIG` and `V4L2_MEM2MEM_DEV` are selected and that `mtk-jpeg` module objects link for all compatible variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/Makefile

## Purpose
This Makefile builds the MediaTek JPEG mem2mem driver and its encode/decode hardware helper objects when `CONFIG_VIDEO_MEDIATEK_JPEG` is enabled.

## Important APIs, Types, And Functions
The build rules add `mtk_jpeg.o`, `mtk-jpeg-enc-hw.o`, and `mtk-jpeg-dec-hw.o` under `CONFIG_VIDEO_MEDIATEK_JPEG`. `mtk_jpeg-y` is composed from `mtk_jpeg_core.o` and `mtk_jpeg_dec_parse.o`. The encode and decode hardware modules are built from `mtk_jpeg_enc_hw.o` and `mtk_jpeg_dec_hw.o`.

## Control Flow And State
Build state follows the Kconfig tristate. The split object layout keeps the V4L2/mem2mem core and JPEG header parser in one logical module object, with hardware-specific encode/decode helpers as additional objects.

## Dependencies And Integration Points
This file maps to `mtk_jpeg_core.c`, `mtk_jpeg_core.h`, parser code, and encode/decode hardware accessors. The core includes both encode and decode hardware headers and chooses behavior through OF match variant data.

## Risks
The object names use both underscores and hyphens. Module/object renames must update all composite assignments consistently. If hardware helper symbols are referenced by the core, omitting either helper from the config build will fail link.

## Test Signals
Build `CONFIG_VIDEO_MEDIATEK_JPEG=m` and verify that the resulting module contains core, parser, encoder hardware, and decoder hardware code. Build all OF variant paths to catch missing helper symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_core.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_core.c

## Purpose
This file implements the V4L2 mem2mem core for MediaTek JPEG hardware. It supports single-core and multi-core encode/decode variants, exposes JPEG and raw YUV formats, parses JPEG headers for decode resolution and output format, manages vb2 multiplanar queues, controls runtime PM/clocks, dispatches work to hardware, handles interrupts/timeouts, and registers the platform driver for several MediaTek compatibles.

## Important APIs, Types, And Functions
Format tables `mtk_jpeg_enc_formats[]` and `mtk_jpeg_dec_formats[]` describe JPEG, NV12M, NV21M, YUYV, YVYU, YUV420M, and YUV422M support with sampling, alignment, plane count, and direction flags. Variant tables (`mt8173_jpeg_drvdata`, `mtk_jpeg_drvdata`, `mtk8195_jpegenc_drvdata`, `mtk8195_jpegdec_drvdata`) select formats, vb2 ops, mem2mem ops, ioctl ops, default queue formats, IRQ handlers, reset functions, worker functions, multi-core mode, and 34-bit support.

Key functions include format helpers `mtk_jpeg_enum_fmt()`, `mtk_jpeg_try_fmt_mplane()`, `mtk_jpeg_s_fmt_mplane()`, event/selection handlers, decode qbuf/header parsing, vb2 callbacks, single-core device runs `mtk_jpeg_enc_device_run()` / `mtk_jpeg_dec_device_run()`, multi-core workers `mtk_jpegenc_worker()` / `mtk_jpegdec_worker()`, IRQ handlers `mtk_jpeg_enc_irq()` / `mtk_jpeg_dec_irq()`, timeout work, queue initialization, file open/release, probe/remove, and PM hooks.

## Control Flow
Probe allocates `mtk_jpeg_dev`, stores OF match variant data, populates child platform devices, initializes either single-core MMIO/IRQ/clocks or multi-core waitqueue/workqueue state, registers V4L2, initializes the m2m device with variant ops, allocates/registers the video device, and enables runtime PM.

Open allocates `mtk_jpeg_ctx`, initializes work, done queue, file handle, m2m context, controls for encoder variants, and default queue formats. Userspace negotiates multiplanar output/capture formats. Decode output queueing parses the JPEG header with `mtk_jpeg_parse()`, stores per-source decode parameters, emits a source-change event on first valid header, updates queue data, and transitions the context state from `INIT` to `RUNNING` or `SOURCE_CHANGE`.

Single-core encode/decode `device_run()` obtains source/destination buffers, resumes runtime PM, schedules timeout work, resets hardware, writes source/destination/config registers, and starts the hardware. Decode refuses to run when a queued JPEG implies resolution/format change; it emits a source-change event and waits for userspace streamoff acknowledgment. IRQ handlers cancel timeout work, remove buffers, set payload sizes, mark buffer state done or error, finish the m2m job, and put runtime PM. Multi-core variants queue context work; workers select an idle component device under a hardware lock, wait on `hw_wq` if all cores are busy, program the selected component, and finish the scheduler job while completion is later handled by component hardware code through shared buffer metadata.

## State And Persistence
Device state includes mutex, hardware lock, V4L2/m2m/video objects, variant pointer, single-core register base and timeout work, multi-core component arrays, waitqueue, `hw_rdy`, and hardware index. Context state includes output/capture queue data, `MTK_JPEG_INIT/RUNNING/SOURCE_CHANGE`, encoder controls, work item, frame numbering, and encode done queue. Per-source buffers store bitstream size and parsed decode parameters. No state persists beyond open/device lifetime.

## Dependencies And Integration Points
The core depends on V4L2 mem2mem, vb2 DMA-contig, runtime PM, clock bulk APIs, OF platform population, MediaTek JPEG encode/decode hardware helpers, and the JPEG decode parser. It exposes `V4L2_CAP_STREAMING | V4L2_CAP_VIDEO_M2M_MPLANE` and handles source-change events required by stateful decode workflows.

## Risks
Stateful decode depends on userspace honoring source-change events and streamoff sequencing. `mtk_jpeg_buf_prepare()` can set JPEG capture payload to `sizeimage + MTK_JPEG_MAX_EXIF_SIZE` when EXIF is enabled, so queue size validation must stay consistent. Error paths in `device_run()` and workers must remove and complete exactly the buffers they acquired; otherwise m2m queues can hang or double-complete. Multi-core workers use retry loops and `hw_rdy` accounting; mismatched increment/decrement or interrupted waits can starve hardware. Timeout work assumes current context and buffers still exist. Runtime PM and clock cleanup differ between single-core bulk clocks and component-device clocks.

## Test Signals
Build all compatibles. Run V4L2 compliance for encoder and decoder nodes, including multiplanar queue setup, controls, crop/compose selection, event subscription, and encoder/decoder commands. Runtime tests should encode YUYV/NV12M/NV21M to JPEG, decode JPEG to YUV420M/YUV422M, handle resolution changes midstream, validate EXIF APP1 sizing, inject invalid JPEG headers, trigger hardware timeout, suspend/resume while jobs are queued, and stress multi-core encode/decode with parallel contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_core.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_core.h

## Purpose
This header defines the core data model and variant contract for the MediaTek JPEG V4L2 mem2mem driver. It is shared by the core, parser, and encode/decode hardware support files.

## Important APIs, Types, And Constants
Constants define driver name, format direction flags, min/max dimensions, default JPEG buffer size, hardware timeout, maximum EXIF size, and low-address alignment mask. `enum mtk_jpeg_ctx_state` models decode/encode context state (`INIT`, `RUNNING`, `SOURCE_CHANGE`). `struct mtk_jpeg_variant` is the OF-selected behavior table containing clocks, formats, vb2 ops, IRQ/reset/m2m/ioctl callbacks, queue defaults, multi-core flag, worker callback, and 34-bit DMA support.

`struct mtk_jpeg_src_buf` extends a vb2 buffer with frame number, list node, bitstream size, parsed decode parameters, and current context pointer. `struct mtk_jpeg_hw_param` captures active source/destination/context for a hardware component. `struct mtk_jpegenc_comp_dev` and `struct mtk_jpegdec_comp_dev` describe per-core encode/decode component devices with registers, clocks, IRQ, timeout work, hw state, and lock. `struct mtk_jpeg_dev` is the master device object. `struct mtk_jpeg_fmt`, `struct mtk_jpeg_q_data`, and `struct mtk_jpeg_ctx` describe formats, queue state, and per-open state.

## Control Flow And State
The header has no runtime control flow. It defines how control flow is parameterized: variant callbacks choose encode versus decode, single-core versus multi-core, and SoC-specific hardware behavior. State ownership is split between the master device, per-component hardware devices, per-file contexts, per-queue format data, and per-source buffers.

## Dependencies And Integration Points
The header depends on Linux clocks/interrupts and V4L2/vb2 headers, and includes `mtk_jpeg_dec_hw.h` for decode parameter types. It is consumed by `mtk_jpeg_core.c` and component hardware implementations, which must agree on `mtk_jpeg_hw_param`, component device layout, and variant callback semantics.

## Risks
Structure fields are concurrency-sensitive: `hw_state` and component parameters are protected by spinlocks, while queue/context fields are protected by the device mutex and m2m framework. The same `mtk_jpeg_src_buf` type is used for source buffers and, in multi-core code, to attach frame metadata to destination buffers, so buffer struct sizing and container assumptions must match queue setup. Adding formats or variants requires consistent updates to format flags, default fourccs, queue plane counts, and hardware helper support.

## Test Signals
Build all source files that include this header. Static review should verify all fields documented in variants are initialized by each OF match table. Runtime tests should validate context state transitions, multi-core component state accounting, and per-buffer decode parameter lifetime across qbuf, device run, IRQ, timeout, and streamoff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_core.h -->
