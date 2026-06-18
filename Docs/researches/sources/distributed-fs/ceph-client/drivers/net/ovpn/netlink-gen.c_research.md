# sources/distributed-fs/ceph-client/drivers/net/ovpn/netlink-gen.c

Purpose: generated YNL kernel source for the ovpn generic netlink family: attribute policies, split operation table, multicast groups, and family descriptor.

Important APIs/types/functions: exports nested policy arrays for key config, key direction, peer attributes, and command inputs. `ovpn_nl_ops` maps commands `PEER_NEW`, `PEER_SET`, `PEER_GET` do/dump, `PEER_DEL`, `KEY_NEW`, `KEY_GET`, `KEY_SWAP`, and `KEY_DEL` to hand-written handlers. `ovpn_nl_family` defines family name/version, netns support, parallel ops, ops, and peer multicast group.

Control flow: genetlink core uses the policies to validate incoming attributes, then invokes generated ops entries with `ovpn_nl_pre_doit()`/`post_doit()` around hand-written command handlers where configured. Dump peer get uses a separate dumpit op and policy.

State and persistence: static const policies and a `__ro_after_init` family descriptor. No runtime mutable state except genetlink registration state handled elsewhere.

Dependencies and integration: generated from `Documentation/netlink/specs/ovpn.yaml`; includes UAPI `linux/ovpn.h`, generic netlink, and prototypes from `netlink-gen.h`. It must match hand-written `netlink.c` handlers and UAPI enum values.

Risks: manual edits would be overwritten and can desynchronize from the YAML spec. Attribute range limits, max slot/key id/cipher values, and nested policy bounds are ABI-sensitive. Parallel ops require handlers to perform their own object locking.

Test signals: regenerate from YAML and compare, register family, validate malformed attributes are rejected, exercise all commands, test peer dump, and subscribe to the peers multicast group.
