<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_devgroup.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_devgroup.c

## Purpose
`xt_devgroup.c` implements matching by Linux network device group for input and output interfaces. It supports policy based on administrative grouping rather than interface names.

## Important APIs, Types, and Functions
`devgroup_mt()` checks `xt_in(par)` and `xt_out(par)` against `struct xt_devgroup_info`. `devgroup_mt_check_hooks()` rejects rules whose requested direction is impossible for the hook mask, and `devgroup_mt_checkentry()` validates flags before delegating to the hook checker.

## Control Flow, State, and Persistence
The match checks requested input and output group fields independently. For each enabled side, it requires the corresponding device pointer to exist and compares `dev->group` masked by `src_mask` or `dst_mask`, applying `XT_DEVGROUP_INVERT_SRC` or `XT_DEVGROUP_INVERT_DST`. No state is persisted.

## Dependencies and Integration Points
The module integrates with x_tables hook metadata and `struct net_device.group`. It registers one NFPROTO_UNSPEC match with IPv4 and IPv6 aliases.

## Risks and Test Signals
Risks include hook misuse, missing device pointers in local paths, and masks accidentally matching broad groups. Tests should cover PREROUTING/INPUT source-side matching, OUTPUT/POSTROUTING destination-side matching, FORWARD both-side matching, invalid flags, unsupported hook masks, inversion, and device group changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_devgroup.c -->
