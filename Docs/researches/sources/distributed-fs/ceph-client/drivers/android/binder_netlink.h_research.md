# sources/distributed-fs/ceph-client/drivers/android/binder_netlink.h

## Purpose
`binder_netlink.h` is the generated kernel-side header for Binder generic netlink support. It exposes the multicast group enum and the Binder generic-netlink family object.

## Important APIs, Types, And Functions
The header includes netlink and generic-netlink kernel headers plus the Binder netlink UAPI header. It defines enum value `BINDER_NLGRP_REPORT` and declares `extern struct genl_family binder_nl_family`.

## Control Flow
The header has no executable flow. Binder netlink implementation and registration code include it to reference the family and report group.

## State And Persistence
No state is stored here. The declared family is defined in `binder_netlink.c` and persists after registration.

## Dependencies
It depends on generated UAPI definitions from `uapi/linux/android/binder_netlink.h` and on generic netlink infrastructure. The comment states it is generated from `Documentation/netlink/specs/binder.yaml`.

## Integration Points
Consumers use this header to register or send messages through Binder's generic-netlink family and report multicast group. It is part of the kernel/userspace reporting ABI.

## Risks
Manual edits can diverge from the YAML spec and UAPI header. Adding or renumbering groups is ABI-relevant for userspace subscribers. If included without generic-netlink support, configuration dependencies must ensure the required types are available.

## Test Signals
Regenerate from the YAML spec and diff, build Binder netlink users, inspect generic-netlink family/group IDs at runtime, and run userspace subscription tests for Binder reports.
