# sources/distributed-fs/ceph-client/drivers/input/misc/88pm860x_onkey.c

## Purpose

This platform child driver reports Marvell 88PM860x PMIC ONKEY status as a Linux power key. It reads PMIC status over I2C, re-enables long-onkey detection after interrupts, and participates in PMIC wakeup flag management.

## Important APIs, Types, and Functions

`struct pm860x_onkey_info` stores input, parent chip, selected I2C client, device, and IRQ. `pm860x_onkey_handler()` reads `PM8607_STATUS_2`, masks `ONKEY_STATUS`, reports `KEY_POWER`, syncs, and sets `LONG_ONKEY_EN` in `PM8607_WAKEUP`. Probe selects the correct PM8607 I2C client or companion, allocates input, registers it, requests a threaded IRQ, stores driver data, and enables wakeup. PM hooks manipulate `chip->wakeup_flag`.

## Control Flow

The MFD child probe gets its IRQ, chooses the PMIC I2C endpoint based on chip ID, exposes an input power key, registers input, then requests the IRQ. On every ONKEY interrupt, it samples current status and reports that state. Suspend/resume do not touch IRQs directly; they set or clear the parent chip wakeup flag bit for `PM8607_IRQ_ONKEY` when device wakeup is enabled.

## State and Persistence Behavior

Driver-local persistent state is resource pointers only. The parent chip's `wakeup_flag` is persistent cross-device PM state. Long-onkey detection is programmed after each interrupt rather than once at probe, implying PMIC hardware may clear or require refresh.

## Dependencies and Integration Points

It depends on the 88PM860x MFD core, PMIC I2C register helpers, platform IRQs, input power-key events, and parent PM wakeup flag handling.

## Risks and Edge Cases

`pm860x_reg_read()` return value is masked without checking for negative errors, so I2C failures can be reported as key states. Input is registered before IRQ request; if IRQ request fails, devm cleanup removes the input later but the device may briefly exist. Wakeup flag manipulation assumes no concurrent unsynchronized updates from sibling drivers.

## Test Signals

Test chip/client selection, status read failures, press/release reporting, long-onkey re-enable writes, IRQ request failure after input registration, wakeup flag set/clear, and module unload with active PMIC child devices.
