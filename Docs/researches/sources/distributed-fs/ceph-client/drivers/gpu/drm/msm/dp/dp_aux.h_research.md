# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_aux.h

Purpose: Declares the MSM DP AUX adapter API.

Important APIs/types: Public functions register/unregister the DRM AUX adapter, service AUX IRQs, enable/disable transfers, initialize/deinitialize/reconfigure hardware, manage HPD and HPD IRQs, read HPD status/link state, and allocate/free the AUX adapter with device, PHY, eDP flag, and MMIO base.

Control flow/state: DP display/control code owns the returned `drm_dp_aux` and calls init/deinit around power state, `enable_xfers()` around external HPD connect state, and `msm_dp_aux_isr()` from the controller IRQ handler.

Dependencies/integration: Includes DRM DP helper and forward-declares PHY. It is included by `dp_ctrl.h` and other DP modules.

Risks and test signals: API users must not call transfer paths before `msm_dp_aux_init()` and must gate external-DP transfers on connection. Test registration ordering, eDP panel probing before full DRM AUX registration, and HPD enable/disable sequences.
