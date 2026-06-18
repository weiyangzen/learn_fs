# sources/distributed-fs/ceph-client/drivers/regulator/rt5133-regulator.c

Purpose: supports Richtek RT5133/RT5133A multi-output LDO PMICs with a base rail, eight LDOs, GPIO outputs, CRC-protected I2C regmap access, and interrupt notifications.

Important APIs/types/functions: `struct rt5133_priv` stores regmap, enable GPIO, regulator devices, GPIO chip, selected chip data, GPIO output cache, and CRC table. `rt5133_regmap_hw_read()` and `rt5133_regmap_hw_write()` implement custom CRC8 SMBus transfers. `rt5133_validate_vendor_info()` selects RT5133 vs RT5133A descriptor tables. `rt5133_intr_handler()` reports LDO over-current and power-good failures through regulator notifiers.

Control flow: probe populates CRC tables, optionally asserts hardware enable, initializes the CRC regmap bus, validates vendor info, performs a software reset, registers base plus eight LDO regulators from the selected descriptor table, applies shutdown policy DT booleans, registers a three-line GPIO chip, clears and unmasks interrupts, and requests a threaded IRQ. Runtime regulator ops are mostly regmap-backed voltage-table and enable operations.

State and persistence: descriptor choice and GPIO output flags are driver state. Hardware registers hold LDO enables, voltage selections, active discharge, base enable, shutdown policy, GPIO control, and interrupt latches. Reset during probe reinitializes device register state.

Dependencies and integration: depends on I2C/SMBus block transfers, CRC8, regmap custom bus, GPIO framework, regulator framework, optional enable GPIO, IRQ line, and OF regulator children.

Risks and test signals: CRC framing and one-byte raw access limits are central risks. The probe logs enable GPIO acquisition errors but continues even for non-deferred failures. Interrupt handling reads three bytes into a `u32`, requiring byte order expectations. Tests should cover CRC mismatch, vendor detection, reset, descriptor-table differences for LDO8, GPIO set/get caching, DT shutdown booleans, IRQ clear/unmask, and notifier delivery.
