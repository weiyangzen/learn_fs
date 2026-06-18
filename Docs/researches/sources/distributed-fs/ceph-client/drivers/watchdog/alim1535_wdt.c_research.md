# sources/distributed-fs/ceph-client/drivers/watchdog/alim1535_wdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/alim1535_wdt.c` is a legacy miscdevice watchdog driver for the ALi M1535 PMU watchdog associated with the ALi 7101 PMU. It scans PCI devices, programs watchdog bits in PCI config register `0xCC`, and exposes `/dev/watchdog` ioctls. The complete 450-line source was read for this report.

## Important APIs, Types, and Functions

Module parameters are `timeout` and `nowayout`. Hardware helpers are `ali_start()`, `ali_stop()`, `ali_keepalive()`, and `ali_settimer()`. Userspace interface functions are `ali_write()`, `ali_ioctl()`, `ali_open()`, and `ali_release()`. System and module lifecycle functions are `ali_notify_sys()`, `ali_find_watchdog()`, `watchdog_init()`, and `watchdog_exit()`. State includes `ali_is_open`, `ali_expect_release`, `ali_pci`, `ali_timeout_bits`, and `ali_lock`.

## Control Flow

Init scans for an ALi bridge and 7101 PMU, enables the PMU PCI device, clears/reset watchdog monitor bits, validates timeout, computes encoded timeout bits, registers a reboot notifier, and registers `/dev/watchdog`. Open starts the watchdog. Writes optionally set magic close and restart the timer. Ioctls expose status, enable/disable, keepalive, set/get timeout. The reboot notifier stops on `SYS_DOWN` or `SYS_HALT`. Exit stops hardware, deregisters miscdevice/notifier, and releases the PCI device reference.

## State and Persistence Behavior

The encoded timeout is cached in `ali_timeout_bits`; hardware state lives in PCI config space register `0xCC`. `ali_lock` serializes config-space updates. There is no disk persistence. The driver keeps the watchdog running after unexpected close.

## Dependencies and Integration Points

It depends on PCI config access, legacy miscdevice watchdog ABI, reboot notifier API, and watchdog ioctl definitions. Kconfig `ALIM1535_WDT` depends on x86/PCI and maps to `alim1535_wdt.o`.

## Risks and Edge Cases

The driver does not register a real `pci_driver`; it scans devices manually and exports a PCI table only for module metadata. Timeout encoding has multiple ranges and rejects negative or >=18000 seconds. `nowayout` is declared but not used to pin the module on open, unlike some legacy drivers. Failure paths after `pci_enable_device()` rely on later `pci_dev_put()` but do not disable the device.

## Test Signals

Test PCI detection absence, timeout encoding boundaries, config register bit masking, spinlock-covered start/stop races, magic close and unexpected close behavior, reboot notifier stop, and module unload cleanup.
