<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/stw481x-vmmc.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/stw481x-vmmc.c

Purpose: registers the STw4810/STw4811 internal VMMC regulator as a voltage-table regulator and disables external VMMC selection before exposing the internal rail.

Important APIs/types/functions: `stw481x_vmmc_voltages[]` defines eight selector values, including duplicate 1.8 V entries. `stw481x_vmmc_ops` uses table voltage listing and regmap-backed enable, disable, is_enabled, get selector, and set selector helpers. `vmmc_regulator` describes enable and vsel fields in `STW_CONF1`. `stw481x_vmmc_regulator_probe()` obtains parent platform data and registers the regulator.

Control flow: probe receives `struct stw481x` through platform data, clears `STW_CONF2_VMMC_EXT` to disable external VMMC, builds regulator config with parent regmap and OF init data, registers `VMMC`, and logs success. Runtime operations are standard regmap helper callbacks.

State and persistence: no private driver state is stored. Voltage and enable state live in the STw481x registers. Clearing external VMMC is a probe-time hardware side effect.

Dependencies and integration: depends on the STw481x MFD parent, `linux/mfd/stw481x.h`, platform data, parent regmap, OF compatible `st,stw481x-vmmc`, and regulator constraints.

Risks and test signals: the enable mask combines power-down and level-shifter status bits, so polarity and status interaction need hardware validation. `enable_time` is marked FIXME. Test disabling external VMMC, voltage table selector behavior, enable/disable polarity, missing platform data/regmap assumptions, and board constraints for MMC consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/stw481x-vmmc.c -->
