<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-cavium.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-cavium.c

Purpose: common MDIO transaction implementation for Cavium OCTEON and Thunder MDIO bus drivers.

Important APIs/types/functions: exports `cavium_mdiobus_read_c22`, `cavium_mdiobus_write_c22`, `cavium_mdiobus_read_c45`, and `cavium_mdiobus_write_c45`. Internal helpers are `cavium_mdiobus_set_mode` and `cavium_mdiobus_c45_addr`.

Control flow: transactions switch hardware mode between C22/C45 as needed, program write data or address phase, write SMI command fields, poll pending bits with bounded delays, and return data or `-EIO`. Clause 45 reads/writes first issue a C45 address command, then read or write data using the appropriate operation code.

State and persistence: state is held in the caller's `struct cavium_mdiobus`, especially MMIO base and current mode. Register state is hardware-resident and volatile.

Dependencies/integration: depends on `mdio-cavium.h` register/bitfield definitions and 64-bit MMIO accessors. Platform frontends such as `mdio-octeon.c` assign these callbacks to mii_bus.

Risks and test signals: risks include mode switch races if callers bypass mii_bus locking, timeout calibration, endian/bitfield layout, and C45 command field correctness. Tests should use register mocks or hardware diagnostics for C22/C45 reads/writes, invalid read data, pending timeout, and mode transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-cavium.c -->
