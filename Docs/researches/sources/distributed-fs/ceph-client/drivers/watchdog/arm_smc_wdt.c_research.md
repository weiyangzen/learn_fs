# sources/distributed-fs/ceph-client/drivers/watchdog/arm_smc_wdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/arm_smc_wdt.c` is a watchdog-core platform driver for watchdogs implemented by ARM EL3 firmware and accessed through Secure Monitor Calls. It abstracts firmware operations such as init, set timeout, enable, pet, and get timeleft into watchdog-core callbacks. The complete 199-line source was read for this report.

## Important APIs, Types, and Functions

`enum smcwd_call` defines firmware subcommands `SMCWD_INIT`, `SMCWD_SET_TIMEOUT`, `SMCWD_ENABLE`, `SMCWD_PET`, and `SMCWD_GET_TIMELEFT`. `smcwd_call()` performs `arm_smccc_smc()` using the SMC function id stored in watchdog driver data and maps PSCI-style return codes to Linux errors. Watchdog operations include `smcwd_ping()`, `smcwd_get_timeleft()`, `smcwd_set_timeout()`, `smcwd_stop()`, and `smcwd_start()`. Probe is `smcwd_probe()`.

## Control Flow

Probe allocates a watchdog device, reads optional DT property `arm,smc-id` or defaults to `0x82003D06`, calls firmware init, chooses ops with or without `get_timeleft` based on firmware support, initializes min/max/default timeout from firmware return registers, applies nowayout and optional module timeout, programs the selected timeout, and registers the watchdog. Start/stop/ping/set/get callbacks are thin SMC wrappers.

## State and Persistence Behavior

The driver stores the SMC function id as watchdog driver data and stores timeout limits in `watchdog_device`. Actual watchdog state lives in secure firmware. Existing running state can be inferred when `SMCWD_GET_TIMELEFT` succeeds during probe.

## Dependencies and Integration Points

It depends on ARM SMCCC, PSCI return-code definitions, OF binding `arm,smc-wdt`, platform devices, and watchdog core. Kconfig requires ARM/ARM64, OF, and `HAVE_ARM_SMCCC`.

## Risks and Edge Cases

The contract with firmware is not self-describing beyond return codes; mismatched argument conventions or non-PSCI error semantics would produce incorrect Linux errors. `get_timeleft` support is optional and probe uses return values to select ops. The `watchdog_ops` structures lack `.owner`, unlike most drivers, which can matter for module reference expectations. Stop-on-reboot/unregister assumes firmware supports disable.

## Test Signals

Test firmware return-code mapping, default and DT-provided SMC ids, missing optional get-timeleft, min/max timeout propagation, timeout module parameter, nowayout behavior, and stop-on-reboot/unregister calls.
