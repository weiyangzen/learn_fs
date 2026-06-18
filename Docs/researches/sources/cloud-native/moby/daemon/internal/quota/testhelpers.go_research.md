<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/quota/testhelpers.go -->
# sources/cloud-native/moby/daemon/internal/quota/testhelpers.go

Purpose: supplies privileged Linux helpers for project quota integration tests.

Important APIs and types: `CanTestQuota`, `PrepareQuotaTestImage`, `WrapMountTest`, and `WrapQuotaTest`.

Control flow: `CanTestQuota` requires UID 0 and `mkfs.xfs`. `PrepareQuotaTestImage` creates a 300 MiB sparse file and formats it with compatibility options. `WrapMountTest` mounts the image with loop and optional `prjquota`, creates a backing block device and temp directory, invokes the test function, and unmounts. `WrapQuotaTest` creates a `Control` and quota test subdir for nested test functions.

State and persistence: creates temporary sparse files, filesystems, mounts, device nodes, and directories, then cleans them up.

Dependencies and integration: used by `projectquota_test.go`; depends on external `mkfs.xfs` and `mount`.

Risks: privileged mount helpers can fail for host-policy reasons; cleanup failures call `Fatalf`. The sparse image size is fixed to satisfy XFS minimums.

Test signals: provides the scaffolding that makes quota tests realistic rather than mocked.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/quota/testhelpers.go -->
