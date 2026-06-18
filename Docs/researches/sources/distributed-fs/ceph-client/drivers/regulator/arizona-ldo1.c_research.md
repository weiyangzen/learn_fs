# sources/distributed-fs/ceph-client/drivers/regulator/arizona-ldo1.c

Purpose: registers the LDO1/DCVDD supply for Wolfson/Cirrus Arizona and Madera audio codecs, including variants where LDO1 powers the codec core itself.

Important APIs/types/functions: `struct arizona_ldo1` holds regulator, regmap, default init data, DCVDD consumer supply, and optional enable GPIO. High-current ops `arizona_ldo1_hc_set_voltage_sel()`/`get_voltage_sel()` treat the highest selector as a separate high-power bit. `arizona_ldo1_common_init()` handles shared OF/platform-data/GPIO registration.

Control flow: Arizona and Madera platform drivers allocate state from the parent MFD, choose a descriptor and default constraints based on chip type, parse optional `ldo1` child and `DCVDD-supply`, request `wlf,ldoena`, register the regulator, and update parent flags (`external_dcvdd` or `internal_dcvdd`). Remove releases the manually acquired GPIO.

State and persistence: parent MFD flags record whether DCVDD is external or internal. Regulator settings live in codec regmap registers; enable GPIO state is external hardware state. No persistent file state exists.

Dependencies and integration: depends on Arizona/Madera MFD regmaps, platform data, OF regulator init data, GPIO descriptors, and regulator core. Probe is forced synchronous because codec core power relationships are ordering-sensitive.

Risks and test signals: GPIO is intentionally non-devm and must be put on remove; probe failure after acquisition relies on manual cleanup only through remove not failure unwind. DCVDD external detection depends on phandle and consumer counts. Tests should cover chip-type descriptor selection, high-current selector behavior, `DCVDD-supply` external cases, missing GPIO, and parent flag updates.
