## sources/distributed-fs/ceph-client/drivers/net/dsa/rzn1_a5psw.h

Purpose: this header defines the Renesas RZ/N1 A5PSW register map, bitfields, limits, FDB entry packing, and private driver state used by `rzn1_a5psw.c`.

Important APIs, types, and functions: register macros cover global port enable, flood masks, VLAN verification and resource entries, management tag/control, lookup-table control/data/learn-count/ageing, MDIO config/command/data, per-port command/frame-length/status, and per-port statistics. `struct fdb_entry` and `union lk_data` map lookup-table data registers onto MAC/valid/static/priority/port-mask fields. `struct a5psw` stores MMIO base, clocks, device, MDIO bus, PCS array, DSA switch, locks, bridged-port mask, and bridge netdev pointer.

Control flow: the header itself has no runtime behavior, but its constants determine how the implementation sequences lookup-table reads/writes, VLAN resource manipulation, MDIO commands, port link command configuration, and stats reads. `A5PSW_PORT_OFFSET(port)` is the base macro for per-port register banks.

State and persistence: hardware state represented here includes the 8192-entry lookup table, 32 VLAN resources, five switch ports with CPU port 4, MDIO controller, 10 KiB jumbo frame limit, A5PSW 8-byte DSA tag allowance, and per-port counters. Software state in `struct a5psw` persists for the lifetime of the platform device and tracks bridge membership and allocated PCS/MDIO resources.

Dependencies and integration points: the header includes clock, platform, OF MDIO, `pcs-rzn1-miic`, and DSA headers because it declares `struct a5psw` with those types. It is tightly coupled to the A5PSW DSA driver and the RZN1 MIIC PCS provider.

Risks: several hardware limits are baked into macros: five ports, CPU port as the last port, 32 VLAN entries, 8192 FDB entries, and minimum MDIO divider 5. The packed FDB bitfield layout must match endianness and register layout assumptions. `A5PSW_EXTRA_MTU_LEN` reserves space for the DSA tag and two VLAN tags; incorrect accounting would cause unexpected drops or oversize acceptance.

Test signals: compile with the C driver, validate register offsets against the hardware manual, exercise FDB bitfield encoding by adding/dumping entries, test maximum MTU calculation, confirm CPU port index assumptions in DT, and check MDIO divider and VLAN resource limits at runtime.
