# sources/distributed-fs/ceph-client/security/selinux/ss/services.h

## Purpose
`services.h` declares the compact shared types used by the SELinux security server and SID conversion code. It avoids exposing most `services.c` internals while giving policy load, sidtab conversion, and extended permission code a common contract.

## Important APIs, Types, and Functions
`struct selinux_mapping` maps one kernel security class to a policy class value and policy permission bits. `struct selinux_map` stores the mapping array and size. `struct selinux_policy` bundles the active `sidtab`, `policydb`, class/permission map, and `latest_granting` sequence. `struct convert_context_args` carries old/new policydb pointers for context conversion. Prototypes cover extended permission driver discovery/decision computation and `services_convert_context()`.

## Control Flow
The mapping types are populated during `security_load_policy()` and consumed by access computation to translate kernel class/permission numbering into policy numbering and back. Conversion args are passed by `sidtab_convert()` into `services_convert_context()` for every existing SID context during policy reload.

## State and Persistence
`struct selinux_policy` is the RCU-published unit of SELinux policy state. Its `latest_granting` value persists as the sequence used to invalidate AVC/audit users after policy changes.

## Dependencies and Integration Points
The header depends on `policydb.h` and is consumed by `services.c`, `sidtab.c`, and other SELinux files that need active policy or conversion interfaces. It is part of the boundary between parsed policy state and runtime decision services.

## Risks
Changing these structures affects RCU-published policy lifetime and sidtab conversion. Mapping array bounds and permission bit widths must stay aligned with `secclass_map` and `u32` access vectors.

## Test Signals
Compile-time coverage should include extended permissions and policy reload. Runtime signals include AVC decisions after policy load, policy reload with existing SIDs, and ioctl/netlink extended permission checks.
