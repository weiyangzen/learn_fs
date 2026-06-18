# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/port_hidden.c

## Purpose
Implements access to undocumented/hidden per-port registers used by some mv88e6390/mv88e6341 errata and development paths.

## Important APIs, Types, and Functions
Exports `mv88e6xxx_port_hidden_write`, `mv88e6xxx_port_hidden_wait`, and `mv88e6xxx_port_hidden_read`. The functions use the reserved 0x1a register through the data port and control port constants from `port.h`.

## Control Flow and State
Writes first load the data port, then write a BUSY|WRITE command containing block, port, and register fields to the control port. Reads write a BUSY|READ command, wait until BUSY clears, and then read the data port. Persistent state is entirely in hidden hardware registers; no software cache is maintained here.

## Dependencies and Integration Points
Depends on `mv88e6xxx_port_write`, `mv88e6xxx_port_read`, and `mv88e6xxx_port_wait_bit`. `port.c` uses it for `mv88e6341_port_set_cmode_writable`, enabling forced cmode and SGMII autonegotiation bits before normal cmode programming.

## Risks and Test Signals
Risk centers on undocumented register semantics, missing waits after writes, and block/port/reg field overflow. Calls should be made under the normal register lock. Tests should cover the affected errata path on supported chips, timeout behavior if BUSY never clears, and ensuring unsupported chips never select hidden-register ops.
