<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/cleanup/disk.go -->
# sources/control-plane/rook/pkg/daemon/ceph/cleanup/disk.go

Purpose: implements OSD disk sanitization for cleanup jobs, covering LVM OSD zapping, raw device shredding/zapping, encrypted device handling, and metadata/WAL device cleanup.

Important APIs/types/functions: `DiskSanitizer`, `ShredCommand`, `NewDiskSanitizer`, `StartSanitizeDisks`, `SanitizeRawDisk`, `SanitizeLVMDisk`, `wipeLVM`, `returnPVDevice`, `buildDataSource`, `buildShredArgs`, `buildQuickShredCommands`, `buildShredCommands`, and `executeSanitizeCommand`.

Control flow: `StartSanitizeDisks` lists LVM OSDs then raw OSDs through ceph-volume helpers and sanitizes each set. Raw sanitization launches one goroutine per OSD. LVM sanitization records each LV's PV, runs `ceph-volume lvm zap --osd-id --destroy` concurrently, waits, then sanitizes PV devices. `executeSanitizeCommand` resolves encrypted backing devices, removes dm mappings, then runs quick zap or full `shred` commands for block, metadata, and WAL paths.

State and persistence behavior: no internal persistent state, but commands destructively modify disks and LVM metadata. The sanitizer depends on `SanitizeDisksSpec` method, data source, and iteration count; logs record command output.

Dependencies and integration points: integrates `clusterd.Context` executor, Ceph cluster info, CephVolume OSD discovery, operator OSD info structs, encryption helpers, and Ceph CRD sanitize policy.

Risks: destructive operations run concurrently and errors are logged but often not returned to a caller. `returnPVDevice(...)[0]` assumes the LVS command produced at least one colon-delimited value. Full shred command construction around zero/random data source must match user expectations.

Test signals: command construction for quick/complete zero/random modes, encrypted path substitution, LVM PV parsing failures, concurrent error handling, metadata/WAL coverage, and real cleanup job integration on test devices.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/cleanup/disk.go -->
