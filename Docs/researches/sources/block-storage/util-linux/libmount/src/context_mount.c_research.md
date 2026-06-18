# File Research: sources/block-storage/util-linux/libmount/src/context_mount.c

Mount-specific high-level implementation for libmount contexts.

Key responsibilities:
- Evaluates mount permissions for root and restricted users.
- Normalizes/fixes mount option strings and user/group IDs.
- Applies helper command-line options to contexts.
- Executes `/sbin/mount.<type>` helpers.
- Performs mount attempts via hook-backed mount stages.
- Tries filesystem type lists and filesystem patterns.
- Prepares target paths and target prefixes.
- Implements `mnt_context_prepare_mount()`, `mnt_context_do_mount()`, `mnt_context_finalize_mount()`, and `mnt_context_mount()`.
- Implements mount-all and remount-all iteration helpers.
- Maps mount failures into mount-compatible exit codes/messages.
- Includes `TEST_PROGRAM` tests for permissions and option fixing.

Important behavior:
- Preparation order is fstab apply, flag merge, FS/option-list sync, permission evaluation, option fixing, source prep, fstype guess, target prep, helper discovery, only-once check, and prep hooks.
- `mnt_context_mount()` retries read-only on EROFS/EACCES/write-protected cases unless explicit RW/remount/bind forbids it.
- EROFS regular files can be retried with loop device setup after ENOTBLK.
- Helper execution drops permissions, switches to the original namespace, passes source/target/options/type/namespace, and records helper status.
- Mount-all ignores swap, root, `noauto`, nonmatching patterns, and already mounted filesystems.
- Remount-all iterates mountinfo and protects filter patterns from being interpreted as an ordinary `-t type`.

Dependencies:
- Depends on generic context APIs from `context.c`, hook stages, option-list APIs, table APIs, namespace support, util-linux string helpers, and Linux mount syscalls/constants.

Notable risks:
- Return codes deliberately separate libmount errors, syscall errno, and helper status; callers must use status/excode helpers.
- Helper argument array has a fixed size and relies on exact option-count assumptions.
- Forked mount-all children exit with raw `rc`, which may be negative if not normalized by caller.
- Error messaging path is large and tightly coupled to syscall status, user flags, and context state.
