# sources/distributed-fs/ceph-client/drivers/regulator/max77675-regulator.c

Purpose: implements the MAX77675 four-channel SIMO buck-boost regulator. It configures global chip behavior from DT, registers present SBB child regulators, supports active discharge, and reports channel/thermal error flags.

Important APIs/types/functions: `struct max77675_regulator` stores regmap, parsed global config, and per-SBB FPS/slew settings. `max77675_parse_config()` validates global DT properties; `max77675_apply_config()` writes global registers; `max77675_of_parse_cb()` parses per-regulator `adi,fps-slot` and `adi,fixed-slew-rate`; `max77675_get_error_flags()` maps global interrupt bits to regulator errors.

Control flow: I2C probe initializes regmap, logs reset/fault events, parses and applies global config, locates the `regulators` subnode, and registers only SBB child nodes found in DT.

State and persistence: parsed global/per-regulator settings are kept in driver memory and programmed into hardware. Error and status registers are volatile under maple cache.

Dependencies and integration: depends on I2C, regmap with volatile-register policy, OF child-node parsing, bitfield helpers, and regulator core.

Risks and test signals: duplicate macro definitions and many DT property encodings raise maintenance risk. Missing individual SBB nodes are warnings, not fatal; missing `regulators` is fatal. Test invalid enum properties, fixed versus DVS slew selection, FPS default readback, per-channel fault flags, thermal alarm mapping, and partial regulator registration.
