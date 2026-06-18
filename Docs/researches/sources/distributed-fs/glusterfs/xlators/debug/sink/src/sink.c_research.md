# sources/distributed-fs/glusterfs/xlators/debug/sink/src/sink.c

## Purpose
Implements a minimal `debug/sink` translator. It can terminate a graph for debugging by reporting itself up/down to parents and satisfying only root lookup with a directory-like inode response.

## Important APIs, types, and functions
`init()` and `fini()` are no-op lifecycle hooks. `notify()` maps `GF_EVENT_PARENT_UP` to `GF_EVENT_CHILD_UP` and `GF_EVENT_PARENT_DOWN` to `GF_EVENT_CHILD_DOWN` through `default_notify()`. `sink_lookup()` returns success for lookup by unwinding with `op_ret = 0`, `op_errno = 0`, the supplied inode, a zeroed `struct iatt` with `ia_type = IA_IFDIR`, the original xdata, and a zeroed postparent. The exported `fops` table only registers `.lookup`; `cbks` is empty; `xlator_api` identifies the module as `sink`, category `GF_TECH_PREVIEW`.

## Control flow
Mount or `glfs_init()` root lookup reaches `sink_lookup()`, which manufactures enough directory metadata for the root to appear valid and immediately unwinds. Parent graph events are reflected as child graph events so the xlator can be considered available. All other events are ignored, and all unimplemented FOPs fall back to absent/default behavior from the xlator framework.

## State and persistence behavior
There is no private state, allocation, background thread, or durable persistence. Returned lookup metadata is transient and minimal.

## Dependencies and integration points
Includes `glusterfs/defaults.h` for default notification and xlator definitions. Integrates as a debug graph endpoint or placeholder where a child xlator would normally exist.

## Risks and test signals
Because only lookup is implemented and the returned `iatt` is sparse, this xlator is suitable only for narrow debug use. Tests should verify parent-up/down notification mapping, root lookup success, and expected failures or unsupported behavior for non-lookup operations. If advanced debugging use is added, lookup should distinguish paths and populate more metadata.
