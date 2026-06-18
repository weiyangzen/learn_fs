# sources/distributed-fs/ceph-client/include/linux/rio.h

Purpose: this is the core RapidIO interconnect service header. It defines device, master port, network, switch, mailbox, doorbell, DMA, scan, and driver model structures plus low-level operation callbacks.

Important APIs/types/functions: major types are `struct rio_switch`, `struct rio_switch_ops`, `enum rio_device_state`, `struct rio_dev`, `struct rio_msg`, `struct rio_dbell`, `struct rio_mport`, `struct rio_net`, link speed/width enums, `enum rio_mport_flags`, `struct rio_mport_attr`, `struct rio_ops`, `struct rio_driver`, `union rio_pw_msg`, optional DMA transfer types, `struct rio_scan`, and `struct rio_scan_node`. APIs include mport initialization/registration, mailbox open/close, and mport query helpers.

Control flow: mport drivers provide `rio_ops` for local and remote config-space access, doorbells, mailboxes, inbound/outbound mappings, and capability query. Enumeration/discovery populates `rio_net`, `rio_dev`, and switch route state. Device drivers bind through `rio_driver` and operate on resources, messages, doorbells, and mappings. Optional DMA support embeds a DMA device in the mport and describes RapidIO-specific transfer addressing.

State and persistence: `rio_dev` persists identity, capabilities, resources, destination/hop routing, state, and optional switch data. `rio_mport` persists resource ranges, mailbox callbacks, ops, IDs, sys size, physical feature pointers, device object, scan ops, state, and port-write reference count. `rio_net` persists fabric membership lists and primary port.

Dependencies and integration points: depends on device model, resources, `rio_regs.h`, mod_devicetable, optional DMA engine, and RapidIO fabric enumeration.

Risks: hardware callback contracts are broad and must handle config-space size, route tables, mailbox lifetimes, and error management. Atomic state gates running/gone/shutdown behavior. Test signals include mport registration, fabric enumeration/discovery, config reads/writes, mailbox and doorbell loopback, route programming, DMA transfers, port-write error handling, and driver bind/remove.
