# sources/distributed-fs/ceph-client/fs/ubifs/debug.c

## Purpose
`debug.c` implements UBIFS diagnostic dumping, consistency checking, recovery fault injection, debugfs controls, and assertion handling. Most functionality is gated by debug configuration and runtime flags, but the file is central to validating TNC/index structure, lprops/accounting, inode reference counts, and recovery behavior under simulated power cuts.

## Important APIs, Types, and Functions
- Formatting helpers: `dbg_snprintf_key()`, `dbg_ntype()`, `dbg_cstate()`, and `dbg_jhead()`.
- Dumpers: `ubifs_dump_inode()`, `ubifs_dump_node()`, `ubifs_dump_budg()`, `ubifs_dump_lprops()`, `ubifs_dump_lpt_info()`, `ubifs_dump_leb()`, `ubifs_dump_znode()`, `ubifs_dump_tnc()`, and `ubifs_dump_index()`.
- Space and inode checks: `dbg_save_space_info()`, `dbg_check_space_info()`, `dbg_check_synced_i_size()`, and `dbg_check_dir()`.
- TNC/index checks: `dbg_check_key_order()`, `dbg_check_znode()`, `dbg_check_tnc()`, `dbg_walk_index()`, and `dbg_check_idx_size()`.
- Filesystem scan structures: `struct fsck_inode` and `struct fsck_data` support `dbg_check_filesystem()`.
- Node order checks: `dbg_check_data_nodes_order()` and `dbg_check_nondata_nodes_order()`.
- Recovery injection wrappers: `dbg_leb_write()`, `dbg_leb_change()`, `dbg_leb_unmap()`, and `dbg_leb_map()`.
- debugfs entry points: `dbg_debugfs_init_fs()`, `dbg_debugfs_exit_fs()`, `dbg_debugfs_init()`, and `dbg_debugfs_exit()`.
- `ubifs_assert_failed()`, `ubifs_debugging_init()`, and `ubifs_debugging_exit()` handle assertion policy and per-mount debug allocation.

## Control Flow
Dump functions print structured views of in-memory and on-flash objects. `ubifs_dump_node()` first validates UBIFS magic/type and clamps printable length against node type ranges before printing type-specific fields. `ubifs_dump_leb()` scans a whole LEB into a temporary buffer and dumps each scanned node. TNC dumpers traverse either the in-memory TNC or the on-flash index via `dbg_walk_index()`.

Consistency checks are opt-in through global or per-filesystem debug flags. Space checking snapshots lprops/budgeting state, normalizes `freeable_cnt`, and later compares calculated free space with the saved value. Directory checks rebuild directory size and nlink from dent nodes. TNC checks traverse znodes, validate parent/child relationships, dirty propagation, key ordering, collision ordering, and zbranch address/length invariants. Filesystem checks walk all index leaves, validate leaf nodes, build an RB tree of inode summaries, account dent/xent/data references, then compare calculated counts and sizes against inode metadata.

Recovery testing wraps UBI LEB operations. `power_cut_emulated()` randomly chooses delay mode and failure probability based on the target LEB class, sets `pc_happened`, may corrupt write buffers through `corrupt_data()`, and then returns `-EROFS` to simulate a sudden failure. Once a simulated power cut happened, later wrapped operations fail immediately.

debugfs setup creates both global UBIFS knobs and per-mount knobs. Writes to dump files trigger immediate dumps; writes of `0` or `1` toggle check/recovery/RO-error flags. Assertion failure honors `c->assert_action`: panic, switch to read-only error mode, or report with stack dump.

## State and Persistence Behavior
Debug state is held in `struct ubifs_debug_info` per mount and `ubifs_dbg` globally. It includes saved accounting snapshots, power-cut counters, flags controlling optional checks, and debugfs dentries. The debug code normally does not create persistent UBIFS metadata, except that fault-injection wrappers can intentionally corrupt or partially apply UBI writes to test recovery. The filesystem checker reads persistent index leaves and compares them with live VFS cache state when cached inodes exist.

## Dependencies and Integration Points
The file depends on debugfs, UBI LEB operations, random number generation, TNC/index walking/loading, lprops/statistics helpers, scan helpers, journal/accounting structures, and VFS inode lookup. It is referenced broadly through macros and prototypes in `debug.h`; many production paths call check helpers conditionally to validate assumptions during mount, commit, GC, replay, directory operations, writeback, and lprops updates.

## Risks and Edge Cases
- Many checks are heavy and read the whole index; enabling them on large filesystems can materially affect latency.
- `dbg_walk_index()` loads znodes into the TNC and explicitly notes that it does not perfectly mimic non-debug behavior.
- Fault injection deliberately mutates write buffers despite `const void *` by casting away const in `corrupt_data()`, which is acceptable for testing but dangerous if enabled unintentionally.
- debugfs read/write dispatch compares dentries directly; stale or missing debugfs dentries can produce `-EINVAL`.
- Filesystem checking may use cached VFS inode state instead of on-flash inode state, which is intentional after replay but makes results dependent on cache residency.

## Test Signals
Key signals include enabling each debugfs knob and verifying checks fire, running `dbg_check_tnc()` across clean/dirty/colliding-key indexes, running `dbg_check_filesystem()` after directory/xattr/data mutations, validating dump functions on truncated/corrupt nodes, exercising power-cut recovery with `tst_recovery`, and verifying assertion actions produce panic/RO/report behavior as configured.
