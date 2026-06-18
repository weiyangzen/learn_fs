## sources/control-plane/ceph-csi/internal/cephfs/mounter/volumemounter.go

Purpose: Common mounter selection, probing, and bind-mount helpers for CephFS node operations.

Important APIs: Global `availableMounters`, `quotaSupport`, `LoadAvailableMounters`, `VolumeMounter`, `New`, `BindMount`, and helper `execCommandErr`.

Control flow: Startup probes `mount.ceph` and `ceph-fuse --version`. Kernel mounter is loaded only if forced or kernel version supports CephFS quota; FUSE is loaded if available. `New` chooses the requested mounter if loaded, otherwise falls back to the first available. `BindMount` runs `mount -o <options> from to` and remounts read-only when requested.

State and persistence: `availableMounters` is process-global startup state. Bind mounts mutate the node mount table. No durable files are created here.

Dependencies and risks: Depends on external binaries, kernel version detection, and mount commands. Fallback to the first available mounter can hide unsupported requested mounters unless logs are reviewed. `availableMounters` is global and not reset by this file, so tests would need cleanup. Integration should verify mounter ordering, forced kernel behavior, and read-only remount.
