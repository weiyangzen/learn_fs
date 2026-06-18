<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/hisi_powerkey.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/hisi_powerkey.c

## Purpose
`hisi_powerkey.c` is a Hisilicon HI65xx PMIC power-key platform driver. It reports `KEY_POWER` down/up and toggles `KEY_RESTART` for a long-hold interrupt.

## Important APIs, Types, and Functions
Three ISR functions map named IRQs to input events: `hi65xx_power_press_isr()` reports power down and calls `pm_wakeup_dev_event()`, `hi65xx_power_release_isr()` reports power up and calls `pm_wakeup_event()`, and `hi65xx_restart_toggle_isr()` flips the current `KEY_RESTART` state based on the input key bitmap. `hi65xx_irq_info[]` maps firmware IRQ names `down`, `up`, and `hold 4s` to handlers.

## Control Flow
Probe allocates a devm input device, sets phys/name, advertises `KEY_POWER` and `KEY_RESTART`, loops over the three named IRQs with `platform_get_irq_byname()`, requests them with `devm_request_any_context_irq()` and `IRQF_ONESHOT`, registers input, and enables device wakeup. Runtime event flow is direct IRQ-to-input reporting.

## State and Persistence Behavior
The input key bitmap stores current key states. The restart key is toggled rather than emitted as a press/release pair. No persistent state exists.

## Dependencies and Integration Points
The driver depends on platform IRQ resources, input, PM wake events, and wakeup configuration. Binding is by platform driver name `hi65xx-powerkey`.

## Risks and Test Signals
Risks include long-hold toggle semantics leaving `KEY_RESTART` asserted until the next hold, all IRQs being mandatory, and no explicit remove logic beyond devm cleanup. Tests should cover all three IRQ paths, wake event durations, missing named IRQs, registration failure, and repeated hold toggles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/hisi_powerkey.c -->
