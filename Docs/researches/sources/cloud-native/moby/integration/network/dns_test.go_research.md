<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/dns_test.go -->
# sources/cloud-native/moby/integration/network/dns_test.go

Purpose: tests daemon DNS behavior for fallback resolvers, avoiding recursive use of Docker's internal DNS as an external resolver, and DNS forwarding from IPv6-only bridge networks.

Important APIs/types/functions: `TestDaemonDNSFallback`, `TestIntDNSAsExtDNS`, and `TestExtDNSInIPv6OnlyNw` use daemon restart/config helpers, container `nslookup`, `network.StartDaftDNS`, `network.GenResolvConf`, `container.WithDNS`, and internal network creation options.

Control flow: DNS fallback starts a daemon with a bad DNS server followed by `8.8.8.8`, creates a network, runs `nslookup docker.com`, and polls for success. Internal-DNS test runs cases where external DNS list is only `127.0.0.11` or self plus external DNS, expecting `SERVFAIL` or a non-authoritative answer. IPv6-only test runs a local daft DNS server on loopback, starts a daemon using generated resolv.conf, creates an IPv6-only bridge network, and validates container lookup of `test.example`.

State/persistence: creates daemon instances, temp resolver configuration through daemon helper, networks, containers, and a local test DNS server. No repository state.

Dependencies/integration: depends on Linux daemon networking, internal DNS resolver behavior, external internet DNS for some cases, and host loopback resolver setup. Skips remote daemon, Windows, user namespace, and rootless modes where unsupported.

Risks: tests can be flaky if external DNS is unreachable or blocked. The internal DNS address is a special Docker resolver constant; behavior changes require clear compatibility decisions. IPv6-only DNS relies on host resolver visibility from the daemon namespace.

Test signals: passing tests show resolver fallback works, self-recursive resolver configurations fail safely instead of looping, and IPv6-only networks can still use external DNS via the daemon resolver path.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/dns_test.go -->
