<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/da9063_onkey.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/da9063_onkey.c

## Purpose
`da9063_onkey.c` supports the ONKEY blocks in Dialog DA9063, DA9062, and DA9061-class PMICs. It reports `KEY_POWER`, handles short-versus-long press behavior, optionally disables long key-power reporting via firmware property, and can command PMIC shutdown when a key-reset fault is observed.

## Important APIs, Types, and Functions
`struct da906x_chip_config` abstracts register and bit differences between DA9063 and DA9062 variants. `struct da9063_onkey` stores delayed work, input device, regmap, config, physical path, and whether `KEY_POWER` long-press reporting is enabled. `da9063_onkey_irq_handler()` classifies presses; `da9063_poll_on()` polls for release, unlocks the key-delay latch, reports release, checks the fault log for key reset, clears it, and writes the shutdown register when needed.

## Control Flow
Probe allocates state, selects chip config from OF match data, gets the parent regmap, reads `dlg,disable-key-power`, allocates input, sets `KEY_POWER`, creates auto-cancel delayed work, gets the `ONKEY` IRQ, requests a low-triggered oneshot threaded IRQ, configures the IRQ as a wake source when possible, and registers input. On IRQ, if long-press reporting is enabled and the nonkey status bit is set, it reports press and starts immediate polling. Otherwise it emits a press-release pair for a short press.

## State and Persistence Behavior
State is held in regmap-controlled PMIC status/control registers and transient delayed work. Wake IRQ configuration persists only for device lifetime. Key reset handling mutates the PMIC fault log and shutdown control register.

## Dependencies and Integration Points
The driver depends on DA9063/DA9062 MFD register definitions, regmap, firmware properties, OF compatibles `dlg,da9063-onkey` and `dlg,da9062-onkey`, input, workqueues, threaded IRQs, and `pm_wakeirq` helpers.

## Risks and Test Signals
Risks include misconfigured match data, failed unlock of nonkey latch, polling forever after read errors, and unexpected PMIC shutdown if the fault-log bit is stale or misinterpreted. Tests should cover variant register mappings, disabled-key-power short-press behavior, long-press press/release polling, wake IRQ setup failure tolerance, fault-log clear and shutdown path, and work autocancel on driver removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/da9063_onkey.c -->
