# sources/distributed-fs/ceph-client/drivers/phy/intel/Kconfig

## Purpose
Kconfig entries for Intel Keem Bay and Lightning Mountain PHY drivers: eMMC, USB, combo PHY, and LGM eMMC.

## Important APIs, types, and functions
Defines `PHY_INTEL_KEEMBAY_EMMC`, `PHY_INTEL_KEEMBAY_USB`, `PHY_INTEL_LGM_COMBO`, and `PHY_INTEL_LGM_EMMC`.

## Control flow
The symbols gate object compilation and select required framework symbols such as `GENERIC_PHY`, `REGMAP_MMIO`, `MFD_SYSCON`, and `REGMAP`.

## State and persistence
Only kernel configuration state.

## Dependencies and integration points
Architecture gates are `ARCH_KEEMBAY`, `X86`, and `COMPILE_TEST`, with `HAS_IOMEM`/`OF` as needed. The Makefile consumes these symbols.

## Risks and test signals
Risks are missing dependency selections for code paths using clk/reset/syscon or over-broad bool/tristate mismatch. Test modular and built-in build combinations.
