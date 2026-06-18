# sources/distributed-fs/ceph-client/drivers/input/misc/retu-pwrbutton.c

## Purpose
`retu-pwrbutton.c` exposes the Nokia Retu PMIC power button as `KEY_POWER`. It reads Retu status in a threaded IRQ and reports the inverted `PWRONX` status bit.

## Important APIs, Types, and Functions
The key handler is `retu_pwrbutton_irq()`, which retrieves `struct retu_dev` from input driver data, reads `RETU_REG_STATUS`, tests `RETU_STATUS_PWRONX`, and reports key state. `retu_pwrbutton_probe()` gets the platform IRQ, allocates an input device, stores the Retu parent data, requests a threaded IRQ, and registers input.

## Control Flow
Probe validates the IRQ and parent input resources, sets `EV_KEY/KEY_POWER`, registers a threaded IRQ with `IRQF_ONESHOT`, then registers the input device. On each interrupt, the handler reads the PMIC status register, reports pressed when `PWRONX` is clear, and syncs.

## State and Persistence Behavior
There is no custom runtime state object. The input device holds driver data pointing to the parent Retu MFD object. Hardware state is read-only from this driver.

## Dependencies and Integration Points
It depends on the Retu MFD API, platform child enumeration, IRQ core, and input core. It integrates with userspace through evdev `KEY_POWER`.

## Risks and Edge Cases
`retu_pwrbutton_irq()` does not check `retu_read()` errors separately, so a failed read could be interpreted as a button state depending on return value. There is no wakeup configuration in this file. The driver assumes the parent Retu object is valid for the input device lifetime.

## Test Signals
Test press/release status-bit transitions, Retu read errors, IRQ request failure, input registration failure, module removal, and userspace power-button event observation.
