# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/gpu/drm_mm.sh

Purpose: Shell kselftest wrapper for the DRM range-manager unit test module `test-drm_mm`.

Important APIs/functions: `/sbin/modprobe -n -q`, `/sbin/modprobe -q`, `/sbin/modprobe -q -r`, `uname -r`, and kselftest exit code `77` for skip.

Control flow: The script first dry-runs module lookup. If the module is unavailable, it prints a skip message and exits `77`. If load succeeds, it immediately unloads the module and reports `drivers/gpu/drm_mm: ok`; otherwise it reports failure and exits `1`.

State and persistence: It transiently loads and removes `test-drm_mm`. No files are written.

Dependencies and integration points: Requires root/module privileges, the test module in `/lib/modules/$(uname -r)`, and kernel module selftests compiled for DRM.

Risks and test signals: Failure means the module selftest failed to load or unload cleanly. A skip means the module is absent, not necessarily a DRM allocator regression.
