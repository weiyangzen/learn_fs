<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/genl.c -->
# sources/distributed-fs/ceph-client/net/handshake/genl.c

## Purpose
Generated generic-netlink family registration data for the handshake UAPI defined by `Documentation/netlink/specs/handshake.yaml`.

## APIs, Types, and Functions
Defines netlink policies for `HANDSHAKE_CMD_ACCEPT` and `HANDSHAKE_CMD_DONE`, the split ops table dispatching to `handshake_nl_accept_doit()` and `handshake_nl_done_doit()`, multicast groups `none` and `tlshd`, and the exported `handshake_nl_family`.

## Control Flow, State, and Persistence
There is no complex runtime logic beyond generic-netlink dispatch. The ops table enforces admin permission for ACCEPT, allows DONE without admin permission, and binds policies and max attribute IDs. The family is netns-aware, permits parallel ops, and is registered/unregistered by `netlink.c`.

## Dependencies and Integration
Depends on generated UAPI constants in `uapi/linux/handshake.h`, generic-netlink core, and handler functions declared in `genl.h`. It is generated code and should be updated from the YAML spec rather than edited directly.

## Risks and Test Signals
Risks include generated policy drift from the YAML spec, handler-class max constraints diverging from UAPI, and multicast group indexes changing without matching userspace. Test signals are family registration, YNL conformance tests, ACCEPT requiring admin permission, DONE fd/status parsing, and multicast listener group behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/handshake/genl.c -->
