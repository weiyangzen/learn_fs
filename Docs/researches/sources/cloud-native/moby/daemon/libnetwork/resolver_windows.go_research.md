<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/resolver_windows.go -->
## sources/cloud-native/moby/daemon/libnetwork/resolver_windows.go

Purpose: Windows resolver NAT stub.

Important APIs/functions: `func (r *Resolver) setupNAT(context.Context) error` returns nil.

Control flow: no firewall setup occurs for the embedded resolver on Windows through this path.

State and persistence: no state.

Dependencies and integration points: selected by Windows build tags so shared resolver startup compiles and runs without Unix iptables/nftables.

Risks and test signals: behavior depends on Windows networking/DNS integration elsewhere. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/resolver_windows.go -->
