# sources/distributed-fs/ceph-client/drivers/char/hw_random/xgene-rng.c

Purpose: AppliedMicro/APM X-Gene SoC RNG driver with alarm interrupt recovery for health-test failures and FRO shutdowns.

Important APIs, types, and functions: `struct xgene_rng_dev`, `xgene_rng_init_internal()`, `xgene_rng_chk_overflow()`, `xgene_rng_irq_handler()`, `xgene_rng_data_present()`, `xgene_rng_data_read()`, `xgene_rng_init()`, probe/remove, and ACPI/OF match tables.

Control flow: probe maps CSR space, requests alarm IRQ, enables optional clock, stores context in a global hwrng, registers it, and enables wakeup. Init sets timer state, logs revision/options, programs refill/alarm/FRO registers, clears status, enables RNG and error masks. IRQ decodes health failures, logs, recovers FRO shutdown by detune/enable, tracks repeated failures over a minute, and clears status. Reads wait for ready then read up to four words and clear ready.

State and persistence: context holds CSR base, IRQ, revision, datum size, failure counter/timestamp, timer, and device. Timer resets failure count after 120 seconds.

Dependencies and integration: platform/ACPI/OF, interrupts, optional clock, timers, wakeup, MMIO, and hwrng.

Risks and test signals: global hwrng is not multi-instance safe; remove disables wakeup but does not explicitly delete `failure_timer`. Tests should cover IRQ recovery, repeated shutdown detection, ready polling, timer expiry, remove after timer setup, clock/IRQ failures, and wakeup setup errors.
