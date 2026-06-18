# sources/distributed-fs/ceph-client/drivers/net/ethernet/via/via-velocity.h

## Purpose
This header is the private hardware and state definition layer for `via-velocity.c`. It defines descriptor formats, register offsets and bit masks, MAC register layout, PHY constants, module option structures, WOL packet structures, private adapter state, and inline helper routines for EEPROM reload, IP capture, MIB updates, and flow-control initialization.

## Important APIs, types, and constants
Descriptor types are `struct rx_desc`, `struct tx_desc`, `struct velocity_rd_info`, and `struct velocity_td_info`. RX descriptors expose receive status, length/ownership, VLAN tag/checksum metadata, DMA address, and buffer size/interrupt-enable fields. TX descriptors expose transmit status, length/ownership, VLAN/TCR command fields, and up to seven DMA buffer segments.

`struct mac_regs` maps the 256-byte register window used by the C file, including station address, command set/clear registers, CAM/MAR, interrupt status/mask, RX/TX queue control, ring base registers, MII registers, EEPROM registers, MIB registers, WOL registers, pattern CRCs, and byte masks.

`struct velocity_info` is the main private state: device and PCI pointers, netdev, `no_eeprom`, VLAN bitmap, cached IP, chip ID, mapped registers, resource addresses, TX/RX ring substructures, MIB counters, options, interrupt mask, flags, MII/PHY status, CAM masks, spinlock, WOL settings, saved context, ethtool nesting, revision ID, and NAPI object.

Important enums and constants include descriptor ownership bits, RSR/TSR/TCR checksum/VLAN/error bits, interrupt mask/status bits, command bits, CAM bits, MII control bits, WOL bits, MTU limits, descriptor count limits, PHY IDs, speed/duplex modes, init types, and flow-control modes.

Inline APIs used by the C file include `mac_eeprom_reload`, `velocity_get_ip`, `velocity_update_hw_mibs`, and `init_flow_control_register`. Many register helpers are macros such as `mac_read_isr`, `mac_write_isr`, `mac_disable_int`, `mac_enable_int`, `mac_rx_queue_run`, and `mac_tx_queue_wake`.

## Control flow and integration
This file has only inline/macro control flow. The C file uses it to allocate and program descriptor rings, interpret hardware completion status, configure interrupts and queue wakeups, operate the MII/PHY interface through `velocity_mii_read/write`, set WOL patterns, and synchronize software netdev state with hardware MIB counters.

## State and persistence behavior
The header defines the in-memory state that persists for each probed netdev and the hardware register state saved in `struct velocity_context` across suspend/resume. `velocity_get_ip` caches the first IPv4 address for ARP WOL. `velocity_update_hw_mibs` accumulates read-and-clear hardware counters into software counters. WOL options and MAC context persist in `struct velocity_info` while the netdev exists.

## Dependencies and integration points
It depends on kernel networking types (`sk_buff`, `net_device`, VLAN bitmap sizing, NAPI), PCI/device types, MII constants, endian annotations, and I/O accessors. It is tightly coupled to `via-velocity.c`; the macros call functions such as `velocity_mii_read` and `velocity_mii_write` that are implemented there.

## Risks and edge cases
The register macros perform read-modify-write without internal locking, so callers must serialize access. Many descriptor and status constants are endian-wrapped values; mixing host-endian and little-endian fields incorrectly would break ownership and status checks. The `MII_GET_PHY_ID` macro reads into a `u32` through `u16 *` casts, which is compact but sensitive to endian/layout assumptions. `struct mac_regs` is a hardware overlay and must remain aligned with the documented 256-byte register map. Inline loops that wait for hardware bits have no scheduling points.

## Test signals
Compile coverage should catch structure and macro drift with `via-velocity.c`. Runtime signals include correct descriptor ownership transitions, MIB counter accumulation, interrupt mask behavior, EEPROM reload completion, WOL ARP IP capture, MII reads/writes against supported PHYs, and suspend/resume context restoration.
