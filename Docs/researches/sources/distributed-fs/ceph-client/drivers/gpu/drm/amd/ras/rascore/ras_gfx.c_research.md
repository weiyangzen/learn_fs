# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_gfx.c

Purpose: this is the generic GFX RAS IP dispatch layer. It chooses an IP-version-specific GFX RAS function table and exposes a wrapper for mapping driver GFX subblocks to RAS TA subblocks.

Important APIs: `ras_gfx_hw_init()` copies `gfx_ip_version` from config and selects `gfx_ras_func_v9_0` for IP versions 9.4.3, 9.4.4, and 9.5.0. `ras_gfx_get_ta_subblock()` calls the selected `get_ta_subblock` operation. `ras_gfx_hw_fini()` is currently a no-op.

Control flow and state: the file stores only `ras_core->ras_gfx.gfx_ip_version` and `ip_func`. Initialization fails with `-EINVAL` when the GFX IP is unsupported. There is no persistence.

Dependencies and integration: PSP error injection calls `ras_gfx_get_ta_subblock()` before sending a TA trigger-error command for GFX blocks. The selected implementation comes from `ras_gfx_v9_0.c`. Risks include no null guard in `ras_gfx_get_ta_subblock()` if called before successful hardware init and no fallback for unknown IPs. Test signals should include supported/unsupported IP initialization, calling GFX error injection with valid and invalid subblocks, and verifying 9.5.0 behavior where UMC code also branches on GFX version for row handling.
