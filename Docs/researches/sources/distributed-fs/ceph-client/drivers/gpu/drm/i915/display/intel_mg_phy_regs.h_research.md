# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_mg_phy_regs.h

Purpose: defines MG PHY register address macros and bitfields for Type-C PHY transmitters, DP mode, clock hub, DFLEX/FIA lane mapping, reference clock, PLL divider, loop filter, fractional lock, SSC, bias, and TDC controls.

Important APIs/types/functions: `MG_PHY_PORT_LN()` builds lane/port MMIO addresses. TX macros cover link params, PISO readload, swing control, driver control, DCC, and clock hub for TX1/TX2 lanes. DP mode macros define x1/x2 modes. FIA/DFLEX macros expose lane mapping registers. PLL macros define refclk, core clock, high-speed clock, divider, LF, FRAC_LOCK, SSC, BIAS, and TDC fields.

Control flow: other PHY/DPLL code includes this header to compute MMIO register addresses and bitfield values for MG PHY programming and readout.

State and persistence behavior: definitions only. Hardware register contents are persistent runtime device state controlled by consumers of the header.

Dependencies and integration points: depends on display register helper macros and Type-C port numbering. Integrates with MG PHY PLL and signal-level code outside this subset.

Risks: register formulas span multiple Type-C ports and lanes; wrong base offsets or lane increments can program the wrong transmitter. Several fields use raw shifts rather than `REG_FIELD_PREP`, so caller values must already fit. The header is shared hardware contract material with little runtime validation.

Test signals: MG PHY register programming traces, Type-C lane mapping validation, DP x1/x2 mode changes, PLL lock/readout across ports, and signal-level updates on each TX/lane combination.
