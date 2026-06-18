# sources/cloud-native/containerd/internal/cri/server/container_create_windows.go

## Purpose
This Windows-specific create helper supplies platform hooks used during container creation. It adds snapshot labels for Windows rootfs sizing and otherwise leaves extra per-platform OCI spec options empty.

## Important APIs, Types, and Functions
`containerSpecOpts` returns no extra `oci.SpecOpts` on Windows. `snapshotterOpts` reads `config.GetWindows().GetResources().GetRootfsSizeInBytes()` and, when nonzero, returns a snapshot label `containerd.io/snapshot/windows/rootfs.sizebytes`.

## Control Flow, State, and Persistence
There is no persistent state in this file. Snapshot labels flow into `customopts.WithNewSnapshot` during `createContainer`, affecting the writable layer prepared by the selected snapshotter.

## Dependencies and Integration Points
The file integrates CRI Windows resource limits with containerd snapshot service options. It depends on runtime API Windows resources, snapshot labels, and OCI option types.

## Risks and Test Signals
The key risk is snapshotter-specific label drift or rootfs quota silently not applying. Windows spec behavior is mostly covered in `container_create_windows_test.go`; rootfs-size label behavior would need snapshotter-level or option inspection coverage.
