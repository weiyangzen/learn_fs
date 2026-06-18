# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/gr2d.c

Purpose: platform and host1x client driver for Tegra 2D graphics engines.

Important APIs/functions: `gr2d_probe()` allocates the client, gets clock/reset resources, initializes OPP data, registers the host1x client, and builds the address-register bitmap. `gr2d_init()` requests a host1x channel and syncpoint, attaches IOMMU, and registers with Tegra DRM. `gr2d_exit()` unregisters, suspends, detaches, and releases channel/syncpoint. `gr2d_open_channel()`/`close_channel()` expose the channel to DRM contexts. `gr2d_is_addr_reg()` and `gr2d_is_valid_class()` feed the firewall. Runtime PM acquires/deasserts resets and enables the clock on resume, and stops the channel/asserts memory-client reset/turns off the clock on suspend.

Control flow and state: `struct gr2d` stores one shared channel, one syncpoint, reset bulk array, SoC version, and an address-register bitmap. Userspace jobs flow through `tegra_drm_submit`.

Dependencies/integration: integrates host1x, reset controller, runtime PM/autosuspend, OPP common setup, IOMMU attach, and firewall register classification.

Risks: suspend intentionally avoids full GR2D reset in some cases to prevent host1x cmdproc stalls; reset sequencing is hardware-sensitive. The firewall map must include every address-bearing register or userspace could submit unchecked addresses.

Test signals: host1x client registration, runtime PM suspend/resume, simple 2D job submission, invalid address-register submit rejection, and reset/clock error injection.
