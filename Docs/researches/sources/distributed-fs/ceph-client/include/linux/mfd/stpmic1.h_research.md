# sources/distributed-fs/ceph-client/include/linux/mfd/stpmic1.h

## Purpose

This 212-line header defines STPMIC1 PMIC register addresses, regulator/interrupt/control masks, pull-down settings, USB/boost controls, power-key behavior, and parent-device state.

## Important APIs, Types, and Functions

It exports status/control/register addresses from turn-on/off status through interrupt source registers, `PMIC_MAX_REGISTER_ADDRESS`, IRQ register count, voltage/enable/HPLP/standby masks, pull-down register/mask pairs for bucks/LDOs/VREF, ICC timeout masks, bypass and main control bits, pad control bits, VINLOW and USB/boost control bits, PONKEY turnoff fields, and `struct stpmic1`.

## Control Flow

No executable flow is in the header. Regulator, power, USB/boost, and IRQ code use these masks for regmap update/read/clear operations; MFD parent stores regmap and regmap-irq data in `struct stpmic1`.

## State and Persistence Behavior

PMIC hardware persists regulator voltage/enables, standby state, pull-down settings, mask/rank/reset behavior, interrupt pending/latch/mask/source state, watchdog, power-key, and USB boost/switch state.

## Dependencies and Integration Points

It integrates STPMIC1 MFD core with regulator, power/reset, USB boost, IRQ, regmap, and device wakeup handling.

## Risks and Edge Cases

Interrupt registers come in four parallel banks with pending, latch, clear, mask, set-mask, clear-mask, and source views; using the wrong bank can fail to clear or mask events. Power-key and software switch-off bits can shut down the system.

## Test Signals

Regulator mask tests, IRQ bank mapping tests, power-key turnoff tests, watchdog/boost smoke tests, and suspend/resume wakeup validation.
