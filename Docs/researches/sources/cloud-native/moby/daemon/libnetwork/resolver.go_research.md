<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/resolver.go -->
## sources/cloud-native/moby/daemon/libnetwork/resolver.go

Purpose: Docker embedded DNS server implementation. It listens in the sandbox namespace, answers Docker-owned names, and forwards other DNS queries to configured external resolvers.

Important APIs/types/functions: `DNSBackend` defines sandbox/network callbacks. `Resolver` stores backend, external DNS lists, UDP/TCP servers, forwarding policy, semaphore, and logger. Public methods include `NewResolver`, `SetupFunc`, `Start`, `Stop`, `SetExtServers`, `SetForwardingPolicy`, `SetExtServersForSrc`, `NameServer`, and `ResolverOptions`. Query handlers include A/AAAA, MX, PTR, SRV, forwarding, and upstream exchange.

Control flow: `SetupFunc` binds UDP/TCP sockets. `Start` installs NAT redirect rules via OS-specific `setupNAT` and starts DNS servers. `serveDNS` dispatches local query handlers, truncates authoritative responses to negotiated UDP/TCP sizes, handles ndots behavior, and otherwise calls `forwardExtDNS`. Forwarding selects per-source or global upstreams, enforces `maxConcurrent`, skips host-loopback upstreams when proxying is disabled, retries on SERVFAIL/REFUSED, and records A/AAAA responses with the backend.

State and persistence: all state is in-memory. External DNS is persisted by sandbox state, not resolver itself.

Dependencies and integration points: uses `miekg/dns`, OpenTelemetry, rate limiting, sandbox `ExecFunc`, and network service records.

Risks and test signals: concurrency, namespace dialing, truncation, invalid records, and forwarding policy are sensitive. Tests cover oversized upstream replies, SERVFAIL, NXDOMAIN proxying, invalid PTR, local A/MX resolution, and upstream retry.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/resolver.go -->
