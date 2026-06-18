# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/ct_fs_smfs.c

Purpose: Provides the software steering (SMFS/DR) backend for CT flow steering.

Important APIs: `mlx5_ct_fs_smfs_ops_get()` returns ops. Init extracts DR tables, creates a forward action to post-CT, initializes matcher lists. Rule add validates flow rule, creates a flow-counter action, gets a protocol matcher, and creates a DR rule with counter, modify-header, and forward actions. Update creates a replacement rule on the existing matcher and destroys the old rule. Delete destroys rule, matcher ref, counter action, and wrapper.

State and persistence: `struct mlx5_ct_fs_smfs` owns CT/CT-NAT DR tables, matcher pools for NAT/non-NAT, a shared fwd action, CT-NAT table pointer, and lock. Matchers are refcounted and maintained in priority-sorted used lists.

Dependencies and integration: Uses `lib/smfs`, mlx5 DR matcher/action/rule APIs, CT validity helpers, flow spec match masks, and `ZONE_TO_REG` register matching.

Risks and tests: Mask generation must match CT tuple semantics for IPv4/IPv6 and TCP/UDP/GRE. Priority allocation through a sorted used list can regress with concurrent matcher creation/destruction. Tests should cover backing table absence, all protocol matcher combinations, NAT vs non-NAT, update failure preserving old rule, count action cleanup, and matcher refcount/list removal.
