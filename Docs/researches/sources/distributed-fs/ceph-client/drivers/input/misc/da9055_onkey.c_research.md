<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/da9055_onkey.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/da9055_onkey.c

## Purpose
`da9055_onkey.c` is the DA9055 PMIC ONKEY input driver. It registers an input device that reports `KEY_POWER` and compensates for hardware that interrupts on assertion but not release.

## Important APIs, Types, and Functions
`struct da9055_onkey` carries the parent DA9055 handle, input device, and delayed work item. `da9055_onkey_irq()` reports the press immediately, then calls `da9055_onkey_query()`. The query function reads `DA9055_REG_STATUS_A`, masks `DA9055_NOKEY_STS`, reports release when the bit clears, and reschedules itself after 10 ms while the bit remains set.

## Control Flow
Probe gets the platform IRQ named `ONKEY`, allocates private data and a manually managed input device, initializes `EV_KEY/KEY_POWER`, creates delayed work, requests a threaded high-triggered oneshot IRQ, registers the input device, and stores driver data. Error paths free the IRQ, cancel work, and free input. Remove retrieves the virtual IRQ through `regmap_irq_get_virq()`, frees it, cancels delayed work, and unregisters the input device.

## State and Persistence Behavior
The pressed state is maintained by the input core, while release polling is transient delayed work. The driver does not persist configuration or state.

## Dependencies and Integration Points
It integrates with the DA9055 MFD/regmap IRQ infrastructure, Linux platform devices, threaded IRQs, input, and workqueues. It is bound as `platform:da9055-onkey`.

## Risks and Test Signals
Risk areas include inconsistent IRQ number handling between probe and remove, release latency from 10 ms polling, register-read failures that leave state unchanged, and input allocation not being devm-managed. Test signals include high-level IRQ press reporting, delayed release after status clear, repeated polling while held, probe failure cleanup, and remove with pending work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/da9055_onkey.c -->
