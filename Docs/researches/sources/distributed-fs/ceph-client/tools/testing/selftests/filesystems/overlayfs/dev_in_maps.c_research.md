# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/overlayfs/dev_in_maps.c

## Purpose

`dev_in_maps.c` verifies that a memory-mapped overlayfs file appears in `/proc/self/maps` with the same device and inode values reported by `statx` on the file.

## Important APIs, Types, and Functions

`get_file_dev_and_inode` parses `/proc/self/maps` for the mapping start address and extracts major, minor, and inode. `ovl_mount` constructs tmpfs and overlayfs mounts through `fsopen`, `fsconfig`, `fsmount`, and `move_mount`. `test` creates and mmaps a file on the detached overlay mount and compares maps data to `statx`.

## Control Flow, State, and Persistence

`main` first probes that overlay fsopen works, enters a new mount namespace, makes `/` slave, sets a one-test plan, and runs `test`. The test creates a tmpfs mounted at `/tmp`, creates work/upper/lower directories, configures overlay source/lower/upper/work, obtains a detached overlay fd, opens `test` on it, mmaps one page shared writable, parses `/proc/self/maps`, stats the fd, and compares device/inode triples. Mount state is isolated to the namespace and not explicitly cleaned.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies are overlayfs, tmpfs, new mount API wrappers, procfs maps format, mmap, statx, and namespace privilege. It integrates overlayfs with procfs VMA reporting. Risks are strict maps parsing, assuming mapping start equals `addr`, no cleanup beyond namespace lifetime, and older kernels lacking overlay fsopen. Passing signal is `ksft_test_result_pass("devices are matched")` with identical dev major/minor and inode.
