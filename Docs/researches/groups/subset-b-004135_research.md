# subset-b-004135 research

This grouped report covers media platform driver files under `sources/distributed-fs/ceph-client/drivers/media/platform` for ASPEED, Atmel, Broadcom, Cadence, and Chips&Media build wiring. Each section preserves the source path for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/aspeed/aspeed-video.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/aspeed/aspeed-video.c

## Purpose
This platform driver exposes the ASPEED AST2400/AST2500/AST2600 video engine as a V4L2 capture device for BMC screen capture. It detects host VGA or BMC graphics input timings, captures into internal DMA source buffers, compresses frames as standard JPEG or ASPEED-specific JPEG, and delivers compressed frames through a videobuf2 DMA-contiguous queue.

## Important APIs, Types, and Functions
`struct aspeed_video` owns MMIO, clocks, reset, SCU/GFX regmaps, V4L2/vb2 objects, source/JPEG/BCD DMA buffers, timing state, controls, and stream flags. Key helpers are `aspeed_video_start_frame()`, `aspeed_video_irq()`, `aspeed_video_get_resolution_vga()`, `aspeed_video_set_resolution()`, `aspeed_video_update_regs()`, `aspeed_video_start_streaming()`, and `aspeed_video_setup_video()`. It implements V4L2 ioctls for formats, inputs, stream parameters, DV timings, and source-change events, plus controls for JPEG quality, chroma subsampling, ASPEED HQ mode, and HQ quality.

## Control Flow
Probe maps the VE registers, reads SoC variant config, requests the interrupt, prepares clocks, allocates the JPEG header DMA table, and registers one video node. The first open powers the engine, initializes registers, detects the current resolution, and sizes DMA buffers. `STREAMON` updates compression registers and starts a frame from the queued vb2 list. Compression-complete IRQs finish the current buffer, update sequence/timestamps, swap source buffers for ASPEED JPEG delta mode, and start the next frame if streaming continues. Mode-detect watchdog IRQs reset the engine, error all queued buffers, and schedule delayed resolution work; the work item re-detects timings, emits a V4L2 source-change event when dimensions change, or restarts capture.

## State and Persistence
All state is volatile driver and hardware state. The driver persists no settings across module unload or reboot. `flags` coordinates clocks, streaming, frame-in-progress, resolution detection, and stopped state. `video_lock` serializes V4L2/vb2 operations; `lock` protects the buffer list in IRQ context. DMA state includes two source buffers, a JPEG table buffer, and an optional BCD buffer used for ASPEED JPEG change detection. Runtime controls mutate register state while streaming.

## Dependencies and Integration Points
The driver depends on platform OF compatibles, `eclk`/`vclk`, reset controls, optional reserved memory, 32-bit coherent DMA, ASPEED SCU and GFX syscon regmaps, V4L2 controls/events/DV timings, and `videobuf2-dma-contig`. It uses `uapi/linux/aspeed-video.h` for ASPEED-specific input and pixel-format controls. Debugfs can expose capture/compression/performance state.

## Risks and Edge Cases
Resolution detection depends on stable sync and pixel clock; no-signal paths fall back to minimum timings and return `-ENOLINK` from query timings. Stop waits for `VIDEO_FRAME_INPRG`; timeout forces reset and register reinitialization. Standard JPEG deliberately keeps the last buffer queued when it is the only buffer, which differs from ASPEED JPEG buffer consumption. Input switching requires SCU/GFX regmaps and is rejected while vb2 is busy. Source buffer allocation failures leave capture unable to proceed. Small VGA modes use sync mode because direct fetch lacks interrupts below the threshold.

## Test Signals
Build with AST2400, AST2500, and AST2600 compatibles. Exercise open/close, `VIDIOC_QUERYCAP`, JPEG/AJPG format selection, input switching, `VIDIOC_QUERY_DV_TIMINGS`, nonblocking resolution-change behavior, controls during streaming, and vb2 MMAP/DMABUF/READ capture. Hardware tests should cover no signal, resolution changes, VGA versus GFX input, stop timeout recovery, debugfs output, and DMA buffer sizing at 640x480 through 1920x1200.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/aspeed/aspeed-video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/atmel/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/atmel/Kconfig

## Purpose
This Kconfig file declares the Atmel media platform driver menu entry and the `VIDEO_ATMEL_ISI` option for the Atmel Image Sensor Interface capture driver.

## Important APIs, Types, and Functions
The primary symbol is `VIDEO_ATMEL_ISI`, a tristate option. It depends on `V4L_PLATFORM_DRIVERS`, `VIDEO_DEV`, `OF`, and either `ARCH_AT91` or `COMPILE_TEST`. It selects `VIDEOBUF2_DMA_CONTIG` and `V4L2_FWNODE`.

## Control Flow
When enabled, Kbuild includes `atmel-isi.o` through the sibling Makefile. The dependencies restrict visibility to V4L2 platform-driver builds with device-tree support and either AT91 hardware or compile-test coverage.

## State and Persistence
The only persistent state is the selected kernel configuration. Runtime capture state lives in `atmel-isi.c`.

## Dependencies and Integration Points
The option wires the driver to the V4L2 core, OF graph/fwnode endpoint parsing, and DMA-contiguous vb2 allocation used by the ISI DMA engine.

## Risks and Edge Cases
Missing `V4L2_FWNODE` or vb2 DMA selection would break the driver at build time. Overly narrow architecture dependencies would reduce compile coverage; overly broad dependencies could expose an unsupported platform driver.

## Test Signals
Use `ARCH_AT91` builds and `COMPILE_TEST` allmodconfig coverage. Confirm `CONFIG_VIDEO_ATMEL_ISI=m` produces `atmel-isi.ko`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/atmel/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/atmel/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/atmel/Makefile

## Purpose
This Makefile maps the Atmel ISI Kconfig option to its driver object.

## Important APIs, Types, and Functions
The only build rule is `obj-$(CONFIG_VIDEO_ATMEL_ISI) += atmel-isi.o`.

## Control Flow
Kbuild includes `atmel-isi.o` as built-in or module according to `CONFIG_VIDEO_ATMEL_ISI`.

## State and Persistence
There is no runtime state. Its persistent effect is build artifact composition.

## Dependencies and Integration Points
The rule must stay aligned with `drivers/media/platform/atmel/Kconfig` and the `atmel-isi.c` source filename.

## Risks and Edge Cases
A stale object name or symbol mismatch makes the Kconfig option build nothing or fail during compilation.

## Test Signals
Enable `CONFIG_VIDEO_ATMEL_ISI=m` and confirm the module builds with no orphaned Kconfig symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/atmel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/atmel/atmel-isi.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/atmel/atmel-isi.c

## Purpose
This driver exposes the Atmel Image Sensor Interface as a V4L2 capture device connected to one async-bound camera subdevice over an OF graph endpoint. It configures ISI geometry, bus polarity, DMA descriptors, and format conversion/swap settings, then streams sensor frames into vb2 DMA-contiguous buffers.

## Important APIs, Types, and Functions
`struct atmel_isi` contains register base, clock, IRQ, runtime PM state, V4L2/vb2 objects, async notifier, current format, supported user formats, DMA descriptor pool, queued buffers, and the active buffer. `struct fbd`, `struct isi_dma_desc`, and `struct frame_buffer` model hardware frame descriptors and vb2 buffers. Key functions include `configure_geometry()`, `isi_interrupt()`, `atmel_isi_wait_status()`, `start_dma()`, `start_streaming()`, `stop_streaming()`, `isi_try_fmt()`, `isi_set_fmt()`, `isi_formats_init()`, `isi_graph_init()`, and `atmel_isi_probe()`.

## Control Flow
Probe parses the endpoint, registers a V4L2 device, allocates the video node and vb2 queue, allocates a coherent descriptor array, maps registers, requests IRQ, initializes an async notifier, and enables runtime PM. When the remote subdevice binds and the notifier completes, the driver discovers overlapping media-bus formats, programs bus parameters, sets a default VGA format, and registers the video device. On open, the sensor is powered and the active format is pushed to the subdevice. `STREAMON` resumes runtime PM, starts the sensor stream, resets ISI, disables stale IRQs, programs geometry, and starts DMA for the active queued buffer. Transfer-complete IRQs complete the active buffer and arm the next descriptor. `STREAMOFF` stops the sensor, returns queued buffers as errors, waits for codec-path completion if needed, disables interrupts/ISI, and releases runtime PM.

## State and Persistence
Runtime state is in `atmel_isi`, the DMA descriptor free list, `video_buffer_list`, `active`, `fmt`, `current_fmt`, and `sequence`. Nothing persists across unbind. `lock` serializes file/vb2 operations, while `irqlock` protects active/queued buffer state shared with the ISR. Runtime PM gates the peripheral clock.

## Dependencies and Integration Points
The driver uses V4L2 device/video/subdev APIs, V4L2 async notifier, V4L2 fwnode endpoint parsing, OF graph, vb2 DMA-contig, runtime PM, and one `isi_clk` clock. It calls subdevice `s_power`, `s_stream`, `set_fmt`, `enum_mbus_code`, `enum_frame_size`, and frame interval operations. Register constants and platform data are defined in `atmel-isi.h`.

## Risks and Edge Cases
Reset and disable completion require a camera pixel clock; missing sensor clocking can cause 500 ms timeouts. Descriptor count is capped at `VIDEO_MAX_FRAME`; buffers fail prepare if descriptors are exhausted. Preview versus codec DMA path is selected from the output fourcc, so unsupported format combinations can route to the wrong channel if format tables drift. `clamp(..., 0U, MAX)` permits zero width/height through the clamp before subdevice negotiation. Sensor subdevice failures during stream-on must return queued buffers to vb2.

## Test Signals
Test OF endpoints for 8-bit, 10-bit, BT.656 embedded sync, and sync/pixel-clock polarities. Validate supported format discovery against multiple sensors, `VIDIOC_ENUM_FMT`, `TRY/S_FMT`, frame size/interval forwarding, MMAP/READ/DMABUF streaming, reset/disable timeout logs, runtime suspend/resume clock gating, and buffer return state on stream-on failure and stream-off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/atmel/atmel-isi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/atmel/atmel-isi.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/atmel/atmel-isi.h

## Purpose
This header defines Atmel ISI v2 register offsets, bit masks, DMA control bits, status bits, data-width flags, and `struct isi_platform_data` used by `atmel-isi.c`.

## Important APIs, Types, and Functions
Important definitions include `ISI_CFG1`, `ISI_CFG2`, `ISI_PSIZE`, `ISI_CTRL`, `ISI_STATUS`, interrupt registers, DMA descriptor registers for preview and codec paths, polarity bits, frame-rate divisors, grayscale/YCC swap controls, reset/disable bits, transfer-done flags, overflow/error flags, and `ISI_DMA_CTRL_*`. `struct isi_platform_data` carries embedded-sync, polarity, full-mode, data-width, and frame-rate configuration.

## Control Flow
The header has no executable control flow. The C driver uses these constants to program bus configuration, image dimensions, preview size, DMA descriptor fetch/writeback, interrupt enables/disables, reset, disable, and status polling.

## State and Persistence
No state is stored in the header. It defines the names and bit encodings used for volatile hardware state.

## Dependencies and Integration Points
It includes only `linux/types.h` and is tightly coupled to the Atmel ISI hardware register map and the driver logic in `atmel-isi.c`.

## Risks and Edge Cases
Incorrect bit definitions can silently corrupt capture setup, DMA routing, interrupt handling, or bus polarity. Width/height masks encode limited field sizes, so driver validation must stay within hardware limits.

## Test Signals
Compile the Atmel ISI driver and validate register programming on hardware or register traces for reset, disable, bus polarity, frame dimensions, and both DMA paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/atmel/atmel-isi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/broadcom/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/broadcom/Kconfig

## Purpose
This Kconfig entry declares `VIDEO_BCM2835_UNICAM`, the Broadcom BCM283x/BCM271x Unicam CSI-2/CCP2 capture driver.

## Important APIs, Types, and Functions
`VIDEO_BCM2835_UNICAM` is a tristate depending on `ARCH_BCM2835 || COMPILE_TEST`, `COMMON_CLK`, `PM`, and `VIDEO_DEV`. It selects `MEDIA_CONTROLLER`, `V4L2_FWNODE`, `VIDEO_V4L2_SUBDEV_API`, and `VIDEOBUF2_DMA_CONTIG`.

## Control Flow
Enabling the symbol makes the Makefile build `bcm2835-unicam.o`. The selected media-controller and subdev APIs are required because the driver exposes an internal bridge subdev plus image and metadata video nodes.

## State and Persistence
Only kernel configuration state is persisted. Runtime receiver, media graph, and DMA state live in `bcm2835-unicam.c`.

## Dependencies and Integration Points
The symbol integrates Broadcom SoC camera hardware with V4L2, media controller, OF/fwnode graph parsing, runtime PM, common clocks, and vb2 DMA-contig.

## Risks and Edge Cases
Dropping media-controller or subdev selections would break builds or runtime graph registration. Missing PM/common-clock dependencies would expose code that cannot manage the Unicam power and clock requirements.

## Test Signals
Build for Raspberry Pi/BCM2835 and `COMPILE_TEST`; confirm `bcm2835-unicam.ko` is produced and media-controller dependencies are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/broadcom/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/broadcom/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/broadcom/Makefile

## Purpose
This Makefile maps the Broadcom Unicam Kconfig option to its driver object.

## Important APIs, Types, and Functions
The build rule is `obj-$(CONFIG_VIDEO_BCM2835_UNICAM) += bcm2835-unicam.o`.

## Control Flow
Kbuild includes the object as built-in or module based on `CONFIG_VIDEO_BCM2835_UNICAM`.

## State and Persistence
No runtime state exists here. The file controls build output only.

## Dependencies and Integration Points
The rule must match `VIDEO_BCM2835_UNICAM` from Kconfig and the `bcm2835-unicam.c` source file.

## Risks and Edge Cases
Symbol or filename drift causes selected configurations to fail or omit the driver.

## Test Signals
Enable `CONFIG_VIDEO_BCM2835_UNICAM=m` and verify `bcm2835-unicam.ko` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/broadcom/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/broadcom/bcm2835-unicam-regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/broadcom/bcm2835-unicam-regs.h

## Purpose
This header defines the Broadcom VC4/BCM2835 Unicam register offsets and bitfields used by the Unicam capture driver.

## Important APIs, Types, and Functions
It defines offsets for core control/status, analogue/lane control, clock/data lane timing, packet compare, image DMA, embedded-data DMA, double-buffering, and miscellaneous registers. Important masks include `UNICAM_CTRL` mode and enable bits, `UNICAM_STA_MASK_ALL`, lane enable/termination/status bits, `UNICAM_ICTL` frame-start/frame-end/line-count interrupts, `UNICAM_IPIPE` pack/unpack fields, image ID fields, embedded-data control bits, and packet compare fields.

## Control Flow
There is no executable flow. `bcm2835-unicam.c` consumes these definitions while starting RX, handling interrupts, programming DMA buffers, configuring packing/unpacking, enabling embedded data, and disabling the hardware.

## State and Persistence
The header defines encodings for volatile MMIO state only. It stores no driver state and persists nothing.

## Dependencies and Integration Points
It includes `linux/bits.h` for `BIT()` and `GENMASK()`. Its definitions are coupled to the Unicam hardware documentation and Broadcom-derived register naming.

## Risks and Edge Cases
Bad masks can break interrupt acknowledgement, lane state, DMA bounds, or pixel packing. Some registers only exist on instances with more than two lanes, so users must guard DAT2/DAT3 access as the driver does.

## Test Signals
Validate register traces for lane enable, interrupt masks/status clearing, image and metadata DMA address programming, `UNICAM_IPIPE` packing modes, and stop/reset sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/broadcom/bcm2835-unicam-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/broadcom/bcm2835-unicam.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/broadcom/bcm2835-unicam.c

## Purpose
This driver directly controls the Broadcom BCM283x/BCM271x Unicam CSI-2/CCP2 receiver without VideoCore firmware. It registers a media device, an internal V4L2 bridge subdevice with stream routing, and two capture nodes: one for image data and one for embedded metadata. It receives sensor data and writes it to SDRAM, optionally repacking Bayer formats.

## Important APIs, Types, and Functions
`struct unicam_device` owns MMIO, clocks, media/V4L2 devices, async notifier, sensor endpoint, bridge subdev, bus configuration, pipeline state, and two `struct unicam_node` instances. `struct unicam_node` owns a video device, vb2 queue, DMA queue, current/next buffers, default format, and dummy buffer. Important functions include `unicam_isr()`, `unicam_start_rx()`, `unicam_start_metadata()`, `unicam_disable()`, subdev routing/format/stream ops, `unicam_start_streaming()`, `unicam_stop_streaming()`, `unicam_video_link_validate()`, `unicam_register_node()`, `unicam_async_nf_init()`, and `unicam_probe()`.

## Control Flow
Probe allocates `unicam_device`, maps Unicam and CMI registers, obtains `lp` and `vpu` clocks, requests the IRQ, enables runtime PM, registers the media/V4L2 device, initializes the internal subdev, and registers an async notifier for the remote sensor. When binding completes, it creates immutable links from sensor to bridge and from bridge source pads to the image and metadata video nodes. Starting a video queue starts the media pipeline, records which Unicam nodes are active, validates data lanes, arms the first queued buffer, waits until all required nodes are started, resumes runtime PM, and enables bridge streams. The bridge stream enable programs metadata DMA if needed, configures lanes, packet IDs, interrupts, packing, DMA stride/address, and starts the sensor. IRQ handling clears status, handles frame-end before frame-start, completes current buffers, schedules dummy buffers when user buffers are unavailable, schedules next queued buffers at frame-start/line interrupts, increments sequence, and queues frame-sync events.

## State and Persistence
State is volatile. `kref` protects device lifetime across registered video nodes. `media_pipeline` tracks active graph use. `sequence` and `frame_started` track sensor frame numbering independent of dequeued buffer count. Each node has `cur_frm`, `next_frm`, a spinlock-protected DMA queue, and a coherent dummy buffer. Runtime PM raises the VPU clock minimum to 250 MHz and enables the CSI clock while streaming.

## Dependencies and Integration Points
The driver uses the media controller, V4L2 async/fwnode/subdev stream APIs, vb2 DMA-contig, runtime PM, common clocks, OF graph endpoints, MIPI CSI-2 data types, and the register definitions in `bcm2835-unicam-regs.h`. It accepts CSI-2 D-PHY and CCP2 endpoints and queries sensor mbus config/frame descriptors when available.

## Risks and Edge Cases
Frame-start/frame-end ordering is delicate; the driver handles simultaneous FE/FS to avoid losing buffers. Dummy buffers avoid stopping hardware but mean frames can be dropped when userspace is late. Image capture is required in any active pipeline; metadata-only pipelines fail. Data-lane counts must match sensor and DT limits. Link validation has legacy RGB/BGR compatibility warnings. Runtime clock rate constraints are essential to avoid FIFO overruns and image corruption. The remove path must unregister nodes and async state without dropping references prematurely.

## Test Signals
Use media-ctl to verify immutable links, routes, and subdev nodes. Test CSI-2 1/2/4-lane and CCP2 endpoint parsing, image plus metadata synchronized streaming, late-buffer dummy behavior, frame-sync events, Bayer repacking formats, link-validation failures, runtime PM clock programming, IRQ status under frame start/end/line interrupts, and pipeline start/stop ordering for one or both video nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/broadcom/bcm2835-unicam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/cadence/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/cadence/Kconfig

## Purpose
This Kconfig file declares Cadence media platform options for the MIPI CSI-2 RX and TX controller bridge drivers.

## Important APIs, Types, and Functions
It defines `VIDEO_CADENCE_CSI2RX` and `VIDEO_CADENCE_CSI2TX` tristate symbols. Both depend on `VIDEO_DEV` and select `MEDIA_CONTROLLER`, `VIDEO_V4L2_SUBDEV_API`, and `V4L2_FWNODE`. RX additionally selects `GENERIC_PHY` and `GENERIC_PHY_MIPI_DPHY`.

## Control Flow
Enabled symbols cause the sibling Makefile to build `cdns-csi2rx.o` or `cdns-csi2tx.o`. The selected APIs match the drivers' role as V4L2 bridge subdevices, not standalone video nodes.

## State and Persistence
Only kernel configuration state persists. Runtime subdev, clock, reset, lane, stream, and D-PHY state live in the C drivers.

## Dependencies and Integration Points
The file integrates Cadence bridge drivers with media-controller graphs, fwnode endpoint parsing, V4L2 subdev device nodes, and generic PHY support for CSI2RX external D-PHY configuration.

## Risks and Edge Cases
If generic PHY support is not selected for RX, external D-PHY configuration will not build. If subdev/media-controller selections are removed, the drivers' pad/link operations are unavailable.

## Test Signals
Run allmodconfig and targeted builds with each symbol as module. Confirm `cdns-csi2rx.ko` and `cdns-csi2tx.ko` build and expose V4L2 subdevice APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/cadence/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/cadence/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/cadence/Makefile

## Purpose
This Makefile maps Cadence CSI-2 RX and TX Kconfig symbols to driver objects.

## Important APIs, Types, and Functions
The object rules are `obj-$(CONFIG_VIDEO_CADENCE_CSI2RX) += cdns-csi2rx.o` and `obj-$(CONFIG_VIDEO_CADENCE_CSI2TX) += cdns-csi2tx.o`.

## Control Flow
Kbuild evaluates each tristate and includes the corresponding bridge driver object as built-in or module.

## State and Persistence
There is no runtime state. It only controls build composition.

## Dependencies and Integration Points
The rules must match the Kconfig symbols and C source filenames in the Cadence platform directory.

## Risks and Edge Cases
Filename or symbol mismatches break selected builds or leave enabled drivers without objects.

## Test Signals
Enable each Cadence symbol as `m` and confirm the expected modules are produced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/cadence/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/cadence/cdns-csi2rx.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/cadence/cdns-csi2rx.c

## Purpose
This driver registers the Cadence MIPI CSI-2 RX controller as a V4L2 media bridge subdevice. It receives CSI-2 data from a remote source, configures lane mapping and stream output interfaces, optionally configures an external D-PHY, counts protocol/error IRQs, and forwards streaming to the upstream sensor or bridge.

## Important APIs, Types, and Functions
`struct csi2rx_priv` stores clocks, resets, MMIO, optional D-PHY, lane/stream capabilities, pixel-per-clock settings, error counters, media pads, source subdevice, and a stream reference count. Important functions are `csi2rx_get_resources()`, `csi2rx_parse_dt()`, `csi2rx_configure_ext_dphy()`, `csi2rx_start()`, `csi2rx_stop()`, `csi2rx_s_stream()`, `csi2rx_set_fmt()`, `cdns_csi2rx_negotiate_ppc()`, `csi2rx_irq_handler()`, and async bind/probe/remove helpers.

## Control Flow
Probe maps registers, obtains `sys_clk`, `p_clk`, per-stream pixel clocks, optional resets, optional external D-PHY, reads device capability registers, parses CSI-2 endpoint lane mapping, sets up the async notifier, initializes a five-pad bridge subdev, optionally requests `error_irq`, finalizes subdev state, and registers the subdev. Stream-on is reference-counted. The first user enables the P clock, resets the controller and streams, configures error IRQ masks, writes static lane mapping, enables D-PHY lanes and external D-PHY timing, enables each stream pixel clock/reset, configures FIFO mode and pixels-per-clock, maps VC0 to each stream, enables system clock/reset, then calls upstream `s_stream(true)`. Stream-off by the last user stops streams, polls readiness, asserts resets, disables clocks, calls upstream `s_stream(false)`, and powers off D-PHY.

## State and Persistence
Runtime state is volatile. `count` protects shared hardware enablement across multiple source pads. `events[]` accumulates error IRQ counts until driver removal and is reported by `.log_status`. Active subdev formats live in V4L2 subdev state; `num_pixels[]` stores negotiated stream PPC register encodings.

## Dependencies and Integration Points
The driver uses V4L2 subdev/media entity APIs, V4L2 async notifier, fwnode endpoint parsing, media links, clocks, resets, generic PHY MIPI D-PHY helpers, and exported `cdns_csi2rx_negotiate_ppc()` for downstream users such as `j721e-csi2rx`.

## Risks and Edge Cases
Internal D-PHY is explicitly unsupported. The lane mapping fallback loop computes an unused physical lane but writes `i + 1`, so lane-map assumptions should be checked carefully when changing this area. All streams are enabled together and statically select VC0, limiting multi-VC flexibility. `csi2rx_s_stream(false)` decrements `count` without underflow protection. External D-PHY link frequency depends on upstream pad link-frequency data. Optional error IRQ absence removes hardware error visibility.

## Test Signals
Test DT parsing for invalid bus type, lane counts, and lane IDs; probe with external D-PHY and no/internal D-PHY cases; stream through linked sensors; inspect stream clocks/resets; call `.log_status` after CRC/ECC/FIFO errors; validate PPC negotiation; and run media graph link validation with all source pads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/cadence/cdns-csi2rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/cadence/cdns-csi2tx.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/cadence/cdns-csi2tx.c

## Purpose
This driver registers the Cadence MIPI CSI-2 TX controller as a V4L2 bridge subdevice. It accepts up to four input stream pads, configures CSI-2 data type/line format registers, and transmits over a CSI-2 D-PHY source pad.

## Important APIs, Types, and Functions
`struct csi2tx_priv` stores MMIO, clocks, variant D-PHY operations, media pads, active pad formats, lane capabilities, stream count, and stream reference count. `struct csi2tx_vops` selects v1.3 or v2.1 D-PHY setup. Key functions are `csi2tx_get_resources()`, `csi2tx_check_lanes()`, `csi2tx_dphy_setup()`, `csi2tx_v2_dphy_setup()`, `csi2tx_start()`, `csi2tx_stop()`, `csi2tx_s_stream()`, and pad format handlers.

## Control Flow
Probe maps registers, obtains `p_clk`, `esc_clk`, per-stream pixel clocks, reads capability registers, selects variant ops from OF compatible, initializes a source pad plus four sink stream pads, seeds sink pad formats with 1280x720 RGB888, and registers the async subdev. Pad operations enumerate only UYVY8 and RGB888 formats and reject format get/set on the multiplexed source pad. The first stream-on resets the block, enters configuration mode, initializes the internal D-PHY if variant ops exist, walks enabled sink links, programs each active stream's CSI-2 data type, bytes per line, max line number, and stream fill level, then exits configuration mode. The last stream-off asserts config and reset bits.

## State and Persistence
Runtime state is volatile. `count` reference-counts hardware start/stop across users. `pad_fmts[]` stores active sink-pad formats. Lane configuration comes from the local endpoint and is kept in `lanes[]`/`num_lanes`.

## Dependencies and Integration Points
The driver depends on V4L2 subdev/media entity APIs, OF graph/fwnode endpoint parsing, MIPI CSI-2 data type definitions, platform clocks, and OF compatibles `cdns,csi2tx`, `cdns,csi2tx-1.3`, and `cdns,csi2tx-2.1`.

## Risks and Edge Cases
The source pad is multiplexed and has no exposed format, limiting userspace visibility into mixed-stream output. Only two media-bus formats are supported. Stream data type mapping is static and comments note stream ID is not a correct general data-type selector. Pixel and escape clocks are acquired but not explicitly enabled in the visible start path, so clocking assumptions depend on integration. `count` can underflow if disable is unbalanced. The probe error path after `media_entity_pads_init()` does not explicitly clean the entity before freeing private data.

## Test Signals
Build and probe each compatible variant, validate endpoint lane rejection, inspect D-PHY register programming for v1.3 and v2.1, create enabled media links on each sink pad, stream with UYVY and RGB888 formats, verify DT/line-format registers, and test balanced/unbalanced stream enable/disable paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/cadence/cdns-csi2tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/Kconfig

## Purpose
This Kconfig file introduces the Chips&Media media platform driver menu and includes subordinate codec driver Kconfig files.

## Important APIs, Types, and Functions
It contains a comment and sources `drivers/media/platform/chips-media/coda/Kconfig` and `drivers/media/platform/chips-media/wave5/Kconfig`.

## Control Flow
When the parent media platform Kconfig reaches this file, it delegates option definitions to the Coda and Wave5 subdirectories.

## State and Persistence
No runtime state exists. The persisted effect is the user's kernel `.config` selections from the sourced child files.

## Dependencies and Integration Points
It integrates Chips&Media codec IP options into the larger media platform Kconfig hierarchy.

## Risks and Edge Cases
Incorrect `source` paths hide entire driver families. Adding symbols here instead of child files could make ownership and menu organization less clear.

## Test Signals
Run Kconfig menu traversal and allmodconfig to confirm both Coda and Wave5 options are visible and parse without warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/Makefile

## Purpose
This Makefile descends into the Chips&Media Coda and Wave5 codec driver subdirectories.

## Important APIs, Types, and Functions
The rules are `obj-y += coda/` and `obj-y += wave5/`.

## Control Flow
Kbuild always enters both subdirectories when this directory is visited; the child Makefiles then conditionally build objects according to their Kconfig symbols.

## State and Persistence
There is no runtime state. Build composition is controlled by child Makefiles and selected configuration.

## Dependencies and Integration Points
It must stay aligned with child directories and the corresponding sourced Kconfig files.

## Risks and Edge Cases
Removing a subdirectory entry would prevent enabled child symbols from building. Stale directory names break Kbuild traversal.

## Test Signals
Use allmodconfig and targeted `VIDEO_CODA`/Wave5 builds to confirm child objects are reached.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/Kconfig

## Purpose
This Kconfig file declares the Chips&Media Coda mem2mem video codec driver and the related i.MX VDOA helper option.

## Important APIs, Types, and Functions
`VIDEO_CODA` is a tristate for Coda multi-standard codec IP. It depends on `V4L_MEM2MEM_DRIVERS`, `VIDEO_DEV`, `OF`, and `ARCH_MXC || COMPILE_TEST`. It selects `SRAM`, `VIDEOBUF2_DMA_CONTIG`, `VIDEOBUF2_VMALLOC`, `V4L2_JPEG_HELPER`, `V4L2_MEM2MEM_DEV`, and `GENERIC_ALLOCATOR`. `VIDEO_IMX_VDOA` defaults to `VIDEO_CODA` on `SOC_IMX6Q || COMPILE_TEST`.

## Control Flow
Selecting `VIDEO_CODA` causes the child Makefile to build the aggregate `coda-vpu.o`. `VIDEO_IMX_VDOA` controls the optional `imx-vdoa.o` helper used on i.MX6Q-style integrations.

## State and Persistence
Selections persist in the kernel configuration. Runtime codec contexts, queues, firmware, and SRAM allocation are handled by the Coda C sources.

## Dependencies and Integration Points
The option connects Coda to the V4L2 mem2mem framework, vb2 DMA/vmalloc allocators, SRAM/genalloc memory management, OF platform probing, and JPEG helper code.

## Risks and Edge Cases
The driver needs both DMA-contiguous and vmalloc vb2 allocators; dropping either selection can break supported queue paths. Architecture gating focuses normal visibility on i.MX while preserving compile-test coverage.

## Test Signals
Build with `CONFIG_VIDEO_CODA=m`, `CONFIG_VIDEO_IMX_VDOA=m`, i.MX configs, and `COMPILE_TEST`. Confirm codec modules link with mem2mem, SRAM, and JPEG helper dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/Makefile

## Purpose
This Makefile builds the Chips&Media Coda VPU codec driver from multiple implementation objects and optionally builds the i.MX VDOA helper.

## Important APIs, Types, and Functions
`coda-vpu-objs` aggregates `coda-common.o`, `coda-bit.o`, `coda-gdi.o`, `coda-h264.o`, `coda-mpeg2.o`, `coda-mpeg4.o`, and `coda-jpeg.o`. `obj-$(CONFIG_VIDEO_CODA) += coda-vpu.o` builds the linked driver. `obj-$(CONFIG_VIDEO_IMX_VDOA) += imx-vdoa.o` builds the auxiliary helper.

## Control Flow
Kbuild links the listed Coda component objects into `coda-vpu.o` when `VIDEO_CODA` is enabled, and independently includes `imx-vdoa.o` according to `VIDEO_IMX_VDOA`.

## State and Persistence
No runtime state exists here. Its persistent effect is object composition and module naming.

## Dependencies and Integration Points
The aggregate object must match the Coda source decomposition and the Kconfig symbols in the same directory.

## Risks and Edge Cases
Omitting a component object can remove codec support or shared helpers while still producing a module. Stale object names break builds. VDOA must remain separately gated because it is platform-specific.

## Test Signals
Enable `VIDEO_CODA` and verify all codec component objects link into `coda-vpu.ko`; enable `VIDEO_IMX_VDOA` and confirm `imx-vdoa.ko` or built-in object output appears.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/Makefile -->
