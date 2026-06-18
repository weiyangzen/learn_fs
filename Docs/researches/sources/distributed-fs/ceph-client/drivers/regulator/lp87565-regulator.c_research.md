<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/lp87565-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/lp87565-regulator.c

Purpose: platform regulator driver for TI LP87565-family buck regulators, including grouped multiphase variants.

Important APIs/types/functions: `LP87565_REGULATOR()` defines descriptors and control-register metadata. `lp87565_buck_set_ramp_delay()` maps requested ramp to register codes, writes slew-rate bits, and adjusts constraints. Descriptor entries cover BUCK0-3 plus BUCK10, BUCK23, and BUCK3210 grouped rails.

Control flow: probe retrieves parent `struct lp87565`, chooses descriptor index range based on `dev_type`, and registers the matching rails. Standard regmap helpers handle enable, voltage, current limit, and voltage timing.

State and persistence: driver stores no private mutable state. Register state persists in the PMIC; selected ramp delay is reflected in regulator constraints with a conservative margin.

Dependencies and integration: `linux/mfd/lp87565.h`, platform MFD enumeration, regmap, bitfield helpers, linear ranges, and current-limit tables.

Risks and test signals: descriptor selection by device type must match hardware phase grouping. The ramp-delay margin multiplies by 85/100 despite the comment saying 15 percent margin, so effective timing semantics deserve review. Test each device type, grouped rail registration, enable mask/value behavior, current limits, and ramp boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/lp87565-regulator.c -->
