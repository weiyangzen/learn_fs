# sources/distributed-fs/ceph-client/fs/lockd/share.h

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/share.h` declares DOS share-mode support used by lockd's server personality. The source was read as a complete 33-line header.

## Important APIs, Types, and Functions

The key type is `struct nlm_share`, which links a share record to a host, file, owner handle, access mode, and deny mode. It defines `LOCKD_SHARE_SVID` as a synthetic owner ID and declares `nlmsvc_share_file`, `nlmsvc_unshare_file`, and `nlmsvc_traverse_shares`.

## Control Flow

There is no executable flow. Server share-management code uses this contract to add, remove, and traverse DOS share records associated with `struct nlm_file`.

## State and Persistence Behavior

Share records are in-memory server-side state hanging from `nlm_file->f_shares`; they persist only while lockd tracks the remote client's share.

## Dependencies and Integration Points

The header depends on `struct nlm_host`, `struct nlm_file`, `struct xdr_netobj`, and `nlm_host_match_fn_t` from lockd internals. It integrates with server resource traversal and cleanup on host reboot/shutdown.

## Risks and Edge Cases

Share owner comparison depends on opaque owner handles and the synthetic SVID used for lookup. Traversal callbacks must safely remove shares during host/resource cleanup.

## Test Signals

Signals include server-side SHARE/UNSHARE procedure tests, conflicting access/deny mode tests, owner-handle matching, host reboot cleanup, and share traversal under concurrent file resource cleanup.
