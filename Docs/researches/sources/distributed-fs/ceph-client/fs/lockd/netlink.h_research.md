# sources/distributed-fs/ceph-client/fs/lockd/netlink.h

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/netlink.h` is the generated internal header for lockd's generic-netlink interface. It declares command handlers and the family object produced from the lockd netlink YAML specification. The source was read as a complete 20-line generated file.

## Important APIs, Types, and Functions

The header declares `lockd_nl_server_set_doit`, `lockd_nl_server_get_doit`, and `extern struct genl_family lockd_nl_family`.

## Control Flow

There is no executable flow in this header. It allows the generated family table in `netlink.c` and the hand-written command implementations to share prototypes.

## State and Persistence Behavior

No state is owned here. The family object is defined in `netlink.c`, and persistent configuration lives in `struct lockd_net`.

## Dependencies and Integration Points

The header includes generic netlink headers and UAPI `linux/lockd_netlink.h`, tying generated kernel dispatch to userspace-visible command and attribute definitions.

## Risks and Edge Cases

Manual edits will be lost on regeneration. Prototype drift between this generated header and command implementation will fail builds.

## Test Signals

Build coverage with lockd netlink enabled, regeneration checks from the YAML spec, and netlink command selftests that include this family.
