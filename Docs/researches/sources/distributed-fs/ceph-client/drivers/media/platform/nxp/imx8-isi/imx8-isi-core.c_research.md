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
