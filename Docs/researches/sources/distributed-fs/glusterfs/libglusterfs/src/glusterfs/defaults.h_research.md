# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/defaults.h

## Purpose
Defines the default translator operation surface for libglusterfs. It gives translators standard pass-through FOPs, callbacks, resume handlers, failure callbacks, notify/release/forget hooks, and argument carrier structures.

## APIs, Types, and Functions
`default_args_cbk_t` stores callback state such as op status, inode/fd, stat/pre/post buffers, vectors, iobrefs, xattrs/xdata, checksums, dirents, seek offsets, leases, and lock lists. `default_args_t` stores request-side state such as locs, fds, offsets, modes, masks, flags, link names, lock domains, xattr operations, lease data, and copy-file-range fds/offsets. The header declares `default_fops`, `default_notify()`, `default_forget()`, `default_release()`, `default_releasedir()`, normal `default_*` FOP/MOP entry points, `default_*_resume()` variants, `default_*_cbk()` and `default_*_cbk_resume()` handlers, `default_*_failure_cbk()` helpers, `default_mem_acct_init()`, and `default_fini()`.

## Control Flow, State, and Persistence
Default operations typically wind a request to the first child or unwind a standardized failure. Resume variants re-enter operations after call-stub/synctask suspension. Callback variants relay child results back up the stack. The structures are transient per-call state, while `default_fops` is a shared function table.

## Dependencies and Integration
Depends on `dict.h`, `iatt.h`, `locking.h`, and `stack.h`, plus core translator, inode, fd, iobuf, dirent, lease, and lock types. It is the integration baseline for xlators that only override selected operations.

## Risks and Test Signals
Risks include prototype mismatches across normal/resume/callback paths, incorrect default behavior for newer FOPs, refcount mistakes in saved arguments, and failure callbacks that lose required xdata or pre/post attributes. Test signals are translator pass-through tests, stacked xlator smoke tests, FOP signature compile coverage, leak checks on stubbed calls, and negative-path tests for each failure callback.
