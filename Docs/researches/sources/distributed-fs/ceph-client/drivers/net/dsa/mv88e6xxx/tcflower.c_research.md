# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/tcflower.c

## Purpose
Implements a minimal tc flower offload frontend that parses supported flow keys and installs/removes TCAM entries.

## Important APIs, Types, and Functions
Exports `mv88e6xxx_cls_flower_add`, `mv88e6xxx_cls_flower_del`, and `mv88e6xxx_flower_teardown`. Internal `mv88e6xxx_flower_parse_key` supports basic keys, control address type, and IPv4 source/destination addresses. Supported action is `FLOW_ACTION_TRAP`.

## Control Flow and State
Add validates TCAM support, parses keys into `mv88e6xxx_tcam_key`, locks registers, rejects duplicate cookies, allocates an entry, copies priority/cookie/key, translates trap to a DPV replace action targeting the CPU port, restricts source port vector to the ingress port, and calls `mv88e6xxx_tcam_entry_add`. Delete finds by cookie and delegates to TCAM delete. Teardown frees all software entries without hardware reprogramming, intended for driver cleanup.

## Dependencies and Integration Points
Depends on DSA switch private data, flow dissector APIs, netlink extack, TCAM helpers, port masks, and DSA upstream port lookup. It integrates with the DSA cls_flower callback surface.

## Risks and Test Signals
Risks include unsupported keys/actions returning clear extack messages, endian/offset mistakes for EtherType/IP fields, duplicate cookie handling, memory leaks on add failure, and teardown leaving stale hardware unless paired with hardware flush. Test signals include tc flower add/delete tests, trap-to-CPU packet delivery, unsupported key/action negative tests, and repeated add/delete ordering with priorities.
