# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/call-stub.h

## Purpose
`call-stub.h` declares the deferred-call representation used to capture GlusterFS FOP calls and callbacks for later resume or unwind. It centralizes prototypes for creating stubs across the full FOP surface.

## Important APIs, Types, and Functions
- `call_stub_t`: contains list linkage, `call_frame_t *`, unions of FOP function pointers and callback pointers, FOP id, poison/wind state, and captured `default_args_t`/`default_args_cbk_t`.
- `fop_*_stub()` declarations: capture forward FOP invocations such as lookup, open, readv, writev, locks, xattrs, create, put, and copy_file_range.
- `fop_*_cbk_stub()` declarations: capture callbacks with op_ret/op_errno and returned data.
- `call_resume()`, `call_resume_keep_stub()`: resume captured work.
- `call_stub_destroy()`: release captured references.
- `call_unwind_error()`, `call_unwind_error_keep_stub()`: unwind captured calls with errors.

## Control Flow
The header itself declares contracts; implementation code allocates `call_stub_t`, stores the selected function pointer in the correct union member, captures arguments into `default_args_t` or callback args, then later resumes or unwinds based on `fop`/`wind`. Callers can keep or destroy the stub depending on the resume/unwind variant.

## State and Persistence
Stub state is in-memory, listable, and frame-associated. It captures references to GlusterFS objects and must follow ownership rules enforced by implementation. There is no persistence.

## Dependencies and Integration Points
Depends on `defaults.h`, `default-args.h`, `list.h`, FOP typedefs, `call_frame_t`, `loc_t`, `fd_t`, `dict_t`, `inode_t`, lock types, and iovec/iobref structures. Translators use it for delayed operations, serialization, throttling, barriers, and error unwinds.

## Risks and Edge Cases
- Prototype drift from generator metadata or FOP typedefs can break compilation or ABI assumptions.
- Captured pointer lifetimes are subtle; implementation must ref/unref all objects consistently.
- Some declarations intentionally map closely related callback types, which makes copy/paste type mistakes likely.
- `poison` and `wind` fields indicate lifecycle state and misuse can lead to double resume or double free.

## Test Signals
Compile-time coverage is critical across all FOP stubs. Runtime tests should capture/resume/destroy representative entry, inode, fd, xattr, lock, read/write, and callback stubs, including error unwind and keep-stub variants with refcount leak checks.
