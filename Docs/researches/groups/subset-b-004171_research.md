# subset-b-004171 Research

Grouped research for the requested Linux media driver files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/dw-mipi-csi2rx.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/dw-mipi-csi2rx.c

## Purpose
Implements a V4L2 media-controller sub-device bridge for the Synopsys DesignWare MIPI CSI-2 receiver. It terminates a CSI-2 D-PHY input from a remote sensor/bridge, configures the receiver and PHY, exposes sink/source pads, and forwards stream enable/disable calls to the upstream sub-device. It supports at least Rockchip RK3568 and NXP i.MX93 through per-SoC register maps and optional callback hooks.

## Important APIs, Types, And Functions
Core state is held in `struct dw_mipi_csi2rx_device`, with MMIO base, clocks, PHY, optional reset, pad/notifier/subdev objects, bus type, lane count, and `drvdata`. `struct dw_mipi_csi2rx_drvdata` supplies register layout plus optional D-PHY reset and IPI enable callbacks. `struct dw_mipi_csi2rx_format` maps media-bus codes to bit depth and CSI-2 data type.

Register helpers `dw_mipi_csi2rx_has_reg()`, `dw_mipi_csi2rx_read()`, and `dw_mipi_csi2rx_write()` mask SoC differences. V4L2 pad ops include `enum_mbus_code`, `set_fmt`, `set_routing`, `get_frame_desc`, `enable_streams`, and `disable_streams`. Platform lifecycle is `dw_mipi_csi2rx_probe()` / `dw_mipi_csi2rx_remove()` plus runtime PM callbacks.

## Control Flow
Probe allocates the device, maps registers, fetches match data, gets all clocks, gets the MIPI PHY and optional reset, enables runtime PM, initializes the PHY, and registers a V4L2 sub-device. Registration parses endpoint 0, records D-PHY/CPHY bus metadata, installs an async notifier for the remote source, initializes two pads, finalizes subdev state, and registers the async subdev.

Streaming starts in `dw_mipi_csi2rx_enable_streams()`: stream masks are translated from source to sink, runtime PM resumes clocks/resets, `dw_mipi_csi2rx_start()` validates lanes, derives link frequency from the remote pad, configures the PHY for D-PHY, writes receiver lane/control registers, powers on the PHY, deasserts receiver resets, optionally enables i.MX93 IPI, then asks the remote source to stream. Disable reverses the remote stream, powers off the PHY, resets receiver state, masks errors when present, and drops runtime PM.

## State And Persistence
Persistent driver state is in memory only. V4L2 active state stores routing and pad formats; runtime state tracks bus type and lane count parsed from firmware. Hardware state is register programming, PHY mode/configuration, clock/reset state, and runtime PM reference count. No filesystem state is written.

## Dependencies And Integration Points
The driver integrates with Linux platform bus, OF match data, clocks, resets, generic PHY, runtime PM, V4L2 async notifier, media entity graph, fwnode endpoint parsing, and MIPI CSI-2 helpers. It requires an upstream source exposing `V4L2_CID_LINK_FREQ` or compatible link-frequency calculation and a firmware graph connection on endpoint 0.

## Risks
CPHY is explicitly unsupported. i.MX93 IPI enable currently selects `csi2->formats->csi_dt`, the first supported format, rather than the negotiated active pad format, which is a functional risk for non-default formats. Stream enable assumes a remote pad exists and that the remote entity is a V4L2 subdev. Error cleanup around `phy_power_on()` failures does not unwind previously asserted receiver reset state beyond returning the error, relying on later stop/runtime behavior. Register existence checks prevent crashes on missing registers but can hide incomplete SoC data behind one-time errors.

## Test Signals
Useful signals are successful media graph creation, async link binding to the sensor, `v4l2-compliance` subdev routing/format tests, stream-on/off with a D-PHY sensor at multiple lane counts and media-bus codes, runtime PM suspend/resume cycles, and error-path tests for missing link frequency, unsupported CPHY endpoints, absent remote pads, and invalid lane counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/dw-mipi-csi2rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/hdmirx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/hdmirx/Kconfig

## Purpose
Defines build-time configuration for the Synopsys DesignWare HDMI Receiver driver and its optional default EDID preload feature.

## Important APIs, Types, And Functions
The `VIDEO_SYNOPSYS_HDMIRX` tristate enables the HDMI 2.0 receiver module named `synopsys_hdmirx`. It depends on Rockchip architecture support or compile-test coverage and `VIDEO_DEV`, and selects media-controller, V4L2 subdev, contiguous vb2 DMA, CEC core, and HDMI helpers. `VIDEO_SYNOPSYS_HDMIRX_LOAD_DEFAULT_EDID` is a bool that preloads a Linux Foundation-branded EDID for out-of-box testing.

## Control Flow
Kconfig selection controls whether `snps_hdmirx.c` and `snps_hdmirx_cec.c` are compiled through the local Makefile. The default EDID option changes runtime behavior in `hdmirx_load_default_edid()`, where the driver either keeps HPD low until userspace programs EDID or writes the built-in EDID and raises HPD.

## State And Persistence
No runtime state exists in this file. Build configuration persists through the kernel `.config`; the EDID option affects initial in-kernel device state at probe.

## Dependencies And Integration Points
Integrates the driver with Linux media, vb2 DMA, CEC, HDMI infoframe/EDID helpers, and Rockchip-oriented platform support. The optional EDID knob is explicitly suitable for non-production setups.

## Risks
Enabling the default EDID in a product can expose generic identity and limited modes instead of board/vendor-specific EDID. Disabling it leaves the device mostly unusable until userspace sets EDID, which is intentional but can look like a probe/runtime failure during bring-up.

## Test Signals
Build matrix coverage should verify builtin and module configurations, with and without default EDID. Runtime smoke tests should confirm HPD behavior and `v4l2-ctl --get-edid` after probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/hdmirx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/hdmirx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/hdmirx/Makefile

## Purpose
Builds the Synopsys HDMI receiver as a composite kernel object.

## Important APIs, Types, And Functions
`synopsys-hdmirx-objs` combines `snps_hdmirx.o` and `snps_hdmirx_cec.o`. `obj-$(CONFIG_VIDEO_SYNOPSYS_HDMIRX)` emits the final `synopsys-hdmirx.o` object when the Kconfig symbol is enabled.

## Control Flow
There is no runtime flow. Kbuild compiles both main capture/HDMI logic and the CEC helper into one module/builtin unit.

## State And Persistence
No runtime state. The only persistent effect is the selected kernel build artifact.

## Dependencies And Integration Points
Depends on the local Kconfig symbol and Kbuild object-composition conventions. The CEC implementation is inseparable from the main module from a build perspective.

## Risks
Any compile failure in CEC support prevents the whole HDMI receiver driver from building. There is no conditional object split for CEC despite `CEC_CORE` being selected by Kconfig.

## Test Signals
Kernel builds for `CONFIG_VIDEO_SYNOPSYS_HDMIRX=m` and `=y` should produce the expected module/object and include both source files in dependency output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/hdmirx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/hdmirx/snps_hdmirx.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/hdmirx/snps_hdmirx.c

## Purpose
Implements the Synopsys DesignWare HDMI receiver capture driver for Rockchip RK3588-style integrations. It exposes a V4L2 video capture node backed by vb2 contiguous DMA, controls HDMI RX PHY/controller/packet/DMA blocks, manages HPD and EDID, reports DV timings and input status, surfaces AVI infoframes through debugfs, and registers a CEC adapter through the companion CEC file.

## Important APIs, Types, And Functions
Primary state is `struct snps_hdmirx_dev`, which owns the V4L2 device, controls, timings, GPIO, delayed work, CEC handle, regmaps, completions, IRQ numbers, EDID cache, current pixel format/depth, locks, clocks, resets, and MMIO base. `struct hdmirx_stream` owns the video node, vb2 queue, current/next buffers, format, queue locks, stopping state, sequence, and DMA interrupt counters. `struct hdmirx_buffer` wraps `vb2_v4l2_buffer` plus DMA plane addresses.

Key user APIs are the V4L2 ioctl table: querycap, input enumeration, EDID get/set, DV timing query/get/set/caps/enumeration, stream parameters, format enum/get/set, vb2 buffer ioctls, event subscription, and control logging. Important internals include `hdmirx_phy_config()`, `hdmirx_controller_init()`, `hdmirx_dma_config()`, `hdmirx_wait_signal_lock()`, `hdmirx_start_streaming()`, `hdmirx_stop_streaming()`, `hdmirx_hdmi_irq_handler()`, and `hdmirx_dma_irq_handler()`.

## Control Flow
Probe sets a 32-bit DMA mask, parses clocks/resets/GPIO/syscon/reserved memory, requests HDMI/DMA/5V IRQs with `IRQ_NOAUTOEN`, maps MMIO, initializes locks/completions/work items, enables clocks/resets, validates interrupt functionality through a PHY register read, disables stale interrupts, registers the V4L2 device and video node, registers CEC, optionally loads default EDID, enables IRQs, and creates debugfs infoframe support.

Hotplug starts at the 5V GPIO IRQ, which schedules `hdmirx_delayed_work_hotplug()`. That work samples 5V, updates `V4L2_CID_DV_RX_POWER_PRESENT`, tears down prior plug state, and if present initializes submodules, asserts `POWERPROVIDED`, configures PHY, and enables HDMI interrupts. Signal-change IRQs schedule `hdmirx_delayed_work_res_change()`, which reinitializes controller/PHY, waits for lock and AVI packet reception, updates pixel format/color depth/AVI controls, configures DMA, and re-enables interrupts.

Streaming uses vb2. Queued buffers store physical addresses for Y and chroma planes. `start_streaming` picks the first buffer, writes DMA address registers, configures line-flag position and DMA interrupt masks, clears status, and enables DMA. The DMA IRQ uses line-flag interrupts to program the next buffer and idle interrupts to complete the previous buffer, skipping early frames with `FILTER_FRAME_CNT` and handling interlaced field cadence. Stop sets `stopping`, waits for the IRQ to acknowledge, disables DMA, and returns all buffers.

## State And Persistence
Persistent runtime state includes EDID bytes and block count, current DV timings, current fourcc, HDMI pixel format/color depth, 5V plug state, tmds clock ratio, V4L2 controls, vb2 queue contents, current/next buffers, and debugfs infoframe object. Suspend disables IRQs, CEC IRQ, HPD, plug state, clocks, and pinctrl state; resume restores clocks/resets, rewrites cached EDID, restores HPD, reenables CEC/IRQs, and schedules hotplug work. No filesystem persistence exists.

## Dependencies And Integration Points
Integrates with platform resources named `hdmi`, `dma`, `cec`, and HPD GPIO; Rockchip `grf` and `vo1-grf` syscon regmaps; clocks and resets; optional reserved memory/CMA; V4L2 controls/events/ioctls; videobuf2 DMA-contig; HDMI infoframe helpers; CEC core via `snps_hdmirx_cec_register()`; debugfs infoframe helpers; pinctrl PM; and RK3588 device tree compatible `rockchip,rk3588-hdmirx-ctrler`.

## Risks
The driver is strongly tied to RK3588 register layout and firmware behavior; it explicitly detects a broken downstream TF-A interrupt remap and requires open-source TF-A behavior. Many operations depend on hardware timing, completions, and delayed work, so plug/unplug races are controlled mostly by `work_lock` and IRQ disable ordering. EDID writes temporarily force HPD low and must not race with plug work. DMA buffer handoff is interrupt-driven and sensitive to missing line-flag/idle interrupts. The DMA path assumes 32-bit physical addresses. Suspend notes TODOs for CEC state save/restore. The built-in default EDID is limited to lower compatibility modes and is not production identity.

## Test Signals
Use `v4l2-compliance`, `v4l2-ctl --query-dv-timings`, EDID get/set, event subscription for source changes, hotplug plug/unplug testing, CEC adapter discovery and transmit/receive tests, DMA streaming with mmap and dmabuf, interlaced/progressive modes, RGB/YUV formats, high TMDS clock ratio transitions, suspend/resume with EDID retained, and debugfs AVI infoframe reads. Kernel logs around lock waits, PHY register completions, DMA underrun/overflow, and interrupt-not-handled messages are key bring-up signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/hdmirx/snps_hdmirx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/hdmirx/snps_hdmirx.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/hdmirx/snps_hdmirx.h

## Purpose
Provides register offsets, bit masks, and bitfield helper macros for the Synopsys HDMI receiver driver and Rockchip-specific integration registers.

## Important APIs, Types, And Functions
The header exports `UPDATE()` and `HIWORD_UPDATE()` helpers plus hundreds of defines for SYS_GRF, VO1_GRF, HDMI PHY, controller, SCDC, packet decoder, CEC, DMA, interrupt, HDCP, audio, video, and monitor registers. These names form the internal register API used by `snps_hdmirx.c` and `snps_hdmirx_cec.c`.

## Control Flow
There is no executable control flow. The constants drive all MMIO programming paths: PHY init, SCDC setup, HDCP disable/switch override, timing detection, DMA format/addressing, EDID SRAM access, interrupt masking/clearing, CEC TX/RX, and infoframe parsing.

## State And Persistence
No state is stored in the header. The defined addresses and masks describe mutable hardware state in the HDMI RX and Rockchip GRF blocks.

## Dependencies And Integration Points
Depends on Linux `bitfield`, `bitops`, and `hw_bitfield` helpers. It is tightly integrated with Synopsys HDMIRX IP register layout and Rockchip RK3588 syscon bits.

## Risks
Incorrect offsets or masks can corrupt unrelated hardware state. Some register names encode downstream documentation assumptions, and comments note errata or undocumented behavior in the C source. Duplicate `OPMODE_STS_MASK` definition is harmless but signals manual register-table maintenance. The header exposes no type safety around register groups, so C code must avoid mixing GRF, controller, CEC, and DMA offsets.

## Test Signals
Compile coverage catches missing macros only. Real validation comes from probing hardware, successful PHY register reads/writes, interrupt behavior, EDID access, CEC traffic, and DMA capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/hdmirx/snps_hdmirx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/hdmirx/snps_hdmirx_cec.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/hdmirx/snps_hdmirx_cec.c

## Purpose
Implements HDMI CEC support for the Synopsys HDMI receiver as a CEC framework adapter sharing the main HDMI receiver MMIO block through callback operations.

## Important APIs, Types, And Functions
The exported entry points are `snps_hdmirx_cec_register()` and `snps_hdmirx_cec_unregister()`. Internal CEC adapter operations are `hdmirx_cec_enable()`, `hdmirx_cec_log_addr()`, and `hdmirx_cec_transmit()`. The interrupt path is split into `hdmirx_cec_hardirq()` for status clearing/message extraction and `hdmirx_cec_thread()` for notifying the CEC core.

## Control Flow
Registration allocates `struct hdmirx_cec`, enables the CEC block, enables RX auto-ack, clears TX/interrupt state, allocates a CEC adapter with monitor support, requests a no-auto-enable threaded IRQ, registers the adapter, unmasks key CEC TX/RX interrupts, and enables the IRQ. Adapter enable resets logical addresses, optionally calls parent enable/disable hooks, toggles `CEC_ENABLE`, and masks/unmasks CEC interrupts.

Transmit writes byte count and up to four packed 32-bit data registers, then starts transmission. The hard IRQ clears interrupt status, maps TX done/NACK/arbitration/lane errors to CEC framework status, copies RX messages on end-of-message, locks the RX buffer, and wakes the threaded handler. The threaded handler reports completed transmit attempts and received messages to the CEC core.

## State And Persistence
State is in `struct hdmirx_cec`: logical-address bitmask, adapter pointer, current RX message, TX status, TX/RX completion booleans, IRQ number, parent pointer, and ops. Hardware state includes CEC address, interrupt masks/clears, TX/RX FIFOs, and CEC enable/config bits. No durable state is stored.

## Dependencies And Integration Points
Depends on `media/cec.h`, the main HDMIRX register definitions, Linux IRQ APIs, devm allocation, and parent callbacks for MMIO access. Userspace sees a normal CEC character device associated with the HDMI receiver device.

## Risks
The transmit path relies on the CEC core to pass valid message lengths. RX uses memory barriers between hard IRQ and threaded IRQ; changes to this path must preserve ordering. Interrupt clearing and RX buffer locking are hardware-specific and can drop messages if mishandled. Logical address programming always sets bit 15 along with the requested address, which should be checked against the hardware manual when changing addressing behavior.

## Test Signals
CEC adapter registration under `/dev/cec*`, logical address allocation, `cec-ctl` ping/transmit tests, monitor-all receive behavior, TX status reporting for ACK/NACK/arbitration loss, plug/unplug with parent IRQ disable ordering, and suspend/resume behavior through the main driver are useful validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/hdmirx/snps_hdmirx_cec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/hdmirx/snps_hdmirx_cec.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/hdmirx/snps_hdmirx_cec.h

## Purpose
Declares the internal interface between the main Synopsys HDMI receiver driver and its CEC adapter implementation.

## Important APIs, Types, And Functions
`struct hdmirx_cec_ops` abstracts parent MMIO access and optional parent enable/disable hooks. `struct hdmirx_cec_data` is the registration input containing parent device, ops, Linux device, and IRQ. `struct hdmirx_cec` is the adapter runtime state. Exported functions are `snps_hdmirx_cec_register()` and `snps_hdmirx_cec_unregister()`.

## Control Flow
The main driver fills `hdmirx_cec_data` after obtaining the CEC IRQ and calls register during probe. Unregister is called during remove before main HDMI resources are fully disabled.

## State And Persistence
The header defines in-memory state fields for the CEC adapter, including address mask, adapter, RX message, TX completion state, IRQ, and parent pointers. No persistent state exists.

## Dependencies And Integration Points
Requires a forward declaration of `struct snps_hdmirx_dev` and relies on the CEC core type `struct cec_adapter` being visible to C users through included media headers in implementation contexts. It is private to the hdmirx module.

## Risks
Because MMIO access is callback-based, the parent must keep registers mapped and clocks/interrupts valid while CEC is active. The header exposes runtime fields directly to the CEC implementation, so locking and memory-barrier discipline must be maintained there rather than enforced by types.

## Test Signals
Compile tests ensure the main and CEC objects agree on this private ABI. Runtime tests are the same CEC registration, IRQ, and transmit/receive checks used for `snps_hdmirx_cec.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/hdmirx/snps_hdmirx_cec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/Kconfig

## Purpose
Groups Texas Instruments media platform driver configuration and sources the TI subdirectory Kconfig files.

## Important APIs, Types, And Functions
Defines helper symbols `VIDEO_TI_VPDMA`, `VIDEO_TI_SC`, and `VIDEO_TI_CSC`; capture drivers `VIDEO_TI_CAL`, `VIDEO_TI_CAL_MC`, `VIDEO_TI_VIP`, and `VIDEO_TI_J721E_CSI2RX`; and mem2mem driver `VIDEO_TI_VPE` plus debug option `VIDEO_TI_VPE_DEBUG`. It sources AM437x, DaVinci, OMAP, OMAP3 ISP, and other TI Kconfig files.

## Control Flow
Kconfig dependencies and selects determine which TI media drivers are compiled. `VIDEO_TI_CAL_MC` changes CAL default API mode through a module parameter default, while the rest mostly map SoC/feature dependencies to build objects.

## State And Persistence
No runtime state. Kernel `.config` persists selected features and affects available modules and compiled code paths.

## Dependencies And Integration Points
Integrates TI media drivers with V4L2 platform drivers, media controller, subdev API, vb2 DMA-contig, V4L2 fwnode, SOC_DRA7XX, ARCH_K3, Cadence CSI2RX/DPHY, and TI helper modules.

## Risks
Kconfig select/depend drift can create build-only failures, especially under `COMPILE_TEST`. Enabling wrapper drivers like J721E CSI2RX without the underlying Cadence bridge is prevented by dependencies but still requires correct device tree/runtime resources.

## Test Signals
Allmodconfig, allyesconfig, and targeted SoC defconfig builds should cover the matrix. Runtime validation belongs to the specific driver symbols selected here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/Makefile

## Purpose
Adds TI media driver subdirectories to the kernel media platform build.

## Important APIs, Types, And Functions
Unconditionally descends into `am437x/`, `cal/`, `vpe/`, `davinci/`, `j721e-csi2rx/`, `omap/`, and `omap3isp/`. Individual objects are gated by each subdirectory's Kconfig symbols.

## Control Flow
No runtime flow. Kbuild visits each subdirectory and lets local Makefiles decide which objects to emit.

## State And Persistence
No state beyond build output.

## Dependencies And Integration Points
This is the build integration point between `drivers/media/platform/ti` and all TI-specific media drivers.

## Risks
Removing a subdirectory here silently prevents all contained driver symbols from producing objects even if Kconfig still exposes them. Unconditional descent means subdirectory Makefiles must be robust for disabled configs.

## Test Signals
Targeted kernel builds should confirm each enabled TI Kconfig symbol produces its expected object or module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/am437x/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/am437x/Kconfig

## Purpose
Defines the AM437x VPFE video capture driver configuration symbol.

## Important APIs, Types, And Functions
`VIDEO_AM437X_VPFE` is a tristate for the TI AM437x Video Processing Front End capture driver. It depends on V4L2 platform drivers, video device support, and `SOC_AM43XX` or compile-test. It selects media controller, V4L2 subdev API, vb2 DMA-contig, and V4L2 fwnode helpers.

## Control Flow
When enabled, the AM437x Makefile builds `am437x-vpfe.o`. Runtime behavior is in `am437x-vpfe.c`.

## State And Persistence
Only build configuration state is persisted.

## Dependencies And Integration Points
Integrates the driver with AM43xx SoC support, V4L2 media graph/subdev APIs, fwnode endpoint parsing, and contiguous DMA buffers.

## Risks
Compile-test builds can expose missing generic dependencies. Runtime use still requires an AM437x-compatible device tree endpoint and a remote camera/decoder subdevice.

## Test Signals
Build as module and builtin, plus boot/probe tests on AM437x hardware or compile-test configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/am437x/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/am437x/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/am437x/Makefile

## Purpose
Builds the AM437x VPFE capture driver object.

## Important APIs, Types, And Functions
`obj-$(CONFIG_VIDEO_AM437X_VPFE) += am437x-vpfe.o` maps the Kconfig symbol directly to the driver object.

## Control Flow
No runtime flow. Kbuild includes the driver only when the symbol is enabled.

## State And Persistence
No runtime state; only build artifact generation.

## Dependencies And Integration Points
Connects `VIDEO_AM437X_VPFE` to `am437x-vpfe.c` in the TI media build.

## Risks
There are no split helper objects, so all VPFE functionality must compile from the single C file.

## Test Signals
Kernel build output should contain `am437x-vpfe.o` or `am437x-vpfe.ko` when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/am437x/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/am437x/am437x-vpfe.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/am437x/am437x-vpfe.c

## Purpose
Implements the TI AM437x VPFE capture driver. It programs the CCDC/image sensor interface, binds one remote camera/decoder subdevice through the firmware graph, exposes a V4L2 video capture node, manages vb2 DMA buffers, and supports standard/input/format/crop configuration plus a private CCDC raw-parameter ioctl.

## Important APIs, Types, And Functions
Important tables are `vpfe_standards` for 525/625-line analog standards and `formats[]` for YUYV/UYVY/YVYU/VYUY Bayer and RGB565 media-bus mappings. CCDC helpers include register accessors, `vpfe_ccdc_restore_defaults()`, `vpfe_ccdc_config_ycbcr()`, `vpfe_ccdc_config_raw()`, `vpfe_ccdc_set_hw_if_params()`, `vpfe_config_ccdc_image_format()`, and `vpfe_config_image_format()`. V4L2 entry points include open/release, querycap, format enum/get/try/set, frame-size enum, input/std ioctls, selection crop get/set, default ioctl `VIDIOC_AM437X_CCDC_CFG`, and vb2 ioctls.

Streaming state is controlled by `vpfe_start_streaming()`, `vpfe_stop_streaming()`, `vpfe_isr()`, `vpfe_schedule_next_buffer()`, `vpfe_handle_interlaced_irq()`, and `vpfe_process_buffer_complete()`. Device integration is handled by `vpfe_get_pdata()`, async notifier callbacks, `vpfe_probe()`, `vpfe_remove()`, and sleep PM context save/restore helpers.

## Control Flow
Probe registers a V4L2 device, parses platform data or OF graph endpoint, maps the CCDC registers, requests the capture IRQ, enables runtime PM long enough to load CCDC defaults, allocates remote subdev slots, and registers an async notifier. When the remote subdevice binds, the driver matches its advertised media-bus codes against local formats, then completion initializes locks/queue/video node and sets input 0.

Open initializes the hardware only for the first file handle: it configures the default input, gets runtime PM, enables CONFIG, restores CCDC defaults, and clears interrupts. Release closes the CCDC and drops runtime PM on the last handle. Format setting asks the subdevice to set pad format, mirrors the returned mbus format into a V4L2 pix format, computes 32-byte-aligned stride/size, updates crop, and writes CCDC image configuration.

Streaming attaches CCDC interrupts, configures raw or YCbCr registers, pops the first queued buffer, writes its SDRAM address, enables the CCDC PCR bit, and starts the remote subdevice stream. The ISR handles VDINT0/VDINT1: progressive capture completes current buffers and schedules next buffers on half-frame interrupts, while interlaced capture tracks hardware field ID and optionally schedules bottom fields. Stop disables PCR, waits briefly for `capture_stop`, detaches interrupts, stops the subdevice, and returns all buffers.

## State And Persistence
In-memory state includes current subdevice/input, current format, crop rectangle, current/next capture buffers, DMA queue, field/sequence counters, CCDC configuration, field offset, runtime PM state, and saved CCDC register context for sleep. Hardware state is the CCDC register block, IRQ masks/status, SDRAM address, and subdevice stream state. No durable state is written.

## Dependencies And Integration Points
Depends on V4L2 core, async subdev notifier, fwnode endpoint parsing, media bus format APIs, videobuf2 DMA-contig, runtime PM, pinctrl PM, platform IRQ/MMIO resources, and a remote subdevice that supports pad format enumeration/setting, frame-size enumeration, optional standard ioctls, and `s_stream`.

## Risks
The implementation is effectively single-endpoint/single-input despite array abstractions. The async-bound comparison indexes the callback `asd` pointer as if it were an array; this is benign for one entry but risky if expanded. Raw Bayer pixel-format handling appears narrow and `vpfe_ccdc_get_pixel_format()` reports YUYV for raw mode, so raw-format paths need careful validation. Several ioctls reject changes while vb2 is busy, but standard/input/crop/format changes still rely on caller locking. Interlaced field synchronization can drop a frame during recovery. Runtime PM error handling in suspend/resume ignores late failures by design.

## Test Signals
Use `v4l2-compliance`, async graph probe with a real camera/decoder, media-bus code intersection tests, format set/get/try across all supported codes, crop selection, std query/set for analog decoders, streaming with at least three buffers, progressive and interlaced capture, buffer sequence/timestamp checks, private raw CCDC ioctl validation, runtime PM open/release cycles, and suspend/resume during active streaming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/am437x/am437x-vpfe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/am437x/am437x-vpfe.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/am437x/am437x-vpfe.h

## Purpose
Defines the AM437x VPFE driver's internal data model for subdevice integration, CCDC configuration, supported formats, vb2 buffers, and the main device state.

## Important APIs, Types, And Functions
Key enums describe pin polarity, hardware interface type, CCDC pixel format, frame format, pixel order, and buffer type. `struct vpfe_hw_if_param` stores endpoint interface type, sync polarities, and bus width. `struct vpfe_subdev_info` and `struct vpfe_config` describe the single remote subdevice and async connection. `struct ccdc_params_raw`, `struct ccdc_params_ycbcr`, `struct ccdc_config`, and `struct vpfe_ccdc` model CCDC hardware programming. `struct vpfe_fmt` maps V4L2 fourcc to mbus code and bits-per-pixel. `struct vpfe_device` is the top-level driver state.

Inline helpers compute maximum bit positions for gamma/data-size settings and include the CCDC register header.

## Control Flow
The header has no executable flow beyond inline helpers. Its structures are populated by device-tree parsing, async bind, V4L2 format/input/std ioctls, CCDC programming helpers, vb2 queue callbacks, IRQ handling, and PM context save/restore.

## State And Persistence
Defines all important in-memory state: V4L2/video objects, notifier, current subdevice/input, selected standard, IRQ, current/next buffers, current format and crop, active format list, vb2 queue, DMA queue/lock, field offset, CCDC config/register context, stopping flag, and capture-stop completion.

## Dependencies And Integration Points
Depends on Linux AM437x VPFE UAPI definitions, clocks, completions, I/O, I2C, V4L2 core, vb2 V4L2, vb2 DMA-contig, and local register definitions. It is shared only by the AM437x implementation.

## Risks
The `VPFE_MAX_SUBDEV` and `VPFE_MAX_INPUTS` constants are one, but several structures look general; future expansion needs careful array and async-notifier auditing. Register context sizing depends on `VPFE_REG_END`. State fields are shared across ioctl, vb2, IRQ, and PM paths, so lock discipline in the C file is critical.

## Test Signals
Compile-time coverage catches structure/API drift. Runtime validation is through the C file: graph binding, format negotiation, capture IRQs, buffer completion, and suspend/resume context restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/am437x/am437x-vpfe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/am437x/am437x-vpfe_regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/am437x/am437x-vpfe_regs.h

## Purpose
Defines AM437x VPFE/CCDC register offsets and bit fields used by the capture driver.

## Important APIs, Types, And Functions
Offsets cover PCR, SYNMODE, timing/window registers, SDRAM address, clamp/black compensation, ALAW, BT.656 interface, CCDCFG, DMA control, sysconfig, config, and IRQ registers. Bit masks and shifts describe polarity, frame format, data size, pixel format, write enable, low-pass filter, ALAW, black clamp/compensation, latch behavior, line offsets, interlaced/progressive memory offsets, input data widths, BT.656 flags, interrupt bits, DMA overflow, and CONFIG enable/standby fields.

## Control Flow
No executable flow. The implementation uses these constants when restoring defaults, configuring raw/YCrCb capture, setting windows/stride, programming SDRAM addresses, enabling/disabling CCDC, and acknowledging interrupts.

## State And Persistence
The header describes mutable hardware register state; it stores no data itself.

## Dependencies And Integration Points
Consumed by `am437x-vpfe.h` and `am437x-vpfe.c`. It encodes the ABI between the driver and AM437x image sensor interface hardware.

## Risks
Incorrect masks or alignment constants can corrupt capture geometry, DMA stride, interrupt acknowledgement, or pixel packing. The driver relies on `VPFE_HSIZE_OFF_MASK`/32-byte alignment and `VPFE_REG_END` for context storage, so register-table changes must keep those users in sync.

## Test Signals
Hardware capture with known patterns, interrupt count behavior, stride alignment checks, DMA overflow reporting, raw and YCbCr mode validation, and suspend/resume context tests provide coverage beyond compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/am437x/am437x-vpfe_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/cal/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/cal/Makefile

## Purpose
Builds the TI CAL driver composite object.

## Important APIs, Types, And Functions
`obj-$(CONFIG_VIDEO_TI_CAL) += ti-cal.o` emits the driver when enabled. `ti-cal-y := cal.o cal-camerarx.o cal-video.o` combines the core CAL device, CameraRx subdevice/PHY code, and video-node code.

## Control Flow
No runtime flow. Kbuild composes the CAL module from three source files.

## State And Persistence
No state beyond kernel build outputs.

## Dependencies And Integration Points
Connects the top-level TI Kconfig `VIDEO_TI_CAL` to the CAL implementation units.

## Risks
The CameraRx file is always part of the CAL object, so changes there affect all CAL builds. Missing one object would break either core, subdev, or video-node functionality.

## Test Signals
Build with `CONFIG_VIDEO_TI_CAL=m` and `=y` and confirm `ti-cal` includes `cal-camerarx.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/cal/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/cal/cal-camerarx.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/cal/cal-camerarx.c

## Purpose
Implements the CameraRx CSI-2 receiver/PHY subdevice for the TI CAL driver. It parses CSI-2 endpoint wiring, configures lane mapping, D-PHY timings, power/reset/interrupt state, forwards streaming to the upstream sensor, exposes sink/source V4L2 subdev pads, and passes frame descriptors for routed CSI-2 streams.

## Important APIs, Types, And Functions
The file operates on `struct cal_camerarx` and the parent `struct cal_dev` from `cal.h`. Register accessors are `camerarx_read()` and `camerarx_write()`. Hardware management helpers include `cal_camerarx_get_ext_link_freq()`, `cal_camerarx_lane_config()`, `cal_camerarx_enable()`, `cal_camerarx_disable()`, `cal_camerarx_config()`, `cal_camerarx_power()`, `cal_camerarx_wait_reset()`, `cal_camerarx_wait_stop_state()`, IRQ enable/disable helpers, PPI enable/disable helpers, `cal_camerarx_start()`, and `cal_camerarx_stop()`. Exported integration functions include `cal_camerarx_i913_errata()`, `cal_camerarx_get_phy_from_entity()`, `cal_camerarx_create()`, and `cal_camerarx_destroy()`.

V4L2 pad ops implement stream enable/disable, media-bus code and frame-size enumeration, format get/set, routing set/init, and frame descriptor retrieval.

## Control Flow
Creation allocates a CameraRx instance, maps the per-instance MMIO resource, initializes syscon regmap fields, parses the OF graph endpoint for CSI-2 lane data and remote source nodes, initializes a stream-capable V4L2 subdev with one sink and multiple source pads, finalizes state, and registers it with the parent V4L2 device.

Stream enable resolves the routed sink stream, then `cal_camerarx_start()` handles first-stream hardware initialization. It gets external link frequency from the source, powers the source, enables CAL CSI-2 error interrupts, configures lane positions/polarities, enables CAMERARX clocks/lanes, deasserts complex I/O reset, writes D-PHY timing registers, programs stop-state timing, forces RX mode, powers the PHY, starts the source stream, waits for reset completion and stop state, then enables the PPI. Additional enabled streams only propagate enable to the source and increment `enable_count`.

Stream disable decrements `enable_count`; if other streams remain, only the corresponding source stream is disabled. For the last stream, it disables PPI and interrupts, powers down complex I/O, asserts reset, disables CAMERARX, disables the source stream, and powers the source off.

## State And Persistence
State includes endpoint lane configuration, source endpoint/node pointers, source subdev/pad, active routing/format state in V4L2 subdev state, register field handles, MMIO base/resource, virtual-channel lock, and `enable_count`. Hardware state includes CAL complex I/O lane config, D-PHY timing/power/reset, CSI-2 PPI, and IRQ masks. No persistent storage is used.

## Dependencies And Integration Points
Depends on parent CAL core register helpers and data tables, syscon regmap fields, platform resources named `cal_rx_core0`/`cal_rx_core1`, OF graph and V4L2 fwnode endpoint parsing, V4L2 subdev streams/routing APIs, media entity validation, upstream source subdevices that provide link frequency and optional frame descriptors, and CAL format tables.

## Risks
Multistream link-frequency fallback deliberately rejects pixel-rate-only sources by passing zero bpp, so sources need `V4L2_CID_LINK_FREQ` for multistream. `enable_count` protects first/last hardware transitions but must stay balanced with all stream enable/disable paths. Endpoint parsing assumes at least one valid data lane before formatting the `data_lanes` debug string. Hardware waits log timeout errors but do not always abort after timeout. The frame descriptor path requires the upstream descriptor to be CSI-2 and contain the routed stream.

## Test Signals
Validate media graph creation, subdev routing, stream enable/disable on single and multiple streams, lane polarity/position programming from DT, link-frequency handling, D-PHY timing values across frequencies, error IRQ reporting, stop-state/reset wait logs, frame descriptor propagation, i913 errata application on affected SoCs, and `v4l2-compliance` for stream-aware subdev operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/cal/cal-camerarx.c -->
