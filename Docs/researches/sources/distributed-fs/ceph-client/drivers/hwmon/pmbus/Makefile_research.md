# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/Makefile

Purpose: object selection for PMBus core, generic PMBus, and chip-specific PMBus hwmon drivers.

Important entries: `obj-$(CONFIG_PMBUS) += pmbus_core.o` builds the common PMBus implementation. The listed work-item drivers map from config symbols to objects such as `acbel-fsg032.o`, `adm1266.o`, `adm1275.o`, `adp1050.o`, `aps-379.o`, `bel-pfe.o`, `bpa-rs600.o`, `crps.o`, `delta-ahe50dc-fan.o`, `dps920ab.o`, `fsp-3y.o`, `hac300s.o`, `ibm-cffps.o`, and `ina233.o`.

Control flow: Kconfig symbol states determine whether each object is omitted, built-in, or built as a module. Most chip objects are single-source modules that call into `pmbus_core`.

State and persistence: no runtime state; this is build metadata.

Dependencies and integration: pairs with `pmbus/Kconfig` and parent hwmon Makefiles. The file must stay synchronized with config names and source file names so module builds resolve correctly.

Risks: stale object lines lead to selected drivers not building or renamed source files not being referenced. Common core must be available for every chip module importing namespace `PMBUS`.

Test signals: build coverage with each listed `CONFIG_SENSORS_*` as module and built-in, `modpost` namespace import resolution, and generated module filenames.
