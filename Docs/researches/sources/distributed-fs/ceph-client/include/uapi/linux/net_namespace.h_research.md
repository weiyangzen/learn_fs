# sources/distributed-fs/ceph-client/include/uapi/linux/net_namespace.h

## Purpose
Defines rtnetlink namespace ID attributes for creating, querying, and translating network namespace identifiers.

## Important APIs, Types, And Functions
Exports `NETNSA_NONE`, `NETNSA_NSID_NOT_ASSIGNED`, `NETNSA_NSID`, `NETNSA_PID`, `NETNSA_FD`, `NETNSA_TARGET_NSID`, `NETNSA_CURRENT_NSID`, and `NETNSA_MAX`.

## Control Flow
Userspace sends RTM_NEWNSID/RTM_GETNSID messages with pid or fd identifying a namespace and receives/sets namespace IDs, optionally translating from current to target namespace IDs.

## State, Persistence, And Dependencies
Namespace ID mappings persist in kernel net namespace state. No external include dependencies.

## Integration Points
Used by iproute2, container runtimes, namespace-aware netlink tooling, and rtnetlink.

## Risks
`NETNSA_NSID_NOT_ASSIGNED` is negative while attrs are enum IDs; callers must not confuse sentinel values with attribute numbers. Fd/pid lifetimes affect namespace lookup.

## Test Signals
Validate nsid assignment/query, pid/fd lookup, target/current translation, unassigned sentinel handling, and namespace teardown behavior.
