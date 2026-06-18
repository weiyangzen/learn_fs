# sources/distributed-fs/ceph-client/drivers/hwmon/sch56xx-common.c

Purpose: shared infrastructure for SCH5627/SCH5636. It scans Super-I/O ports, creates the matching platform device, implements mailbox virtual-register access, exposes a regmap bus wrapper, and registers an optional watchdog.

Important APIs/types/functions: exported register helpers include `sch56xx_read_virtual_reg()`, `write_virtual_reg()`, `read_virtual_reg16()`, `read_virtual_reg12()`, `sch56xx_regmap_read16()`, `write16()`, `devm_regmap_init_sch56xx()`, and `sch56xx_watchdog_register()`. Internal helpers handle Super-I/O enter/select/exit and mailbox command polling.

Control flow: module init probes 0x4e then 0x2e, selects embedded controller logical device, validates enable/address, checks ACPI resource conflicts, and registers a platform device. Virtual-register commands write a request packet into mailbox registers, trigger execution, poll interrupt/source and EC-to-host completion, then read or write payload.

State and persistence: global `sch56xx_pdev` tracks the created platform device. Regmap contexts hold address and shared lock. Watchdog state caches control/output/preset registers and persists as a devm watchdog device.

Dependencies/integration: raw I/O port access, ACPI resource conflict checks, platform bus, regmap, watchdog core, mutexes.

Risks: mailbox timing is empirical and uses busy plus sleep polling. Raw I/O ordering must match vendor app notes. `devm_regmap_init_sch56xx()` checks `reg_bits != 16 && val_bits != 8`, which accepts some invalid configs if only one field differs. Watchdog cannot truly stop, only disables reset output.

Test signals: Super-I/O detection at both base ports, unsupported/disabled/no-address cases, mailbox read/write retries, regmap read/write16, watchdog start/stop/ping/timeout, and ACPI conflict handling.
