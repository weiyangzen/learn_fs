
# sources/distributed-fs/ceph-client/net/devlink/netlink_gen.h

## Purpose
This auto-generated YNL header is the declaration boundary between the generated devlink generic-netlink table in `netlink_gen.c` and the hand-written devlink implementation files. It declares exported nested policies, the split-ops table, pre/post dispatch hooks, and every `devlink_nl_*` command handler referenced by the generated ops table.

## Important APIs, Types, And Functions
The header exports three common nested policies: `devlink_dl_port_function_nl_policy`, `devlink_dl_rate_tc_bws_nl_policy`, and `devlink_dl_selftest_id_nl_policy`. It declares `extern const struct genl_split_ops devlink_nl_ops[75]`, which is the command table installed by the devlink family.

Pre/post hooks declared here are `devlink_nl_pre_doit()`, `devlink_nl_pre_doit_port()`, `devlink_nl_pre_doit_port_optional()`, `devlink_nl_pre_doit_dev_lock()`, `devlink_nl_post_doit()`, and `devlink_nl_post_doit_dev_lock()`. They are implemented outside this header and provide object lookup and lock management around command handlers.

The handler declarations span all devlink feature areas: device get/reload/info/flash/selftests/notify-filter, port get/set/new/del/split/unsplit and port params, shared buffers, eswitch, dpipe, resources, params, regions, health reporters, traps/groups/policers, rates, and linecards.

## Control Flow
The header has no runtime control flow. Its declarations allow `netlink_gen.c` to compile references to functions implemented in other translation units and allow `devl_internal.h` to include the generated interface. The actual flow is generic-netlink dispatch into `devlink_nl_ops`, then into these declared handlers.

## State And Persistence
No state is owned here. The only state-like declaration is the static ops table exported from `netlink_gen.c`; all mutable devlink state lives in `struct devlink`, `struct devlink_port`, xarrays, lists, and driver callbacks in the hand-written implementation.

## Dependencies And Integration Points
The file includes `<net/netlink.h>`, `<net/genetlink.h>`, and UAPI `<uapi/linux/devlink.h>`. It is included by `devl_internal.h`, which means most devlink core implementation files see the generated policies and handler prototypes through the internal header. It must stay synchronized with `netlink_gen.c` and the YAML netlink spec.

## Risks And Edge Cases
Because this header is generated, manual edits create a high maintenance risk and may be lost on regeneration. The fixed `devlink_nl_ops[75]` declaration must match the generated source exactly; a command-table size mismatch would be caught at compile time. Function prototype drift between hand-written handler implementations and this header is also compile-time visible.

## Test Signals
The test signal is compile/link coverage plus devlink generic-netlink command execution. If any handler prototype, exported policy, or table size diverges, the devlink object will fail to build. Runtime selftests that call devlink commands indirectly validate that the declarations match generated dispatch.
