<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/hi6421v600-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/hi6421v600-regulator.c

Purpose: SPMI-era Hi6421V600 regulator platform driver for eight known LDO rails, backed by a parent regmap supplied by `hi6421-spmi-core`.

Important APIs/types/functions: `struct hi6421_spmi_reg_priv` serializes enables; `struct hi6421_spmi_reg_info` stores descriptors plus ECO metadata; `HI6421V600_LDO()` defines rails. Custom enable, mode, and optimum-mode callbacks wrap standard table-voltage regmap operations.

Control flow: probe obtains the parent regmap from driver data, allocates the mutex private object, and registers every descriptor. Enable sets the enable mask while holding the mutex, then sleeps for the descriptor off/on delay to avoid simultaneous power-up.

State and persistence: only the enable mutex and static descriptor metadata are driver state. Voltage, enable, and idle-mode state live in SPMI PMIC registers.

Dependencies and integration: platform child of a SPMI PMIC core, standard regmap helpers, OF regulator nodes, and regulator consumer load-to-mode selection.

Risks and test signals: parent drvdata absence is a WARN path. ECO mode is rejected when a rail lacks an ECO mask, but get-mode still reads the register without error handling. Test with serialized concurrent enables, no-parent probe, each LDO’s voltage table, idle eligibility, and off/on delay timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/hi6421v600-regulator.c -->
