# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/smi.c

## Purpose
Implements System Management Interface bus access selection for 88E6xxx switches, covering direct single-chip, dual-direct, and indirect multi-chip addressing modes.

## Important APIs, Types, and Functions
The exported entry point is `mv88e6xxx_smi_init`. Internal ops implement direct `mdiobus_read_nested`/`mdiobus_write_nested`, dual-direct address offsetting by `chip->sw_addr`, indirect command/data register transactions, and busy polling through `mv88e6xxx_smi_direct_wait`.

## Control Flow and State
Initialization selects `chip->smi_ops` based on `chip->info->dual_chip`, strapped `sw_addr`, and `chip->info->multi_chip`, then stores `chip->bus` and `chip->sw_addr`. Indirect reads write a BUSY|mode22|read command, wait for busy clear, then read data. Indirect writes write data, issue BUSY|mode22|write, then wait. Persistent state is the selected bus ops pointer and switch address.

## Dependencies and Integration Points
Depends on MDIO bus APIs, jiffies timeout helpers, and `struct mv88e6xxx_bus_ops` consumed by common register accessors. It is one of the earliest setup pieces before higher-level register helpers work.

## Risks and Test Signals
Risks include wrong addressing mode selection, timeout tuning for slow MDIO, indirect command field errors, and nested MDIO locking assumptions. Test signals include probing strapped address variants, multi-chip indirect access, timeout injection, and basic register read/write sanity before chip ID detection.
