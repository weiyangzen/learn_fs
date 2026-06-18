# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvpp2/mvpp2_debugfs.c

## Purpose
`mvpp2_debugfs.c` builds a debugfs inspection tree for PPv2 parser, classifier, C2 TCAM, flow table, per-port filters, VLAN filters, and per-port flow hash settings. It is diagnostic-only: files are read-only from the driver's perspective despite some mode bits allowing write permissions, and show functions read hardware/shadow state through parser and classifier helper APIs.

## Important APIs, Types, and Functions
- Private entry structures bind debugfs files to parser TIDs, C2 IDs, classifier flow IDs, flow-table IDs, ports, and the shared `struct mvpp2`.
- `struct mvpp2_dbgfs_entries` preallocates per-entry backing storage for all parser, C2, flow-table, flow, and per-port flow debugfs nodes.
- Show functions expose flow table hits, lookup hits, flow type/id, per-port hash options and engine, C2 hits/default RXQ/RSS enable, parser VLAN IDs, parser entries active on a port, MAC filters, parser lookup ID, port map, AI, header data, SRAM bytes, parser hits, and parser validity.
- Initialization helpers create nested debugfs directories: parser entries, classifier C2 entries, classifier flow table entries, per-port summaries, and logical flow directories.
- Public lifecycle functions are `mvpp2_dbgfs_init()`, `mvpp2_dbgfs_cleanup()`, and `mvpp2_dbgfs_exit()`.

## Control Flow
`mvpp2_dbgfs_init()` lazily creates the global `mvpp2` root, creates a per-device directory, allocates `priv->dbgfs_entries`, initializes parser and classifier subtrees, creates per-port directories, then creates flow directories with per-port subdirectories. Each debugfs file uses `DEFINE_SHOW_ATTRIBUTE()` plumbing to call a small show function. Cleanup removes the per-device tree recursively and frees the backing entries; global exit removes the top-level root.

## State and Persistence
Debugfs state is held in `priv->dbgfs_dir`, `priv->dbgfs_entries`, and static `mvpp2_root`. The files expose live hardware and shadow state rather than storing independent data. Parser validity and lookup values come from `priv->prs_shadow` plus hardware reads. C2/default queue/RSS data comes from C2 registers. Flow hash fields and engine values come from classifier flow-table entries. State persists only for the device lifetime and debugfs mount lifetime.

## Dependencies and Integration Points
The file depends on Linux debugfs, seq_file show helpers, slab allocation, `mvpp2.h`, parser helpers from `mvpp2_prs.h`, and classifier helpers from `mvpp2_cls.h`. Main driver probe/setup calls `mvpp2_dbgfs_init()`, teardown calls `mvpp2_dbgfs_cleanup()`, and module/driver exit calls `mvpp2_dbgfs_exit()`. The diagnostics are useful for validating parser/classifier/RSS/RFS behavior implemented in `mvpp2_prs.c` and `mvpp2_cls.c`.

## Risks and Edge Cases
The code does not check `debugfs_create_dir()` or `debugfs_create_file()` return values in most places, which is common for debugfs but can leave partial trees. Some parser files are created with `0644` even though only show operations are defined by `DEFINE_SHOW_ATTRIBUTE()`, so writes are not meaningful. `mvpp2_dbgfs_flow_type_show()` switches on ethtool flow constants while `mvpp2_cls_flow.flow_type` stores internal `MVPP22_FLOW_*` bitmasks, so displayed names may degrade to `other` unless values happen to match. `port_flow_entries` has one slot per port but is reused while creating every flow's per-port directory, so all flow per-port debugfs files for a given port can point at the most recently initialized flow entry rather than the directory's intended flow. `mvpp2_dbgfs_exit()` removes only `mvpp2_root` non-recursively, while per-device cleanup uses recursive removal.

## Test Signals
Mount debugfs and confirm the expected tree appears under `/sys/kernel/debug/mvpp2/<device>/`. Read parser entry files, classifier C2 files, flow table hit files, port filter files, and per-flow per-port hash/engine files under traffic. Verify hit counters increase, parser port maps match configured ports, VLAN/MAC filters reflect netdev settings, C2 default RXQ and RSS enable match ethtool RSS state, and cleanup removes device directories without use-after-free warnings. Specific regression checks should validate flow type names and per-flow per-port hash files across multiple flow directories.
