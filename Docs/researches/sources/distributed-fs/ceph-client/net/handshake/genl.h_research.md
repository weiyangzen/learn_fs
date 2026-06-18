<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/genl.h -->
# sources/distributed-fs/ceph-client/net/handshake/genl.h

## Purpose
Generated header for the handshake generic-netlink family, shared by generated family data and handwritten netlink handlers.

## APIs, Types, and Functions
Declares `handshake_nl_accept_doit()`, `handshake_nl_done_doit()`, multicast group indexes `HANDSHAKE_NLGRP_NONE` and `HANDSHAKE_NLGRP_TLSHD`, and external `struct genl_family handshake_nl_family`.

## Control Flow, State, and Persistence
The header has no control flow or state. It provides the compile-time linkage contract between generated netlink registration code and the implementation in `netlink.c`.

## Dependencies and Integration
Depends on netlink/genetlink headers and the handshake UAPI. It is generated from `Documentation/netlink/specs/handshake.yaml` and integrated by `genl.c` and `netlink.c`.

## Risks and Test Signals
Risks are generated-code drift and stale declarations after UAPI changes. Test signals include clean compilation after regenerating YNL sources and successful registration of `handshake_nl_family`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/genl.h -->
