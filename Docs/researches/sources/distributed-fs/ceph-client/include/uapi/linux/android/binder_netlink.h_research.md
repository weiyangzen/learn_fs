<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/android/binder_netlink.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/android/binder_netlink.h

## Purpose
Defines the generated generic-netlink family used by Binder to report errors/events to listeners.

## Important APIs, Types, And Functions
Exports family name/version, report attributes for error, context, source/target pid/tid, reply flag, transaction flags, code, and data size. `BINDER_CMD_REPORT` is the command and `BINDER_MCGRP_REPORT` is the multicast group.

## Control Flow
The Binder kernel code emits a `BINDER_CMD_REPORT` generic-netlink message to the report multicast group. Userspace subscribes to the family/group and parses the fixed attributes.

## State And Persistence
No persistent state is defined here. Events are transient multicast netlink records; listeners must handle loss or late subscription.

## Dependencies And Integration Points
Generated from `Documentation/netlink/specs/binder.yaml` and integrates with YNL tooling, Binder driver event paths, and diagnostic/monitoring daemons.

## Risks And Edge Cases
Generated headers should not be hand-edited. Attribute availability may vary by event; consumers must not assume every optional field is present. Multicast delivery is best-effort.

## Test Signals
YNL spec regeneration checks, netlink family discovery, subscription tests, emitted report parsing, and unknown-attribute tolerance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/android/binder_netlink.h -->
