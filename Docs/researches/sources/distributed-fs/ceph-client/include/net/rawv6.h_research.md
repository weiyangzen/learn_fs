# sources/distributed-fs/ceph-client/include/net/rawv6.h

Purpose: declares IPv6 raw socket hash state, match/receive/error delivery functions, and optional Mobile IPv6 header filter registration.

Important APIs and types: `raw_v6_hashinfo` is the IPv6 raw hash table. `raw_v6_match()` matches sockets by netns, protocol, local/remote IPv6 addresses, and ingress device indices. APIs include raw abort, ICMPv6 error delivery, local-deliver predicate, rawv6 receive, and optional mobility-header filter register/unregister.

Control flow: IPv6 receive dispatch asks rawv6 to deliver packets to matching raw sockets; ICMPv6 errors are converted and delivered; Mobile IPv6 filters can intercept mobility header traffic when configured.

State and persistence: runtime socket hash entries and optional filter callback pointer(s); no durable state.

Dependencies and integration points: depends on IPv6 protocol dispatcher and raw socket core, with optional CONFIG_IPV6_MIP6.

Risks and test signals: risks include address/device matching mistakes, shared `raw_abort()` declaration consistency, ICMPv6 inner offset handling, and filter unregister races. Test raw IPv6 sockets, ICMPv6 errors, device-bound sockets, namespace isolation, and MIP6 filter module load/unload.
