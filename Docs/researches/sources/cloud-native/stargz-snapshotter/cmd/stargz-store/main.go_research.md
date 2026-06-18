# sources/cloud-native/stargz-snapshotter/cmd/stargz-store/main.go

Purpose: Main daemon for `stargz-store`, a FUSE-backed store that mounts lazy-pulled layers and exposes a controller socket for dynamic credentials.

Important APIs/types: `Config`, `KubeconfigKeychainConfig`, `ResolverConfig`, `main`, `waitForSignal`, `getMetadataStore`, `controller.AddCredential`, `storeKeychain.add`, `storeKeychain.credentials`, and `serveController`.

Control flow: `main` parses flags, requires a mount point, configures logging and TOML config, starts the credential controller, builds credential functions from in-memory store keychain and optional kubeconfig keychain, creates registry hosts, prepares mountpoint, rejects disabled verification, configures metadata store, creates `store.LayerManager`, mounts FUSE store, sends systemd ready/stopping notifications, and waits for interrupt or controller error. `serveController` removes the socket path, starts a gRPC server, and returns an error channel.

State and persistence: Root dir holds optional metadata DB and store data through `store.NewLayerManager`. Credentials are held in memory keyed by image reference. The mounted filesystem is unmounted on exit.

Dependencies and integration: Integrates resolver config, kubeconfig keychain, metadata memory/DB stores, store package, protobuf controller, bbolt, gRPC, systemd notify, and Unix mount lifecycle.

Risks: `serveController` removes socket path without ensuring parent directory exists. Content verification cannot be disabled. Credentials are only applied when host matches the original ref hostname, avoiding mirrors. `waitForSignal` only listens for `os.Interrupt`, not SIGTERM.

Test signals: No direct tests in this subset.
