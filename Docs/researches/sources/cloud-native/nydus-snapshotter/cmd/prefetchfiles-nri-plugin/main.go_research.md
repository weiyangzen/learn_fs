# sources/cloud-native/nydus-snapshotter/cmd/prefetchfiles-nri-plugin/main.go

Purpose: NRI plugin that forwards pod prefetch annotations to the Nydus system controller.

Flow: reads optional `/etc/nydus/prefetchConfig.toml`, selects Unix socket path from config or CLI, registers for `RunPodSandbox`, and when annotation `containerd.io/nydus-prefetch` exists sends it via HTTP PUT to `/api/v1/prefetch` over the Unix socket.

State/dependencies: global socket string and syslog writer; uses containerd NRI stub, go-toml, and custom HTTP transport.

Integration points: pairs with system controller socket and `misc/nri-prefetch/prefetchConfig.toml`.

Risks/tests: if config file load fails, `config.Get` is still called on a possibly nil tree, which may panic depending on library behavior. Response body close ignores error and non-200 returns error.
