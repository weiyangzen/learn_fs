<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/arbiter/src/arbiter.c -->
# sources/distributed-fs/glusterfs/xlators/features/arbiter/src/arbiter.c

## Purpose
Feature translator used for arbiter bricks in replicated volumes. It lets AFR receive successful metadata-shaped responses for selected inode write operations without writing user data to the arbiter brick, while still allowing lookup/self-heal style operations to reach the child.

## APIs, Types, and Functions
Important helpers are `__arbiter_inode_ctx_get()`, `arbiter_inode_ctx_get()`, `arbiter_lookup_cbk()`, `arbiter_fill_writev_xdata()`, and `arbiter_forget()`. FOPs include `lookup`, write-like short-circuit handlers for `truncate`, `ftruncate`, `writev`, `fallocate`, `discard`, and `zerofill`, plus defensive `readv` and `seek` returning `ENOSYS`. The translator exports standard `init`, `fini`, `reconfigure`, `mem_acct_init`, `fops`, `cbks`, `options`, and `xlator_api`.

## Control Flow, State, and Persistence
`lookup` winds to the child and its callback allocates or retrieves `arbiter_inode_ctx_t` under the inode lock, then caches the returned `iatt`. Short-circuited write-like FOPs retrieve that cached `iatt`, return success, and unwind with pre/post buffers both pointing to the cached attributes; `writev` returns `iov_length()` and may echo requested `GLUSTERFS_OPEN_FD_COUNT` and `GLUSTERFS_WRITE_IS_APPEND` xdata. `forget` deletes and frees inode ctx. There is no on-disk persistence in this translator; persistence remains with lower translators for FOPs that are allowed through defaults.

## Dependencies and Integration
Depends on GlusterFS dict, stack, logging, inode ctx, iovec, and memory-accounting APIs. It must have exactly one child and is intended to sit where AFR can target an arbiter child.

## Risks and Test Signals
Risks include stale cached `iatt` if lookup is old, successful write-like replies that do not reflect storage changes, no owned xdata on most short-circuit replies, assumptions that inode/fd and ctx are present, and correctness dependence on AFR not sending normal application reads to the arbiter. Test signals are arbiter-volume lookup/write/truncate/fallocate/discard/zerofill behavior, `ENOSYS` for accidental reads/seeks, inode ctx cleanup on forget, xdata echo behavior for writev, and validation that self-heal/stat/xattr operations still pass through by default.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/arbiter/src/arbiter.c -->
