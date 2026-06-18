## sources/cloud-native/buildkit/util/network/network.go

Purpose: defines common network provider, namespace, and dialer contracts used by executors, CNI, host, none, and proxy implementations.

Important types: `Provider` embeds `io.Closer` and creates `Namespace`. `Namespace` embeds `io.Closer`, mutates OCI specs with `Set`, and optionally returns resource samples. `NamespaceOptions` is currently empty. `Dialer` supplies namespace-aware `DialContext`.

State/persistence: interface-only file. Dependencies: context, io, net, OCI specs, BuildKit resource sample types.

Integration points: central abstraction for worker networking and proxy egress. Risks: empty `NamespaceOptions` suggests future extension; not every namespace implements `Dialer`, so proxy provider checks dynamically. Test signals: implementations are tested elsewhere.
