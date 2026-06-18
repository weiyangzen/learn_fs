## sources/cloud-native/buildkit/util/network/cniprovider/cni.go

Purpose: shared CNI network provider implementation with namespace pooling, setup/removal, hostname args, network sampling hooks, and provider close lifecycle.

Important APIs/types: `Opt`, `New(opt)`, `cniProvider`, `cniNS`, `newCNIPool`, `cniProvider.New`, `cniProvider.Close`, `cniNS.Set`, `Close`, `Sample`, `release`.

Control flow: `New` validates config and binary paths, builds CNI options including loopback/min network count on non-Windows and config file/conflist, creates CNI handle in detached netns if necessary, cleans old namespaces, builds pool, initializes one namespace, and asynchronously fills pool. `New` on provider uses the pool for empty hostnames or Windows; custom hostnames get a fresh non-pooled namespace. `newNS` creates a native namespace, runs CNI setup (serially in detached netns), extracts the host veth name, and primes sampling baseline. `Close` returns namespaces to pool or releases resources. `release` removes CNI config, unmounts, and deletes namespace.

State/persistence: creates OS network namespaces under root, CNI runtime state, pooled namespace objects, optional veth sample offsets. Dependencies: containerd go-cni, BuildKit identity/logging/network/netpool, OCI specs, OpenTelemetry trace.

Integration points: `netproviders` default CNI mode; executor calls `Set` on OCI specs and `Sample` for resource metrics. Risks: pooled namespaces must be reset correctly via CNI; custom-hostname namespaces are not pooled; Windows lacks cleanup mechanism per comment; setup uses `context.TODO` for CNI calls after namespace creation. Test signals: Linux dialing/sampling-adjacent behavior is covered in `cni_linux_test.go`; generic pooling is tested in `netpool`.
