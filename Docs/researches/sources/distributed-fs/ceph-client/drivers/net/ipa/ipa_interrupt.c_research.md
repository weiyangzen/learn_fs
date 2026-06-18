# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_interrupt.c

Purpose: manages the IPA hardware interrupt line, interrupt masks, TX_SUSPEND endpoint bits, wake IRQ registration, and threaded interrupt dispatch for IPA-specific events distinct from GSI events.

Important APIs/functions: `ipa_interrupt_init()` allocates the interrupt wrapper after resolving the `"ipa"` IRQ. `ipa_interrupt_config()` allocates endpoint suspend bitmap, disables all IPA IRQ types, requests the threaded IRQ, and configures device wakeup/wakeirq. `ipa_interrupt_enable()`/`disable()` update the IPA IRQ mask register. `ipa_interrupt_suspend_enable()`/`disable()` toggle per-endpoint TX_SUSPEND bits and enable the global TX_SUSPEND IRQ only while needed. `ipa_interrupt_simulate_suspend()` lets endpoint code invoke the suspend path for an aggregation hardware quirk.

Control flow: `ipa_isr_thread()` takes a runtime PM reference, reads `IPA_IRQ_STTS`, intersects pending bits with the enabled mask, and processes each set interrupt until no enabled pending bits remain. UC interrupts are cleared before calling `ipa_uc_interrupt_handler()`. TX_SUSPEND clears endpoint suspend status via `IRQ_SUSPEND_INFO`/`IRQ_SUSPEND_CLR` before clearing the IRQ. Disabled pending interrupts are logged at debug level and cleared.

State/persistence: `struct ipa_interrupt` persists IRQ number, enabled mask, per-endpoint suspend bitmap, and back pointer to `ipa`. Wakeup state is registered with the device until deconfig.

Dependencies/integration: depends on register definitions, runtime PM, Linux wakeirq helpers, endpoint availability bitmap, and the IPA microcontroller interrupt handler.

Risks: interrupt handling requires IPA power; PM failures currently warn and still put. The suspend bitmap and hardware bit updates must stay synchronized, especially the transition from zero to one enabled endpoint and back. On IPA v3.0, suspend clear/control behavior differs.

Test signals: IRQ request/wakeirq setup succeeds, UC interrupt tests reach `ipa_uc_interrupt_handler()`, suspend/resume wake works for RX endpoints, and disabled pending interrupts are cleared without storms.
