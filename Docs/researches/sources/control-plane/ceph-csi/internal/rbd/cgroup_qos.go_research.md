# sources/control-plane/ceph-csi/internal/rbd/cgroup_qos.go

Purpose: Adds cgroup v2 QoS support for krbd-mounted RBD volumes by storing QoS parameters in RBD metadata and applying them to Kubernetes pod cgroups during publish.

Important APIs/types/functions: `QoSHandler`, cgroup metadata constants, `cgroupQoSHandler`, `cgroupQoS`, `parseCgroupQoSParams`, `hasCgroupQoSParams`, `getDeviceID`, `formatIOMax`, `writeIOMax`, `findPodCgroupPath`, `applyCgroupQoS`, `validateCgroupQoSParams`, `rbdVolume.saveCgroupQoS`, `getCgroupQoS`, and `applyCgroupQoSForVolume`.

Control flow: Handler ignores cgroup QoS for `rbd-nbd` mounter so NBD QoS remains responsible. Save validates positive integer limits, writes provided values to `.rbd.csi.ceph.com/*` metadata, and removes omitted cgroup metadata keys for partial updates. Apply retrieves metadata, resolves device major:minor from `/proc/partitions`, finds the pod's cgroup path by trying Guaranteed, Burstable, and BestEffort slice layouts, formats an `io.max` line, and writes it to the pod cgroup.

State and persistence behavior: QoS intent persists in RBD image metadata with a dot-prefixed key intended not to copy to clones/snapshots. Runtime enforcement persists in kernel cgroup v2 `io.max` files for the pod cgroup.

Dependencies and integration points: Depends on RBD metadata methods, Kubernetes pod UID availability (`podInfoOnMount`), cgroup v2 filesystem layout, `/proc/partitions`, device symlink resolution, librbd not-found errors, and RBD publish flow.

Risks: Hard-coded cgroup path layouts may vary by distro, CRI, or cgroup driver. `getDeviceID` scans `/proc/partitions` by basename, which can fail for unusual device names. Missing pod UID silently skips enforcement. Metadata removal handles `ErrNotExist` while retrieval handles `ErrNotFound`, reflecting subtle librbd error differences.

Test signals: Dedicated tests cover parameter parsing, presence detection, io.max formatting, validation, pod path construction/order, and write behavior. Tests do not mock `/proc/partitions` or real cgroup application.
