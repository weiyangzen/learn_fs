# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_debugfs.c

Purpose: Registers OMAP DRM debugfs files for GEM object inspection, DRM MM address-space inspection, framebuffer inspection, and optional DMM/TILER map visualization.

Important APIs/functions: `gem_show()` locks `priv->list_lock` and calls `omap_gem_describe_objects()`. `mm_show()` prints the DRM VMA offset manager address-space `drm_mm`. `fb_show()` lists fbcon and userspace framebuffers when fbdev emulation is enabled. `omap_debugfs_init()` creates common files and conditionally adds `tiler_map` when `dmm_is_available()` reports a DMM/TILER device.

Control flow: The DRM driver installs `omap_debugfs_init` in `drm_driver.debugfs_init`. DRM core invokes it for a minor, and show callbacks read current driver state on demand.

State and persistence: No persistent state is stored; debugfs output reflects live kernel objects and TILER allocations.

Dependencies/integration: Depends on DRM debugfs, fb helper, framebuffer list locking, GEM describe helpers, and DMM/TILER debug map helper.

Risks and test signals: Debugfs callbacks must tolerate missing fbdev helper depending on config and device state. `fb_show()` assumes `dev->fb_helper` is valid when fbdev emulation exists. Test debugfs reads during normal operation, with and without DMM, with multiple framebuffers, and during driver teardown races.
