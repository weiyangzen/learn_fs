<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/chtwc_int33fe.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/chtwc_int33fe.c

## Purpose
Pseudo-driver for Cherry Trail Whiskey Cove `INT33FE` ACPI devices on specific GPD mini laptops. It creates missing I2C clients and software nodes for MAX17047 fuel gauge, FUSB302 Type-C controller, PI3USB30532 mux, USB connector, and DisplayPort altmode relationships.

## Important APIs, Types, And Functions
`struct cht_int33fe_data` tracks created clients and the DP fwnode. Software nodes describe max17047 supplies, FUSB302 role-switch, connector PDOs, PI3USB30532 orientation/mode switch, and DP altmode. `cht_int33fe_add_nodes()` finds the xHCI role-switch software node, registers the node group, and attaches a secondary fwnode to GPU child `DD04`. `cht_int33fe_register_max17047()` handles duplicate firmware enumeration by adding secondary properties and reprobeing.

## Control Flow
Probe is gated by DMI for GPD Win/Pocket patterns. It waits for the bq24292i VBUS regulator and FUSB302 IRQ, registers software nodes, creates or augments the max17047 fuel gauge from ACPI I2C resource 1, creates FUSB302 from resource 2 with IRQ, and creates PI3USB30532 from resource 3. Failure paths unregister clients and software nodes in reverse order.

## State And Persistence
State is the three I2C client pointers, registered software nodes, and DP secondary fwnode association. These are removed on driver removal. Hardware state is owned by the child drivers.

## Dependencies And Integration Points
Integrates ACPI, DMI, I2C ACPI resource instantiation, regulators, USB Type-C/PD properties, xHCI role-switch software node, PCI GPU child fwnodes, and standard max17047/FUSB302/PI3USB30532 drivers.

## Risks And Test Signals
Risks are fragile DMI gating, probe ordering with the role-switch and regulator, stale global `fusb302_mux_refs`, and duplicate fuel-gauge reprobe side effects. Test on target GPD systems for all child devices binding, Type-C role/orientation changes, DP altmode, charging/fuel-gauge properties, and clean remove/reprobe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/chtwc_int33fe.c -->
