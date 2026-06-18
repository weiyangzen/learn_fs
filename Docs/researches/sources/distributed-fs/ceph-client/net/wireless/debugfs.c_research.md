# sources/distributed-fs/ceph-client/net/wireless/debugfs.c

## Purpose
This file creates cfg80211 debugfs entries for wiphy and per-radio parameters and provides helper wrappers for debugfs read/write handlers that must run under the wiphy lock.

## Important APIs, types, and functions
Readonly debugfs macros generate files for `rts_threshold`, `fragmentation_threshold`, `short_retry_limit`, `long_retry_limit`, and per-radio `radio_rts_threshold`. `ht40allow_map_read()` emits per-channel HT40 plus/minus availability or disabled state. `cfg80211_debugfs_rdev_add()` creates the files under the wiphy debugfs directory and per-radio directories.

`wiphy_locked_debugfs_read()` and `wiphy_locked_debugfs_write()` allocate on-stack work descriptors, queue a `wiphy_work`, enter debugfs cancellation, wait for completion, and then copy results to/from userspace. Their worker functions call caller-supplied handlers while the wiphy work context holds the lock.

## Control flow
Registration-time setup calls `cfg80211_debugfs_rdev_add()`. Simple readonly files directly format current wiphy fields. Locked helper reads zero the output buffer, queue work, wait, validate handler length, and return through `simple_read_from_buffer()`. Locked writes enforce NUL-terminated input by requiring `count < bufsize`, copy from userspace, queue work, and return the handler result.

## State and persistence
Debugfs exposes live in-memory cfg80211 state. The helpers use temporary stack work structures and completions; no persistent file-local state is stored.

## Dependencies and integration points
The file depends on debugfs, cfg80211 wiphy work helpers, and registered-device debugfs directories created by `core.c`. It is compiled only when `CONFIG_CFG80211_DEBUGFS` is enabled.

## Risks
Handlers must not return more bytes than the provided buffer. Cancellation must complete pending work to avoid a hung debugfs file operation. The HT40 map is bounded to one page, so very large channel lists may truncate output by construction.

## Test signals
Debugfs tests should read all generated files, exercise locked read/write cancellation during device removal, verify permission modes, and run lockdep while handlers access wiphy state.
