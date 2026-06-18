<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/quota/projectquota.go -->
# sources/cloud-native/moby/daemon/internal/quota/projectquota.go

Purpose: implements Linux XFS project quota controls for assigning per-directory quota limits, compiled only on Linux with cgo and without `exclude_disk_quota`.

Important APIs and types: C quota/ioctl constants, `pquotaState`, `getPquotaState`, `updateMinProjID`, `NewControl`, `SetQuota`, `GetQuota`, `setProjectQuota`, `getProjectID`, `setProjectID`, `findNextProjectID`, `makeBackingFsDev`, and `hasQuotaSupport`.

Control flow: `NewControl` rejects user namespaces, creates a backing block device node under the base path, checks project quota support via `quotactl`, reads the base project ID, tests setting quota on the next ID, initializes `Control`, updates global next-ID state, and scans existing directories to avoid reusing project IDs. `SetQuota` assigns a new project ID to a target directory if not already known, increments global `nextProjectID`, records it in the control map, and sets the block hard/soft limit. `GetQuota` looks up the target's project ID and reads quota limits. Helper functions use `opendir`, `dirfd`, FSGETXATTR/FSSETXATTR ioctls, mknod, and quotactl.

State and persistence: project IDs and inherit flags persist as filesystem extended attributes; quota limits persist in filesystem quota state. `Control.quotas` maps target paths to project IDs, and global `pquotaState` allocates IDs process-wide.

Dependencies and integration: used by storage drivers such as overlay that apply project quotas to container directories. Depends on cgo, Linux quota headers, XFS project quota support, `moby/sys/userns`, and privileged syscalls.

Risks: requires root-like privileges and a filesystem with project quota accounting/enforcement enabled. Global next-ID allocation can race with external quota tools or other daemon instances. `makeBackingFsDev` creates a block device node inside the storage root. Scanning only immediate children and grandchildren assumes storage-driver layout.

Test signals: `projectquota_test.go` and `testhelpers.go` create an XFS loopback image and verify support detection, enforcement, and retrieval when environment permits.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/quota/projectquota.go -->
