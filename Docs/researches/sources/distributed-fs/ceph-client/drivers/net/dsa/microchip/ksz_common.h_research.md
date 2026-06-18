# sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz_common.h

## Purpose
`ksz_common.h` is the shared private contract for the Microchip KSZ DSA driver family. It defines the device, port, chip capability, IRQ, MIB, ALU, and operation-table structures used by common code, bus drivers, and chip-specific implementations, plus the register helper API for 8/16/32-bit regmaps.

## Important APIs, Types, and Functions
Major data types include `struct ksz_chip_data`, `struct ksz_device`, `struct ksz_port`, `struct ksz_dev_ops`, `struct ksz_irq`, `struct ksz_ptp_irq`, `struct ksz_port_mib`, `struct vlan_table`, and `struct alu_struct`. Enumerations model supported chips (`enum ksz_model`), abstract register slots (`enum ksz_regs`), mask slots, shift slots, and xMII bit encodings.

The header declares the common lifecycle exports, MIB/stat helpers, STP helper, xMII helpers, switch MAC address helpers, wake-reason helper, and `ksz_switch_chips[]`. Inline helpers wrap `regmap_read()`, `regmap_write()`, and `regmap_update_bits()` for global and per-port register access, and encode model-family predicates such as `is_ksz8()`, `is_ksz9477()`, `is_lan937x()`, and `ksz_is_sgmii_port()`.

## Control Flow
This header does not execute by itself, but it shapes the driver flow. Bus drivers allocate `ksz_device`, initialize three regmaps, and call `ksz_switch_register()`. Common code then consults `ksz_chip_data` and calls hooks in `ksz_dev_ops` for reset, setup, port address calculation, PHY access, VLAN/FDB/MDB operations, MIB reads, MTU changes, PME register access, PCS creation, and chip-specific teardown.

## State and Persistence
All persistent runtime state is in memory and hardware registers referenced by these structures. `ksz_device` owns global switch state and synchronization primitives; each `ksz_port` owns per-port link, STP, learning, interface, RGMII delay, MIB, IRQ, PTP, and flow-control state. No disk persistence is defined. Regmap caching is explicitly disabled in the generated SPI regmap configs.

## Dependencies and Integration Points
The header depends on Linux networking and driver subsystems: DSA, phylink, PCS XPCS, PHY, regmap, IRQ, mutexes, platform data, and optional PTP declarations from `ksz_ptp.h`. It is consumed by `ksz_common.c`, bus access drivers such as `ksz_spi.c`, DCB/PTP files, and chip-specific KSZ8/KSZ9477/LAN937x modules.

## Risks and Edge Cases
The abstract register arrays must stay aligned with `enum ksz_regs`, masks, and shifts; missing entries can cause common code to write the wrong hardware address. Inline read helpers assign output values even when regmap reads fail, so callers must respect return codes. Per-port helpers depend on a correct `get_port_addr()` implementation. Family predicates drive large feature decisions and must be updated with any new chip IDs. The regmap macro parameters encode SPI command endianness, address width, padding, and alignment, making bus access fragile if reused incorrectly.

## Test Signals
Compile coverage should include PTP enabled and disabled configurations, all bus drivers using the regmap macros, and chip-specific modules consuming `ksz_dev_ops`. Runtime signals include correct register addresses from per-port helpers, expected chip-family predicate behavior, clean locking through custom regmap lock/unlock callbacks, and successful probe on chips with SGMII, side MDIO, PTP, and WoL capabilities.
