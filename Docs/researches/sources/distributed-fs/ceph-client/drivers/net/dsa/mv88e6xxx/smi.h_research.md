# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/smi.h

## Purpose
Declares SMI command/data register fields, the SMI init function, and inline read/write dispatchers for the selected bus ops.

## Important APIs, Types, and Functions
Defines `MV88E6XXX_SMI_CMD`, `MV88E6XXX_SMI_DATA`, BUSY, Clause 22/45 mode and operation masks, device address mask, and register address mask. Exposes `mv88e6xxx_smi_init`, `mv88e6xxx_smi_read`, and `mv88e6xxx_smi_write`.

## Control Flow and State
Inline read/write helpers check `chip->smi_ops` and the relevant callback before dispatching, otherwise returning `-EOPNOTSUPP`. Runtime state is held in `chip->smi_ops`, `chip->bus`, and `chip->sw_addr`, initialized by `smi.c`.

## Dependencies and Integration Points
Includes `chip.h` and feeds the common mv88e6xxx bus abstraction. It is consumed by core register read/write helpers and therefore sits below port, global, PHY, TCAM, and other functional modules.

## Risks and Test Signals
Risks are missing ops initialization and macro drift from firmware/hardware command layout. Test signals include direct and indirect MDIO access tests, all supported addressing modes, and compile checks for inline fallback behavior when ops are absent.
