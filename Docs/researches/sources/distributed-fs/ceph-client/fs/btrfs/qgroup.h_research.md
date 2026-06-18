# sources/distributed-fs/ceph-client/fs/btrfs/qgroup.h

Purpose: defines the public qgroup data model and API surface used across Btrfs quota accounting, reservation, snapshot, rescan, and relocation code.

Important APIs/types/functions: documents the reserve/trace/account architecture and the delayed subtree tracing optimization for balance. Defines runtime status flags, reservation types, `struct btrfs_qgroup_extent_record`, `struct btrfs_qgroup_swapped_block`, `struct btrfs_qgroup_rsv`, `struct btrfs_qgroup`, relation glue `struct btrfs_qgroup_list`, `struct btrfs_squota_delta`, and mode enum. It declares all qgroup lifecycle, graph, tracing, accounting, reservation, rescan, swapped-block, and simple-quota delta functions.

Control flow: no executable flow, but the comments describe when callers should reserve space, trace dirty extents, account records at commit/rescan, and defer expensive balance subtree scans until a COW touches swapped blocks.

State and persistence: `struct btrfs_qgroup` mirrors persisted rfer/excl counts and limits while also holding runtime reservations, list membership, iterator links, temporary refcounts, and sysfs kobject state. Extent records tie transaction dirty extents to old roots and data reservations. Swapped-block records are per-root runtime records discarded at transaction commit.

Dependencies and integration: exposes qgroup hooks to inode write paths, delayed refs, transactions, ioctl quota control, root/subvolume management, relocation, sysfs, and sanity tests.

Risks and test signals: the header’s comments encode important invariants, especially reservation type lifetime and the single-level nested iterator expectation. Runtime flag bits share storage with persisted status flags and must remain collision-free. Compile tests catch API drift; behavior tests should exercise all declared call sites because misuse of reservation type or delayed tracing can silently skew quota accounting.
