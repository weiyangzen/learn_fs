<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/glimpse.c -->
# sources/distributed-fs/lustre-release/lustre/llite/glimpse.c

## Purpose

`glimpse.c` implements llite/VVP glimpse-size support. A glimpse asks the Lustre lock and object layers for current file size, block count, and timestamps without revoking conflicting client locks. It is used by getattr, seek, fiemap, and other paths that need fresh file-size information from OST-side object state.

## Important APIs, Types, And Functions

- `dirty_cnt(struct inode *inode)`: returns a binary indication that the inode may have dirty page-cache or mmap state. It checks the mapping dirty tag and VVP mmap count.
- `cl_glimpse_lock(const struct lu_env *env, struct cl_io *io, struct inode *inode, struct cl_object *clob, int agl)`: requests a whole-file CL read lock with `CEF_GLIMPSE | CEF_MUST`; optional AGL mode adds speculative nonblocking flags.
- `cl_io_get(struct inode *inode, struct lu_env **envout, struct cl_io **ioout, u16 *refcheck)`: obtains a CL environment and `cl_io` for regular-file special operations.
- `__cl_glimpse_size(struct inode *inode, int agl)`: initializes a `CIT_GLIMPSE` CLIO, requests the glimpse lock, merges attributes for normal glimpses, and retries when FLR mirror state asks for restart.

The static `whole_file` descriptor represents a read lock over `[0, CL_PAGE_EOF]`.

## Control Flow

Callers enter through `__cl_glimpse_size()`. Non-regular inodes return `0` from `cl_io_get()` and are skipped. Regular files allocate a thread CL environment, set `ci_ndelay` and `ci_verify_layout`, and initialize a `CIT_GLIMPSE` I/O. If initialization says there is no work, the stored `ci_result` is returned. Otherwise `cl_glimpse_lock()` submits a whole-file glimpse lock request.

For normal, non-AGL glimpses, a successful request is followed by `ll_merge_attr()` so inode size, blocks, and timestamps reflect OST attributes. If the file has positive size but zero blocks, `dirty_cnt()` supplies a minimal block count so userspace tools do not treat a dirty or mmaped file as fully sparse. The CL lock is released and the CLIO finalized each iteration. `-EAGAIN` from a non-AGL FLR path can set `ci_need_restart` until all needed mirrors are tried.

## State And Persistence Behavior

No persistent state is written. The code updates in-memory inode attributes through `ll_merge_attr()` and may set `inode->i_blocks` to `1` when dirty/mmaped state indicates unwritten local data. It consumes transient CL environment, CLIO, and CL lock objects and releases them before returning.

## Dependencies And Integration Points

The file depends on LDLM/CLIO/VVP infrastructure, Linux page-cache dirty tags, and llite inode/object helpers. It integrates with `file.c` through `ll_merge_attr()` and the public glimpse wrapper used by getattr, seek, and fiemap paths. It relies on OSC behavior for `CEF_GLIMPSE`: conflicting locks trigger glimpse callbacks rather than ordinary lock revocation, and valid attributes can be returned even when the actual lock enqueue fails with `-ENAVAIL`.

## Risks And Edge Cases

- `dirty_cnt()` intentionally returns only 0 or 1, not a full dirty-page count. It is a sparse-file correctness hint, not an accurate block estimate.
- AGL mode is speculative and nonblocking, so callers must tolerate incomplete/non-authoritative refresh.
- Retry behavior depends on FLR mirror state in `cl_io`; missing retry limits in callers would risk loops, though the code tracks tried mirrors.
- The page-cache dirty lookup uses mapping internals and should be checked against kernel API changes.
- `ll_merge_attr()` can fail independently of the glimpse lock, so stat/seek callers need to propagate or tolerate those errors.

## Test Signals

Tests should cover regular versus non-regular input, normal glimpse with dirty pages and with mmap count, zero-size and positive-size sparse files, AGL nonblocking behavior, layout-change/FLR retry on `-EAGAIN`, failure injection around `OBD_FAIL_GLIMPSE_DELAY`, and attribute merge errors. Stat and seek integration tests should verify that freshly written remote sizes become visible after glimpse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/glimpse.c -->
