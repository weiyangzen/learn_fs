# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_debugfs.c

Purpose: exposes NITROX firmware, device, and request-statistics information through debugfs.

Important APIs and control flow: `firmware_show()` prints two firmware version strings; `device_show()` prints device index, part name, frequency, IDs, revision, and core counts; `stats_show()` prints posted/completed/dropped counters. `nitrox_debugfs_init()` creates a top-level directory named `KBUILD_MODNAME` and files `firmware`, `device`, and `stats`; `nitrox_debugfs_exit()` removes the tree.

State and persistence: debugfs files read live fields from `struct nitrox_device`; no extra persistent state beyond `ndev->debugfs_dir`.

Dependencies and integration points: depends on debugfs, seq_file, `nitrox_dev.h`, and hardware info/stats populated elsewhere.

Risks and test signals: risks include one top-level directory name per device causing collisions on multiple devices, ignoring debugfs creation errors, and firmware array printing only the first two entries despite larger firmware storage. Test signals include debugfs files present with CONFIG_DEBUG_FS, correct removal on device teardown, stats changing during requests, and behavior with multiple NITROX devices.
