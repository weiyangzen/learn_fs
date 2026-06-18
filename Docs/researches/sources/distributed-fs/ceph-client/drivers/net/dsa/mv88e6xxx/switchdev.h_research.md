# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/switchdev.h

## Purpose
Provides the switchdev integration declaration for mv88e6xxx ATU miss handling.

## Important APIs, Types, and Functions
Declares `mv88e6xxx_handle_miss_violation(struct mv88e6xxx_chip *chip, int port, struct mv88e6xxx_atu_entry *entry, u16 fid)`.

## Control Flow and State
No runtime logic. It exposes a single integration point that converts hardware ATU miss context into a switchdev FDB notification in `switchdev.c`.

## Dependencies and Integration Points
Includes `chip.h` for chip and ATU entry definitions. It is consumed by ATU/global interrupt or violation handling code.

## Risks and Test Signals
Risks are compile-time interface drift with the caller and `switchdev.c`. Test signals are successful builds with switchdev support and locked-FDB miss handling tests.
