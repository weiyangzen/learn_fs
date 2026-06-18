# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lt_phy_regs.h

Purpose: defines LT PHY timing constants, MAC/VDR/P2P message bus registers, TX control fields, port buffer control fields, and PLL internal register addresses used by `intel_lt_phy.c`.

Important APIs/types/functions: latency constants define wait budgets for message bus, MacCLK, calibration, reset, and powerdown transitions. `LT_PHY_TXY_CTL*` macros address TX swing/cursor/lane-enable registers. `LT_PHY_VDR_*` macros define VDR config, rate/mode encoding, register address/data slots, and rate update. `XE3PLPD_PORT_BUF_CTL5()` and `XE3PLPD_PORT_P2M_MSGBUS_STATUS_P2P()` map port/lane MMIO. PLL address macros and `PLL_REG_ADDR()` select PLL type offset.

Control flow: LT PHY code uses these constants for sequencing, message-bus writes, state readout, signal level programming, and PLL table construction.

State and persistence behavior: definitions only; state resides in hardware registers and DPLL state.

Dependencies and integration points: depends on register helper macros, XeLPDP/CX0 port indexing, and LT PHY hardware programming model.

Risks: wrong offsets, bit masks, or latency budgets directly cause PHY programming failures. Address macros must match table values and HDMI calculation output.

Test signals: register programming traces, PLL enable/disable timeout behavior, signal-level register writes, and table verification using defined VDR fields.
