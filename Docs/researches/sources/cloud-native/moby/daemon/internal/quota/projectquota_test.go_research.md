<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/quota/projectquota_test.go -->
# sources/cloud-native/moby/daemon/internal/quota/projectquota_test.go

Purpose: integration-tests Linux project quota behavior on an XFS loopback filesystem.

Important APIs and types: `TestBlockDev`, `testBlockDevQuotaDisabled`, `testBlockDevQuotaEnabled`, `testSmallerThanQuota`, `testBiggerThanQuota`, `testRetrieveQuota`, and constant `testQuotaSize`.

Control flow: skips when quota tests cannot run, creates a sparse XFS image, mounts it with and without `prjquota`, checks support detection, sets quotas, verifies writing below quota succeeds, writing above quota fails, and quota retrieval returns expected size.

State and persistence: creates temporary image files, mounts loopback filesystems, writes test files, sets filesystem project quota state, and unmounts in helpers.

Dependencies and integration: requires Linux, root, `mkfs.xfs`, mount support, and quota-enabled XFS.

Risks: environment-heavy test can skip or fail due to host kernel/userspace capabilities. Writing a file above quota may return different error shapes; the test only asserts an error exists.

Test signals: strong end-to-end signal where supported, but often skipped in unprivileged CI.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/quota/projectquota_test.go -->
