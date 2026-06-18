# sources/distributed-fs/ceph-client/drivers/input/misc/rk805-pwrkey.c

## Purpose
`rk805-pwrkey.c` is a simple Rockchip RK805 PMIC power-key driver. It maps one falling interrupt to `KEY_POWER` press and one rising interrupt to release.

## Important APIs, Types, and Functions
`pwrkey_fall_irq()` reports `KEY_POWER=1`; `pwrkey_rise_irq()` reports `KEY_POWER=0`. `rk805_pwrkey_probe()` allocates the input device, obtains two platform IRQs, requests them with `devm_request_any_context_irq()`, registers input, stores driver data, and marks the device wake-capable.

## Control Flow
Probe creates `rk805 pwrkey`, enables `EV_KEY/KEY_POWER`, obtains IRQ 0 and IRQ 1, requests falling and rising handlers with edge flags and `IRQF_ONESHOT`, registers input, and calls `device_init_wakeup()`. Runtime IRQ flow only reports the corresponding key state and syncs.

## State and Persistence Behavior
State is entirely input-core and IRQ-core state; no custom structure is allocated. Wake capability persists in the device core.

## Dependencies and Integration Points
The driver depends on platform IRQ resources from the RK805 MFD, input core, IRQ core, and platform device binding `rk805-pwrkey`.

## Risks and Edge Cases
No suspend/resume ops explicitly enable IRQ wake despite `device_init_wakeup()`, so wake behavior relies on parent IRQ configuration. Both IRQs are requested against `&pwr->dev` rather than `&pdev->dev`, which ties devm cleanup to the input device lifecycle. The driver assumes IRQ ordering is fall then rise.

## Test Signals
Test IRQ ordering, press/release event delivery, any-context IRQ behavior, wake capability on target boards, error handling for missing IRQs, and repeated probe/remove.
