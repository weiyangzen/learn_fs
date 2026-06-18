# sources/cloud-native/nydus/smoke/tests/hot_upgrade_test.go

## Purpose
This suite tests direct `nydusd` FUSE hot upgrade mechanics without a full snapshotter. It simulates snapshotter supervision, transfers FUSE daemon state from an old process to a new upgrade-mode process, and verifies the filesystem remains accessible.

## Important APIs, Types, And Functions
`HotUpgradeTestSuite` contains `buildLayer`, `newNydusd`, and `TestHotUpgrade`. `buildLayer` packs a texture lower layer with RAFS v5/lz4 and merges it into a bootstrap. `newNydusd` creates a `tool.Nydusd` with a shared supervisor socket, optionally adds `--upgrade`, starts it, waits for `RUNNING` or `INIT`, then mounts the RAFS source by API at `/`. `TestHotUpgrade` creates a `supervisor.SupervisorSet`, starts old and new daemons, uses `FetchDaemonStates`, `SendFd`, `SendFd`, `Exit`, `Takeover`, and `StartByAPI`, then verifies the mounted file tree.

## Control Flow
The sequence is build image, start supervisor, start old daemon and mount, fetch old FUSE fd, start new daemon in upgrade mode, ask old daemon to exit, send saved state to new daemon, call takeover, wait for `RUNNING` or `READY`, fetch the new daemon state, start it by API when needed, and verify content.

## State And Persistence
The workdir contains blobs, bootstrap, config JSON files, per-daemon API sockets, and the supervisor socket. The live FUSE fd is state transferred through the supervisor rather than through disk. Workdir cleanup removes artifacts after unmounts.

## Dependencies And Integration Points
This integrates `containerd/nydus-snapshotter/pkg/supervisor`, `tool.Nydusd` daemon API helpers, `texture` layers, and `snapshotter-converter`. It exercises `/api/v1/daemon/fuse/sendfd`, `/api/v1/daemon/fuse/takeover`, `/api/v1/daemon/exit`, `/api/v1/daemon/start`, and `/api/v1/mount`.

## Risks
Timing and state transitions differ across old and new daemon versions, so the test allows `RUNNING` or `READY`. It assumes supervisor socket semantics and FUSE fd transfer work on the host. Deferred `Umount` on old and new daemons may race if takeover changes ownership.

## Test Signals
A passing test means old daemon served content, supervisor captured its state, new daemon accepted takeover, reached a serving state, and preserved file-tree semantics after hot upgrade.
