<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ipc/hw-ish.h -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ipc/hw-ish.h

## Purpose
`hw-ish.h` declares the Intel ISH hardware IPC provider interface, supported PCI device IDs, revision constants, reset/time-sync payload formats, firmware status enum values, and exported IPC hardware functions.

## Important APIs, Types, and Functions
The PCI ID list covers CHV/BXT/APL/SPT/CNL/GLK/ICL/CML/CMP/EHL/TGL/ADL/RPL/MTL/ARL/LNL/PTL/WCL/NVL variants. Revision constants distinguish Cherry Trail stepping-specific register behavior. `struct ipc_rst_payload_type`, `struct time_sync_format`, and `struct ipc_time_update_msg` define management payloads. `struct ish_hw` stores the MMIO base. Exported functions include `ish_irq_handler`, `ish_dev_init`, `ish_hw_start`, `ish_device_disable`, `ish_disable_dma`, and `ish_set_host_ready`.

## Control Flow
The header has no executable flow. `pci-ish.c` probes matching PCI devices, calls `ish_dev_init`, requests IRQs using `ish_irq_handler`, starts hardware with `ish_hw_start`, and disables it with `ish_device_disable`. `ipc.c` implements the exported hooks.

## State and Persistence Behavior
`struct ish_hw` is embedded after `struct ishtp_device` allocation and persists for the PCI device lifetime. Payload structs are transient management messages. Firmware status enum values describe persistent firmware states visible through the hardware status register.

## Dependencies and Integration Points
The header depends on PCI, interrupt, register definitions, and the ISHTP device structure. It is the bridge between the PCI glue and the low-level IPC implementation.

## Risks and Edge Cases
PCI ID additions must be synchronized with `pci-ish.c` matching and firmware generation metadata. Wrong revision constants can choose the wrong interrupt/host-ready programming path. Time-sync struct packing is firmware ABI-sensitive.

## Test Signals
Probe every supported PCI ID class where available, validate MMIO mapping and IRQ routing, confirm firmware status transitions, and test reset/time-sync management messages across older CHV and newer BXT-style hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ipc/hw-ish.h -->
