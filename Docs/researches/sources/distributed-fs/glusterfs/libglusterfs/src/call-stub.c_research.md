# sources/distributed-fs/glusterfs/libglusterfs/src/call-stub.c

## Purpose
`call-stub.c` implements the allocation, storage, replay, unwind, and destruction path for GlusterFS `call_stub_t` objects. A stub captures either a forward FOP invocation (`wind == 1`) or a callback/unwind payload (`wind == 0`) so translators can queue work, resume it later, or synthesize error unwinds without keeping the original stack active.

## Important APIs, Types, And Functions
The file centers on `call_stub_t`, defined in `glusterfs/call-stub.h`, whose fields include a list hook, `call_frame_t *frame`, FOP callback unions, `glusterfs_fop_t fop`, `wind`, `default_args_t args`, and `default_args_cbk_t args_cbk`.

`stub_new(frame, wind, fop)` allocates and initializes a stub, including the list heads and callback directory-entry list. Every public `fop_*_stub` and `fop_*_cbk_stub` constructor delegates to it, stores the function pointer in `fn` or `fn_cbk`, and deep/ref-count stores arguments through the `args_*_store` helpers from `default-args`.

The constructor family covers the normal filesystem surface: lookup/stat/fstat, create/open/read/write/put, namespace ops, xattr ops, locks, readdir/readdirp, rchecksum, setattr, fallocate/discard/zerofill, ipc, lease, seek, get/set active locks, icreate, namelink, and copy-file-range. A few internal helpers fill callbacks manually where no generic store helper is used, such as `args_icreate_store_cbk` and `args_namelink_store_cbk`.

`call_resume_wind()` switches on `stub->fop` and calls the captured forward FOP. `call_resume_unwind()` does the same for callback paths using `STUB_UNWIND`, which either invokes the stored callback function or falls back to `STACK_UNWIND_STRICT`. `call_resume()` and `call_resume_keep_stub()` remove the stub from its list, set `THIS` to `stub->frame->this` for the duration, and resume the proper path. `call_unwind_error()` and `call_unwind_error_keep_stub()` overwrite `op_ret`/`op_errno` and unwind an error. `call_stub_destroy()` wipes either `args` or `args_cbk` and frees the stub.

## Control Flow
A caller constructs a stub with a FOP-specific constructor. The constructor validates selected mandatory arguments, allocates the stub, writes the function pointer, and stores arguments with ownership-preserving copies or refs. Later, `call_resume()` removes it from any queue, binds `THIS`, invokes the wind or unwind switch, restores `THIS`, and destroys the stub. The keep-stub variants perform the same replay but intentionally leave ownership of argument cleanup to the caller.

## State And Persistence Behavior
State is in-memory only. The file persists no data to disk. It manipulates reference-counted GlusterFS runtime objects such as `dict_t`, `fd_t`, `inode_t`, `loc_t`, `iobref`, and directory-entry lists through `args_*_store` and `args_*_wipe`. The `list` hook makes stubs suitable for translator queues. The `THIS` global is temporarily rebound around replay, which is part of runtime execution context state rather than durable state.

## Dependencies And Integration Points
This code depends on `glusterfs/call-stub.h`, `glusterfs/default-args.h`, stack macros, `GF_CALLOC/GF_FREE`, `GF_VALIDATE_OR_GOTO`, `gf_msg_callingfn`, `STACK_UNWIND_STRICT`, and the translator FOP type system. It integrates with translators that defer or serialize operations, with sync/async stack unwinding, and with the generic `default_args` ownership model.

## Risks And Edge Cases
The switch statements must remain synchronized with `call_stub_t` unions, constructor coverage, and `glusterfs_fop_t` values. Missing a new FOP in either resume switch causes an invalid-FOP log instead of replay. Constructor validation is uneven: some constructors validate primary pointers while others rely on lower layers or store helpers. `fop_fgetxattr_cbk_stub()` creates a stub with `GF_FOP_GETXATTR` rather than `GF_FOP_FGETXATTR`, which is worth reviewing because the unwind switch has distinct cases. `fop_setactivelk_cbk_stub()` stores callback xdata into `stub->args.xdata` instead of `stub->args_cbk.xdata`, which looks suspicious for cleanup and unwind behavior. Keep-stub APIs can leak retained refs if callers do not later destroy or wipe the stub.

## Test Signals
Useful tests should cover deferred replay for representative wind and unwind FOPs, error unwind synthesis, argument ref/wipe balance under ASAN or leak checking, missing-callback fallback to `STACK_UNWIND_STRICT`, directory-entry cleanup, active-lock callback xdata ownership, and parity between every new `GF_FOP_*` enum value and the constructor/resume/unwind switch coverage.
