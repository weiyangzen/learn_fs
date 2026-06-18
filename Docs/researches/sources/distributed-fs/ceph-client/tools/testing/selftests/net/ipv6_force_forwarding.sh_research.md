# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ipv6_force_forwarding.sh

Purpose: Tests the IPv6 per-interface `force_forwarding` sysctl, proving it forwards packets even when global IPv6 forwarding is disabled.

Important commands: Sources `lib.sh`, creates three namespaces, two veth pairs, IPv6 addresses and routes, manipulates `net.ipv6.conf.all.forwarding` and `net.ipv6.conf.<if>.force_forwarding`, and uses `ping -6`.

Control flow: Setup builds sender, router, and receiver namespaces with routes through the router and disables global forwarding in the router namespace. The test first confirms ping fails when `force_forwarding` is zero on both router interfaces, then sets it to one on both interfaces and confirms ping succeeds. It skips if the per-interface sysctl file is absent.

State and persistence: Temporary namespaces and sysctl values only. Cleanup removes namespaces.

Dependencies and integration: Requires root, `lib.sh`, kernel support for `force_forwarding`, IPv6, veth, and ping.

Risks: Uses only one ping per phase, so transient neighbor discovery timing could matter. It requires enabling both ingress and egress router interfaces.

Test signals: Returns pass when disabled forwarding blocks traffic and forced forwarding permits it; returns kselftest skip when unsupported.
