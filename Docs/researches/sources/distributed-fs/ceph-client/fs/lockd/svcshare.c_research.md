# sources/distributed-fs/ceph-client/fs/lockd/svcshare.c

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/svcshare.c` manages NLM DOS-style share reservations for files served by lockd. It creates, updates, removes, and bulk-traverses per-file `nlm_share` records. The source was read as a complete 125-line file for this report.

## Important APIs, Types, and Functions

The local helper `nlm_cmp_owner` compares an existing `nlm_share` owner handle with a request owner handle. Public/common functions are `nlmsvc_share_file`, `nlmsvc_unshare_file`, and `nlmsvc_traverse_shares`. State is stored in the `file->f_shares` singly-linked list of `struct nlm_share` objects.

## Control Flow

`nlmsvc_share_file` first rejects files that cannot lock, then scans existing shares. If a share for the same host and owner exists, it updates the access and mode fields. If another share conflicts by requested access/mode, it returns denied. Otherwise it allocates one object plus inline owner-handle storage, copies the owner, links it at the head of `file->f_shares`, and returns granted. `nlmsvc_unshare_file` scans the same list, removes matching host/owner entries, and returns granted even if no matching share exists. `nlmsvc_traverse_shares` removes all shares whose host matches a supplied predicate.

## State and Persistence Behavior

Share state is in-memory only and attached to `struct nlm_file`. Owner-handle bytes are stored inline after each allocated `struct nlm_share`. Shares disappear when explicitly unshared, when host resources are freed, or when the file record is reclaimed by `svcsubs.c`.

## Dependencies and Integration Points

The file integrates with lockd host/file structures from `lockd.h`, share declarations from `share.h`, and the NLM procedure handlers in `svcproc.c`/`svc4proc.c`. Resource cleanup is driven by `nlmsvc_traverse_files` in `svcsubs.c`.

## Risks and Edge Cases

Conflicts depend on bitwise overlap of access and deny modes, so procedure-layer validation of mode values matters. There is no local locking in this file; callers must serialize access through the owning file/resource traversal path. Owner handles are length-sensitive binary blobs, not NUL-terminated strings. The X/Open behavior of successful unshare for a missing reservation is intentional.

## Test Signals

Test same-host same-owner updates, conflicting and non-conflicting share combinations, unshare of present and absent entries, FREE_ALL and host-reboot cleanup through `nlmsvc_traverse_shares`, allocation failure status, and SHARE/UNSHARE during grace/reclaim from both v1/v3 and v4 handlers.
