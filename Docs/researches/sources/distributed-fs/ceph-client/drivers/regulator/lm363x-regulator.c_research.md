<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/lm363x-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/lm363x-regulator.c

Purpose: platform regulator child driver for TI LM3631, LM3632, and LM36274 backlight/biased-display PMIC devices.

Important APIs/types/functions: `lm363x_regulator_desc[]` contains boost and positive/negative/contrast LDO descriptors for multiple chip IDs. `lm363x_regulator_enable_time()` decodes LM3631 enable-time registers. GPIO helpers optionally wire external enable pins for LM3632/LM36274 LDOs and set external-enable bits.

Control flow: probe uses `pdev->id` as an index into the descriptor table, gets the parent `ti_lmu` regmap, optionally acquires nonexclusive enable GPIOs, configures external-enable mode, and registers one regulator.

State and persistence: no per-device mutable state is stored. Enable GPIO ownership is passed to the regulator core. Hardware registers hold voltage, enable, and timing state.

Dependencies and integration: MFD `ti-lmu`, register definitions in `ti-lmu-register.h`, GPIO descriptors, OF matching via descriptor `of_match`, and regulator regmap helpers.

Risks and test signals: `pdev->id` must be valid; there is no explicit bounds check before indexing descriptors. GPIO lifecycle is deliberately non-devm because regulator core owns it. Test with each chip child ID, optional GPIO absence/presence, external-enable write failure, and LM3631 enable-time decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/lm363x-regulator.c -->
