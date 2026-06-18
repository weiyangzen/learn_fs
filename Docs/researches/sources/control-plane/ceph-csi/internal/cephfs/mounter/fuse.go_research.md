## sources/control-plane/ceph-csi/internal/cephfs/mounter/fuse.go

Purpose: Implements Ceph-FUSE mounting and unmount tracking for CephFS volumes.

Important APIs: `FuseMounter`, `mountFuse`, `(*FuseMounter).Mount`, `Name`, `UnmountVolume`, `UnmountAll`, constants `volumeMounterFuse` and `cephEntityClientPrefix`, global `fusePidMap`, mutex, and `fusePidRx`.

Control flow: `mountFuse` builds `ceph-fuse` args with monitor list, config path, client identity/keyfile, root path, optional FUSE mount options and filesystem namespace, optionally runs through `nsenter`, parses stderr for the FUSE daemon PID, and records it by mountpoint. Unmount runs `umount`, tolerates not-mounted/not-found messages, removes PID tracking, and waits for the daemon process if it is known.

State and persistence: Maintains process-local map from mountpoint to FUSE daemon PID; actual mount state lives in the node mount table. No durable state is written here.

Dependencies and risks: Depends on `ceph-fuse` output format containing `starting fuse`, shell command execution helpers, and optional network namespace support. PID tracking is lost on plugin restart, which is why `fuserecovery.go` exists. Tests are absent; integration should cover stderr parsing, nsenter path, option construction, and unmount idempotency.
