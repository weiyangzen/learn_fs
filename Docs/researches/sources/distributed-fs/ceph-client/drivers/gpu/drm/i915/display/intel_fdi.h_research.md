# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fdi.h

Purpose: declares the FDI programming interface used by modeset, DDI/PCH encoder, state checker, and atomic bandwidth code.

Important APIs/types/functions: exposes lane/bandwidth helpers (`intel_fdi_add_affected_crtcs()`, `intel_fdi_link_freq()`, `ilk_fdi_compute_config()`, `intel_fdi_atomic_check_link()`), training and normal-mode helpers (`intel_fdi_link_train()`, `intel_fdi_normal_train()`, `hsw_fdi_link_train()`), disable/PLL helpers, initialization/frequency update hooks, and assertion helpers for TX/RX/PLL states.

Control flow: no executable flow; the header defines the legal call surface for FDI-capable platforms.

State and persistence: no storage is defined. State lives in `struct intel_display`, `struct intel_crtc_state`, and hardware registers.

Dependencies and integration: forward-declares display atomic, CRTC, encoder, and link-bandwidth types. Used by PCH encoder code, modeset compute/check paths, and state verification.

Risks: platform code must call the right sequence: compute config, atomic link check, PLL enable, train, normal mode, and disable. The header cannot enforce generation restrictions.

Test signals: compile all FDI and non-FDI platform paths; state checker tests should call assertion helpers around enable/disable transitions.
