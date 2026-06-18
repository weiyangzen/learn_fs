# sources/distributed-fs/ceph-client/tools/net/ynl/tests/rt-route.c

Purpose: rtnetlink route dump selftest for generated `rt-route` bindings.

Important APIs/functions: `rt_route_print()` ignores local-table routes, optionally resolves output interface, formats destination and gateway binary addresses with `inet_ntop()`, and uses header fields such as family/table/dst length. Fixture opens `ynl_rt_route_family`.

Control flow/state: `dump` expects connected routes from wrapper-provided addresses: `192.168.1.0/24` and `2001:db8::/64`. It allocates `rt_route_getroute_req_dump`, performs dump, iterates all non-local routes, and sets found flags based on address length, prefix length, and `memcmp()`.

Dependencies/integration: requires route YAML-generated bindings, YNL runtime, IPv4/IPv6, kselftest, and netdevsim setup from `rt-route.sh`.

Risks/test signals: validates fixed `rtmsg` headers, binary route attributes, dump list handling, and route table filtering. Environment route noise is tolerated except local table routes. Failure can reflect missing setup addresses or generated parser regressions.
