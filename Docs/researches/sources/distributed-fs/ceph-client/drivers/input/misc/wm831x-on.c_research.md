# sources/distributed-fs/ceph-client/drivers/input/misc/wm831x-on.c

## Purpose
`wm831x-on.c` reports the WM831x PMIC ON pin as `KEY_POWER`. The PMIC only interrupts on assertion, so the driver polls a status bit until the pin is released.

## Important APIs, Types, and Functions
`struct wm831x_on` stores input device, delayed work, and parent `struct wm831x`. `wm831x_on_irq()` schedules immediate polling. `wm831x_poll_on()` reads `WM831X_ON_PIN_CONTROL`, reports key state from `WM831X_ON_PIN_STS`, and reschedules while pressed. Probe allocates input, requests the mapped WM831x IRQ, and registers input; remove frees IRQ and cancels work.

## Control Flow
Probe resolves the MFD IRQ through `wm831x_irq()`, initializes delayed work, creates an input device with `EV_KEY/KEY_POWER`, requests a rising threaded IRQ, registers input, and stores state. On interrupt, work runs immediately. The worker reads ON-pin status, reports pressed/released, and if still pressed schedules itself again after 100 jiffies. Remove frees the IRQ and cancels delayed work.

## State and Persistence Behavior
Persistent state is the input pointer, parent PMIC pointer, and delayed work item. Key state is stored by input core. Hardware is read-only from this driver.

## Dependencies and Integration Points
Depends on WM831x MFD core/IRQ/register APIs, platform child enumeration, input core, threaded IRQs, and workqueues. It integrates with userspace through a `wm831x_on` input device.

## Risks and Edge Cases
Probe requests the translated IRQ but remove frees `platform_get_irq(pdev, 0)` without translating through `wm831x_irq()`, which can mismatch depending on IRQ mapping. The poll reschedule delay uses raw `100` jiffies rather than `msecs_to_jiffies()`. If status reads fail, the worker logs and continues polling by treating the key as pressed. No wakeup handling is configured.

## Test Signals
Test assertion IRQ, polling until release, register read errors, IRQ mapping/freeing correctness, remove while delayed work is pending, long press behavior, and userspace `KEY_POWER` delivery.
