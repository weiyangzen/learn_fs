## sources/cloud-native/buildkit/util/network/netproviders/network.go

Purpose: selects and returns BuildKit network providers and optional exec proxy provider based on configured mode and platform support.

Important API/type: `Opt{CNI,Mode}` and `Providers(opt) (map[pb.NetMode]network.Provider, network.ProxyProvider, resolvedMode string, err error)`.

Control flow: supports `cni`, `host`, `bridge`, `auto`, and empty mode. `bridge` maps resolved mode to `cni`. Auto uses `BUILDKIT_NETWORK_BRIDGE_AUTO=true` to prefer bridge, else CNI config path if present, else platform fallback. It always registers `UNSET` default and `NONE`; registers proxy provider on supported platforms with UNSET and optional HOST egress; registers HOST if available.

State/persistence: may instantiate CNI/bridge/proxy providers that create namespaces, bridges, pools, and certs. Dependencies: solver protobuf net modes, CNI provider, proxy provider, BuildKit network, `os`, `strconv`.

Integration points: worker/executor network setup. Risks: provider construction has side effects before full map return; auto fallback differs by platform; proxy egress providers include only default and host, not none. Test signals: no direct tests in this subset.
