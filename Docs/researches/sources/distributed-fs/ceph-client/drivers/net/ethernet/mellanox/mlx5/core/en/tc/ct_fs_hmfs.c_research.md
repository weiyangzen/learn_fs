# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/ct_fs_hmfs.c

Purpose: Provides the hardware steering (HWS/HMFS) backend for CT flow steering using HWS tables, BWC matchers, HWS actions, and BWC rules.

Important APIs: `mlx5_ct_fs_hmfs_ops_get()` returns ops. Init captures CT, CT-NAT, and post-CT HWS tables and creates shared forward and last actions. Rule add validates the flow rule, gets a matcher keyed by NAT/IP version/protocol, fills counter/modify/fwd/last actions, creates a BWC rule, and stores counter/matcher refs. Update replaces rule actions and swaps counter ownership. Delete destroys the rule, releases the HWS counter action, matcher, and wrapper.

State and persistence: `struct mlx5_ct_fs_hmfs` owns HWS table pointers, context, shared actions, a lock, and two arrays of six refcounted matchers for NAT/non-NAT combinations. Per-rule state owns a BWC rule, matcher ref, and counter pointer.

Dependencies and integration: Uses HWS pools/actions/tables, flow counters as HWS actions, CT validity helpers, IP version helpers, modify header HWS action data, and post-CT table forwarding.

Risks and tests: Matcher refcounting and action ownership are high risk. `get_matcher_idx()` encodes protocol combinations; unsupported protocols collapse to UDP slot when not TCP/GRE. Error paths must release `mlx5_fc_get_hws_action()` ownership. Tests should cover missing HWS tables, matcher creation races, NAT and non-NAT matchers, IPv4/IPv6 TCP/UDP/GRE, add failure after matcher get, action update failure, counter swap, and destroy order.
