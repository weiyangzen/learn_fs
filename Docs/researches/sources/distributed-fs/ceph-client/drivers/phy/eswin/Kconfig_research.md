# sources/distributed-fs/ceph-client/drivers/phy/eswin/Kconfig

## Purpose
Declares `PHY_EIC7700_SATA`, the ESWIN EIC7700 SATA SerDes/PHY driver option.

## APIs and dependencies
The symbol is tristate, depends on `ARCH_ESWIN || COMPILE_TEST`, depends on `HAS_IOMEM`, and selects `GENERIC_PHY`.

## Control flow and state
When enabled, Kbuild can compile the EIC7700 SATA PHY object. Kconfig has no runtime state; the kernel config is persistent.

## Integration, risks, and test signals
The entry integrates ESWIN SATA PHY support with Generic PHY and MMIO-capable builds. Risk is low, though regmap, reset, and clock framework dependencies are implicit. Test `y`, `m`, disabled, ESWIN, and compile-test configurations.
