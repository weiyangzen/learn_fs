<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_drv.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_drv.c

Purpose: parent platform driver for the Amphion VPU device. It owns top-level register mapping, V4L2/media-device registration, encoder/decoder function creation, debugfs root, child core population, platform resource callbacks, and module init/exit.

Important APIs/functions: `vpu_writel()`/`vpu_readl()` access parent registers. `vpu_probe()` initializes `struct vpu_dev`, media/V4L2 devices, encoder/decoder `vpu_func` descriptors, debugfs, runtime PM, and child devices. `vpu_remove()` unwinds them. `vpu_driver_init()` registers the parent driver then the core driver; exit unregisters in reverse.

Control flow: matching `nxp,imx8qxp-vpu` or `nxp,imx8qm-vpu` selects platform resources with setup/reset hooks from `vpu_imx8q.c`. Probe registers decoder then encoder V4L2 functions, registers the media device, creates debugfs, and populates child nodes. Reference callbacks call setup hooks on first VPU/encoder/decoder use but only decrement counters on put.

State and persistence: `struct vpu_dev` holds parent state, function descriptors, media device, core list, refs, and debugfs. State is recreated on probe and removed at driver unload. No disk persistence.

Dependencies and integration: depends on OF matching/population, pm_runtime, media controller, V4L2 device registration, debugfs, and function registration helpers implemented elsewhere in the driver.

Risks: setup reference counters are not guarded against underflow on mismatched puts. `of_platform_populate()` return value is ignored. Parent runtime PM is enabled but no parent PM ops are defined here. Child population after debugfs/media registration means later child failures do not fail parent probe.

Test signals: parent probe/remove on supported compatibles, child core discovery, media graph presence, `/dev/video*` function registration, debugfs root creation/removal, module unload with active children rejected by core lifetimes, and error injection through `vpu_add_func()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_drv.c -->
