# sources/distributed-fs/ceph-client/fs/cachefiles/ondemand.c

## Purpose
`ondemand.c` implements CacheFiles on-demand mode, where cache misses are delegated to a userspace backend through `/dev/cachefiles` messages and per-object anonymous fds.

## Important APIs, Types, and Functions
Important APIs include `cachefiles_ondemand_copen`, `cachefiles_ondemand_restore`, `cachefiles_ondemand_daemon_read`, `cachefiles_ondemand_init_object`, `cachefiles_ondemand_clean_object`, `cachefiles_ondemand_init_obj_info`, `cachefiles_ondemand_deinit_obj_info`, and `cachefiles_ondemand_read`. Local pieces include `struct ondemand_anon_file`, `cachefiles_ondemand_fd_fops`, fd release/write/llseek/ioctl handlers, `cachefiles_ondemand_get_fd`, `cachefiles_ondemand_select_req`, `cachefiles_ondemand_finish_req`, and `cachefiles_ondemand_send_req`.

## Control Flow
Opening an object sends an `OPEN` request with volume and cookie keys. Daemon read selects a marked new request from the request xarray fairly, creates an anonymous fd for `OPEN`, copies the message to userspace, and installs the fd after successful copy. Userspace completes `OPEN` by writing `copen id,size`, which updates cookie object size and opens state, or stores an error. Cache misses call `cachefiles_ondemand_read`, enqueue a `READ` request, and wait for userspace to write data through the anonymous fd and issue `CACHEFILES_IOC_READ_COMPLETE`. Object cleanup sends `CLOSE`, cancels outstanding object requests, marks dropping, and waits for reopen work to finish. Restore re-marks all pending requests as new after daemon recovery.

## State and Persistence Behavior
Runtime state is held in `cache->reqs`, `cache->ondemand_ids`, cyclic request/message counters, object `ondemand_id`, object on-demand state (`CLOSE`, `OPEN`, `REOPENING`, `DROPPING`), and anonymous fd references. Persistent cache content is written indirectly when userspace writes to the anonymous fd, which calls the ordinary CacheFiles prepare/write path against the backing file.

## Dependencies and Integration Points
This file depends on the userspace ABI in `linux/cachefiles.h`, anon inodes, xarrays, wait completions, fscache workqueue, daemon read/write/poll paths, CacheFiles direct write helpers, and unbind pinning from `daemon.c`.

## Risks and Edge Cases
The request protocol has many races: daemon death versus enqueue, fd release versus `copen`, interrupted wait versus daemon completion, close requests without replies, and read requests on closed objects requiring reopen work. Unbind pinning must keep cache state alive while anonymous fds exist. Message ID reuse is deliberately avoided with cyclic free-slot selection. `restore` can replay half-processed requests after daemon crash, so request handlers must be idempotent enough for recovery.

## Test Signals
Test open/read/close happy paths, daemon crash and `restore`, anonymous fd close before `copen`, interrupted waits, object drop with pending requests, duplicate opens, read completion ioctl validation, userspace write alignment and errors, and on-demand-off build stubs.
