# sources/distributed-fs/ceph-client/drivers/clk/ti/Kconfig

## Purpose

This Kconfig file defines the optional TI ADPLL clock driver symbol.

## Important APIs, Types, And Functions

`CONFIG_COMMON_CLK_TI_ADPLL` is a tristate "Clock driver for dm814x ADPLL". It depends on `ARCH_OMAP2PLUS || COMPILE_TEST`, defaults to `y` for `SOC_TI81XX`, and enables the DM814x ADPLL CCF platform driver.

## Control Flow

When selected, the TI Makefile builds `adpll.o`. The default enables the driver for TI81xx SoCs that need it while still allowing compile coverage elsewhere.

## State And Persistence Behavior

No runtime state is stored here. The file controls build inclusion only.

## Dependencies And Integration Points

The dependency matches OMAP2+ clock infrastructure and compile-test use. The ADPLL driver itself also depends on platform devices, device tree, and CCF.

## Risks And Edge Cases

If ADPLL support is needed on a newly supported TI SoC, the default or dependency may need adjustment. Keeping this as a separate symbol from the OMAP2PLUS core clock files allows modular compile testing but also means DT nodes will not bind if the symbol is off.

## Test Signals

Build with `CONFIG_COMMON_CLK_TI_ADPLL=y`, `m`, and disabled. On TI81xx configs, confirm the default includes ADPLL support.
