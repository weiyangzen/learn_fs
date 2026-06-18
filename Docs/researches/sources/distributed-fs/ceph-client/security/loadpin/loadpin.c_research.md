<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/loadpin/loadpin.c -->
# sources/distributed-fs/ceph-client/security/loadpin/loadpin.c

## Purpose

`loadpin.c` implements the LoadPin LSM. It records the superblock of the first file loaded through kernel file-reading paths and then allows future kernel loads only from that superblock or, when configured, from dm-verity devices whose root digests are trusted.

## Important APIs, Types, and Functions

- `loadpin_check()` is the core policy function for `kernel_read_file` and `kernel_load_data`.
- `loadpin_read_file()` and `loadpin_load_data()` are LSM hook adapters.
- `loadpin_sb_free_security()` reacts when the pinned superblock is unmounted.
- `parse_exclude()` processes boot/module parameter read-file type exclusions.
- `proc_handler_loadpin()` controls `/proc/sys/kernel/loadpin/enforce` writes when sysctl support is enabled.
- Under `CONFIG_SECURITY_LOADPIN_VERITY`, `read_trusted_verity_root_digests()`, `dm_verity_ioctl()`, and `init_loadpin_securityfs()` implement a one-shot securityfs ioctl interface for trusted verity root digests.
- `DEFINE_LSM(loadpin)` registers the LSM, hooks, and optional fs initcall.

## Control Flow

Initialization logs enforcing state, parses excluded read-file IDs, optionally registers the `kernel/loadpin/enforce` sysctl, and registers LSM hooks. On each kernel-read operation, LoadPin ignores configured IDs, rejects old fileless APIs in enforcing mode, and otherwise uses the file's mount superblock as the load root. The first accepted file pins `pinned_root` under a spinlock, records whether the device is writable, and logs the pin.

After pinning, a load is allowed only if its superblock matches `pinned_root` or, with verity support, `dm_verity_loadpin_is_bdev_trusted()` accepts the source block device. Mismatches are logged and either denied with `-EPERM` or ignored in permissive mode. If the pinned filesystem is unmounted, enforcing mode stores `ERR_PTR(-EIO)` to deny future loads; permissive mode clears the pin so it can be reestablished.

The verity ioctl reads a supplied fd through `kernel_read_file(..., READING_POLICY)`, requires a fixed header, parses newline-separated hex digests into `dm_verity_loadpin_trusted_root_digests`, rejects malformed input, clears partial state on failure, and permanently denies retry after corrupt input.

## State and Persistence Behavior

Key state includes `enforce`, exclusion arrays, `pinned_root`, `loadpin_root_writable`, and optional `deny_reading_verity_digests`. The pinned root persists until unmount. Trusted verity digests can be loaded only once and persist in the global dm-verity LoadPin list. The sysctl allows changing enforcement only while the pinned root was writable; read-only pinning prevents later userspace relaxation.

## Dependencies and Integration Points

LoadPin depends on LSM hooks for `sb_free_security`, `kernel_read_file`, and `kernel_load_data`; block-device read-only checks; kernel read-file ID names; module parameters; sysctl; securityfs; and dm-verity LoadPin helpers. It integrates with all kernel subsystems that use the kernel file-reading API, including module, firmware, kexec, and policy loading.

## Risks and Edge Cases

The first load defines trust for the rest of the boot, so early unexpected loads can pin the wrong filesystem. Old fileless module APIs are impossible to attribute and are denied only when enforcing. Unmounting the pinned root in enforcing mode intentionally bricks later loads. Exclusions weaken coverage and must match kernel read-file names exactly. Verity digest parsing is intentionally one-shot because accepting retries after malformed input could allow policy confusion.

## Test Signals

Tests should cover first-load pinning, allowed same-superblock loads, denied different-superblock loads, permissive logging, excluded IDs, null-file load-data behavior, unmount handling, sysctl changes before and after read-only pinning, boot parameter enforcement, and verity digest loading with valid header, malformed hex, duplicate attempts, and trusted/untrusted dm-verity devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/loadpin/loadpin.c -->
