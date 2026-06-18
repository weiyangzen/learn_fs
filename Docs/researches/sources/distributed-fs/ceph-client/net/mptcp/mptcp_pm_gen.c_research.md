<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/mptcp_pm_gen.c -->
# sources/distributed-fs/ceph-client/net/mptcp/mptcp_pm_gen.c

## Purpose
Generated Generic Netlink policy and ops table for the MPTCP path-manager family, derived from `Documentation/netlink/specs/mptcp_pm.yaml`.

## Important APIs, Types, and Functions
Defines `mptcp_pm_address_nl_policy` for nested endpoint address attributes and per-command policies for add, delete, get, flush, set/get limits, set flags, announce, remove, subflow create, and subflow destroy. `mptcp_pm_nl_ops` maps eleven `MPTCP_PM_CMD_*` commands to their doit/dump callbacks and policies.

## Control Flow
There is no custom runtime logic beyond static genl dispatch metadata. The genetlink core uses these policy arrays to validate and dispatch incoming messages to functions implemented by PM backend/userspace code.

## State and Persistence
The file owns static constant policy and ops tables. No mutable state is stored.

## Dependencies and Integration Points
Depends on genetlink/netlink policy APIs and `uapi/linux/mptcp_pm.h`. It is included in the MPTCP core build and consumed by the PM netlink family registration and callback implementations in files such as `pm_kernel.c` and userspace PM code.

## Risks
As generated code, manual edits risk divergence from the YAML spec. Callback prototypes, maxattr values, admin permission flags, and nested policy shapes must match UAPI expectations. `GENL_DONT_VALIDATE_STRICT` is used throughout, so callback-side validation remains important.

## Test Signals
YNL/genetlink selftests for every PM command, policy rejection of malformed nested address attributes, permission checks on admin commands, dump support for GET_ADDR, and regeneration diff checks from the YAML spec.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/mptcp_pm_gen.c -->
