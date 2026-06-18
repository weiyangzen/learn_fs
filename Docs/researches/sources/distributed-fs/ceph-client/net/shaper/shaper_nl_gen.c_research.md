# sources/distributed-fs/ceph-client/net/shaper/shaper_nl_gen.c

## Purpose
Auto-generated YNL generic-netlink source for the net shaper family. It defines attribute validation policies, split operation tables, and the `net_shaper_nl_family` descriptor that binds netlink commands to hand-written callbacks in `shaper.c`.

## Important APIs, Types, And Functions
Exports `net_shaper_handle_nl_policy`, `net_shaper_leaf_info_nl_policy`, and `net_shaper_nl_family`. The ops table maps `NET_SHAPER_CMD_GET`, `SET`, `DELETE`, `GROUP`, and `CAP_GET` doit/dump variants to `net_shaper_nl_*` callbacks.

## Control Flow
Netlink core uses the policy arrays to validate top-level and nested attributes before invoking callbacks. Do commands run pre/doit/post hooks; dump commands run start/dumpit/done hooks. Administrative permission is required for set, delete, and group. The family is namespace-aware and allows parallel operations, relying on the hand-written callbacks to acquire device references and locks.

## State And Persistence
No mutable runtime state beyond the registered family descriptor. Policies and ops are static const data.

## Dependencies And Integration Points
Generated from `Documentation/netlink/specs/net_shaper.yaml`, includes `uapi/linux/net_shaper.h`, and requires all callback prototypes from `shaper_nl_gen.h` to be implemented by `shaper.c`.

## Risks
Manual edits would be overwritten. Drift between YAML, UAPI enums, policies, and hand-written parser expectations can admit invalid messages or reject valid ones. `parallel_ops = true` increases reliance on correct per-device locking in callbacks.

## Test Signals
Regenerate with `tools/net/ynl/ynl-regen.sh`, compile-check callback symbol coverage, run YAML/YNL netlink selftests for policy validation, and fuzz nested handle/leaves attributes.
