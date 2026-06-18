# sources/distributed-fs/ceph-client/include/linux/mfd/mt6358/registers.h

## Purpose

This header is the MT6358 PMIC register-address contract. It is narrower than the full MT6357 map but covers the addresses used by Linux consumers: chip ID/status, top interrupt registers, RTC and secure RTC blocks, PSC/BM/HK interrupt blocks, buck and LDO regulator blocks, analog regulator monitor blocks, and audio interrupt registers.

## Important APIs, Types, and Functions

The file exports only `MT6358_*` macros. Important definitions include `MT6358_SWCID`, `MT6358_TOP_INT_STATUS0`, `MT6358_MISC_TOP_INT_CON0`, `MT6358_SCK_TOP_INT_CON0`, RTC addresses from `MT6358_RTC_BBPU` to `MT6358_RTC_SEC_WRTGR`, IRQ top registers for PSC/BM/HK/BUCK/LDO/AUD, individual buck register blocks such as `MT6358_BUCK_VPROC11_CON0` and `MT6358_BUCK_VCORE_ELR0`, LDO blocks such as `MT6358_LDO_VXO22_CON0`, `MT6358_LDO_VSRAM_PROC11_DBG0`, and aliases for MT6366-compatible regulator naming.

## Control Flow

No executable flow is present. Runtime drivers use the constants in regmap transactions. `mt6397-core.c` reads `MT6358_SWCID` and registers RTC/key child devices. `mt6358-irq.c` combines these addresses with `MT6358_TOP_GEN()` for hierarchical IRQ handling. `mt6358-regulator.c` uses the regulator and analog monitor addresses to implement enable, voltage selection, mode, and status operations.

## State and Persistence Behavior

The file maps hardware state but owns none. PMIC state includes latched interrupt bits, RTC time/alarm/power-down data, regulator enable and voltage state, debug monitor values, and analog trim/ELR values. Writes to regulator and RTC registers can change platform power behavior until later driver action or hardware reset.

## Dependencies and Integration Points

The header is consumed with `mt6358/core.h` by the shared IRQ code, with `mt6397/core.h` by MFD children, and by MT6358/MT6366 regulator descriptors. It depends on convention more than C types: suffixes like `_CON0`, `_DBG0`, `_ELR0`, `_ANA_CON0`, `_INT_CON0`, and `_INT_STATUS0` must match macro construction and driver descriptor expectations.

## Risks and Edge Cases

Cross-chip aliasing is a real risk: MT6358 and MT6366 share driver paths but do not expose identical regulators, so the MT6366 aliases must point at intentionally reused address slots. Incorrect RTC base offsets or write-trigger addresses break time/alarm updates. Regulator descriptor masks are defined elsewhere, so a correct address with a wrong companion mask can still misprogram voltage or mode.

## Test Signals

Build MT6358 MFD, IRQ, RTC, keyboard, and regulator drivers; boot on MT6358/MT6366 hardware; verify `SWCID`; list regulators from debugfs/sysfs; test enable/disable and voltage selection on representative buck/LDO supplies; run RTC read/set/alarm; and generate key/charger/audio IRQs where hardware supports them.
