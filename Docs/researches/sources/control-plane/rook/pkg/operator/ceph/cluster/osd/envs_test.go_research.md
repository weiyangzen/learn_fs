# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/envs_test.go

## Purpose
This file tests the stable environment variable helpers from `envs.go`, with emphasis on ceph-volume defaults, activation monitor wiring, and TCMalloc configuration lookup.

## Important APIs, Types, and Helpers
The `sysconfig` byte slice models `/etc/sysconfig/ceph` content containing `TCMALLOC_MAX_TOTAL_THREAD_CACHE_BYTES=134217728`. `TestCephVolumeEnvVar` checks the three ceph-volume env vars. `TestOsdActivateEnvVar` verifies that activation env vars include ceph-volume settings plus `ROOK_CEPH_MON_HOST` and `CEPH_ARGS=-m $(ROOK_CEPH_MON_HOST)`. `TestGetTcmallocMaxTotalThreadCacheBytes` exercises no-file, empty-file, explicit argument, and parsed-file behavior by redirecting the package global `cephEnvConfigFile` to a temporary file.

## Control Flow Covered
The TCMalloc test covers the branch where no explicit value is provided and file loading fails, the branch where file loading succeeds but no key exists, the branch where an explicit value bypasses file parsing, and the branch where the key is found in sysconfig. The ceph-volume and activation tests assert helper output positionally, which also protects callers that may rely on deterministic env order in generated pod specs or snapshot comparisons.

## State and Persistence Behavior
The tests do not use Kubernetes state. They mutate the package global `cephEnvConfigFile` to point to a temporary file. The temp file is removed with defer, but the global is not reset in this file, so test isolation relies on package test ordering not depending on the default path afterward.

## Dependencies and Integration Points
The tests use only the standard library and `testify/assert`. They indirectly protect pod-spec consumers in create, deployment, activation, and key-rotation code by ensuring shared env helpers do not change unexpectedly.

## Risks and Gaps
There appears to be a minor assertion typo: the `DM_DISABLE_UDEV` value checks `cvEnv[1].Value` and `osdActivateEnv[1].Value` instead of index 2. The expected value is still `"1"`, so the test passes while not directly asserting the third variable's value. Broader `getConfigEnvVars()` behavior is not covered here, including prepare-mode FSID, crush-root, non-portable PVC hostname hiding, and store-config optional env vars.

## Test Signals
The file is a focused regression signal for low-level env helper contracts. Its coverage is narrow but important because these variables are shared across OSD provisioning, activation, and maintenance jobs.
