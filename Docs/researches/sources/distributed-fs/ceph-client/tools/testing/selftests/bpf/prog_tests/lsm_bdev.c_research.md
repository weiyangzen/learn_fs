<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lsm_bdev.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lsm_bdev.c

Purpose: integration test for BPF LSM hooks around block-device integrity/dm-verity metadata, including root hash visibility and allocation accounting.

Important APIs and functions: `run_cmd()` shells out with `popen()` and optional output capture. `has_prerequisites()` checks required tools/kernel support. `test_lsm_bdev()` creates temporary data/hash images, attaches loop devices, formats dm-verity metadata with `veritysetup`, loads and attaches `lsm_bdev`, opens a dm-verity device, stats `/dev/mapper/bpf_test_verity`, and looks up recorded device info in `verity_devices`.

Control flow: prerequisite check, temp image creation/truncation, loop setup, verity format, skeleton load/attach before activation, verity open, map lookup by device number, assertions, then structured cleanup for dm device, loops, files, fds, and skeleton.

State and persistence: manipulates real `/tmp` images, loop devices, a device-mapper target, and a BPF map. Cleanup removes dm-verity and loop state; failure paths try to close/unlink resources.

Dependencies and integration: depends on root privileges, loop devices, `losetup`, `veritysetup`, `dmsetup`/device mapper, stat-able mapper device, and `lsm_bdev.skel.h`.

Risks and test signals: map value fields `has_roothash`, `sig_valid`, `setintegrity_cnt`, and BSS `alloc_count` are key signals. Risks are environmental: missing tooling, stale mapper names, insufficient privileges, or cleanup failure leaving block resources behind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/lsm_bdev.c -->
