<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/da9052_onkey.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/da9052_onkey.c

## Purpose
`da9052_onkey.c` is a platform child driver for the Dialog DA9052 PMIC ONKEY pin. It exposes a simple input device named `da9052-onkey` that reports `KEY_POWER` press and release events.

## Important APIs, Types, and Functions
`struct da9052_onkey` stores the parent MFD pointer, input device, and delayed work. `da9052_onkey_query()` reads `DA9052_STATUS_A_REG` through the DA9052 MFD API and derives the pressed state from `DA9052_STATUSA_NONKEY`. `da9052_onkey_irq()` calls the query routine from the PMIC IRQ path, while `da9052_onkey_work()` polls later to synthesize release detection.

## Control Flow
Probe obtains the parent `struct da9052` with `dev_get_drvdata()`, allocates private data and an input device, initializes delayed work, declares `EV_KEY/KEY_POWER`, requests `DA9052_IRQ_NONKEY` through `da9052_request_irq()`, and registers the input device. The IRQ only fires on assertion, so the handler reads the current status, reports it, and if still pressed schedules another query after 50 ms. Remove frees the PMIC IRQ, cancels delayed work, unregisters input, and frees private memory.

## State and Persistence Behavior
The only durable state is the delayed polling loop while the button remains pressed. The input core carries the current key state. No state persists across remove or reboot.

## Dependencies and Integration Points
This driver depends on the DA9052 MFD core/register definitions, Linux input, platform bus binding `platform:da9052-onkey`, workqueues, and PMIC interrupt services. It assumes the PMIC status bit is authoritative for deassertion because the hardware does not emit a release IRQ.

## Risks and Test Signals
Important risks are missed release if register reads fail, polling churn while a key is held, and cleanup ordering around delayed work and IRQ teardown. Tests should exercise press/release through mocked DA9052 status transitions, register-read errors, probe failures at each allocation/request step, and remove while delayed work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/da9052_onkey.c -->
