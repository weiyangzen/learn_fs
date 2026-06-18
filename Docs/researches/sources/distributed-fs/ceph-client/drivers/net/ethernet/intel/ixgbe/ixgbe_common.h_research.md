# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_common.h

## Purpose
`ixgbe_common.h` exposes the shared ixgbe hardware-service API and low-level register access wrappers used by the driver. It declares generic MAC, EEPROM, flow-control, filtering, bus, firmware, thermal, RX, and link helpers implemented mostly in `ixgbe_common.c`, and it centralizes macros for safe MMIO reads/writes and driver logging.

## Important APIs, Types, And Functions
- Public declarations cover generic init/start/stop, counter clearing, PBA string and MAC address reads, bus conversion/info, EEPROM read/write/checksum operations, RAR/MTA/VFTA/VMDq filtering, flow control, SW/FW synchronization, SAN MAC and WWN reads, LED control, anti-spoofing, firmware host-interface commands, thermal sensors, RX enable/disable, and multispeed fiber link setup.
- `ixgbe_mvals_8259X` is declared as a shared register-value table for MAC-specific values.
- Thermal sensor constants define EMC/I2C register addresses used by generic thermal helpers.
- Removed-device sentinels define failed read values for MMIO and PCI config access.
- `ixgbe_removed()`, `ixgbe_write_reg()`, `ixgbe_write_reg64()`, `IXGBE_READ_REG`, `IXGBE_WRITE_REG`, array access macros, and `IXGBE_WRITE_FLUSH` define the main hardware access surface.
- Logging macros map hardware and adapter contexts to `netdev_*`, `dev_*`, and `netif_*` logging APIs.

## Control Flow
Including this header gives chip-specific and adapter-level files access to the generic operation set. Most calls are indirect through operation tables in `struct ixgbe_hw`, but direct callers also use declarations for DCB, SR-IOV, firmware, ethtool, and reset support. The inline write wrappers first read `hw->hw_addr` with `READ_ONCE`, check for a removed adapter, and skip writes if the MMIO base is gone.

## State And Persistence
The header itself stores no runtime state, but its APIs mutate hardware MMIO, EEPROM/NVM, PHY/I2C state, and fields inside `struct ixgbe_hw` and `struct ixgbe_adapter`. The inline MMIO helpers are intentionally defensive against surprise device removal and therefore influence how all callers behave during PCI error removal or hot-unplug handling.

## Dependencies And Integration Points
This header depends on `ixgbe_type.h` for hardware structures, enums, and register constants, and on `ixgbe.h` for adapter-facing types and logging context. It is an integration hub for chip-specific source files, netdev operations, ethtool/debugfs paths, DCB code, firmware-management code, and low-level reset/link paths.

## Risks
- Since register macros are globally used, a mistake in removed-device handling or write ordering can affect nearly every hardware path.
- Function prototype drift between this header and implementations can break operation table assignments at compile time or silently push callers toward wrong generic helpers.
- Logging macros assume `hw->back` points to a valid `struct ixgbe_adapter`; early probe, teardown, or error paths must not call them before that invariant is true.
- `writeq` fallback ordering is low-word then high-word; callers depending on atomic 64-bit writes must be aware of hardware expectations.

## Test Signals
Compile coverage with all ixgbe chip variants enabled is the primary signal. Runtime signals include safe behavior on device removal, no MMIO access faults after hot-unplug/AER, successful reset and link setup using operation-table generic helpers, and expected logs from `hw_dbg`, `hw_err`, and adapter logging macros.
