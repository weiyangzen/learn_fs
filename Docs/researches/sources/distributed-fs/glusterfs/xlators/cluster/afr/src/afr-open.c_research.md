# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-open.c

## Purpose
Implements AFR file open and background fd reopen repair. Opens are broadcast to all up children while avoiding direct truncation outside AFR transactions; fd repair reopens fds on children that were down or not opened when the fd was first established.

## Important APIs, types, and functions
`afr_open()` checks quorum and consistency, stores fd flags in `afr_fd_ctx_t`, refreshes split-brain/readability state when needed, then calls `afr_open_continue()`. `afr_open_cbk()` records child open status and optionally issues an AFR-level `ftruncate` when the original open included `O_TRUNC`. `afr_fix_open()` creates an internal frame for fd repair. `afr_fd_ctx_set_need_open()` marks eligible children `AFR_FD_OPENING`; `afr_is_reopen_allowed()` queries locks with `lk(F_GETLK)` and `fd-reopen-status`; `afr_do_fix_open()` winds open/opendir to missing children.

## Control flow
Normal open initializes local/fd context, strips `O_TRUNC` from child `open`, winds open to all up children, handles reply quorum, and unwinds or runs truncation through the translator. Reopen repair first validates the fd is non-anonymous and has a gfid, marks missing children, asks up children whether reopen is safe around locks, and either opens missing children or resets their state to not opened.

## State and persistence behavior
Fd context persists in memory with `flags` and `opened_on[]` states. `O_TRUNC` can cause durable size change through a transaction-safe ftruncate path. Reopen repair only changes fd state and child open handles; it does not directly mutate file contents.

## Dependencies and integration points
Depends on AFR transaction/ftruncate, inode refresh and split-brain helpers, child open/opendir/lk FOPs, fd context helpers, protocol `fd-reopen-status` values, Gluster statedump/logging, and read paths that call `afr_fix_open()` before fd-based operations.

## Risks and test signals
Risks include truncating outside correct transaction ordering, reopening despite conflicting locks, leaving `AFR_FD_OPENING` stuck after failures, fd repair on anonymous/null-gfid fds, and quorum handling for partial opens. Tests should cover open with and without `O_TRUNC`, child-down then child-up fd repair, conflicting locks blocking reopen, directory fd repair, all-open-fail, and xdata propagation from successful child opens.
