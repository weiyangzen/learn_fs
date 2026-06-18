# sources/cloud-native/soci-snapshotter/idtools/idmap.go

Purpose: implements UID/GID remapping support for idmapped snapshots, copied from containerd/Moby and customized for SOCI snapshotter filesystem paths.

Important APIs and flow: `IDMap` stores OCI runtime UID and GID mapping slices. `LoadIDMap` reads containerd snapshot UID/GID mapping labels and calls `Unmarshal`. `ToHost` maps a container `User` pair to host IDs, returning identity mapping when the map is empty. `deserializeLinuxIDMapping` parses `containerID:hostID:size` strings and rejects negative or invalid-ID-sized values. `safeSum` protects range arithmetic from uint32 overflow. `RemapDir`, `RemapRoot`, and `RemapRootFS` copy or traverse roots and call `chown`. `chown` uses `Lchown` to avoid dereferencing symlinks and restores setuid/setgid/sticky mode bits after ownership changes.

State and persistence: remapping mutates filesystem ownership recursively. `RemapDir` creates the target base directory and copies the original mountpoint using `cp -a --no-preserve=links` before walking it.

Dependencies and integration: integrates with containerd snapshot labels, containerd temporary mounts, OCI runtime ID mapping types, OS process execution, and Linux stat/chown syscalls. It is used by idmapped snapshot workflows tested in integration.

Risks and test signals: recursive `filepath.Walk` and external `cp` can be expensive and platform-dependent. Mapping failures stop the walk. A zero-size mapping parses successfully but cannot map IDs. Tests cover valid mapping, unmapped IDs, and overflow cases; integration runtime tests verify host/container ownership under user namespace remap.
