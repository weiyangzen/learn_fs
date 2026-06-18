# Research: sources/cloud-native/buildkit/cmd/buildctl/debug/monitor.go

Purpose: implements `buildctl debug monitor`, a live build-history event monitor for active or completed builds.

Important APIs and flow: `monitor` resolves the client, calls `ListenBuildHistory` with `ActiveOnly` inverted from `--completed` and optional `--ref`, then prints each event with ref, cache counts, warning count, logs/trace descriptors, result descriptors, attestations, and named result groups.

State and dependencies: reads history event stream state from the daemon and does not persist locally. It depends on control API history records, app context, and straightforward formatted stdout.

Risks and test signals: the loop currently returns any receive error, including EOF, so it is mainly intended for continuous streams. The printed shape is ad hoc and not template driven. There are no direct tests in the subset.
