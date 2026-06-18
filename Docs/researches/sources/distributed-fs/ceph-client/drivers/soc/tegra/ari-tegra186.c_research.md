# sources/distributed-fs/ceph-client/drivers/soc/tegra/ari-tegra186.c

## Purpose

`ari-tegra186.c` registers a panic notifier for Tegra186 that reads uncore machine-check registers through firmware SMC calls and logs pending SError/MCA state during panic.

## Important APIs, Types, and Functions

`read_uncore_mca()` wraps `arm_smccc_smc()` using `SMC_SIP_INVOKE_MCE | MCE_SMC_READ_MCA`. `tegra186_ari_panic_handler()` loops over `bank_names[]` and prints status, address, and misc registers when `SERR_STATUS_VAL` is set. `tegra186_ari_panic_nb` is registered by `tegra186_ari_init()` using `atomic_notifier_chain_register()` if the machine is compatible with `"nvidia,tegra186"`.

## Control Flow

At early init, Tegra186 systems register the panic notifier. During panic, the handler reads the status subindex for each uncore MCA bank. Banks with valid SError status trigger additional reads of address, MSC1, and MSC2 subindices and emit `pr_crit()` diagnostics.

## State and Persistence Behavior

The file keeps only the static notifier and bank-name table. It does not clear MCA state or persist logs beyond the kernel console/log buffer.

## Dependencies and Integration Points

It depends on ARM SMCCC, the Tegra186 firmware MCE SMC ABI, OF machine matching, and the kernel panic notifier chain. It integrates with platform crash diagnostics rather than normal error recovery.

## Risks and Edge Cases

SMC return status is not checked; `res.a2` is trusted. Panic notifier context is fragile, so calls must not sleep. If firmware ABI changes, decoded values can be wrong. Only instance 0 is read for all banks.

## Test Signals

On Tegra186, trigger controlled panic paths with injected MCA/SError state and verify bank diagnostics appear. Confirm non-Tegra186 systems do not register the notifier.
