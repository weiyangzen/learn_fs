# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvpp2/mvpp2_cls.h

## Purpose
`mvpp2_cls.h` defines the classifier/RSS/RFS interface for the PPv2 driver. It provides table sizes, engine IDs, header-extracted-key option bits, C2 action encodings, flow IDs, flow-table index macros, iteration macros over classifier flows, table-entry structures, and exported classifier/RSS/ethtool helper prototypes.

## Important APIs, Types, and Definitions
- Table constants define 512 classifier flow entries, three data words per flow entry, 64 lookup entries, and 256 classifier RX queues.
- `enum mvpp2_cls_engine` identifies supported classifier engines, especially C2 and hash engines C3HA/C3HB.
- `MVPP22_CLS_HEK_OPT_*` bits describe selectable hash/match fields such as MAC DA, VLAN, IPv4/IPv6 addresses, and L4 ports.
- `enum mvpp2_cls_field_id` maps those logical fields to hardware HEK field IDs.
- `struct mvpp2_cls_c2_entry`, `struct mvpp2_cls_flow_entry`, and `struct mvpp2_cls_lookup_entry` model C2 TCAM/action entries, flow table entries, and lookup table entries.
- `enum mvpp2_prs_flow` assigns parser/classifier flow IDs for traffic classes.
- Index macros such as `MVPP2_CLS_FLT_FIRST()`, `MVPP2_CLS_FLT_C2_RFS()`, `MVPP2_CLS_FLT_C2_RSS_ENTRY()`, `MVPP2_CLS_FLT_HASH_ENTRY()`, and `MVPP22_CLS_C2_RFS_LOC()` encode how flow table and C2 TCAM ranges are partitioned by flow and port.
- Prototypes expose RSS context operations, ethtool hash/rule operations, classifier initialization, hit counters, table reads, and oversize RXQ configuration.

## Control Flow
This header supplies the macros used by `mvpp2_cls.c` to walk classifier flow definitions and to calculate hardware table indices. The `for_each_cls_flow_id*` macros depend on the `cls_flows` array in the C file and skip duplicate contiguous flow IDs. Public prototypes are called from main driver setup, ethtool handlers, and debugfs readers.

## State and Persistence
The header defines the shape of transient software copies of hardware entries. Persistent runtime state is stored elsewhere (`struct mvpp2`, `struct mvpp2_port`, hardware tables), but the macros here determine where each flow, per-port hash entry, RFS entry, and RSS/default C2 entry is stored in those tables.

## Dependencies and Integration Points
It includes `mvpp2.h` and `mvpp2_prs.h`, so it is tightly coupled to global PPv2 register definitions and parser result-info definitions. It is consumed by `mvpp2_cls.c`, `mvpp2_debugfs.c`, and any main-driver ethtool glue that forwards RSS/RFS operations.

## Risks and Edge Cases
The flow iteration macros reference `cls_flows` by name, so they are only usable in scopes where that symbol exists. Flow table partitioning is dense and arithmetic-heavy; off-by-one errors can overlap RSS, RFS, and hash entries. `MVPP22_CLS_C2_PORT_RANGE` reserves only `MVPP2_N_RFS_ENTRIES_PER_FLOW + 1` C2 entries per port, so ethtool rule limits must remain synchronized. The C2 attribute word count is defined as five while implementation currently reads/writes four attribute registers, so any future use of a fifth word must audit the hardware accessors.

## Test Signals
Compile tests should catch prototype drift and macro visibility issues. Runtime validation should confirm classifier table indices are unique across all flows/ports/rule locations, C2 entry ranges stay below 256 entries, flow iteration covers each intended flow ID once where required, and debugfs/ethtool readers decode the same fields that setters wrote.
