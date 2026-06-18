# sources/distributed-fs/ceph-client/include/linux/pm_wakeirq.h

Purpose: declares helpers for associating a device with a wake IRQ used by PM wakeup handling.

Important APIs and types: APIs include `dev_pm_set_wake_irq()`, dedicated wake IRQ variants including reverse ordering, `dev_pm_clear_wake_irq()`, and devres-managed `devm_pm_set_wake_irq()`. The actual `struct wake_irq` is opaque and maintained by the PM core.

Control flow: a driver discovers its normal or dedicated wake interrupt, registers it with the device PM core, then clears it on removal or relies on devm cleanup. During suspend/resume, PM core can enable the IRQ for wakeup and coordinate ordering relative to runtime/system PM callbacks.

State and persistence: wake IRQ association is runtime device PM state tied to `struct device`; no persistent data is defined here.

Dependencies and integration points: integrates with `struct device`, IRQ wakeup configuration, PM sleep/runtime flows, and wakeup-source state. With `CONFIG_PM` disabled, all helpers are successful no-ops.

Risks and test signals: risks include wrong IRQ lifetime, registering a shared functional IRQ as a dedicated wake IRQ, clear/register imbalance, and relying on wake IRQ behavior in PM-disabled builds. Test suspend wake from the device, probe/remove cleanup, runtime suspend with wake IRQs, IRQ wake enable failure handling, and PM-disabled compilation.
