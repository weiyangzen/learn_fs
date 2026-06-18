# sources/cloud-native/soci-snapshotter/service/plugin/plugin.go

Purpose: registers SOCI snapshotter as a containerd snapshot plugin and wires service configuration, keychains, registry host configuration, and optional CRI image-service proxy.

Important APIs/types/functions: `Config` embeds `config.ServiceConfig` and adds `RootPath`, `CRIKeychainImageServicePath`, and resolver `Registry`. `init` registers a containerd plugin with type snapshot, ID `soci`, config, and init function. `getCriConn` creates a gRPC client connection to the backend CRI service with containerd dialer defaults and bounded backoff.

Control flow: plugin init validates config, resolves root path, exports root metadata, builds credential functions starting with Docker config, optionally adds kubeconfig keychain, optionally starts a Unix-socket CRI image service proxy and appends its credential provider, then creates the snapshotter service with custom registry hosts derived from CRI-compatible config.

State and persistence: creates/removes Unix socket path for CRI proxy, starts a gRPC server goroutine, and exposes root in plugin metadata. Service state is owned by `service.NewSociSnapshotterService`.

Dependencies/integration points: containerd plugin registry, service package, keychain packages, resolver registry host builder, gRPC, containerd dialer/default message sizes, and CRI API. It supports both external proxy plugin and built-in containerd plugin modes.

Risks: when `CRIKeychainConfig.EnableKeychain` is true, CRI proxy only starts if `CRIKeychainImageServicePath` is non-empty. `connectV1CRI` calls `getCriConn(config.CRIKeychainConfig.ImageServicePath)` rather than the resolved `criAddr`, so default-property fallback may not be used as intended. Socket removal with `RemoveAll` can remove non-socket paths if misconfigured.

Test signals: no direct unit tests; integration tests with snapshotter startup and CRI keychain settings validate registration and service boot.
