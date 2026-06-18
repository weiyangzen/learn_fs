# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dkl_phy_regs.h

### Purpose
`intel_dkl_phy_regs.h` defines the Dekel PHY register address model used by the i915 display driver for Type-C/TC PHY programming. It gives callers typed register descriptors that carry both the visible 4 KB MMIO aperture offset and the bank index needed to select the upper PHY address bits.

### Important APIs, Types, And Functions
The central type is `struct intel_dkl_phy_reg`, with a 24-bit `reg` field and 4-bit `bank_idx`. `_DKL_REG()`, `_DKL_REG_LN()`, `DKL_REG_MMIO()`, and `DKL_REG_TC_PORT()` are the important address helpers. The header then names lane and common registers such as `DKL_PCS_DW5()`, `DKL_PLL_DIV0()`, `DKL_PLL_DIV1()`, `DKL_PLL_SSC()`, `DKL_PLL_BIAS()`, `DKL_REFCLKIN_CTL()`, `DKL_TX_DPCNTL*()`, `DKL_TX_FW_CALIB()`, `DKL_DP_MODE()`, and `DKL_CMN_UC_DW_27()`. `HIP_INDEX_REG()`, `HIP_INDEX_VAL()`, and `_HIP_INDEX_SHIFT()` describe the indexing registers used to map a bank into the limited aperture.

### Control Flow
This header has no runtime control flow, but it encodes the register-selection flow used by its callers: derive the PHY base from a TC port, split an internal PHY offset into aperture offset plus bank index, program the appropriate HIP index register for the port group, then perform MMIO through the aperture. Lane-specific macros derive lane 1 offsets from lane 0/1 stride definitions.

### State, Persistence, And Dependencies
There is no stored software state. Hardware state lives in the Dekel PHY registers and HIP index registers. The file depends on `linux/types.h` and `intel_display_reg_defs.h` for integer types, `_MMIO`, `_PORT`, and `REG_BIT`/`REG_GENMASK` helpers.

### Integration Points
The macros are consumed by display PHY, PLL, and Type-C link training code that must program Dekel PHY lanes and common PLL blocks. The bank-aware descriptor is significant because callers need more than a plain `i915_reg_t` to reach the correct internal PHY bank.

### Risks
The bank/aperture split is easy to misuse: writing `DKL_REG_MMIO()` without setting the matching HIP index would address the wrong internal page. Port math assumes fixed 0x1000 spacing from PHY1 through PHY6. A macro typo exists in the formal parameter name of `DKL_CLKTOP2_HSCLKCTL(rc_port)`, while the body uses `tc_port`; this relies on macro expansion context and should be treated with caution. Bit masks are hardware contracts, so off-by-one shifts can break PLL or lane calibration.

### Test Signals
Useful signals are display bring-up on every supported TC port, PLL lock/link training success for DP/Type-C modes, register trace validation that HIP index writes precede banked MMIO, and static checks around generated offsets for lanes 0 and 1.
