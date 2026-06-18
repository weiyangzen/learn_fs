# sources/distributed-fs/ceph-client/drivers/input/misc/stpmic1_onkey.c

## Purpose
`stpmic1_onkey.c` reports STPMIC1 ONKEY falling/rising interrupts as `KEY_POWER` and programs optional PMIC long-press power-off behavior and pad pull-up behavior from device properties.

## Important APIs, Types, and Functions
`struct stpmic1_onkey` stores input device and falling/rising IRQs. `onkey_falling_irq()` reports press and `onkey_rising_irq()` reports release; both call `pm_wakeup_event()`. `stpmic1_onkey_probe()` parses `power-off-time-sec`, `st,onkey-clear-cc-flag`, and `st,onkey-pu-inactive`, writes PMIC regmap bits, requests named threaded IRQs, and registers input. PM ops enable/disable IRQ wake on both IRQs.

## Control Flow
Probe obtains the parent `struct stpmic1`, named IRQs `onkey-falling` and `onkey-rising`, computes turnoff-control bits from properties, updates `PKEY_TURNOFF_CR`, optionally sets `PADS_PULL_CR`, allocates input, requests both threaded IRQs, registers input, stores state, and enables device wakeup. Runtime IRQs report press/release and sync. Suspend/resume toggles wake for both IRQs when the device is wake-enabled.

## State and Persistence Behavior
The driver persists IRQ numbers and input pointer. PMIC turnoff and pad-control register writes persist in hardware. Wakeup state persists through device core and IRQ wake configuration.

## Dependencies and Integration Points
It depends on STPMIC1 MFD/regmap definitions, platform named IRQs, OF/property APIs, input core, IRQ core, and PM wakeup helpers. Compatible is `st,stpmic1-onkey`.

## Risks and Edge Cases
`power-off-time-sec` accepts only 1 through 16 seconds; zero and out-of-range values fail probe. Both IRQ wake enable calls ignore return values. PMIC register programming happens before input/IRQ registration, so later failures leave configuration changed. IRQ handlers assume the parent IRQ controller has already acknowledged status.

## Test Signals
Test property combinations and boundary values, regmap failures, falling/rising event delivery, wake from suspend by both edges, IRQ wake failure injection, and remove/reprobe after PMIC configuration.
