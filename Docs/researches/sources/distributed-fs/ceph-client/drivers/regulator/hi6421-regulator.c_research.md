<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/hi6421-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/hi6421-regulator.c

Purpose: platform regulator driver for the HiSilicon Hi6421 PMIC, registering 21 LDOs, one audio LDO, and six buck regulators from a parent MFD regmap.

Important APIs/types/functions: `struct hi6421_regulator_pdata` holds the enable mutex; `struct hi6421_regulator_info` embeds each descriptor plus mode metadata. Descriptor macros define table, linear, linear-range, and buck variants. Mode handlers implement ECO idle for LDOs and standby for buck regulators.

Control flow: probe retrieves the parent `hi6421_pmic`, allocates shared private data, initializes the mutex, then iterates the static descriptor table and calls `devm_regulator_register()`. Enable operations are serialized by `hi6421_regulator_enable()` before calling the regmap helper.

State and persistence: runtime state is only the mutex-containing private object. Voltage selectors, enable bits, and mode bits persist in PMIC registers according to hardware behavior, not driver-managed storage.

Dependencies and integration: integrates with `linux/mfd/hi6421-pmic.h`, platform-device MFD enumeration, device tree regulator nodes named `regulators`, and standard regulator regmap helpers.

Risks and test signals: enable serialization is hardware-critical because concurrent regulator startup can damage the chip, but the function ignores the return value of `regulator_enable_regmap()`. Mode read/write calls ignore regmap errors. Test signals include registration of all descriptors, DT matching names, serialized enable behavior, ECO threshold selection, and failure handling on regmap write errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/hi6421-regulator.c -->
