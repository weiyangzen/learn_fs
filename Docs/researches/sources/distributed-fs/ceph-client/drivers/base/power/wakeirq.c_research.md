# sources/distributed-fs/ceph-client/drivers/base/power/wakeirq.c

## Purpose
This file manages wake IRQ attachment for devices, including normal device IRQs used as wake sources and dedicated threaded wake IRQs used to resume runtime-suspended devices or abort system suspend.

## Important APIs, Types, And Functions
Exports include `dev_pm_set_wake_irq()`, `dev_pm_clear_wake_irq()`, `devm_pm_set_wake_irq()`, `dev_pm_set_dedicated_wake_irq()`, and `dev_pm_set_dedicated_wake_irq_reverse()`. Runtime/system PM helpers include `dev_pm_enable_wake_irq_check()`, `dev_pm_disable_wake_irq_check()`, `dev_pm_enable_wake_irq_complete()`, `dev_pm_arm_wake_irq()`, and `dev_pm_disarm_wake_irq()`. Dedicated IRQ handling is done by `handle_threaded_wake_irq()`.

## Control Flow And State
`dev_pm_attach_wake_irq()` stores a `struct wake_irq` in `dev->power.wakeirq` under `dev->power.lock` and attaches it to the device wakeup source when present. Non-dedicated wake IRQs allocate only metadata. Dedicated wake IRQs allocate a name, set `IRQ_DISABLE_UNLAZY`, request a threaded IRQ with `IRQF_ONESHOT | IRQF_NO_AUTOEN`, then mark allocation and optional reverse-order status bits. Runtime suspend calls enable helpers before or after callbacks depending on `WAKE_IRQ_DEDICATED_REVERSE`; resume calls disable helpers. System sleep arming uses `device_may_wakeup()` to call `enable_irq_wake()` and possibly enable a disabled dedicated IRQ.

## Dependencies And Integration Points
This code depends on IRQ core APIs, runtime PM, wakeup-source attachment in `wakeup.c`, and the runtime state machine in `runtime.c`. The threaded handler calls `pm_wakeup_event()` if the IRQ is configured for wakeup, otherwise synchronously resumes the device via `pm_runtime_resume()`.

## Risks And Test Signals
Risks include double attachment, wrong reverse-order selection, unbalanced enable/disable for dedicated IRQs, freeing IRQs while still attached, wake IRQs without wakeup capability, and lost device IRQ semantics after wake-only interrupts. Test signals include suspend/resume with `device_may_wakeup` toggles, runtime suspend/resume ordering checks, threaded wake IRQ resume warnings, IRQ wake enable counts, and devres cleanup on probe failure/remove.
