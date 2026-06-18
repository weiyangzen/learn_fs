# sources/distributed-fs/ceph-client/drivers/regulator/pbias-regulator.c

Purpose: implements TI OMAP/DRA7 PBIAS regulators for MMC/SIM I/O bias voltage selection through a syscon register.

Important APIs/types/functions: `struct pbias_reg_info` describes enable bits, enable mask, disable value, voltage-mode bit, enable time, name, and two-entry voltage table. `struct pbias_of_data` provides the syscon offset for each compatible. `pbias_matches[]` maps child regulator names to static rail data. `pbias_regulator_voltage_ops` uses table voltage listing and regmap selector/enable helpers.

Control flow: probe matches child regulator nodes with `of_regulator_match()`, allocates one descriptor per matched rail, obtains the syscon regmap from the `syscon` phandle, determines the register offset from match data or a legacy memory resource, then fills and registers a descriptor for each matched child. Each descriptor uses the same syscon offset for voltage select and enable control, with rail-specific masks and disable values.

State and persistence: state is the shared SoC control-module/syscon register. The driver keeps no runtime cache; enable and voltage selection persist as register bits managed by regmap helpers.

Dependencies and integration: depends on OF, syscon regmap lookup, platform resources for legacy offset fallback, regulator framework, and OMAP/DRA7 DT child node names such as `pbias_mmc_omap4`.

Risks and test signals: all matched regulators share a single register offset, so masks must be non-overlapping and correct for the SoC. The descriptor pointer is incremented through a contiguous allocation, making `count` and match iteration correctness important. Legacy offset fallback uses `res->start` and warns. Test all compatibles and offsets, both 3.0 V and 3.3 V tables, each enable/disable mask/value, missing syscon phandle, no child matches, partial child matches, and legacy resource fallback.
