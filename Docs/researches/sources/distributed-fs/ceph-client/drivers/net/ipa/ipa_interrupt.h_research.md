# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_interrupt.h

Purpose: exposes the IPA interrupt lifecycle and control functions to the main, endpoint, power, and microcontroller code.

Important APIs: per-endpoint suspend interrupt control (`ipa_interrupt_suspend_enable`, `ipa_interrupt_suspend_disable`, `ipa_interrupt_simulate_suspend`), IRQ type masking (`ipa_interrupt_enable`, `ipa_interrupt_disable`), Linux IRQ line control (`ipa_interrupt_irq_enable`, `ipa_interrupt_irq_disable`), and lifecycle (`ipa_interrupt_init`, `config`, `deconfig`, `exit`).

Control flow: main probe first calls `ipa_interrupt_init()` before the full IPA object exists, then `ipa_interrupt_config()` after registers/power are available. Endpoint enable/disable drives TX_SUSPEND bits. System suspend/resume uses IRQ line disable/enable around forced runtime PM.

State/persistence: the opaque `struct ipa_interrupt` owns the IRQ, enabled IPA interrupt mask, and endpoint suspend bitmap. The header keeps it opaque so callers cannot mutate state directly.

Dependencies/integration: forward-declares `struct ipa`, `struct platform_device`, `struct ipa_interrupt`, and `enum ipa_irq_id` from the register header.

Risks: callers must distinguish IPA interrupt-type masking from Linux IRQ line enable/disable. Simulated suspend is intentionally a hardware workaround and should not be treated as a generic software event path.

Test signals: probe/deconfig ordering has no use-after-free, endpoint RX enable toggles suspend interrupts, and system suspend does not run the threaded IPA handler while runtime PM is forced off.
