# subset-b-005619 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/print-tree.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/print-tree.c

Purpose: implements Btrfs diagnostic tree dumping. It formats root IDs, internal nodes, leaves, and many on-disk item payloads for kernel logs, making it a debugging and corruption-analysis aid rather than a normal data-path component.

Important APIs/types/functions: exported entry points are `btrfs_root_name()`, `btrfs_print_leaf()`, and `btrfs_print_tree()`. Helper printers decode chunks, devices, extent refs, UUID items, inode metadata, directory entries, file extents, csum ranges, RAID stripe items, remap items, and key type names. It relies heavily on accessor helpers so little-endian on-disk structures are read through the usual Btrfs abstraction layer.

Control flow: `btrfs_print_tree()` prints a node header and child pointers, optionally follows children with `read_tree_block()`, validates parent checks, recurses, and frees buffers. Leaves are delegated to `btrfs_print_leaf()`, which iterates slots, stringifies the item key, and dispatches by key type to payload-specific printers. Extent item printing walks inline refs until the item size boundary and warns on malformed sizes or unaligned shared parents.

State and persistence: this file does not mutate filesystem state or persist output. The only state is stack-local formatting and references taken while walking tree blocks. Log output reflects current or read tree buffers.

Dependencies and integration: integrates with `ctree`, `disk-io`, `file-item`, `accessors`, `tree-checker`, `volumes`, and RAID stripe tree definitions. It is used by debugging paths that need human-readable B-tree state.

Risks and test signals: malformed on-disk items can cause misleading output if length checks miss a variable-sized structure; recursive `follow` mode performs IO and can hit BUG checks on level mismatches. Useful signals are Btrfs selftests that print leaves with every key type, fault-injected `read_tree_block()` failures, corrupted extent inline ref sizes, RAID stripe tree item dumps, and debug builds that include extent-buffer lock/ref output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/print-tree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/print-tree.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/print-tree.h

Purpose: declares the public debug-printing interface for Btrfs tree and leaf dumps.

Important APIs/types/functions: defines `BTRFS_ROOT_NAME_BUF_LEN` for callers that need a buffer for `btrfs_root_name()`, forward-declares `struct extent_buffer` and `struct btrfs_key`, and exposes `btrfs_print_leaf()`, `btrfs_print_tree()`, and `btrfs_root_name()`.

Control flow: none directly; it is a compile-time contract for callers that want to dump a single leaf, dump a whole tree optionally following children, or translate a root key objectid to a stable name.

State and persistence: no runtime state and no persistent data. The buffer-size constant is part of the ABI between `print-tree.c` and callers.

Dependencies and integration: includes only Linux types and avoids pulling in full Btrfs headers, keeping the diagnostic interface lightweight.

Risks and test signals: the main risk is contract drift if `btrfs_root_name()` ever formats longer names than `BTRFS_ROOT_NAME_BUF_LEN`. Compile coverage catches prototype drift; runtime debug output for relocation roots checks the offset-containing name case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/print-tree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/props.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/props.c

Purpose: implements Btrfs inode properties stored as `btrfs.*` xattrs. The current handler set supports the inheritable `btrfs.compression` property and maps xattr values to in-memory inode compression flags and persisted xattr items.

Important APIs/types/functions: `struct prop_handler` describes each property with validate, apply, extract, ignore, and inheritance hooks. Public entry points are `btrfs_props_init()`, `btrfs_validate_prop()`, `btrfs_ignore_prop()`, `btrfs_set_prop()`, `btrfs_load_inode_props()`, and `btrfs_inode_inherit_props()`. Compression-specific hooks are `prop_compression_validate()`, `prop_compression_apply()`, `prop_compression_ignore()`, and `prop_compression_extract()`.

Control flow: initialization hashes handlers by Btrfs name hash. Validation rejects malformed or unknown xattr names, then delegates to the handler. Setting a property writes or removes the backing xattr with `btrfs_setxattr()` and applies the in-memory state; if apply fails after write, it rolls the xattr back. Loading inode props scans xattr items for matching handler names and applies values. Inheritance copies inheritable properties from a parent inode to a new inode when supported, reserving extra metadata only after the first property.

State and persistence: persistent state lives in xattr tree items. Runtime state includes `BTRFS_INODE_HAS_PROPS`, inode compression/nocompress flags, and `inode->prop_compress`. Compression values can set filesystem incompat bits for LZO or ZSTD.

Dependencies and integration: integrates xattr handling, inode creation, transactions, compression helpers, directory item parsing, metadata reservation, and Btrfs inode runtime flags.

Risks and test signals: the handler hash depends on xattr name hashing matching item offsets during iteration. `btrfs_set_prop()` removes the xattr on apply failure but does not restore a previous value. Inheritance assumes one current property for reservation sizing. Test signals include valid and invalid compression values, property deletion, ignored inode modes, inherited directory compression, mount-time inode property reload, rollback on injected apply failure, and metadata reservation failures when more properties are added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/props.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/props.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/props.h

Purpose: exposes the Btrfs inode-property API used by xattr, inode-load, and inode-create paths.

Important APIs/types/functions: declares initialization, validation, ignore checks, setting, loading, and inheritance helpers: `btrfs_props_init()`, `btrfs_validate_prop()`, `btrfs_ignore_prop()`, `btrfs_set_prop()`, `btrfs_load_inode_props()`, and `btrfs_inode_inherit_props()`.

Control flow: no implementation flow. The prototypes indicate which paths need a transaction (`set` and `inherit`), which operate on loaded inode state (`validate`, `ignore`, `load`), and which require a caller-supplied path for scanning persisted xattr items.

State and persistence: no state in the header. It defines the boundary for code that mutates persisted property xattrs and runtime inode property flags.

Dependencies and integration: forward declarations keep this header independent of full inode/path/transaction definitions while making the property subsystem available across Btrfs.

Risks and test signals: prototype drift is the main risk. Build coverage of xattr, inode load, and create paths catches signature mismatches; behavior tests should focus on the implementation in `props.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/props.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/qgroup.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/qgroup.c

Purpose: implements Btrfs quota groups in both full accounting mode and simple quota mode. It manages the quota tree, in-memory qgroup graph, reservations, dirty extent tracing, commit-time accounting, rescans, snapshot inheritance, and balance relocation subtree tracking.

Important APIs/types/functions: mode helpers are `btrfs_qgroup_mode()`, `btrfs_qgroup_enabled()`, and `btrfs_qgroup_full_accounting()`. Lifecycle/configuration APIs include `btrfs_read_qgroup_config()`, `btrfs_quota_enable()`, `btrfs_quota_disable()`, and `btrfs_free_qgroup_config()`. User-visible graph operations are create/remove qgroup, add/delete relation, limit update, inherit, rescan, and wait. Accounting APIs include trace extent/leaf/subtree, account extent(s), run dirty qgroups, data/meta reservation/free/convert helpers, swapped-block helpers, and `btrfs_record_squota_delta()`.

Control flow: mount reads status, qgroup info/limit items, then relation items into an rb-tree plus parent/member lists. Enabling creates the quota root, status item, per-subvolume qgroups, sysfs entries, and either simple-mode generation tracking or an inconsistent full-mode state followed by rescan. Full accounting traces dirty extents into the transaction delayed-ref xarray, records old roots when possible, finds new roots during commit, updates referenced/exclusive counters through parent qgroups, frees data reservations, and writes dirty qgroup info/limit/status items. Rescan walks extent roots from persisted progress and rebuilds accounting from backrefs. Simple quota mode bypasses full backref accounting and applies generation-filtered deltas directly to a root and its parents.

State and persistence: persistent state is in the quota tree: status, relation, info, and limit items. In-memory state lives in `fs_info->qgroup_tree`, `dirty_qgroups`, qgroup flags, rescan progress/running state, reservation counters, per-root meta reservation counters, per-inode `EXTENT_QGROUP_RESERVED` bits, transaction dirty extent records, and relocation swapped-block rb-trees. Runtime-only flags occupy high bits of the status flag field and are masked before status persistence.

Dependencies and integration: depends on transactions, delayed refs, backref walking, extent and root trees, sysfs qgroup kobjects, workqueues, extent_io changesets, inode writeback/ordered extents, block group relocation, tree modification logging assumptions, and capability checks for quota override.

Risks and test signals: lock ordering is delicate around `qgroup_ioctl_lock`, transaction start/commit, `qgroup_lock`, and `qgroup_rescan_lock`. Accounting can be marked inconsistent after xarray insertion failures, qgroup item update failures, subtree thresholds, malformed swapped-block records, or backref walk errors. Reservation underflow is guarded but still warns. Important tests include full and simple quota enable/disable, interrupted and resumed rescan, snapshot inherit with and without parent qgroups, relation quick updates, dropped-subvolume cleanup, EDQUOT plus flush retry, data reservation release/free distinctions, meta prealloc-to-pertrans conversion, quota-disable races with ordered extents, balance subtree swaps followed by COW, 32-bit bytenr overflow checks, and mount/unmount leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/qgroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/qgroup.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/qgroup.h

Purpose: defines the public qgroup data model and API surface used across Btrfs quota accounting, reservation, snapshot, rescan, and relocation code.

Important APIs/types/functions: documents the reserve/trace/account architecture and the delayed subtree tracing optimization for balance. Defines runtime status flags, reservation types, `struct btrfs_qgroup_extent_record`, `struct btrfs_qgroup_swapped_block`, `struct btrfs_qgroup_rsv`, `struct btrfs_qgroup`, relation glue `struct btrfs_qgroup_list`, `struct btrfs_squota_delta`, and mode enum. It declares all qgroup lifecycle, graph, tracing, accounting, reservation, rescan, swapped-block, and simple-quota delta functions.

Control flow: no executable flow, but the comments describe when callers should reserve space, trace dirty extents, account records at commit/rescan, and defer expensive balance subtree scans until a COW touches swapped blocks.

State and persistence: `struct btrfs_qgroup` mirrors persisted rfer/excl counts and limits while also holding runtime reservations, list membership, iterator links, temporary refcounts, and sysfs kobject state. Extent records tie transaction dirty extents to old roots and data reservations. Swapped-block records are per-root runtime records discarded at transaction commit.

Dependencies and integration: exposes qgroup hooks to inode write paths, delayed refs, transactions, ioctl quota control, root/subvolume management, relocation, sysfs, and sanity tests.

Risks and test signals: the header’s comments encode important invariants, especially reservation type lifetime and the single-level nested iterator expectation. Runtime flag bits share storage with persisted status flags and must remain collision-free. Compile tests catch API drift; behavior tests should exercise all declared call sites because misuse of reservation type or delayed tracing can silently skew quota accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/qgroup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/raid-stripe-tree.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/raid-stripe-tree.c

Purpose: maintains the RAID stripe tree, which records logical data extents and their per-stripe device/physical locations for supported RAID profiles. It supports insert/update on write completion, deletion/truncation on extent removal, and lookup during IO mapping.

Important APIs/types/functions: public functions are `btrfs_delete_raid_extent()`, `btrfs_insert_raid_extent()`, `btrfs_insert_one_raid_extent()` for tests and ordered-extent bioc insertion, and `btrfs_get_raid_extent_offset()`. Internal helpers partially delete an item by reinserting adjusted stride physical offsets and update an existing item after `-EEXIST`.

Control flow: deletion first skips unsupported filesystems or profiles, then searches for the stripe item overlapping the removal range. It handles four cases: hole punching inside one item, trimming the left side, trimming the right side, or deleting whole items while advancing through the range. Insertion builds a variable-sized `btrfs_stripe_extent` from each `btrfs_io_context`, inserts it by logical start/length, and updates existing entries when necessary. Lookup finds the containing stripe extent, shortens the caller length if the mapping crosses a recorded extent boundary, then selects the matching devid and DUP stripe index.

State and persistence: persistent state is `BTRFS_RAID_STRIPE_KEY` items in `fs_info->stripe_root`, keyed by logical start and length with an array of strides. Ordered extents temporarily own bioc list entries until insertion consumes and releases them.

Dependencies and integration: depends on the RAID stripe tree incompat bit, chunk maps/profile checks, ordered extents, volume mapping, B-tree item insertion/deletion/duplication, tracepoints, and committed-root lookup for some read paths.

Risks and test signals: range deletion is branch-heavy and sensitive to off-by-one length updates, leaf splits after duplicate item, and physical offset adjustments after front trimming. Lookup must handle logically contiguous but physically split extents by shortening length. Tests should cover full delete, left/right trim, middle punch, multi-item delete, duplicate insert update, unsupported profiles, DUP stripe-index selection, committed-root lookup, and missing stripe entries returning `-ENODATA`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/raid-stripe-tree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/raid-stripe-tree.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/raid-stripe-tree.h

Purpose: declares the RAID stripe tree API and small helpers that gate when stripe-tree metadata is needed.

Important APIs/types/functions: defines `BTRFS_RST_SUPP_BLOCK_GROUP_MASK` for supported profiles, declares delete/lookup/insert functions, exposes test-only single-extent insertion under sanity tests, and defines inline helpers `btrfs_need_stripe_tree_update()` and `btrfs_num_raid_stripes()`.

Control flow: the key inline gate returns true only when the RAID stripe tree incompat bit is set, the block group type is data, and the profile is DUP, RAID1-family, RAID0, or RAID10. `btrfs_num_raid_stripes()` derives array length from item size.

State and persistence: no state in the header. It defines which data block groups produce persistent RAID stripe tree items and how item size is interpreted.

Dependencies and integration: includes UAPI tree definitions, fs incompat helpers, and accessors; forward declarations link it to IO context, IO stripe, ordered extent, filesystem, and transaction code.

Risks and test signals: if the supported profile mask or gate diverges from insertion/deletion/lookup assumptions, stripe metadata can be missing or unnecessary. Compile coverage checks prototypes; behavioral tests should verify profile gating and item-size-to-stripe-count calculations for every supported RAID profile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/raid-stripe-tree.h -->
