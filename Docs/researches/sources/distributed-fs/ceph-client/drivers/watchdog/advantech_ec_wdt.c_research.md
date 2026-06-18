# sources/distributed-fs/ceph-client/drivers/watchdog/advantech_ec_wdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/advantech_ec_wdt.c` is a watchdog-core driver for Advantech systems with an ITE-based embedded controller. It probes the EC at fixed I/O ports, programs enable and reset delays through EC command/data registers, and registers a `watchdog_device`. The complete 205-line source was read for this report.

## Important APIs, Types, and Functions

Module parameter `timeout` selects the default timeout from `MIN_TIME` to `MAX_TIME`. EC access is serialized by timing helpers `adv_ec_wdt_timing_gate()`, `adv_ec_wdt_outb()`, and `adv_ec_wdt_inb()` to enforce at least `EC_MIN_DELAY` milliseconds between I/O accesses. Watchdog operations are `adv_ec_wdt_ping()`, `adv_ec_wdt_set_timeout()`, `adv_ec_wdt_start()`, and `adv_ec_wdt_stop()`. The global `adv_ec_wdt_dev` contains info, ops, min/max/default timeout. Probe and registration flow through `adv_ec_wdt_init()`, `adv_ec_wdt_probe()`, and `adv_ec_wdt_exit()` using `struct isa_driver`.

## Control Flow

Module init temporarily reserves the EC I/O range, sends `EC_CMD_EC_PROBE`, reads a magic value, releases the range, and only registers the ISA driver if the EC responds with `EC_MAGIC`. Probe then reserves the ports with devm, initializes timeout, arranges stop-on-reboot and stop-on-unregister, and registers the watchdog. Starting sets the timeout then writes `EC_CMD_WDT_START`; ping writes `EC_CMD_WDT_RESET`; stop writes `EC_CMD_WDT_STOP`.

## State and Persistence Behavior

Driver state is mostly in the singleton `watchdog_device` and `ec_timestamp` timing gate. Hardware timeout state is stored in EC registers with a 100 ms base. The driver clears BIOS-provided enable delay before writing reset delay, so probe/start normalizes EC timing state.

## Dependencies and Integration Points

It depends on ISA bus API, fixed I/O ports `0x299/0x29a`, watchdog core, module parameters, and `devm_watchdog_register_device()`. Kconfig selects `ISA_BUS_API` and `WATCHDOG_CORE`; Makefile builds `advantech_ec_wdt.o`.

## Risks and Edge Cases

The driver is for a specific EC family; fixed-port probing could conflict if another device decodes the range. EC access requires the timing gate; bypassing it risks missed commands. There is no explicit nowayout module parameter in this file, so policy follows watchdog core defaults and configuration rather than a local parameter. The singleton `watchdog_device` assumes one device instance.

## Test Signals

Useful tests include EC probe success/failure, timeout min/max validation, command ordering on start/stop/ping, delay enforcement between I/O accesses, stop-on-reboot behavior, and module unload cleanup.
