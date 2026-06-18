# File Research: sources/block-storage/util-linux/sys-utils/fstrim.c

Purpose: Implements `fstrim(8)`, which discards unused blocks from mounted filesystems through the Linux `FITRIM` ioctl.

Core behavior:
- Supports trimming one mountpoint or multiple filesystems selected by `--all`, `--fstab`, or `--listed-in`.
- Maintains an `fstrim_control` with the `fstrim_range` (`start`, `len`, `minlen`) plus type filtering, verbose output, dry-run mode, and quiet unsupported behavior.
- For a single path, verifies it is a directory, resolves it with `realpath()`, opens it read-only, and sends `FITRIM`; unsupported errors (`EBADF`, `ENOTTY`, `EOPNOTSUPP`, `ENOSYS`) are distinguished from hard failures.
- For batch trimming, parses mount/fstab files with libmount, removes duplicate mount targets, filters pseudo/network/swap/autofs/read-only/notrim filesystems, canonicalizes sources, checks mounted accessibility, optionally resolves bind mounts with statmount support, verifies discard support in sysfs, deduplicates by source, then trims.
- Return codes for batch mode follow mount-style codes: success, all failed, or partial success.

Important implementation details:
- `has_discard()` resolves block devices to whole-disk sysfs contexts and checks `queue/discard_granularity` plus read-only state, reusing a whole-disk `path_cxt` for partitions.
- `is_unwanted_fs()` combines libmount classification, fstype filters, mount options, `statfs()` autofs detection, and write-access checks.
- `/etc/fstab` mode can synthesize a `/` entry from `mnt_guess_system_root()` if root is absent, so root filesystems can still be trimmed.
- `--quiet-unsupported` suppresses unsupported trim warnings, and for single-filesystem mode converts unsupported into success only when requested.

Dependencies and integration:
- Uses Linux `FITRIM`, libmount tables/iterators/cache, util-linux sysfs/path/mount helpers, size parsing/formatting, and `statfs_magic.h`.
- The systemd service in this group invokes `fstrim --listed-in /etc/fstab:/proc/self/mountinfo --verbose --quiet-unsupported`.

Risks and edge cases:
- `has_discard()` returns true on sysfs lookup failure, so the utility may still attempt FITRIM when it cannot prove discard support.
- Batch delta between mount table parsing and actual trimming can race with mounts/unmounts.
- Source deduplication intentionally avoids pseudo/net filesystems but can still skip repeated block-device sources after canonicalization.
