# sources/cloud-native/stargz-snapshotter/cmd/ctr-remote/commands/rpull.go

Purpose: Defines `ctr-remote images rpull`, a remote/lazy pull command that fetches and unpacks an image using the stargz snapshotter.

Important APIs/types: `RpullCommand`, `rPullConfig`, and `pull`. Flags include registry flags, labels, snapshotter selection, `--skip-content-verify`, `--ipfs`, and `--use-containerd-labels`.

Control flow: The action validates ref, opens a containerd client and lease, builds a fetch config, configures optional verification skip, optional IPFS resolver, and snapshotter name, then calls `pull`. `pull` creates a lightweight handler for fetch logging, sets snapshot labels for skip verification, chooses default or containerd label handler wrappers with prefetch size 10 MiB, and calls `client.Pull` with resolver, labels, unpack, snapshotter, and image handler wrapper.

State and persistence: Pulls image content into containerd content store and prepares snapshots with selected snapshotter. May attach labels affecting stargz snapshotter behavior.

Dependencies and integration: Uses containerd pull APIs, snapshot labels from fs config/source packages, optional IPFS resolver, and containerd snapshotter flags.

Risks: `--skip-content-verify` weakens integrity and logs a warning. Prefetch size is hard-coded. IPFS resolver path is experimental. Incorrect snapshotter name causes pull/unpack failures.

Test signals: No direct tests in this subset; integration with containerd is required.
