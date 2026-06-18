## sources/cloud-native/buildkit/util/network/cniprovider/bridge.go

Purpose: Linux-only auto-generated CNI bridge provider that can use BuildKit-shipped CNI plugin binaries or a configured plugin directory.

Important API/functions: `NewBridge(opt)`, `bridgeByName`, `removeBridge`.

Control flow: `NewBridge` looks for `buildkit-cni-bridge`, `buildkit-cni-loopback`, `buildkit-cni-host-local`, and `buildkit-cni-firewall`; if all exist it builds plugin dirs and uses their discovered binary names. Otherwise it requires `opt.BinaryDir/bridge`. It creates a CNI conflist with loopback, bridge IPAM, and firewall, forcing firewall backend to iptables under RootlessKit. It takes init lock, checks for an existing bridge in detached netns when needed, creates CNI handle, schedules bridge removal only if it created it, cleans old namespaces, initializes network, pre-fills namespace pool, and returns provider.

State/persistence: may create bridge device, CNI config state, network namespaces under `opt.Root`, and pool entries. Dependencies: `containerd/go-cni`, netlink, BuildKit logging/network.

Integration points: selected by `netproviders` for mode `bridge` or `BUILDKIT_NETWORK_BRIDGE_AUTO`. Risks: plugin discovery is all-or-nothing; bridge existence check relies on netns context; bridge removal on close can affect other users if ownership detection is wrong. Test signals: no direct bridge test in this subset.
