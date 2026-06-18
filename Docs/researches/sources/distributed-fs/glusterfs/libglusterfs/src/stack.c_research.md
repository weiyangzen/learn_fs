# sources/distributed-fs/glusterfs/libglusterfs/src/stack.c

## Purpose

`stack.c` manages Gluster call stack/frame allocation and diagnostic dumping. It creates root frames for translator operations, records ownership and latency metadata, tracks live stacks in a call pool, and serializes pending frame data either to statedump output or dictionaries.

## Important APIs, Types, and Functions

Important functions are `create_frame()`, `call_stack_set_groups()`, `gf_proc_dump_pending_frames()`, `gf_proc_dump_pending_frames_to_dict()`, and `__is_fuse_call()`. Internal helpers serialize individual frames and stacks: `gf_proc_dump_call_frame()`, `gf_proc_dump_call_stack()`, `gf_proc_dump_call_frame_to_dict()`, and `gf_proc_dump_call_stack_to_dict()`. The code operates on `call_pool_t`, `call_stack_t`, `call_frame_t`, `xlator_t`, and `dict_t`.

## Control Flow and Data Flow

`create_frame()` allocates a stack and root frame from the call pool's mempools, initializes list links and locks, associates the frame with the translator and context, records timing if latency measurement is enabled, links the stack into `pool->all_frames` under the pool lock, increments live counters, and returns the frame. `call_stack_set_groups()` takes ownership of a caller-provided gids buffer, copies small group sets into embedded storage or stores the large allocation pointer, and poisons the caller's pointer with a canary.

Dumping attempts nonblocking locks so diagnostic paths do not stall core execution. Frame data is copied under frame lock before writing. Call-pool dumping locks the pool, writes global counters, iterates live stacks, and serializes stack identity, credentials, operation type, lock owner, creation time, and each frame's translator/parent/wind/unwind fields. Dict dumping follows the same structure with stable key prefixes.

## State and Persistence Behavior

Live stack state is in memory and tied to operation lifetime. Statedump output persists only when `statedump.c` writes it to disk or a caller consumes the generated dict. Latency timestamps are captured at frame creation and later exposed for diagnostics. Group ownership transfer is permanent for the stack until stack destruction.

## Dependencies and Integration Points

The file depends on mempool allocation, Gluster lists and locks, `timespec_now()`, statedump writers, dictionary setters, translator metadata, and FOP name tables. It integrates with `syncop.c` for synctask-created operation frames, with the general call-wind/unwind stack macros, and with process statedumps.

## Risks and Edge Cases

The static `unique` counter in `create_frame()` is incremented only while holding the pool lock, which avoids local races but resets per process. Dump-to-dict functions often return early on allocation or dict errors, producing partial diagnostics. `gf_proc_dump_call_stack()` assumes operation indexes and `gf_fop_list` are valid when type is FOP. `__is_fuse_call()` treats any pid other than `NFS_PID` as FUSE, which is a narrow historical distinction rather than a full protocol classifier.

## Test Signals

Tests should verify frame allocation failure cleanup, pool counter/list updates, small versus large group ownership, latency timestamp population, nonblocking dump behavior when frame or pool locks are held, dict key production, and stack destruction after syncop-created frames. Statedump smoke tests should include pending operations from multiple translators.
