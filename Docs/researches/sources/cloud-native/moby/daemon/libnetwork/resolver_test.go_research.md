<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/resolver_test.go -->
## sources/cloud-native/moby/daemon/libnetwork/resolver_test.go

Purpose: unit/regression tests for resolver query handling and upstream forwarding.

Important APIs/types/functions: fake `dns.ResponseWriter` (`tstwriter`), fake address type, `noopDNSBackend`, `badSRVDNSBackend`, `ptrDNSBackend`, helper response assertions, and `testLogger`.

Control flow: `TestOversizedDNSReply` runs a UDP upstream that returns a non-EDNS reply over 512 bytes and verifies the resolver forwards it successfully. `TestReplySERVFAIL` checks internal errors, disabled proxying, and missing upstreams. `TestProxyNXDOMAIN` verifies an upstream NXDOMAIN with SOA is preserved. `TestInvalidReverseDNS` confirms invalid PTR answers produce SERVFAIL.

State and persistence: only transient test DNS servers and resolver memory. No sandbox persistence.

Dependencies and integration points: uses `miekg/dns`, `netnsutils.AssertSocketSameNetNS`, log redirection, and fake `DNSBackend` implementations.

Risks and test signals: high-value coverage for production DNS edge cases: oversized replies, namespace leakage canary, upstream response preservation, and robust error replies. Tests avoid full daemon setup except local sockets.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/resolver_test.go -->
