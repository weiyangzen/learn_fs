# sources/distributed-fs/ceph-client/tools/net/ynl/tests/rt-addr.c

Purpose: rtnetlink address dump selftest for generated `rt-addr` bindings.

Important APIs/functions: `rt_addr_print()` resolves interface names, validates address length is IPv4 or IPv6, and formats addresses with `inet_ntop()`. Fixture opens `ynl_rt_addr_family`. `dump` allocates a getaddr dump request, calls `rt_addr_getaddr_dump()`, and searches for addresses configured by the wrapper: `192.168.1.1` and `2001:db8::1`.

Control flow/state: expected addresses are encoded with `inet_pton()`. The returned dump list is iterated and freed. Kernel interface address state is established outside the binary by `rt-addr.sh`/`ynl_nsim_lib.sh`.

Dependencies/integration: depends on rtnetlink address YAML-generated headers, YNL runtime, kselftest, IPv4/IPv6 support, and netdevsim setup.

Risks/test signals: tests binary blob parsing, fixed `ifaddrmsg` header fields, address length metadata, and dump completeness. Failure to find addresses may be setup, namespace, or parsing related.
