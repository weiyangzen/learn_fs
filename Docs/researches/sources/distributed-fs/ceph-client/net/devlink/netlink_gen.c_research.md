
# sources/distributed-fs/ceph-client/net/devlink/netlink_gen.c

## Purpose
This auto-generated YNL kernel source binds the devlink generic-netlink family to the command handlers implemented across `net/devlink/*.c`. It is generated from `Documentation/netlink/specs/devlink.yaml` and should not be edited directly. Its primary responsibilities are attribute policy declaration, sparse enum validation, and construction of the `devlink_nl_ops[75]` split-ops table consumed by the devlink family registration code.

## Important APIs, Types, And Functions
The file exports common nested policies used by hand-written handlers: `devlink_dl_port_function_nl_policy`, `devlink_dl_rate_tc_bws_nl_policy`, and `devlink_dl_selftest_id_nl_policy`. It defines per-command `nla_policy` arrays for get/set/new/delete/read/dump commands covering core devlink devices, ports, shared buffers, dpipe, resources, reload, params, regions, health reporters, flash update, traps, rates, linecards, selftests, and notification filters.

`devlink_attr_param_type_validate()` is the notable custom validator. It accepts only the sparse `DEVLINK_VAR_ATTR_TYPE_*` values used for reload-action statistics and rejects unknown enum values with an extended-ack message. `devlink_attr_index_range` gives `DEVLINK_ATTR_INDEX` full unsigned 32-bit range validation through `NLA_POLICY_FULL_RANGE`.

The central exported object is `const struct genl_split_ops devlink_nl_ops[75]`. Each entry maps a `DEVLINK_CMD_*` command to a policy, max attribute number, optional `pre_doit`/`post_doit`, a `doit` or `dumpit` handler, capability flags, and legacy validation suppression flags.

## Control Flow
At runtime, generic netlink dispatches an incoming devlink command through the table. For `doit` operations the selected pre-hook resolves and locks the target devlink object, and sometimes a port, before calling the implementation handler. Common hooks include `devlink_nl_pre_doit`, `devlink_nl_pre_doit_port`, `devlink_nl_pre_doit_port_optional`, and `devlink_nl_pre_doit_dev_lock`; post hooks unlock the same state. Dump operations generally call handler-specific dump functions and rely on `devlink_nl_dumpit()` for iteration across registered instances.

Administrative operations are marked with `GENL_ADMIN_PERM`; read-only get/dump paths usually have only `GENL_CMD_CAP_DO` or `GENL_CMD_CAP_DUMP`. Region read and some health dump paths use dump-specific validation flags because their request attributes are read from dump context rather than a normal `doit` request.

## State And Persistence
This file owns no mutable runtime state. Policies and the ops table are static const data. Persistence is indirect: whatever handler mutates device, port, param, region, resource, rate, or shared-buffer state does so after this layer validates and dispatches the request.

## Dependencies And Integration Points
The file includes netlink/genetlink headers, `netlink_gen.h`, and UAPI `linux/devlink.h`. It is built into devlink core by `net/devlink/Makefile` and references all handler symbols declared in `netlink_gen.h`. The generated policy constants are consumed by hand-written nested parsers in files such as `port.c` and `rate.c`.

## Risks And Edge Cases
The largest risk is spec drift. Because the file is generated, local edits would be overwritten and changes should be made in the YAML spec and regenerated. Handler declarations, policy max attributes, and `devlink_nl_ops` size must remain synchronized with `netlink_gen.h` and the UAPI enum values.

Several ops retain `GENL_DONT_VALIDATE_STRICT` or dump validation bypasses for compatibility. That is intentional for legacy devlink clients but means detailed semantic validation remains in handlers. Policy validation catches types and simple ranges only; cross-field requirements such as "region direct read cannot use a snapshot id" or "rate TC bandwidth must include every traffic class" are enforced later.

## Test Signals
Coverage for this file is mostly integration-level: successful registration of the devlink family and devlink selftests/scripts exercising commands through generic netlink. Local selftest references include hardware-driver tests for devlink port splitting, rate traffic-class bandwidth, and mlxsw resources. The best regression signal for this generated layer is that command dispatch reaches the expected `devlink_nl_*` handlers with the expected policy behavior after regenerating from the YAML spec.
