<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/lp873x-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/lp873x-regulator.c

Purpose: platform regulator driver for TI LP873x PMICs, registering two bucks and two LDOs from an MFD parent.

Important APIs/types/functions: `LP873X_REGULATOR()` builds descriptors plus a `ctrl2_reg` field. Buck callbacks include voltage, ramp, voltage-time, and current-limit operations; LDO callbacks cover voltage and enable. `lp873x_buck_set_ramp_delay()` maps requested slew to register codes and updates constraints.

Control flow: probe gets parent `struct lp873x`, points config OF node at the parent node, then registers all four descriptors. Runtime operations are standard regmap helpers except buck ramp-delay selection.

State and persistence: no private regulator state. Hardware and regmap hold voltage, enable, slew, and current-limit settings; constraints are updated with the selected ramp delay.

Dependencies and integration: `linux/mfd/lp873x.h`, platform MFD child, regmap, regulator linear ranges, bitfield helpers.

Risks and test signals: LDO descriptors inherit buck current-limit fields with dummy control register values from the macro, though LDO ops do not use them. Test all four registrations, ramp-delay bucket boundaries, current-limit selection, OF node parsing, and regmap failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/lp873x-regulator.c -->
