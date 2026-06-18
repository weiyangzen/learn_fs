# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-inode-read.c

## Purpose

`dht-inode-read.c` implements DHT file/inode read-side and metadata FOPs: `open`, `stat`, `fstat`, `readv`, `access`, `flush`, `fsync`, `lk`, `lease`, `readlink`, `xattrop`, `fxattrop`, `inodelk`, `finodelk`, and `seek`. The common theme is forwarding operations to the cached child while detecting migration and retrying on the correct destination.

## Important APIs, Types, and Functions

The public FOPs are the DHT translator entry points declared in `dht-common.h`. Callback/retry pairs include `dht_open_cbk`/`dht_open2`, `dht_file_attr_cbk`/`dht_attr2`, `dht_readv_cbk`/`dht_readv2`, `dht_access_cbk`/`dht_access2`, `dht_flush_cbk`/`dht_flush2`, `dht_fsync_cbk`/`dht_fsync2`, `dht_lk_cbk`/`dht_lk2`, `dht_common_xattrop_cbk`/`dht_common_xattrop2`, and `dht_seek_cbk`/`dht_seek2`. Directory/non-file aggregation uses `dht_attr_cbk` and `dht_iatt_merge`. Xattrop migration support uses `dht_request_iatt_in_xdata` and `dht_read_iatt_from_xdata` to request/read mode hints from xdata.

## Control Flow

For regular files, operations initialize `dht_local_t`, cache original arguments in `local->rebalance` as needed, set `call_cnt = 1`, and wind to `local->cached_subvol`. The callback treats non-migration errors as final but handles missing files, `EREMOTE`, phase2 mode bits, phase1 mode bits, and remote-fd failures by invoking helper synctasks. Complete-migration checks refresh layout and retry on the new cached subvol; in-progress checks validate/open the destination and retry there. Directory `stat`/`fstat` fan out across all layout entries and merge attributes. Directory `access` can walk available subvolumes when one child is down or missing. Lock paths use `dht_get_lock_subvolume` to keep directory locks/unlocks on a stable child.

## State and Persistence Behavior

This file primarily consumes inode layout and fd/migration context established elsewhere. It updates fd context when `open` succeeds on the final target and relies on helper code to open fds on migrated destinations. It stores retry state in `dht_local_t`: flags, offset, size, flock, xattr dicts, pre/post attrs, and original op return. Xattrop paths create or ref request dicts and ask lower translators to return DHT mode/iatt data in xdata so migration phases can be recognized without a separate lookup.

## Dependencies and Integration Points

It depends tightly on `dht-helper.c` for `dht_rebalance_complete_check`, `dht_rebalance_in_progress_check`, `dht_check_and_open_fd_on_subvol`, fd context, lock-subvolume tracking, and attribute merge. It depends on migration mode macros from `dht-common.h`, child FOP tables, dict APIs, and DHT layout context. Sharding is explicitly mentioned as a consumer of xattrop/fxattrop on files.

## Risks and Test Signals

Regression risk is high around retry idempotence: the same FOP must not loop indefinitely, leak request dicts, return migration mode bits to upper layers incorrectly, or operate on an fd not opened on the destination. Xattrop has a noted corruption risk if lower layers do not return the requested iatt/mode in xdata. Tests should cover read/open/stat while a file migrates through phase1 and phase2, fd migration with stale cached subvol, directory stat fanout with partial child failures, access fallback across child availability, lock/unlock on purged directory inodes, seek errors such as `ENXIO`/`EOVERFLOW`, xattrop/fxattrop with and without mode xdata, nested DHT layers, and cleanup of phase bits via `DHT_STRIP_PHASE1_FLAGS`.
