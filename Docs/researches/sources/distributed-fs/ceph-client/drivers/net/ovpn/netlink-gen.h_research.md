# sources/distributed-fs/ceph-client/drivers/net/ovpn/netlink-gen.h

Purpose: generated YNL header declaring ovpn generic netlink policies, command handlers, multicast group indexes, and family object.

Important APIs/types/functions: declares `ovpn_*_nl_policy` arrays, pre/post doit hooks, peer/key command handler prototypes, `OVPN_NLGRP_PEERS`, and `extern struct genl_family ovpn_nl_family`.

Control flow: no runtime logic. It forms the compile-time contract between generated `netlink-gen.c` and hand-written `netlink.c` plus registration code.

State and persistence: no state in the header; it declares generated static data defined in `netlink-gen.c`.

Dependencies and integration: includes generic netlink headers and UAPI `linux/ovpn.h`. The file is generated from `Documentation/netlink/specs/ovpn.yaml` and should not be manually edited.

Risks: prototype or policy declaration drift breaks build or command dispatch. Because this is generated, fixes should be made in the YAML/spec or generator inputs, then regenerated.

Test signals: compile ovpn netlink sources, regenerate and diff, verify all declared handlers are implemented, and load the module to ensure family registration links against the declared `ovpn_nl_family`.
