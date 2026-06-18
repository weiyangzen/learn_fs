# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_combo_phy_regs.h

## Purpose
Defines combo PHY MMIO address calculations and bit fields for ICL-era and later display PHY programming.

## Important definitions
The file maps PHY base addresses for ICL A/B, EHL C, RKL D, and ADL E through `_ICL_COMBOPHY()`. It defines CL registers (`ICL_PORT_CL_DW5`, `DW10`, `DW12`) with lane power masks, COMP registers with `COMP_INIT`, process/voltage fields, `IREFGEN`, and reference-value DWords, PCS registers with DCC/common keeper/latency fields, TX registers for swing, RCOMP, tap/cursor, LDO override, scalar, and ODCC clock settings, plus `ICL_DPHY_CHKN()`.

## Control flow and state
There is no executable flow. These macros are consumed by combo PHY init and link-training code to read/write persistent PHY hardware state.

## Dependencies, risks, and tests
It depends on `intel_display_reg_defs.h` for register/mask helpers. Incorrect offsets or masks can break every encoder using combo PHYs, often as link-training failures or blank displays. Tests should include compile coverage, PHY state verification, link training across PHYs A-E, and platform-specific register dumps.
