# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_mac.c

Purpose: manages the LAN966x hardware MAC table and synchronizes dynamically learned, static, CPU, multicast, and LAG-aware entries with switchdev bridge notifications.

Important APIs and functions: basic table operations are `lan966x_mac_learn`, `lan966x_mac_ip_learn`, `lan966x_mac_forget`, `lan966x_mac_cpu_learn`, and `lan966x_mac_cpu_forget`. Lifecycle and policy functions include `lan966x_mac_init`, `lan966x_mac_set_ageing`, and `lan966x_mac_purge_entries`. Static/software entry APIs are `lan966x_mac_add_entry`, `lan966x_mac_del_entry`, `lan966x_mac_lag_replace_port_entry`, and `lan966x_mac_lag_remove_port_entry`. `lan966x_mac_irq_handler` scans hardware changes and emits switchdev FDB add/delete notifications.

Control flow: learn/forget select a MAC/VID in `ANA_MACLDATA/MACHDATA`, write a MACACCESS command, and poll until idle under `mac_lock`. Driver-managed entries are stored in `lan966x->mac_entries`; adding a user/static entry checks hardware, avoids duplicate software entries, sends `SWITCHDEV_FDB_OFFLOADED`, and learns a locked hardware entry. The MAC IRQ uses `MACACCESS_CMD_SYNC_GET_NEXT` to scan changed rows, compares raw row columns with the software list, notifies bridge deletions for aged/missing entries, and adds/notifies new learned entries.

State and persistence: `lan966x->mac_entries` stores MAC, VID, port index, hardware row, and LAG flag. `mac_lock` protects both the list and serialized table commands. Hardware MAC entries persist in ANA MAC table until aged, forgotten, initialized, or reset. Switchdev notifications provide persistence to the Linux bridge FDB view.

Dependencies and integration points: depends on switchdev FDB notifiers, ANA MACACCESS/MACTINDX register protocol, LAG port migration, MDB/FDB helpers, CPU MAC learning from main and VLAN code, and bridge ageing configuration.

Risks: MACACCESS commands are serialized with a spinlock while polling hardware, so timeout behavior is critical. IRQ row scanning relies on hardware stop conditions and four-column row semantics. Software/hardware divergence can produce duplicate or missing FDB notifications. LAG migration must preserve locked entries when the representative port changes. Atomic allocations in MAC add paths can fail under pressure.

Test signals: hardware learning/ageing notifications to a bridge, static FDB add/delete, CPU MAC learn/forget, multicast MAC types from MDB code, LAG member migration, ageing time changes, MAC table init/purge on probe/remove, and stress with many learned addresses across rows.
