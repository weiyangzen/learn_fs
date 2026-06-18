# sources/distributed-fs/glusterfs/xlators/protocol/client/src/client-common.c

## Purpose

`client-common.c` is the protocol/client v2 marshalling layer. It translates Gluster in-memory arguments (`loc_t`, `fd_t`, `dict_t`, `iatt`, `gf_flock`, `gf_lease`) into `gfx_*` XDR request structures before RPC submission, and translates `gfx_*` XDR responses back into callback-facing C structures and dictionaries. It is shared by `client-rpc-fops_v2.c` request and callback handlers.

## Important APIs, types, and functions

- `client_cmd_to_gf_cmd()` maps POSIX fcntl commands, including reserve-lock and fd-lock variants, to `GF_LK_*` protocol commands.
- `client_post_common_iatt()`, `client_post_common_2iatt()`, `client_post_common_3iatt()`, and `client_post_common_dict()` decode common response shapes and xdata dictionaries.
- `client_post_readv_v2()`, `client_post_create_v2()`, `client_post_lease_v2()`, `client_post_lk_v2()`, `client_post_readdir_v2()`, `client_post_readdirp_v2()`, and `client_post_rename_v2()` handle fop-specific response payloads.
- `client_pre_*_v2()` functions populate request structures for nearly every v2 fop: namespace ops, fd ops, xattr ops, locks, readdir, allocation/discard/zerofill, lease, put, seek, rchecksum, and copy-file-range.
- `CLIENT_GET_REMOTE_FD()` is used through `client_get_remote_fd()` for fd-based requests and selects either a real remote fd, anonymous fd fallback, or EBADFD failure.
- `set_fd_reopen_status()` writes `"fd-reopen-status"` into xdata and relaxes reopen restrictions when `conf->strict_locks` is disabled.

## Control flow

The request builders follow two patterns. Path-based builders validate `loc` and inode/parent availability, choose a gfid from inode when present or from `loc` fallback fields, assert non-null gfids, copy basename/linkname/flags/mode/offset fields, then serialize xdata with `dict_to_xdr()`. Fd-based builders call `CLIENT_GET_REMOTE_FD()` with either `DEFAULT_REMOTE_FD` or `FALLBACK_TO_ANON_FD`, copy the fd inode gfid, fill operation parameters, and serialize xdata.

The response helpers decode only when the server operation succeeded where data is meaningful. Stat-bearing responses copy `gfx_stat` fields with `gfx_stat_to_iattx()`. Dictionary responses call `xdr_to_dict()` for the main dict and xdata. Readdir responses delegate list materialization to helper functions in `client-helpers.c`. Readv binds the RPC response iobref and payload vector to callback output when `op_ret > 0`.

## State and persistence behavior

This file does not own durable state. It reads client configuration through `this->private` only for fd lookup and strict-lock reopen-status policy. It writes transient XDR buffers inside request structs, which callers must free after `client_submit_request()`. Its persistent effect is indirect: by embedding remote fd numbers, gfids, flags, lock data, and xdata in requests, it defines the on-wire state transitions seen by the server.

## Dependencies and integration points

The file depends on Gluster core structures and helpers from `client.h`, `glusterfs3.h`, dict XDR helpers, fd-context lookup through `CLIENT_GET_REMOTE_FD`, gfid utilities, protocol stat/flock/lease conversion helpers, and message IDs from `client-messages.h`. `client-rpc-fops_v2.c` calls these functions before submitting RPCs and after decoding callbacks.

## Risks and edge cases

- Many builders return negative errno values such as `-ESTALE`, `-EINVAL`, or `-EBADF`; callers must convert them correctly when unwinding.
- Null gfid assertions are common and can turn partially initialized `loc_t` or fd/inode state into request failure.
- Fd fallback to anonymous fd is intentionally selective and depends on lock state and strict-lock policy, so widening fallback can break lock correctness.
- `client_pre_writev_v2()` contains a conditional test-only path using `ret` under `GF_TESTING_IO_XDATA`; that configuration depends on external declarations/macros compiling cleanly.
- Several request structs keep borrowed string pointers (`loc->name`, xattr names, volume names); callers must not outlive the original frame data before serialization completes.
- `set_fd_reopen_status()` assumes non-null `xdata`; callers using it must allocate xdata on local error paths.

## Test signals

Good tests cover gfid source precedence for inode vs loc fallback, null-gfid rejection, each fd fallback mode under strict/non-strict locks, lock command/type conversion, xdata round trips, dict decode failure handling, readdir/readdirp decode, copy-file-range dual-fd handling, and `fd-reopen-status` behavior for write-lock vs read/unlock cases.
