# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_rx_filter.h

Purpose: Declares the Ionic receive-filter data model, hash-table sizing, state machine, and public filter-management entry points used by the LIF and netdev address/VLAN paths.

Important APIs and types: `enum ionic_filter_state` defines `SYNCED`, `NEW`, and `OLD` for desired-versus-firmware state reconciliation. `struct ionic_rx_filter` stores local flow ID, firmware filter ID, target RX queue index, state, saved add command, and two hlist nodes. `struct ionic_rx_filters` stores a spinlock plus 1024-bucket `by_hash` and `by_id` indexes. The header declares init/deinit, save, lookup, replay, sync, list-address, and VLAN add/delete functions. `IONIC_RXQ_INDEX_ANY` is the wildcard RX queue selector.

Control flow: The header establishes that callers use lookup helpers for local cache checks, update filter state through `ionic_lif_list_addr()` or add/delete wrappers, and rely on `ionic_rx_filter_sync()` to reconcile pending state with firmware. The two indexes allow lookups both by logical match key and by firmware deletion ID.

State and persistence behavior: State is in-memory only and owned by `struct ionic_lif`. The saved `struct ionic_rx_filter_add_cmd` inside each entry is the replay source after reset. Hash constants define fixed-size tables using `hash_32()` and low bits of firmware IDs.

Dependencies and integration points: Requires `struct ionic_lif`, `struct ionic_admin_ctx`, `struct ionic_rx_filter_add_cmd`, hlist, and spinlock definitions from surrounding Ionic/Linux headers. It is included by the implementation and by LIF code that needs address/VLAN filter management.

Risks: Any change to firmware command layout or match-type enumeration affects the cached `cmd` member. The fixed hash-table size is simple but does not prevent long collision chains. Callers must respect locking expectations around local list mutation.

Test signals: Compile coverage for all declared functions, lockdep under address-list churn, and reset tests that confirm cached add commands are replayable.
