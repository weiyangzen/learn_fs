# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_smp2p.c

Purpose: implements SMP2P communication with the modem for two events: modem-loaded GSI setup readiness and modem queries about AP IPA power state during crash/shutdown scenarios.

Important APIs/functions: `ipa_smp2p_init()` acquires SMEM state bits, installs the `"ipa-clock-query"` IRQ, registers a high-priority panic notifier, and optionally installs `"ipa-setup-ready"` when the modem initializes GSI. `ipa_smp2p_exit()` frees IRQs/notifier and releases any held power reference. `ipa_smp2p_irq_disable_setup()` prevents future setup-ready handling during remove/crash. `ipa_smp2p_notify_reset()` clears notification state for the next modem boot.

Control flow: on clock-query IRQ or panic, `ipa_smp2p_notify()` records whether runtime PM is currently active with `pm_runtime_get_if_active()`, writes the enabled bit, then writes the valid bit for the modem to observe. If the modem loaded GSI firmware, the setup-ready IRQ takes runtime PM, calls `ipa_setup()`, and releases power. On panic, if IPA power is on, UC panic handling is invoked.

State/persistence: `struct ipa_smp2p` stores SMEM states/bits, IRQ numbers, last power_on/notified flags, setup-disabled flag, mutex, and panic notifier. A runtime PM reference may be held after notifying the modem that power is on and is released on reset/exit.

Dependencies/integration: uses Qualcomm SMEM state, platform IRQs, panic notifier chain, runtime PM, `ipa_setup()`, and IPA UC panic handling.

Risks: power notification intentionally can hold a PM reference; failure to reset/release leaks active power. Setup-ready IRQ must be disabled before teardown to avoid concurrent `ipa_setup()`. Panic notifier priority is deliberately high.

Test signals: modem-init boot completes only after setup-ready IRQ, clock-query updates both SMEM bits in order, SSR reset clears bits and releases PM ref, and driver removal cannot race a new setup-ready interrupt.
