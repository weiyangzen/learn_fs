# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-baytrail.c

## Purpose
Intel Bay Trail DesignWare I2C semaphore support. It detects ACPI-declared sharing with PUNIT firmware and installs IOSF mailbox callbacks to block/unblock PUNIT I2C access around host transfers.

## Important APIs, Types, And Functions
The single exported function is `i2c_dw_baytrail_probe_lock_support(struct dw_i2c_dev *dev)`. It uses `ACPI_HANDLE()`, ACPI method `_SEM`, `iosf_mbi_available()`, `iosf_mbi_block_punit_i2c_access`, and `iosf_mbi_unblock_punit_i2c_access`.

## Control Flow
DesignWare platform probing calls this helper through the semaphore callback table. The helper validates `dev`, requires an ACPI handle, evaluates `_SEM`, ignores controllers where `_SEM` is absent or false, defers if IOSF MBI is unavailable, then marks the controller shared with PUNIT and installs acquire/release lock hooks.

## State And Persistence
Only `dw_i2c_dev` fields are changed: `acquire_lock`, `release_lock`, and `shared_with_punit`. The shared flag changes common runtime PM behavior by skipping clock disable/enable in common PM paths.

## Dependencies And Integration Points
Depends on ACPI firmware, x86 IOSF MBI, the DesignWare platform driver semaphore callback table, and common DesignWare lock hooks.

## Risks
ACPI `_SEM` must correctly describe ownership sharing. If IOSF MBI appears late, probe defers. Incorrect `shared_with_punit` PM handling could leave hardware in an unexpected power state. The helper is intentionally no-op on nonmatching platforms by returning `-ENODEV`.

## Test Signals
Validate `_SEM` absent/false paths, IOSF deferral, successful lock callback installation, runtime PM skip behavior for shared buses, and actual transfer serialization against PUNIT-controlled PMIC access.
