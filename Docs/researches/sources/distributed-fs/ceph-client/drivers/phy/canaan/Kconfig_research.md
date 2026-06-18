# sources/distributed-fs/ceph-client/drivers/phy/canaan/Kconfig

## Purpose
Declares `PHY_CANAAN_USB`, the tristate Kendryte K230 USB 2.0 PHY option.

## APIs and dependencies
The symbol depends on `(ARCH_CANAAN || COMPILE_TEST) && OF` and selects `GENERIC_PHY`.

## Control flow and state
When set to `y` or `m`, Kbuild can compile the K230 USB PHY driver. Kconfig has no runtime state; the selected kernel configuration is the persistent outcome.

## Integration, risks, and test signals
It integrates the Canaan platform driver with Generic PHY and OF-based platform discovery. Risk is low, though the entry does not explicitly depend on `HAS_IOMEM` despite the driver mapping MMIO. Test built-in, module, disabled, Canaan, and compile-test configurations.
