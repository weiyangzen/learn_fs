# sources/distributed-fs/ceph-client/include/linux/mfd/mt6357/registers.h

## Purpose

This 1574-line header is the MT6357 PMIC register map. It assigns symbolic names to 16-bit register addresses across the chip's top, GPIO, clock/reset, SPI wrapper, RTC, DCXO, charger/startup, battery monitor, fuel gauge, AUXADC, buck regulator, LDO, LED/current-sink, audio, and accessory-detection blocks. It is a compile-time hardware contract: drivers include it so that regmap reads/writes refer to named MT6357 addresses rather than raw offsets.

## Important APIs, Types, and Functions

The file exports no functions or types. Its API surface is the `MT6357_*` macro namespace. Important groups include chip identity/status registers such as `MT6357_SWCID`, interrupt controller registers such as `MT6357_TOP_INT_STATUS0`, `MT6357_PSC_TOP_INT_CON0`, `MT6357_BM_TOP_INT_STATUS0`, `MT6357_BUCK_TOP_INT_CON0`, `MT6357_LDO_TOP_INT_STATUS0`, and `MT6357_AUD_TOP_INT_STATUS0`, RTC registers from `MT6357_RTC_BBPU` through secure RTC offsets, AUXADC request/status/result registers, regulator control/debug/ELR addresses for buck and LDO supplies, and audio/accessory detection register names.

## Control Flow

There is no executable flow in this header. Runtime flow appears in consumers: `drivers/mfd/mt6397-core.c` uses identity and RTC-related constants while instantiating MFD cells, `drivers/mfd/mt6358-irq.c` uses MT6357 top interrupt register addresses with the shared PMIC IRQ code path, `drivers/regulator/mt6357-regulator.c` maps regulator descriptors to these addresses, `drivers/input/keyboard/mtk-pmic-keys.c` uses power/home key status addresses, and sound codec/accessory drivers use the audio/ACCDET regions.

## State and Persistence Behavior

The file owns no storage. The named addresses target persistent PMIC hardware state: power/reset status, RTC counters/alarm registers, EFUSE/ELR trim values, regulator enable and voltage selection state, interrupt latches and masks, and analog monitor/debug values. Register writes can survive until PMIC reset or, for RTC/backup domains, across AP power transitions depending on the hardware domain.

## Dependencies and Integration Points

The only dependency is the include guard. Integration is through Linux regmap and MFD children below the MT6397-family core. The address map must stay consistent with MT6357 silicon and with companion headers such as `mt6357/core.h`, because IRQ numbers and MFD resources point at these register blocks by name. Regulator, input, RTC, AUXADC, and sound drivers depend on these constants being correct for their bitfield definitions.

## Risks and Edge Cases

The main risk is silent hardware misprogramming from a wrong offset or an MT6358/MT6359 address being reused for MT6357 where banks differ. Long contiguous macro lists also invite copy/paste drift in `_SET` and `_CLR` aliases. RTC and regulator addresses are particularly sensitive because they affect persistent power state. Interrupt status and mask register mistakes can lose wake events or leave storming IRQ lines. There is no type checking around macro use, so cross-chip misuse compiles.

## Test Signals

Useful signals are build coverage for `mt6397-core`, `mt6358-irq`, `mt6357-regulator`, PMIC key, RTC, AUXADC, and sound codec consumers; boot probing on MT6357 hardware; regmap debugfs spot checks for known chip ID/status addresses; regulator enable/voltage smoke tests; PMIC key IRQ tests; RTC read/set/alarm tests; and suspend/resume wake tests that exercise masked and latched interrupt registers.
