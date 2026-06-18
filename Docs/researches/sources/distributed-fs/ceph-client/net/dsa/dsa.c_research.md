# sources/distributed-fs/ceph-client/net/dsa/dsa.c

## Purpose
This is the central DSA topology and switch lifecycle manager. It owns switch-tree discovery, CPU/DSA/user port parsing, routing table construction, tag-protocol binding and runtime switching, switch and port setup/teardown ordering, conduit setup, LAG/bridge numbering state, module init/exit, and exported entry points used by hardware switch drivers.

## Important APIs, Types, And Functions
Global state includes `dsa_tree_list`, `dsa2_mutex`, ordered workqueue `dsa_owq`, and the forwarding-offload bridge bitmap. Exported APIs include `dsa_register_switch()`, `dsa_unregister_switch()`, `dsa_switch_shutdown()`, `dsa_switch_suspend()`, `dsa_switch_resume()`, `dsa_switch_find()`, `dsa_port_from_netdev()`, `dsa_flush_workqueue()`, `dsa_db_equal()`, `dsa_fdb_present_in_other_db()`, `dsa_mdb_present_in_other_db()`, simple HSR helpers, LAG mapping helpers, bridge numbering helpers, conduit state change helpers, and `dsa_tree_change_tag_proto()`.

Key internal flows are `dsa_tree_touch()/put()`, `dsa_switch_parse_of()`, `dsa_switch_parse()`, `dsa_tree_setup()`, `dsa_switch_setup()`, `dsa_port_setup()`, `dsa_tree_setup_conduit()`, `dsa_tree_teardown()`, and `dsa_switch_release_ports()`.

## Control Flow
Driver probe calls `dsa_register_switch()`, which serializes under `dsa2_mutex`, parses OF or platform data, touches/allocates a switch tree, allocates all `struct dsa_port` objects, resolves CPU conduit netdevs, picks a tag protocol, and attempts `dsa_tree_setup()`. Tree setup first builds routing links from DSA port phandles; if the tree is incomplete it returns success without setting up until more switches probe. For a complete tree it assigns CPU ports, sets up each switch, sets up shared CPU/DSA ports before user ports, sets up conduits, allocates LAG ID space, and marks the tree setup.

Switch setup allocates devlink, registers the switch notifier, calls driver `setup`, synchronizes the selected tag protocol with the driver, optionally registers a user MDIO bus, registers devlink, and sets `ds->setup`. Port setup creates devlink ports, registers phylink for CPU/DSA ports when firmware describes links, enables shared ports, and creates user netdevs for user ports. User-port setup failure downgrades the port to unused if possible.

Runtime tag-protocol changes run under RTNL: disconnect old taggers, notify switches, bind the new tagger, change driver tag protocol, update CPU port receive callbacks and user MTUs, and roll back to the old tagger on failure. Removal and shutdown reverse setup, detach conduit/user relationships, clean leaked FDB/MDB/VLAN bookkeeping, and drop tree references.

## State And Persistence
DSA state is in heap-allocated `struct dsa_switch_tree`, `struct dsa_switch`, `struct dsa_port`, `struct dsa_link`, LAG arrays, bridge objects, and per-port address/VLAN lists. It persists while switch drivers are registered. Tree references are kref-managed. CPU conduit netdevs are held with netdev trackers and released during port cleanup.

## Dependencies And Integration Points
This file integrates with device tree, platform data, netdev and RTNL locking, phylink, MDIO, devlink, DSA tag drivers, switchdev user-port code, conduit handling, DSA notifiers, HSR, LAG, bridge offload numbering, and stubs for built-in network stack callers.

## Risks And Edge Cases
Incomplete multi-switch trees return success without setup, so later probes must complete the routing table. A DSA tree may use only one tag protocol; mismatches across CPU ports or switches fail setup. Device-tree CPU ports without resolvable conduit netdevs defer probe. Removal cleans leaked FDB/MDB/VLAN entries but those logs indicate upper-layer tracking bugs. Runtime tagger switching has multiple rollback paths and depends on both tagger and switch callbacks behaving consistently. Bridge-number allocation is limited by `BITS_PER_LONG`.

## Test Signals
Strong tests include OF parsing for complete/incomplete trees, platform-data parsing, multi-CPU-port default assignment, tagger autoload and override, setup/teardown rollback at every stage, conduit state replay, switch unregister cleanup, suspend/resume, shutdown unlinking, FDB/MDB duplicate database detection, and HSR simple offload helpers.
