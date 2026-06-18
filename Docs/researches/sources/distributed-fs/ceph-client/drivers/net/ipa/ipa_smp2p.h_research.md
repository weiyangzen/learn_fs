# sources/distributed-fs/ceph-client/drivers/net/ipa/ipa_smp2p.h

Purpose: declares the SMP2P lifecycle and control APIs for top-level IPA probe/remove and modem crash paths.

Important APIs: `ipa_smp2p_init()` sets up SMEM state bits and interrupts, with `modem_init` selecting whether the setup-ready IRQ is required. `ipa_smp2p_exit()` tears it down. `ipa_smp2p_irq_disable_setup()` blocks modem-triggered setup. `ipa_smp2p_notify_reset()` resets modem power-state notification bits after crash handling.

Control flow: main probe calls init after table init and before powered config; remove/crash paths disable setup-ready before teardown; modem before-powerup notification calls notify reset.

State/persistence: implementation-owned state is opaque and attached to `ipa->smp2p`.

Dependencies/integration: forward-declares `struct platform_device` and `struct ipa`; uses bool from Linux types.

Risks: callers must pass the correct `modem_init` value from firmware-loader selection. Disabling setup-ready is a teardown interlock, not a full SMP2P shutdown.

Test signals: probe succeeds with both AP-loaded and modem-loaded GSI firmware modes, setup-ready IRQ exists only when required, and reset notification is called during modem SSR boot sequencing.
