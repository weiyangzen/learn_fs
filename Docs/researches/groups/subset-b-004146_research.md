# subset-b-004146 research

This grouped report covers NXP i.MX media platform drivers for the PXP, i.MX7 CSI, and i.MX8 ISI components. Each section preserves the original source path so reconciliation can split the report into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx-pxp.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx-pxp.c

## Purpose
`imx-pxp.c` is a V4L2 memory-to-memory driver for the i.MX Pixel Pipeline hardware. It exposes scaling, color-space conversion, rotation, horizontal and vertical flip, and alpha-component output as a `/dev/video*` mem2mem device backed by contiguous DMA buffers.

## Important APIs, Types, and Functions
The core device state is split between `struct pxp_dev`, which owns the V4L2 device, video node, regmap, clock, interrupt lock, and `v4l2_m2m_dev`, and `struct pxp_ctx`, which tracks one open file handle, controls, queue formats, colorimetry, rotation, flip mode, and abort state. Queue state lives in `struct pxp_q_data`, and pixel format capabilities are listed in `formats[]`.

Important helpers include `find_format()`, `get_q_data()`, `pxp_read()`, `pxp_write()`, `pxp_v4l2_pix_fmt_to_ps_format()`, `pxp_v4l2_pix_fmt_to_out_format()`, and `pxp_v4l2_pix_fmt_is_yuv()`. `pxp_setup_csc()` programs CSC1 and CSC2 coefficients for YUV-to-RGB and RGB-to-YUV conversions across BT.601, Rec.709, BT.2020, and SMPTE 240M limited/full range choices. SoC-specific data-path setup is provided by `pxp_imx6ull_data_path_ctrl0()` and `pxp_imx7d_data_path_ctrl0()`. Runtime operation flows through `pxp_start()`, `pxp_device_run()`, `pxp_irq_handler()`, and `pxp_job_finish()`.

The V4L2 surface is implemented by `pxp_ioctl_ops`, `pxp_fops`, `pxp_qops`, and `m2m_ops`. Controls are `V4L2_CID_HFLIP`, `V4L2_CID_VFLIP`, `V4L2_CID_ROTATE`, and `V4L2_CID_ALPHA_COMPONENT`. Probe/remove are handled by `pxp_probe()` and `pxp_remove()` with OF compatibles `fsl,imx6ull-pxp` and `fsl,imx7d-pxp`.

## Control Flow
Probe allocates `pxp_dev`, reads platform match data, gets the `axi` clock, maps MMIO through regmap, requests the IRQ, enables the clock, performs `pxp_soft_reset()`, registers the V4L2 device, initializes the mem2mem core, and registers the video node. With media controller support enabled, it also creates and registers the media device entity for a video pixel formatter.

On open, the driver allocates a per-file `pxp_ctx`, creates the control handler, initializes default 640x480 formats, and creates the mem2mem context with `queue_init()`. Userspace negotiates output and capture formats through try/set ioctls. Width and height are clamped to 8-pixel aligned 8..4096 ranges, bytes-per-line and sizeimage are derived from format depth, and capture colorimetry is either inherited from source when no CSC is possible or mapped to defaults for conversion.

When both queues have buffers, `pxp_device_run()` selects the next source and destination buffers and calls `pxp_start()`. `pxp_start()` obtains DMA addresses, propagates timestamps and buffer flags, computes rotation-adjusted output geometry, configures planar and semiplanar buffer offsets, computes decimation and scale factors, writes output, processed-surface, background, color key, CSC, LUT, data-path, interrupt, and control registers, then starts the hardware. `pxp_irq_handler()` clears the completion interrupt and calls `pxp_job_finish()`, which returns both buffers as done and completes the mem2mem job.

## State and Persistence
Persistent kernel-visible state is in the V4L2 device registration and per-open contexts; all image-processing state is volatile per job and programmed into PXP registers. Buffer sequence counters live in `pxp_q_data` and reset at stream start. Register state is not restored across power loss beyond probe reset and per-job programming. The driver uses `dev_mutex` around file and queue operations and `irqlock` around buffer completion.

## Dependencies and Integration Points
The driver depends on V4L2 mem2mem, videobuf2 DMA-contig, media controller support when configured, regmap MMIO, platform OF matching, an `axi` clock, and an IRQ. It integrates with the register definitions in `imx-pxp.h` and accepts only DMA-contiguous MMAP or DMABUF buffers. Pixel formats map V4L2 FourCC values to PXP processed-surface and output format fields.

## Risks and Edge Cases
`pxp_device_run()` ignores the return value from `pxp_start()`, so a DMA address failure can leave a mem2mem job without explicit error completion. Scaling calculations divide by `dst_width - 1` and `dst_height - 1` in non-decimated paths, but the enforced minimum size makes zero divisors unlikely. Capture and output format capabilities are asymmetric for some FourCCs, so tests must cover both queues. CSC coefficients cover common colorimetry but not arbitrary YCbCr-to-YCbCr or RGB range conversions. Remove resets and clocks off the device but does not coordinate with active users beyond normal device unregister behavior.

## Test Signals
Useful validation includes probing both i.MX6ULL and i.MX7D compatibles, successful soft reset and version read, `v4l2-compliance` mem2mem coverage, format enumeration for capture/output-only asymmetries, streaming with RGB, packed YUV, semiplanar YUV, and planar YUV formats, rotation 90/270 geometry swaps, flip controls, alpha output, full and limited range CSC conversions, interrupt completion, queue stop returning pending buffers with error, and media-controller registration when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx-pxp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx-pxp.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx-pxp.h

## Purpose
`imx-pxp.h` is the register and bitfield definition header for the Freescale/NXP i.MX Pixel Pipeline block. It provides the symbolic offsets, masks, shifts, field-construction macros, and enumerated field values used by `imx-pxp.c` to program the PXP hardware.

## Important APIs, Types, and Functions
The file exports preprocessor macros only. Register offset groups include `HW_PXP_CTRL`, `HW_PXP_STAT`, `HW_PXP_OUT_*`, `HW_PXP_PS_*`, `HW_PXP_AS_*`, `HW_PXP_CSC1_*`, `HW_PXP_CSC2_*`, `HW_PXP_LUT_*`, `HW_PXP_ALPHA_*`, `HW_PXP_DATA_PATH_CTRL*`, `HW_PXP_IRQ_MASK`, `HW_PXP_IRQ`, `HW_PXP_NEXT`, `HW_PXP_DEBUG*`, and `HW_PXP_VERSION`.

For most fields the header defines `BP_*` bit positions, `BM_*` masks, `BF_*()` value packing macros, and `BV_*__*` enumerants. Important groups include global control bits for reset, clock gate, enable, interrupts, rotation, flipping, CSC2, LUT, dither, and PS/AS output; status bits for completion and AXI errors; output and processed-surface buffer addressing, pitch, dimensions, decimation, scale, and format fields; alpha-surface blending and ROP fields; CSC coefficient packing for both CSC engines; data path mux fields; and 36-bit-free 32-bit DMA address fields.

## Control Flow
There is no runtime control flow in this header. It participates at compile time by expanding constants and bitfield constructors in the PXP driver. The driver writes the register offsets through regmap and builds values with these macros when configuring per-job geometry, formats, CSC coefficients, interrupts, and data-path muxing.

## State and Persistence
The header stores no state. It encodes the hardware's volatile register layout. Correctness depends on these macros matching the SoC register specification used by the runtime driver.

## Dependencies and Integration Points
The primary integration point is `imx-pxp.c`, which includes the header and uses its offsets as the regmap address space. The `HW_PXP_VERSION` offset also defines the maximum register exposed in the driver's regmap config. The macro style is compatible with plain C constant expressions and includes a special `BF_PXP_CSC1_COEF0_UV_OFFSET()` multiplication form to work around an old GCC constant-expression issue with negative values.

## Risks and Edge Cases
Generated-style headers are prone to silent hardware misprogramming if masks, offsets, or enumerants drift from the reference manual. Some fields describe unused driver capabilities such as LUT, alpha surfaces, WFE, memory init, and debug paths, so changes could affect future users even if current code does not exercise them. Several signed CSC offset fields are packed through unsigned masks, so coefficient tests should verify negative offset encoding.

## Test Signals
Build coverage is the main static signal: all macros must compile in `imx-pxp.c`. Runtime signals are correct PXP reset, version read at `HW_PXP_VERSION`, successful format programming, correct IRQ masking and clearing, accurate CSC output, and no AXI or status error bits when exercising supported buffer layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx-pxp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx7-media-csi.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx7-media-csi.c

## Purpose
`imx7-media-csi.c` implements the i.MX6UL/i.MX7/i.MX8MQ CSI capture bridge as a V4L2 subdevice plus a video capture node. It receives pixels from a parallel source, a CSI-2 receiver, or a muxed upstream entity, configures the CSI hardware, and writes frames into videobuf2 DMA-contiguous capture buffers.

## Important APIs, Types, and Functions
`struct imx7_csi` is the central state object. It stores MMIO, IRQ, clock, media and V4L2 devices, async notifier, source subdevice, CSI-2 detection, CSI subdev pads, video device, capture format, compose rectangle, vb2 queue, ready queue, two active hardware framebuffer slots, a coherent underrun buffer, streaming state, frame sequence, EOF completion state, and model data. `struct imx7_csi_pixfmt` maps memory FourCCs to media bus codes, bits per pixel, and YUV/RGB classification.

Hardware helpers include `imx7_csi_reg_read()`, `imx7_csi_reg_write()`, `imx7_csi_irq_clear()`, `imx7_csi_init_default()`, `imx7_csi_configure()`, `imx7_csi_enable()`, `imx7_csi_disable()`, and `imx7_csi_error_recovery()`. DMA and buffer helpers include `imx7_csi_alloc_dma_buf()`, `imx7_csi_dma_setup()`, `imx7_csi_setup_vb2_buf()`, `imx7_csi_video_next_buf()`, `imx7_csi_vb2_buf_done()`, and `imx7_csi_fast_track_buffer()`. V4L2 entry points are split across video ioctls, vb2 queue ops, file ops, subdev pad ops, async notifier callbacks, and platform probe/remove.

## Control Flow
Probe allocates `struct imx7_csi`, gets `mclk`, maps MMIO, requests the CSI IRQ, stores model data from OF, initializes the media device and CSI subdev, registers an async notifier for endpoint 0, and later links the bound upstream subdev to the CSI sink pad. The media graph creates a CSI subdev with sink/source pads and a capture video node linked from the source pad.

Format negotiation occurs at both subdev and video-node levels. The subdev sink accepts supported bus codes and propagates size, code, field, and colorimetry to the source pad. The video node chooses a memory FourCC, aligns width to an 8-byte hardware requirement expressed in pixels, derives bytesperline and sizeimage, and stores a fixed compose rectangle. Before streaming, `imx7_csi_video_validate_fmt()` checks that media bus size and YUV/RGB class match the capture node format.

Stream start validates formats, starts the media pipeline, calls the CSI subdev `s_stream(1)`, enables the clock, configures CSI registers for parallel or CSI-2 input, allocates the underrun buffer, primes FB1 and FB2, starts the upstream source, clears FIFO/DMA state, enables interrupts, enables DMA requests, and enables hardware. Each framebuffer completion interrupt chooses FB1 or FB2, returns the completed vb2 buffer if present, fetches the next queued buffer or underrun buffer, writes the hardware base-address register, and increments the frame sequence. Stream stop marks the next EOF as last, waits up to two seconds, disables IRQs and DMA, stops upstream streaming, returns active/queued buffers, resets defaults, and disables the clock.

## State and Persistence
State is runtime-only. The CSI registers, active framebuffer addresses, and coherent underrun buffer are re-created for each stream. The ready queue is protected by `q_lock`; `buf_num`, `active_vb2_buf[]`, and `last_eof` are protected by `irqlock`. The driver uses media graph state to infer whether the upstream source is CSI-2 and to validate stream links. No persistent storage exists.

## Dependencies and Integration Points
The driver depends on V4L2 subdevs, async notifier and fwnode graph bindings, media controller pipeline helpers, videobuf2 DMA-contig, the platform clock named `mclk`, CSI MMIO registers, and an IRQ. It integrates with upstream sensors, muxes, or CSI-2 bridges through media links and stream enable/disable calls. OF compatibles are `fsl,imx8mq-csi`, `fsl,imx7-csi`, and `fsl,imx6ul-csi`.

## Risks and Edge Cases
The two-register DMA scheme has a race when userspace queues a buffer just as hardware switches framebuffers; `imx7_csi_fast_track_buffer()` mitigates this by checking the opposite completion bit but intentionally falls back to the slow path on ambiguity. If both FB1 and FB2 completion bits are set, the handler cannot know which buffer is active and skips updating `buf_num`, which can affect buffer replacement latency. The underrun buffer prevents DMA into invalid memory but can hide userspace starvation as dropped frames. The stop path depends on receiving a final EOF and logs a timeout when hardware or upstream stops unexpectedly. Input format support and YUYV/UYVY packing differ between parallel and CSI-2 paths, making media graph validation important.

## Test Signals
Strong signals include successful async binding and immutable media links, `media-ctl` format propagation, `v4l2-compliance` on the capture node, streaming from parallel and CSI-2 sources, RAW8/10/12/14 and YUV422 8-bit modes, correct width alignment and padded compose reporting, buffer starvation with underrun behavior, fast buffer queuing while streaming, FIFO overflow and HRESP error recovery, stream stop EOF completion, and suspend-like source start/stop ordering through the media pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx7-media-csi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/Kconfig

## Purpose
This Kconfig fragment defines the build-time configuration for the i.MX8 Image Sensor Interface driver and its optional memory-to-memory support.

## Important APIs, Types, and Functions
`config VIDEO_IMX8_ISI` is a tristate option for the main ISI V4L2 driver. It depends on `ARCH_MXC || COMPILE_TEST`, `HAS_DMA && PM`, and `VIDEO_DEV`. It selects `MEDIA_CONTROLLER`, `V4L2_FWNODE`, `VIDEO_V4L2_SUBDEV_API`, and `VIDEOBUF2_DMA_CONTIG`, and conditionally selects `V4L2_MEM2MEM_DEV` when `VIDEO_IMX8_ISI_M2M` is enabled. `config VIDEO_IMX8_ISI_M2M` is a bool dependent on the main driver.

## Control Flow
There is no runtime flow. At configuration time, enabling `VIDEO_IMX8_ISI` makes the ISI module or built-in driver available. Enabling `VIDEO_IMX8_ISI_M2M` includes additional mem2mem sources in the Makefile and enables real m2m registration functions instead of inline no-op stubs from `imx8-isi-core.h`.

## State and Persistence
The file contributes Kconfig symbols to the kernel configuration. Those symbols persist in `.config` and determine which driver objects are built.

## Dependencies and Integration Points
The fragment integrates with the media platform Kconfig tree, V4L2 core, media controller, fwnode parsing, videobuf2 DMA-contig memory allocator, runtime/system PM, and optional V4L2 mem2mem core.

## Risks and Edge Cases
The main option requires `PM`, so compile-test coverage without PM is intentionally excluded. `VIDEO_IMX8_ISI_M2M` is not tristate; it follows the main driver linkage and only toggles extra functionality. Missing selected dependencies would surface as link errors in ISI video, pipe, or m2m code.

## Test Signals
Build tests should cover `VIDEO_IMX8_ISI=m`, `VIDEO_IMX8_ISI=y`, compile-test builds on non-MXC architectures, and both enabled/disabled `VIDEO_IMX8_ISI_M2M` paths. Runtime tests should verify the module exposes capture support without m2m and both capture plus mem2mem nodes when m2m is selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/Makefile

## Purpose
This Makefile assembles the i.MX8 ISI driver objects according to the Kconfig options.

## Important APIs, Types, and Functions
The composite object `imx8-isi.o` is built from `imx8-isi-core.o`, `imx8-isi-crossbar.o`, `imx8-isi-gasket.o`, `imx8-isi-hw.o`, `imx8-isi-pipe.o`, and `imx8-isi-video.o`. `imx8-isi-debug.o` is appended when `CONFIG_DEBUG_FS` is enabled. `imx8-isi-m2m.o` is appended when `CONFIG_VIDEO_IMX8_ISI_M2M` is enabled. `obj-$(CONFIG_VIDEO_IMX8_ISI)` controls whether the composite object is built.

## Control Flow
There is no runtime control flow. Kbuild evaluates the configuration symbols and links the selected object files into the driver.

## State and Persistence
The Makefile stores build composition only. Runtime state is in the C sources it selects.

## Dependencies and Integration Points
It depends on Kbuild composite-object conventions and the symbols from the adjacent Kconfig file. Its object list is tightly coupled to declarations in `imx8-isi-core.h`; omitting a selected source would cause unresolved symbols for crossbar, gasket, hardware, video, pipe, debugfs, or m2m functions.

## Risks and Edge Cases
Optional debugfs and m2m files must remain guarded in headers and source so both selected and unselected builds link. Changes to object names or new source files require this Makefile to stay synchronized with exported functions.

## Test Signals
Build matrix signals are the main validation: build with `CONFIG_VIDEO_IMX8_ISI=m/y`, `CONFIG_DEBUG_FS=y/n`, and `CONFIG_VIDEO_IMX8_ISI_M2M=y/n`, then check that the resulting driver links and exports the expected capture, debugfs, and mem2mem functionality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-core.c

## Purpose
`imx8-isi-core.c` is the platform-driver and media-device core for the i.MX8 ISI driver. It handles device probing, SoC model data, clock and DMA setup, crossbar and pipeline registration, optional mem2mem registration, async source binding, media-device registration, debugfs initialization, and runtime/system power management.

## Important APIs, Types, and Functions
`struct mxc_isi_async_subdev` extends a V4L2 async connection with the input port number. Async callbacks are `mxc_isi_async_notifier_bound()` and `mxc_isi_async_notifier_complete()`. Media setup is driven by `mxc_isi_v4l2_init()` and `mxc_isi_v4l2_cleanup()`, with per-pipe helpers `mxc_isi_pipe_register()` and `mxc_isi_pipe_unregister()`.

SoC data is encoded in `struct mxc_isi_plat_data` instances for i.MX8MN, i.MX8MP, i.MX8QM, i.MX8QXP, i.MX8ULP, i.MX91, i.MX93, and i.MX95. These records define port count, channel count, register stride, interrupt-enable bit layouts, panic thresholds, gasket ops, buffer-active polarity behavior, and 36-bit DMA capability. PM hooks are `mxc_isi_pm_suspend()`, `mxc_isi_pm_resume()`, `mxc_isi_runtime_suspend()`, and `mxc_isi_runtime_resume()`. Driver lifecycle is `mxc_isi_probe()` and `mxc_isi_remove()`.

## Control Flow
Probe allocates `struct mxc_isi_dev`, stores OF match data, allocates the pipe array, gets all clocks, maps the main MMIO region, optionally resolves the gasket syscon, sets a 32-bit or 36-bit coherent DMA mask, enables runtime PM, initializes the crossbar, initializes every pipe, initializes V4L2/media registration, and creates debugfs files. V4L2 initialization registers the media and V4L2 devices, crossbar subdev, each pipe subdev and capture video node, immutable crossbar-to-pipe links, optional m2m device, and an async notifier for remote endpoints on each hardware port.

When an async source binds, the driver creates a stateless device link to enforce suspend/resume ordering and creates immutable fwnode links from the source to the corresponding crossbar input pad. When all sources are bound, it registers subdev nodes and the media device. Remove tears down debugfs, pipe resources, crossbar resources, V4L2/media registration, notifier state, and optional m2m state.

## State and Persistence
The driver maintains runtime state in `struct mxc_isi_dev`, including platform data, clocks, MMIO, gasket regmap, crossbar, pipes, m2m device, media/V4L2 devices, async notifier, and debugfs root. It persists no user data. Runtime PM gates and ungates all clocks; system suspend first asks video and m2m paths to suspend and then force-suspends runtime PM.

## Dependencies and Integration Points
The file depends on platform OF matching, clk bulk APIs, syscon regmap for gasket control, DMA mask APIs, PM runtime, V4L2 async notifier, media controller, and helper modules declared in `imx8-isi-core.h`. It integrates with `imx8-isi-crossbar.c`, pipe/video/m2m modules, `imx8-isi-gasket.c`, `imx8-isi-hw.c`, and `imx8-isi-debug.c`.

## Risks and Edge Cases
The pipe array is allocated with `kzalloc_objs()` and is not explicitly freed in remove, so the allocation model must be understood in the surrounding tree or checked for leak risk. Some error paths after partial pipe initialization go directly to crossbar cleanup and rely on devm or process lifetime for other resources. `dma_set_mask_and_coherent()` return is not checked, which can hide unsupported DMA mask configurations. Async notifier completion registers media only after all described sources bind, so malformed graph endpoints can keep the media device unavailable.

## Test Signals
Validation should include probe on each compatible with the expected number of crossbar pads and pipe nodes, correct 32-bit vs 36-bit DMA mask behavior, gasket syscon lookup on models that require it, async binding for all fwnode ports, media graph registration, runtime PM clock gating, system suspend/resume with active capture and m2m users, and debugfs creation/removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-core.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-core.h

## Purpose
`imx8-isi-core.h` is the shared internal contract for the i.MX8 ISI driver. It defines limits, defaults, formats, platform data, crossbar, pipe, video, m2m, buffer, gasket, and device structures, and declares the cross-module APIs used by the core, crossbar, hardware, video, pipe, debug, and optional mem2mem implementation files.

## Important APIs, Types, and Functions
Key constants define pad indices, width and height limits, default media bus codes and pixel format, driver names, and the maximum number of planes. `struct mxc_isi_format_info` and `struct mxc_isi_bus_format_info` describe memory and bus formats. `struct mxc_isi_buffer`, `struct mxc_isi_video`, `struct mxc_isi_pipe`, `struct mxc_isi_crossbar`, `struct mxc_isi_m2m`, and `struct mxc_isi_dev` define the driver's major state containers.

Platform abstractions include `enum model`, `struct mxc_isi_plat_data`, `struct mxc_isi_ier_reg`, `struct mxc_isi_set_thd`, and `struct mxc_gasket_ops`. Resource and control APIs include crossbar init/register functions, format lookup helpers, pipe acquire/release/enable/disable functions, video registration and vb2 helpers, optional m2m hooks, low-level channel acquire/chaining/configuration functions, buffer address programming, IRQ helpers, and debugfs init/cleanup.

## Control Flow
The header has no direct control flow, but it defines the call graph boundaries. `imx8-isi-core.c` constructs `struct mxc_isi_dev`, initializes crossbar and pipes, and registers video/m2m paths. Pipe and video code use channel acquisition and hardware functions to configure registers. Crossbar code uses gasket ops and stream routing. Conditional inline stubs make m2m and debugfs calls no-ops when their Kconfig symbols are disabled.

## State and Persistence
The structures in this header describe all persistent in-kernel runtime state for the ISI driver. Buffer queues and frame counters live in `struct mxc_isi_video`; resource ownership and channel chaining state live in `struct mxc_isi_pipe`; async media topology and platform capabilities live in `struct mxc_isi_dev`. None of the state is persistent across driver unload or system power loss.

## Dependencies and Integration Points
The header depends on Linux list, mutex, spinlock, V4L2, media controller, async notifier, controls, and videobuf2 types. It is included by all ISI implementation files. It also exposes `mxc_imx8_gasket_ops` and `mxc_imx93_gasket_ops` from the gasket implementation.

## Risks and Edge Cases
Because this header is the internal ABI between multiple objects, field-order or semantic changes can break resource ownership, locking, or buffer handling across modules. The `mxc_isi_pipe.lock` protects a broad set of fields and the channel control register; callers must respect that boundary. Conditional m2m/debug stubs must match the real functions' signatures. The `MXC_ISI_MAX_WIDTH_UNCHAINED` and chained resource fields encode the requirement that wider frames consume resources from an adjacent channel.

## Test Signals
Build coverage across all Kconfig combinations is essential. Runtime signals include correct resource acquisition/release across capture and m2m, correct line-buffer chaining above 2048 pixels, no races in video buffer queues under `buf_lock`, valid format enumeration and try-format results from shared helpers, and correct no-op behavior when debugfs or m2m support is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-crossbar.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-crossbar.c

## Purpose
`imx8-isi-crossbar.c` implements the ISI input crossbar as a V4L2 subdevice with stream-aware routing. It routes external pixel-link inputs and a memory input to ISI pipeline source pads, validates routing constraints, propagates formats, enables upstream streams, and programs optional SoC gasket blocks.

## Important APIs, Types, and Functions
`struct mxc_isi_crossbar` stores the subdevice, pads, input enable counters, and parent ISI pointer. `mxc_isi_crossbar_init()` creates one sink pad per hardware input port plus one memory sink and one source pad per ISI channel. `__mxc_isi_crossbar_set_routing()` validates routes with `V4L2_SUBDEV_ROUTING_NO_N_TO_1` and forbids memory input routes except to the first pipeline. `mxc_isi_crossbar_xlate_streams()` maps requested source-pad streams back to the connected sink pad and remote upstream subdev.

Stream handling is in `mxc_isi_crossbar_enable_streams()` and `mxc_isi_crossbar_disable_streams()`. Optional gasket setup is wrapped by `mxc_isi_crossbar_gasket_enable()` and `mxc_isi_crossbar_gasket_disable()`. Pad ops include media-bus code enumeration, get/set format, set routing, and stream enable/disable.

## Control Flow
Initialization constructs the subdev, marks it as a media mux with stream support, allocates pads and per-input counters, initializes media pads, and finalizes subdev state. The initial state creates a default 1:1 mapping from hardware input ports to pipeline outputs. Sink-pad format setting validates the bus code, clamps dimensions to ISI limits, stores the sink stream format, and propagates it to active source routes. Source-pad formats are read-only mirrors of their routed sink side.

When a downstream pipe enables streams on a crossbar source pad, the crossbar translates the source streams through active routes, finds the remote upstream pad, enables the gasket on the first user of that sink input, and calls `v4l2_subdev_enable_streams()` upstream. Disabling decrements the input enable count, disables upstream streams when it reaches zero, and then disables the gasket.

## State and Persistence
Runtime state is the V4L2 subdev active routing table and each `mxc_isi_input.enable_count`. Routing and formats are stored in V4L2 subdev state. There is no persistent storage. Gasket registers are programmed only while streams are enabled.

## Dependencies and Integration Points
The file depends on V4L2 subdev streams/routing APIs, media pad graph helpers, ISI bus format helpers, and optional gasket ops supplied by platform data. It integrates directly with upstream camera/CSI subdevices and downstream ISI pipe subdevices through immutable media links created by the core.

## Risks and Edge Cases
The enable count is per input, not per stream, with a TODO noting limited multiplexed stream tracking. Route validation forbids fan-in but callers must still avoid unsupported topologies. Gasket enable requires a single-entry frame descriptor from the upstream source; multi-entry descriptors fail. `mxc_isi_crossbar_disable_streams()` decrements without defensive underflow protection, so stream enable/disable pairing must be correct.

## Test Signals
Useful tests include default 1:1 routing, route changes while idle, rejection of memory input to nonzero pipelines, format propagation from sink to source streams, busy rejection while streaming, upstream stream enable/disable call ordering, gasket programming for CSI-2 frame descriptors, and reference-count behavior when multiple consumers use the same input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-crossbar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-debug.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-debug.c

## Purpose
`imx8-isi-debug.c` provides debugfs register dumps for each ISI pipe when `CONFIG_DEBUG_FS` is enabled.

## Important APIs, Types, and Functions
`mxc_isi_debug_dump_regs_show()` is the seq_file show function. It lists a fixed table of channel registers such as `CHNL_CTRL`, `CHNL_IMG_CTRL`, buffer addresses, scaler, crop, CSC, ROI, memory-read, and flow-control registers. When platform data advertises 36-bit DMA, it also dumps the extended address registers. `mxc_isi_debug_init()` creates a debugfs directory named after the device and one read-only file per pipe. `mxc_isi_debug_cleanup()` removes the tree.

## Control Flow
Debugfs initialization runs from core probe after the pipes have been initialized. Reading a pipe file calls `pm_runtime_get_if_in_use()` and returns an empty dump if the device is powered down. If active, it prints register names, offsets, and values, then drops the runtime PM reference.

## State and Persistence
The only stored state is `isi->debugfs_root`. Register values are read live from MMIO. Debugfs files are ephemeral and removed on driver detach.

## Dependencies and Integration Points
The file depends on debugfs, seq_file, runtime PM, MMIO reads, `imx8-isi-core.h`, and `imx8-isi-regs.h`. It integrates with the core through `mxc_isi_debug_init()` and `mxc_isi_debug_cleanup()` declarations, which become inline no-ops when debugfs is disabled.

## Risks and Edge Cases
The dump intentionally avoids waking a suspended device, so absence of output can mean the device is inactive rather than broken. Register reads are unsynchronized with streaming hardware and may show transient state. `sprintf(name, "pipe%u", pipe->id)` uses an 8-byte buffer, which is fine for current small pipe IDs but would need review if channel counts grew dramatically.

## Test Signals
Validation includes debugfs directory creation, one file per pipe, correct register dumps while streaming or runtime-active, no runtime wakeup when idle, inclusion of extended address registers on 36-bit DMA platforms, and cleanup after module removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-gasket.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-gasket.c

## Purpose
`imx8-isi-gasket.c` programs SoC-specific gasket or camera-mux registers between upstream camera interfaces and the ISI crossbar. It converts V4L2 frame descriptors and frame formats into syscon regmap writes for i.MX8MN/i.MX8MP-style gaskets and i.MX93 camera mux hardware.

## Important APIs, Types, and Functions
The file exports `mxc_imx8_gasket_ops` and `mxc_imx93_gasket_ops`. i.MX8 helpers `mxc_imx8_gasket_enable()` and `mxc_imx8_gasket_disable()` write per-port size and control registers under `GASKET_BASE(port)`, including CSI-2 data type and dual-component enable for `MIPI_CSI2_DT_YUV422_8B`. i.MX93 helpers `mxc_imx93_gasket_enable()` and `mxc_imx93_gasket_disable()` program `DISP_MIX_CAMERA_MUX`, including CSI-2 data type, gasket enable, and source type selection for parallel inputs.

## Control Flow
The crossbar calls the selected `mxc_gasket_ops.enable()` before enabling upstream streams for an input, passing the upstream frame descriptor, sink format, and port. The gasket function writes size/type fields and enables the block. When the last user of an input disables streams, crossbar calls the matching disable function, which clears the control register.

## State and Persistence
State is hardware register state in the syscon regmap referenced by `isi->gasket`. No software state is stored in this file. The registers are only meaningful while a stream is active and are cleared on disable.

## Dependencies and Integration Points
The file depends on `linux/bitfield.h`, `linux/regmap.h`, media CSI-2 data type definitions, and the `mxc_gasket_ops` contract from `imx8-isi-core.h`. Platform data in `imx8-isi-core.c` selects these ops for SoCs that require gasket programming.

## Risks and Edge Cases
The code assumes the frame descriptor has already been validated by the crossbar and uses entry 0 directly. YUV422 8-bit dual-component handling is hard-coded for the i.MX8 gasket path. The i.MX93 path ignores the `port` argument because it uses a single camera mux register, which matches current platform data but would not scale without changes. Incorrect `fsl,blk-ctrl` syscon wiring prevents gasket setup entirely.

## Test Signals
Tests should verify regmap writes for CSI-2 RAW and YUV422 data types, dual-component enable for YUV422 on i.MX8MN/i.MX8MP-style platforms, parallel-source source-type selection on i.MX93, gasket clear on stream disable, and failure-free interaction with crossbar stream enable/disable ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-gasket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-hw.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-hw.c

## Purpose
`imx8-isi-hw.c` contains the low-level ISI channel register programming and channel resource management. It programs input and output DMA addresses, memory-to-memory triggers, scaling, crop, color-space conversion, alpha, flip, panic thresholds, channel control, interrupts, reset/clock state, and line-buffer chaining.

## Important APIs, Types, and Functions
Buffer APIs are `mxc_isi_channel_set_inbuf()`, `mxc_isi_channel_set_outbuf()`, and `mxc_isi_channel_m2m_start()`. Pipeline configuration APIs include `mxc_isi_channel_config()`, `mxc_isi_channel_set_input_format()`, `mxc_isi_channel_set_output_format()`, `mxc_isi_channel_set_alpha()`, and `mxc_isi_channel_set_flip()`. IRQ APIs include `mxc_isi_channel_irq_status()` and `mxc_isi_channel_irq_clear()`. Lifecycle and resource APIs include `mxc_isi_channel_acquire()`, `mxc_isi_channel_release()`, `mxc_isi_channel_get()`, `mxc_isi_channel_put()`, `mxc_isi_channel_enable()`, `mxc_isi_channel_disable()`, `mxc_isi_channel_chain()`, and `mxc_isi_channel_unchain()`.

Private helpers cover scaling ratio selection, scaler setup, crop setup, CSC coefficient programming, panic threshold programming, channel control register updates, IRQ enable/disable, and software reset. Static CSC coefficient tables implement YUV-to-RGB and RGB-to-YUV conversions.

## Control Flow
Users of a pipe acquire required resources with `mxc_isi_channel_acquire()`, selecting output-buffer resource always and line-buffer resource unless the channel can bypass processing. `mxc_isi_channel_get()` resets and clocks the channel on first use. Configuration writes input frame size, scaler decimation and factors, crop window, CSC mode and coefficients, panic thresholds, input source selection, bypass bit, chain bit, and memory/device source type. Format helpers program memory input type, input pitch, output format, and output pitch.

During streaming, callers program output buffer 1 or 2 DMA addresses and toggle the corresponding load bit. On 36-bit DMA platforms, upper address registers are also written. Enabling a channel clears and enables interrupts, then sets `CHNL_EN`; disabling clears interrupt enable and clears `CHNL_EN`. Memory-to-memory operation toggles `READ_MEM` with a short delay to start a memory read. Release returns resources and, on final put, resets and disables the channel clock.

## State and Persistence
Hardware register state is volatile. Software state lives in `struct mxc_isi_pipe`: `use_count`, `irq_handler`, `available_res`, `acquired_res`, `chained_res`, and `chained`. `pipe->lock` serializes resource accounting and channel control updates. No state persists across driver unload or power loss.

## Dependencies and Integration Points
The file depends on ISI register macros from `imx8-isi-regs.h`, platform interrupt-layout and threshold data from `struct mxc_isi_plat_data`, and pipe state from `imx8-isi-core.h`. Higher-level pipe, video, and m2m code call these functions to implement capture and mem2mem streaming.

## Risks and Edge Cases
Scaling uses integer ratios and clamps to `ISI_DOWNSCALE_THRESHOLD`; unusual up/downscale combinations need visual validation. The CSC coefficients are fixed and do not vary with V4L2 colorimetry. Crop lower-right coordinates are built from upper-left plus width/height, so off-by-one interpretation must match hardware documentation. `mxc_isi_channel_set_outbuf()` XORs load bits based on current state, so lost register state or concurrent callers would cause wrong buffer loading; callers rely on pipe locking and buffer sequencing outside this file. `mxc_isi_channel_put()` decrements `use_count` without underflow protection. Chaining assumes the adjacent channel exists and reserves both line and output buffer resources from the next pipe.

## Test Signals
Important tests include 32-bit and 36-bit DMA address programming, both output buffers, m2m read start, identity processing bypass, scaling up/down, crop windows, RGB/YUV CSC in both directions, alpha and flip controls, interrupt status clear and enable masks for each SoC IER layout, acquire/release conflict handling, line-buffer chaining above unchained width, and suspend/resume paths that reset and reprogram channel state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-hw.c -->
