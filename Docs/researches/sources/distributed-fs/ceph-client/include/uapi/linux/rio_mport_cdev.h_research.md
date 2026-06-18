<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rio_mport_cdev.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/rio_mport_cdev.h

Purpose: defines the RapidIO master-port character-device ABI for mport discovery, device enumeration, maintenance reads/writes, doorbells, port-write events, memory mapping, DMA allocation, DMA transfers, and dynamic device add/delete.

Important APIs and types: structures describe device info, component tags, network IDs, maintenance operations, events, doorbells, port-write filters, memory mappings, DMA memory, transfer sync/async descriptors, wait tokens, and transactions. Ioctls include `RIO_MPORT_GET_PROPERTIES`, `RIO_MPORT_MAINT_{HDID,COMPTAG,PORT_IDX,READ_LOCAL,WRITE_LOCAL,READ_REMOTE,WRITE_REMOTE}`, event enable/disable, doorbell/portwrite receive/send, outbound/inbound map/unmap, DMA alloc/free, transfer, async wait, and device add/delete.

Control flow: userspace opens an mport cdev, queries properties, performs maintenance transactions to local or remote RapidIO devices, enables events, exchanges doorbells/port-writes, maps RapidIO address windows, allocates DMA memory, submits transfers, waits for async completion, and may add/delete remote device records.

State and persistence: runtime state includes mport properties, enabled event masks, mapping windows, allocated DMA buffers, outstanding transactions, async tokens, and discovered remote devices. Hardware fabric configuration may persist outside the Linux driver, but cdev state is runtime.

Dependencies and integration points: depends on Linux types/ioctl and integrates with RapidIO core, mport drivers, DMA mapping, event queues, maintenance transaction routing, and fabric management tools.

Risks and test signals: high-risk areas are DMA address validation, map/unmap lifetime, async completion token reuse, remote maintenance fault handling, event queue overflow, and privileged fabric mutation. Test property queries, local/remote maintenance access, doorbell/portwrite events, inbound/outbound mapping lifecycle, DMA alloc/free/transfer sync and async, invalid remote IDs, and device add/delete races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rio_mport_cdev.h -->
