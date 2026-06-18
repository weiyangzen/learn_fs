<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pmic-eic-sprd.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-pmic-eic-sprd.c

## Purpose
Spreadtrum/Unisoc PMIC EIC driver exposing 16 input-only GPIOs with debounce and IRQ support. Hardware is level-triggered, so edge behavior is emulated by toggling the active level.

## Important APIs, types, and functions
`struct sprd_pmic_eic` stores chip, parent regmap, base offset, cached IEV/IE/TRIG bytes, buslock, and parent IRQ. Helpers read/update PMIC registers. GPIO callbacks cover request/free, fixed input direction, get, and debounce config. IRQ callbacks handle mask/unmask, set_type, bus sync, trigger toggling, and threaded parent IRQ.

## Control flow
Probe gets parent IRQ/regmap and DT `reg`, requests a no-suspend threaded IRQ, fills the 16-line chip, installs a threaded irqchip, and registers. Bus sync programs active level, enable, and trigger pulse. The IRQ handler reads MIS, clears each bit, dispatches nested IRQ, then toggles edge emulation if needed.

## State and persistence behavior
Cached interrupt bytes are software state; data mask, debounce, active level, enable, status, clear, and trigger live in PMIC registers. No PM restore exists; parent IRQ uses `IRQF_NO_SUSPEND`.

## Dependencies and integration points
Depends on parent PMIC regmap, platform IRQ, OF compatible `sprd,sc2731-eic`, gpiolib threaded IRQs, and pinconf debounce.

## Risks and edge cases
Edge emulation races with changing input levels and retries on mismatch. Debounce truncates microseconds to milliseconds and masks to 12 bits. Regmap read failure returns an odd IRQ return conversion. Wake is skipped.

## Test signals
Request/free DMSK, debounce programming, level IRQs, rising/falling/both emulation under rapid changes, clear/trigger writes, and no-suspend behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-pmic-eic-sprd.c -->
