# sources/distributed-fs/ceph-client/include/net/psp/types.h

Purpose: defines PSP wire header fields, device configuration/capabilities, device state, skb extension, parsed keys, associations, stats, and driver callback table.

Important APIs and types: `struct psphdr` models PSP encapsulation header. Macros define UDP port, encapsulation length, SPI key/phase bits, header flags/version/crypt offset, and supported no-option header/trailer sizes. `struct psp_dev` stores main netdev, ops/caps/private pointer, lock/refcount, ID/generation/config, active/previous/stale association lists, core stats, and RCU head. `struct psp_assoc` stores device pointer, dev ID, generation, version, peer_tx, upgrade sequence, tx/rx keys, refcount/work/list, and driver data. `struct psp_dev_ops` lets drivers set config, rotate keys, allocate RX SPI/key, add/delete TX keys, and report stats.

Control flow: PSP core configures devices, rotates generations, allocates RX keys, installs/removes TX associations, tracks association lists across key generations, and asks drivers for required stats.

State and persistence: runtime security state includes keys, SPI values, generation, association lists, and counters. Drivers/hardware may persist keys transiently; the header defines no durable storage.

Dependencies and integration points: depends on mutexes, refcounts, netdevices, netlink extack, UDP encapsulation, skbuff extensions, and TCP socket helpers.

Risks and test signals: risks include key lifetime across rotations, association list migration, driver data alignment/size, stats memset prohibition, generation mask handling, and optional header assumptions. Test device create/config/rotate/unregister, rx SPI allocation, tx key add/delete, stats reporting, stale association handling, and malformed PSP headers.
