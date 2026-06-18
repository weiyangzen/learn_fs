# sources/distributed-fs/ceph-client/drivers/s390/cio/cio_inject.c

## Purpose
This file implements a debugfs-based CIO test hook for injecting synthetic Channel Report Words. It lets developers trigger the CRW handling path without waiting for hardware machine checks.

## Important APIs, Types, and Functions
State includes `crw_inject_lock`, static key `cio_inject_enabled`, and one pending `crw_inject_data` pointer. Key functions are `crw_inject()`, `stcrw_get_injected()`, `crw_inject_write()`, `enable_inject_write()`, and `cio_inject_init()`. Debugfs files are `enable_inject` and `crw_inject`.

## Control Flow
Userspace first writes `1` to `enable_inject`, enabling the static branch. A write to `crw_inject` parses seven hex fields into a `struct crw`, stores a kmemdup copy if no injection is pending, and calls `crw_handle_channel_report()`. The CRW collector path calls `stcrw_get_injected()` instead of or alongside hardware retrieval when injection is enabled; this copies the synthetic CRW to the caller and frees the pending object.

## State and Persistence
Only one injected CRW can be pending. The pending object is protected by `crw_inject_lock` and is consumed once. The static key controls runtime overhead and state is not persistent.

## Dependencies and Integration Points
It depends on `CONFIG_CIO_INJECT`, debugfs, CRW handling, `cio_debugfs_dir`, static branches, and architecture CRW definitions. It integrates directly with `crw.c` through `stcrw_get_injected()` and `crw_handle_channel_report()`.

## Risks and Test Signals
Risk areas include malformed debugfs input, stale pending CRWs blocking new injections with `-EBUSY`, debugfs init ordering, and ensuring injection is compiled out or inert when disabled. Test signals include enabling/disabling the static key, invalid format handling, one-shot CRW consumption, overflow/chained CRW test injections, and CRW dispatcher callbacks seeing synthetic events.
