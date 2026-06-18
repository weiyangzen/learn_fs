# sources/control-plane/rook/pkg/daemon/ceph/client/subvolumegroup.go

This file manages CephFS subvolume groups and CSI cleanup helpers for subvolumes, snapshots, clones, and OMAP entries.

`CreateCephFSSubVolumeGroup()` builds `ceph fs subvolumegroup create` arguments from quota and data-pool layout, probes existing group info, resizes when an existing quota differs, and then creates the group. `resizeCephFSSubVolumeGroup()` uses `--no-shrink`. `getCephFSSubVolumeGroupInfo()` parses JSON quota, usage, and data-pool details. `DeleteCephFSSubVolumeGroup()` intentionally returns raw command errors so callers can inspect exit status. `PinCephFSSubVolumeGroup()` validates pinning, selects one of distributed/export/random/default distributed settings, and runs `ceph fs subvolumegroup pin`.

The pin validator enforces only one pinning type, export range `-1..256`, distributed values `0` or `1`, and random `0.0..1.0`. CSI cleanup helpers use `rados getomapval`, `rm`, and `rmomapkey`, plus `ceph fs subvolume rm`, snapshot rm, and clone cancel.

State is CephFS subvolume-group metadata, quotas, pinning state, RADOS OMAP keys/values, and subvolume/snapshot/clone records. Risks include creating after resize even when the group already exists, string parsing of `getomapval`, and partial coverage of CLI error semantics. `subvolumegroup_test.go` covers pin validation only.
