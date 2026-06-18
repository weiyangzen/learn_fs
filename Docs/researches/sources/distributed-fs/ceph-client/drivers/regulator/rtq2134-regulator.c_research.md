# sources/distributed-fs/ceph-client/drivers/regulator/rtq2134-regulator.c

Purpose: registers three Richtek RTQ2134 buck regulators with voltage ranges, enable, active discharge, ramp delay, normal/suspend mode, suspend voltage/enable, and error flags.

Important APIs/types/functions: `struct rtq2134_regulator_desc` extends `regulator_desc` with mode, suspend, and DVS control register metadata. `RTQ2134_BUCK_DESC()` creates the three descriptors. `rtq2134_buck_of_parse_cb()` configures DVS control mode and UV hiccup/shutdown behavior from DT properties. `rtq2134_buck_get_error_flags()` reads chip and per-buck fault records.

Control flow: probe initializes the I2C regmap and registers the three static descriptors. During regulator registration, each descriptor's OF parse callback writes `richtek,use-vsel-dvs` and `richtek,uv-shutdown` policy to hardware. Runtime ops use the extended descriptor fields to update active mode, suspend mode, suspend enable, and suspend voltage registers.

State and persistence: no private state is allocated beyond the regmap. The static descriptors encode all per-rail register addresses. Hardware fault records and policy bits persist until cleared or reset according to chip behavior.

Dependencies and integration: depends on I2C, regmap readable/writeable callbacks, OF regulator child names `buck1` through `buck3`, and regulator linear-range APIs.

Risks and test signals: the custom descriptor is cast from `rdev->desc`, so it relies on `struct regulator_desc` being the first field. `rtq2134_is_accissible_reg` is misspelled but functionally referenced. Tests should cover each buck's register addresses, OF parse side effects, mode/suspend mode mapping, UV policy polarity, ramp table entries including zeros, and fault flag mapping.
