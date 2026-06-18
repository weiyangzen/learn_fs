<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/lochnagar-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/lochnagar-regulator.c

Purpose: regulator driver for Cirrus Logic Lochnagar board rails, including MICVDD, MIC1VDD, MIC2VDD, and VDDCORE.

Important APIs/types/functions: descriptor table `lochnagar_regulators[]`, linear ranges for MICVDD and VDDCORE, custom micbias enable/disable wrappers, and `lochnagar_micbias_of_parse()` for `cirrus,micbias-input` routing.

Control flow: platform probe selects a descriptor from OF match data, fills config with parent regmap and `struct lochnagar`, then registers one regulator. MICBIAS enable/disable operations update register bits under `analogue_config_lock` and call `lochnagar_update_config()`.

State and persistence: state lives in Lochnagar hardware registers and parent MFD locks. The regulator driver stores no private allocation.

Dependencies and integration: depends on Lochnagar MFD core and register headers, OF compatible strings per regulator, regmap helpers, and the regulator framework.

Risks and test signals: micbias input parsing writes a shifted raw DT value without range validation against the mask width. Register changes are tied to parent analogue config synchronization. Test each compatible, voltage range mapping, micbias GPIO/source routing, lock usage, and update-config failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/lochnagar-regulator.c -->
