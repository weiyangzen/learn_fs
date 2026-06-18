# sources/distributed-fs/ceph-client/net/ipv4/fou_nl.c

## Purpose
`fou_nl.c` is generated generic-netlink glue for the FOU family. It defines attribute validation policy and operation dispatch entries used by `fou_core.c`.

## Important APIs, Types, And Functions
The file exports `fou_nl_policy[FOU_ATTR_IFINDEX + 1]` and `fou_nl_ops[3]`. Policy entries type-check local port, address family, IP protocol, encap type, remote checksum flag, IPv4/IPv6 local and peer addresses, peer port, and interface index. Operations map `FOU_CMD_ADD`, `FOU_CMD_DEL`, and `FOU_CMD_GET` to `fou_nl_add_doit`, `fou_nl_del_doit`, `fou_nl_get_doit`, and `fou_nl_get_dumpit`.

## Control Flow
Generic netlink validates incoming attributes against `fou_nl_policy` and dispatches commands through `fou_nl_ops`. Add and delete require admin permission. Get supports both single-object `doit` and dump iteration. Strict validation is disabled for compatibility with the generated YNL policy flags used here.

## State And Persistence
This file owns no runtime state beyond read-only policy and operation tables. The tables persist for the module lifetime and are referenced by the `fou_nl_family` in `fou_core.c`.

## Dependencies And Integration Points
It depends on `<uapi/linux/fou.h>`, netlink/genetlink kernel APIs, and declarations from `fou_nl.h`. It is generated from `Documentation/netlink/specs/fou.yaml`, so manual edits should be avoided.

## Risks
The main risk is drift from the YAML spec or from the handlers in `fou_core.c`. A wrong attribute type can allow invalid configuration or reject valid user space requests. Operation count and command ordering must remain aligned with `fou_nl_family`.

## Test Signals
Validate YNL regeneration diffs, generic netlink family introspection, add/delete permission enforcement, malformed attribute rejection, IPv6 exact-length enforcement, and GET dump behavior against `fou_core.c` parser expectations.
