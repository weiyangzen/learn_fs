# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lt_phy.h

Purpose: declares the LT PHY PLL, clock, readout, compare, signal-level, and Xe3LPD wrapper interface.

Important APIs/types/functions: declarations cover PLL enable/disable, state calculation, TBT state calculation/readout, port clock calculation, signal level programming, hardware state dump/compare/readout, HDMI PLL calculation, Xe3LPD wrappers, and table verification.

Control flow: DPLL manager and encoder enable paths call calc/enable/disable/readout helpers; training code calls signal-level programming; state checker calls compare/dump.

State and persistence behavior: APIs operate on `struct intel_dpll_hw_state`, `struct intel_lt_phy_pll_state`, encoder state, and live PHY hardware.

Dependencies and integration points: connects LT PHY implementation to DPLL, DDI, CRTC state, and display initialization code.

Risks: callers must supply matching encoder/CRTC state and respect TBT versus non-TBT paths.

Test signals: build coverage and DPLL manager integration across DP/eDP/HDMI/TBT outputs.
