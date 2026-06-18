<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/resolver_unix.go -->
## sources/cloud-native/moby/daemon/libnetwork/resolver_unix.go

Purpose: Unix/Linux NAT setup for the embedded DNS resolver.

Important APIs/functions: `setupNAT` selects nftables or iptables. `setupIptablesNAT` programs `DOCKER_OUTPUT` and `DOCKER_POSTROUTING` chains. `setupNftablesNAT` creates a `docker-dns` table with DNAT/SNAT base chains.

Control flow: `setupNAT` extracts UDP/TCP listener addresses and ports, then chooses nftables when enabled. iptables path runs inside the sandbox namespace via backend `ExecFunc`, creates or flushes custom chains, inserts jumps from OUTPUT/POSTROUTING, then inserts DNAT/SNAT rules to map port 53 to the actual listener ports. nftables path builds equivalent output and postrouting chains and applies them in namespace.

State and persistence: mutates per-sandbox firewall state. Rules are tied to the sandbox namespace lifecycle.

Dependencies and integration points: depends on libnetwork `iptables`, internal `nftables`, and resolver sockets from `SetupFunc`.

Risks and test signals: firewall rule idempotency and chain cleanup are critical. IPv6 is TODO. Tests indirectly exercise DNS startup and forwarding on Unix.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/resolver_unix.go -->
