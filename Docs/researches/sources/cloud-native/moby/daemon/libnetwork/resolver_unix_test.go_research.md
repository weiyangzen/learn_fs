<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/resolver_unix_test.go -->
## sources/cloud-native/moby/daemon/libnetwork/resolver_unix_test.go

Purpose: Unix/Linux integration tests for resolver behavior with real libnetwork controller, bridge network, sandbox, and local upstream DNS server.

Important APIs/functions: `TestDNSIPQuery` builds a controller/network/endpoint/sandbox, injects service records, and calls `Resolver.serveDNS`. `TestDNSProxyServFail` starts a local TCP DNS server that fails once, configures two identical upstream entries, and verifies retry.

Control flow: the first test joins an endpoint to a sandbox, adds a service record, verifies case-insensitive A lookup, MX implicit success for known names, and SERVFAIL for unknown MX with proxying disabled. The second test runs in a test OS context, waits for the DNS server, then expects two upstream requests because the first returns SERVFAIL.

State and persistence: temporary controller datastore and kernel namespace state; all cleaned up through controller/network/sandbox deletion.

Dependencies and integration points: uses real libnetwork config, default IPAM, bridge network, `netnsutils`, and `miekg/dns`.

Risks and test signals: good integration signal but requires Linux namespace/network support. Covers local service records and upstream retry semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/resolver_unix_test.go -->
