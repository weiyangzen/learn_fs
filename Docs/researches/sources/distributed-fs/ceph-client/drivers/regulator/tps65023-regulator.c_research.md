# sources/distributed-fs/ceph-client/drivers/regulator/tps65023-regulator.c

Purpose: I2C regulator driver for TPS65020/TPS65021/TPS65023 PMICs with three DCDC regulators and two LDOs.

Important APIs/types/functions: `struct tps_pmic` holds registered rdevs, chip-specific descriptor data, and regmap. `struct tps_driver_data` selects descriptor arrays and identifies the adjustable core DCDC. Macros build DCDC and LDO descriptors from voltage tables. DCDC ops restrict voltage changes to the chip-specific core regulator; LDO ops use generic regmap selector helpers.

Control flow: probe allocates PMIC state, chooses driver data from I2C ID, initializes regmap, registers five regulators using optional platform init data array, stores client data, then clears `CORE_ADJ` so output voltage is controlled through I2C. Non-core DCDCs report selector 0 and reject set-voltage requests because they are fixed rails on those variants.

State and persistence: register state lives in the PMIC; the driver keeps descriptor selection and rdev pointers. Voltage changes for DCDC use `DEF_CORE` plus the GO bit in `CON_CTRL2`; enables use `REG_CTRL`.

Dependencies and integration points: I2C, regmap, regulator core, OF/I2C device IDs, and optional legacy platform init data.

Risks: OF match data exists but probe uses `i2c_client_get_device_id()` driver data, so ID table matching must be correct for OF-created clients. `regmap_update_bits` enabling I2C adjustment is not checked. Platform init data is indexed by regulator order.

Test signals: each chip variant, core vs fixed DCDC set-voltage behavior, GO-bit application, LDO selector masks, init-data indexing, and error injection in registration/regmap init.
