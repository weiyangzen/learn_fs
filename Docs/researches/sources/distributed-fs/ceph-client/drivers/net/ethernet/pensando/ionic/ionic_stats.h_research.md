# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_stats.h

Purpose: Defines the small descriptor and interface layer used by Ionic statistics providers to expose ethtool strings, counts, and values.

Important APIs and types: `struct ionic_stat_desc` stores an ethtool stat name and byte offset. `IONIC_*_STAT_DESC()` macros build descriptors for port, LIF, TX, RX, queue, CQ, interrupt, and NAPI structures. `struct ionic_stats_group_intf` defines callbacks for group-specific string/value/count retrieval. `IONIC_READ_STAT64()` and `IONIC_READ_STAT_LE64()` read native and little-endian 64-bit counters via descriptor offsets. `ionic_stats_groups` and `ionic_num_stats_grps` are exported.

Control flow: The header does not implement runtime control flow; it provides the generic offset-table mechanism used by `ionic_stats.c` and potentially other stats groups.

State and persistence behavior: No state is stored here beyond descriptor constants compiled into the driver. The macros intentionally bind field names to offsets at compile time.

Dependencies and integration points: Requires `offsetof`, `ETH_GSTRING_LEN`, and the target stats structure definitions to be visible where descriptors are built. It is part of the Ionic ethtool integration boundary.

Risks: Offset-based generic reading bypasses type checking after descriptor construction; using a descriptor with the wrong base structure silently reads the wrong memory. `IONIC_READ_STAT64()` assumes alignment and `u64` field width.

Test signals: Compile-time coverage for descriptor field names, ethtool stats smoke tests, and checks that native versus little-endian read macros are used for the correct backing structures.
