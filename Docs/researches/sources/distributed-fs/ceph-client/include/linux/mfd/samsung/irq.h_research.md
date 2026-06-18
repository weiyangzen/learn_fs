# sources/distributed-fs/ceph-client/include/linux/mfd/samsung/irq.h

## Purpose

This 455-line header defines interrupt numbers and bit masks for Samsung S2MPA01, S2MPG10, S2MPG11, S2MPS11, S2MPS14, S2MPU02, S2MPU05, and S5M8767 PMIC families.

## Important APIs, Types, and Functions

It exports per-chip IRQ enums such as `s2mpa01_irq`, `s2mpg10_irq`, `s2mpg11_irq`, `s2mps11_irq`, `s2mps14_irq`, `s2mpu02_irq`, `s2mpu05_irq`, and `s5m8767_irq`, plus masks for power-key edges, cable/JIG events, RTC alarms/periodic events, thermal thresholds, watchdog/reset events, over-current warnings, power-meter warnings, NTC warnings, and top-level common IRQ sources.

## Control Flow

There is no executable flow. Samsung IRQ controller code maps status register bits into these Linux IRQ indexes, applies masks through per-chip mask registers, and exposes child interrupts to RTC, regulator, and power-key clients.

## State and Persistence Behavior

The represented state persists in PMIC interrupt status and mask registers. The enum ordering is part of the Linux IRQ ABI for subdrivers, and `*_IRQ_NR` values indicate chip-specific table sizes.

## Dependencies and Integration Points

It integrates Samsung MFD interrupt chips with power-key/input, RTC alarms, regulator thermal/OCP warnings, power-meter/NTC monitoring, and wakeup handling.

## Risks and Edge Cases

Several chips reuse masks but differ in enum order or event names. Inline mask definitions inside enum blocks must stay aligned with adjacent status registers. Incorrect IRQ count values can truncate or overrun regmap-irq tables.

## Test Signals

Regmap-irq table build tests for every chip, IRQ number-to-mask unit tests, wakeup interrupt tests for power-key/RTC, and fault-injection tests for thermal/OCP events.
