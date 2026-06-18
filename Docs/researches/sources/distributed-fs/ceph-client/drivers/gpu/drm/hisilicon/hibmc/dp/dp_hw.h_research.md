# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/dp/dp_hw.h

Purpose: public HIBMC DP hardware interface used by the DRM connector/encoder layer and debugfs. It defines DP connector wrapper state, HPD status values, colorbar pattern/config structs, and exported hardware-control functions.

Important APIs/types: `struct hibmc_dp` embeds `struct drm_encoder`, `struct drm_connector`, `struct drm_dp_aux`, MMIO base, private DP device pointer, debug colorbar config, and last IRQ status. `struct hibmc_dp_cbar_cfg` carries enable, self timing, dynamic rate, and pattern. API prototypes include hardware init, mode set, display enable, colorbar setup, link reset, HPD config, interrupt control, HPD polling, and link capability accessors.

Control flow: this header is included by `hibmc_drm_drv.h` and exposes the DP block to HIBMC KMS code. The connector/encoder code calls into these functions during init, register/unregister, HPD, atomic enable/disable, and mode validation.

State and persistence: the header centralizes in-memory DP state ownership in `struct hibmc_dp`; nested `struct hibmc_dp_dev` remains opaque so low-level DP implementation files own detailed link and DPCD state.

Dependencies and integration points: includes DRM core headers and `drm_dp_helper.h` for AUX/DPCD integration. It is part of the HIBMC PCI DRM driver's private structure and provides the bridge between DRM objects and HIBMC DPTX hardware.

Risks: because `struct hibmc_dp` embeds DRM objects, lifetime must follow DRM device lifetime. The public colorbar config does not encode bounds in the type, so callers must validate the enum-like values.

Test signals: compile coverage of all HIBMC DP users, connector registration, AUX registration, HPD IRQ, colorbar debugfs writes, and mode validation exercise this header contract.
