# sources/distributed-fs/ceph-client/drivers/regulator/aat2870-regulator.c

Purpose: registers four AnalogicTech AAT2870 LDO regulators as platform children of the AAT2870 MFD core. It implements voltage selector, enable, disable, and status operations through MFD-provided read/update callbacks.

Important APIs and data: `struct aat2870_regulator` combines an `aat2870_data` pointer, descriptor, and computed enable/voltage register fields. `aat2870_ldo_ops` provides table voltage listing, ascending voltage mapping, selector set/get, enable/disable, and is-enabled. `aat2870_ldo_voltages[]` is a 16-entry table from 1.2 V to 3.3 V. `aat2870_get_regulator()` maps platform ID to descriptor and register bit layout. `aat2870_regulator_probe()` registers the selected LDO.

Control flow: each platform device has an ID corresponding to LDOA-D. Probe resolves the static descriptor, fills register addresses, shifts, and masks based on ID, stores the parent MFD data pointer, applies optional platform init data, and calls `devm_regulator_register()`. Init uses `subsys_initcall()` to register the platform driver.

State and persistence: descriptor entries are static and are mutated by `aat2870_get_regulator()` with per-ID register fields and parent data. This is acceptable for one device set but not naturally multi-instance safe. Hardware state lives in AAT2870 registers.

Dependencies and integration: depends on `MFD_AAT2870_CORE`, platform child IDs, parent `aat2870_data` callbacks, regulator core, and board platform data for constraints.

Risks: static descriptor mutation could cross-contaminate multiple AAT2870 instances. Invalid platform IDs fail probe. The voltage register pair and nibble shift math must match hardware layout. No OF matching is present; integration is MFD/platform-data oriented.

Test signals: probe LDOA-D IDs, invalid ID rejection, selector set/get for upper and lower nibbles, enable mask per LDO, parent read/update error propagation, voltage table mapping, and multi-instance review if hardware can appear more than once.
