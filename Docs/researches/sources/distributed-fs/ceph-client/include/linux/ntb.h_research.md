
# sources/distributed-fs/ceph-client/include/linux/ntb.h

Purpose: defines the generic Non-Transparent Bridge bus API used by NTB hardware drivers and client drivers to exchange link, memory-window, doorbell, scratchpad, message, DMA-device, and optional MSI capabilities.

Important APIs/types/functions: enums describe topology, link speed, link width, and default port roles. `struct ntb_client_ops`, `ntb_ctx_ops`, and `ntb_dev_ops` define client, callback, and hardware operation contracts. `struct ntb_client` and `struct ntb_dev` integrate with the device model. Public APIs register clients/devices, set/clear client context, publish link/doorbell/message events, query ports and resources, enable/disable links, configure inbound/outbound memory windows, access local and peer doorbells, scratchpads, and messages, select DMA devices, compute multiport resource indexes, and use optional `CONFIG_NTB_MSI` descriptors and IRQ helpers.

Control flow: a hardware driver fills `ntb_dev_ops` and calls `ntb_register_device()`. A client registers with `ntb_register_client()`, probes an accepted NTB, installs context callbacks with `ntb_set_ctx()`, enables the link, configures memory windows, and uses doorbells/messages/scratchpads for synchronization. Hardware interrupt handlers call `ntb_link_event()`, `ntb_db_event()`, or `ntb_msg_event()` to notify the client under context locking.

State and persistence: `struct ntb_dev` stores topology, PCI device, ops, client context, context ops, context spinlock, release completion, and optional MSI state. Hardware registers hold link/window/doorbell/scratchpad state; no durable software state is stored by the header.

Dependencies and integration points: depends on device model, PCI, interrupt handlers, completions, DMA/phys/resource types, modules, and optional NTB MSI support. It integrates NTB core, vendor hardware drivers, NTB transport, DMA engines, and client protocols.

Risks and test signals: risks include incomplete `ntb_dev_ops` tables, optional callback fallback returning success when no translation is done, peer/local doorbell callback checks that can mask missing peer ops, multiport resource-index mistakes, link-state races before memory-window setup, and MSI unsupported paths. Test signals include ntb_tool/ntb_perf, two-port and multiport topology tests, doorbell vector masking tests, memory-window alignment/clear tests, link flap stress, DMA peer doorbell address tests, and builds with and without `CONFIG_NTB_MSI`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ntb.h -->
