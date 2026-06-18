# sources/distributed-fs/ceph-client/fs/btrfs/raid-stripe-tree.h

Purpose: declares the RAID stripe tree API and small helpers that gate when stripe-tree metadata is needed.

Important APIs/types/functions: defines `BTRFS_RST_SUPP_BLOCK_GROUP_MASK` for supported profiles, declares delete/lookup/insert functions, exposes test-only single-extent insertion under sanity tests, and defines inline helpers `btrfs_need_stripe_tree_update()` and `btrfs_num_raid_stripes()`.

Control flow: the key inline gate returns true only when the RAID stripe tree incompat bit is set, the block group type is data, and the profile is DUP, RAID1-family, RAID0, or RAID10. `btrfs_num_raid_stripes()` derives array length from item size.

State and persistence: no state in the header. It defines which data block groups produce persistent RAID stripe tree items and how item size is interpreted.

Dependencies and integration: includes UAPI tree definitions, fs incompat helpers, and accessors; forward declarations link it to IO context, IO stripe, ordered extent, filesystem, and transaction code.

Risks and test signals: if the supported profile mask or gate diverges from insertion/deletion/lookup assumptions, stripe metadata can be missing or unnecessary. Compile coverage checks prototypes; behavioral tests should verify profile gating and item-size-to-stripe-count calculations for every supported RAID profile.
