## sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/util.c

### Purpose
`util.c` implements small qtnfmac utility routines for per-interface station list management and chip ID stringification.

### Important APIs, Types, And Functions
Station helpers are `qtnf_sta_list_init()`, `qtnf_sta_list_lookup()`, `qtnf_sta_list_lookup_index()`, `qtnf_sta_list_add()`, `qtnf_sta_list_del()`, and `qtnf_sta_list_free()`. `qtnf_chipid_to_string()` maps Topaz/Pearl chip IDs to readable names and is exported.

### Control Flow
The station list is initialized with an empty list head and zero atomic size. Lookup scans by MAC or by ordinal index. Add avoids duplicates, allocates a node, copies the MAC, appends to the list, increments size, and bumps `vif->generation`. Delete removes and frees a node while decrementing size and bumping generation. Free drains all nodes and reinitializes the list.

### State, Persistence, And Dependencies
State lives in `struct qtnf_sta_list` and `struct qtnf_vif` from `core.h`. There is no disk persistence. Dependencies include kernel list APIs, atomic counters, Ethernet address comparison/copy, allocator helpers, and hardware ID constants.

### Integration Points
AP/station event handling and station dump paths use the list to track associated peers. `generation` supports userspace-visible station list consistency across dumps. Chip stringification is used by PCI/probe logging or diagnostics.

### Risks
No locking is performed in these helpers; callers must hold the appropriate interface or event lock. The index lookup is linear and assumes the list is stable while traversed. Allocation failure returns `NULL` without changing state.

### Test Signals
Add/delete duplicate MACs, generation increments, free on nonempty list, index lookup bounds, null MAC handling, concurrent caller locking audits, and chip ID formatting tests are useful.
