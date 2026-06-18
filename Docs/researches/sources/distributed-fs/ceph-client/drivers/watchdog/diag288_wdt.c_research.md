# sources/distributed-fs/ceph-client/drivers/watchdog/diag288_wdt.c

## Purpose
`diag288_wdt.c` implements the IBM s390 diag 288 watchdog for z/VM and LPAR. On expiration it requests a CP command under z/VM or a system restart under LPAR.

## Important APIs, types, and functions
The static `wdt_dev` is registered only on CPUs with `S390_CPU_FEATURE_D288`. Operations are `wdt_start`, `wdt_stop`, `wdt_ping`, and `wdt_set_timeout`. `diag288` wraps `__diag288` with diagnostic accounting, while `diag288_str` copies the z/VM command, converts it to EBCDIC uppercase, and passes its physical address.

## Control Flow
Init applies nowayout, allocates `cmd_buf` only when running under z/VM, and registers the watchdog. Start chooses `WDT_FUNC_INIT` with optional conceal on z/VM or `LPARWDT_RESTART` on LPAR. Ping repeats init on z/VM and uses `WDT_FUNC_CHANGE` on LPAR. Stop cancels diag 288. Set-timeout updates the core timeout then pings.

## State and Persistence
Runtime state includes command buffer, command string module parameter, conceal flag, nowayout, and the hypervisor's watchdog configuration. The watchdog action persists in firmware/hypervisor until changed or canceled.

## Dependencies and Integration Points
The driver integrates with s390 machine detection, diag 288 assembly helpers, EBCDIC conversion utilities, diagnostic statistics, and the watchdog core.

## Risks and Test Signals
Risks include z/VM command truncation/conversion, physical address validity of the command buffer, different retrigger semantics between z/VM and LPAR, and nowayout preventing cancel. Tests should cover z/VM and LPAR paths, conceal option, invalid long command handling, timeout min/max, feature-gated module loading, and diag error propagation.
