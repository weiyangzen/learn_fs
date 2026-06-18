# sources/distributed-fs/ceph-client/drivers/reset/starfive/reset-starfive-jh71x0.c

Purpose: common StarFive JH71x0 reset controller implementation for assert/status register banks with optional custom asserted-status polarity.

Important APIs/types/functions: `jh71x0_reset` stores rcdev, spinlock, assert/status bases, and optional asserted table. `jh71x0_reset_update()` RMWs assert bits and polls the status bit with `readl_poll_timeout_atomic()`. `.reset` asserts then deasserts. `reset_starfive_jh71x0_register()` exports common registration.

Control flow: SoC front-ends call the export with register bases and reset count. Runtime assert/deassert holds a spinlock around RMW and status polling.

State and persistence: register bits hold reset state; software tracks bases and status polarity. Device-managed registration owns lifetime.

Dependencies and integration: MMIO accessors, atomic polling, spinlocks, reset framework, exported symbol for SoC drivers.

Risks and test signals: polling while the associated clock is gated can time out; code comments identify this risk. Test timeout behavior, concurrent reset operations, asserted-table and default polarity, and reset pulse sequencing.
