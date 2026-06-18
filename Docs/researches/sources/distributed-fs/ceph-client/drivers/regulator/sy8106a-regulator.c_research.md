<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/sy8106a-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/sy8106a-regulator.c

Purpose: provides I2C regulator support for the Silergy SY8106A buck converter, focused on voltage programming through the VOUT1 selector register.

Important APIs/types/functions: `sy8106a_regmap_config` defines 8-bit registers and values. `sy8106a_ops` supports selector get/set, voltage transition time, and linear voltage listing; enable/disable are intentionally not implemented. `sy8106a_reg` describes 680 mV to 1.95 V in 10 mV steps, selector mask `0x7f`, and a conservative ramp delay. `sy8106a_i2c_probe()` validates DT fixed voltage and ensures `SY8106A_GO_BIT` is set.

Control flow: probe requires `silergy,fixed-microvolt`, validates it against the supported range, initializes regmap, obtains regulator init data, reads the VOUT selector register, and if GO_BIT is clear writes a selector derived from the fixed voltage plus GO_BIT. It then registers the regulator. Runtime voltage changes operate through `SY8106A_REG_VOUT1_SEL`.

State and persistence: no private state is stored. The hardware selector and GO bit carry runtime state. The regulator may behave like a fixed regulator if GO_BIT is not set, so probe forces I2C-controlled mode.

Dependencies and integration: depends on I2C, OF compatible `silergy,sy8106a`, required `silergy,fixed-microvolt`, regmap, and regulator constraints on the device node.

Risks and test signals: missing fixed-voltage property aborts probe. Enable/disable are unavailable, so consumers must treat it as always-on or externally controlled. Test GO_BIT initialization from fixed voltage, out-of-range fixed voltage rejection, voltage selector get/set, ramp timing, and behavior when regulator init data is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/sy8106a-regulator.c -->
