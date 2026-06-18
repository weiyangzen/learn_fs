# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_fdb.c

Purpose: handles switchdev FDB notifications for LAN966x. It converts bridge/port/LAG FDB add/delete events into hardware MAC table operations and maintains a CPU-copy FDB list for bridge master entries that may need to be written when VLAN CPU membership changes.

Important APIs and functions: `lan966x_fdb_init` creates an ordered workqueue and initializes `fdb_entries`; `lan966x_fdb_deinit` destroys the queue and purges entries; `lan966x_handle_fdb` queues switchdev FDB work. `lan966x_fdb_write_entries` and `lan966x_fdb_erase_entries` replay or remove stored bridge FDB entries for a VLAN. Work handlers split events among physical LAN966x ports, bridge masters, and LAG masters.

Control flow: notifier context allocates `lan966x_fdb_event_work`, copies the FDB address, and queues ordered work. Port events only offload user-added entries, calling `lan966x_mac_add_entry` or `lan966x_mac_del_entry`. Bridge-master events maintain a reference-counted software FDB entry; hardware CPU MAC learn/forget is only done if the CPU is a member of the VLAN. LAG-master events only act on the first LAN966x member port to avoid duplicate offload.

State and persistence: `lan966x->fdb_entries` stores MAC/VID plus reference count for bridge-master CPU entries. The ordered workqueue serializes event handling outside atomic notifier context. Hardware state is persisted through `lan966x_mac_cpu_learn`, `lan966x_mac_cpu_forget`, and MAC entry add/delete calls.

Dependencies and integration points: depends on switchdev FDB notifier semantics, bridge and LAG netdevice type helpers, VLAN CPU membership helpers, MAC table helpers, and LAG first-port selection. VLAN code calls write/erase helpers when CPU membership changes.

Risks: allocation failures in notifier context drop FDB updates. Reference-counted bridge entries must match bridge notifications exactly or CPU-copy MAC entries leak/stale. Workqueue destruction must happen after notifier paths are quiesced. LAG first-port selection must stay consistent across membership changes.

Test signals: static FDB add/delete on a port, bridge master, and LAG master; FDB events before/after VLAN CPU membership; duplicate bridge FDB references; notifier flush on teardown; LAG first-port changes; user-added versus learned FDB filtering.
