# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_ioctl.c

## Purpose

`uverbs_ioctl.c` is the generic ioctl execution engine for the RDMA uverbs ABI. It receives `RDMA_VERBS_IOCTL`, validates the userspace `ib_uverbs_ioctl_hdr`, resolves the requested object/method in the precomputed `uverbs_api` radix tree, parses the attribute array, invokes the registered method handler, and then commits or aborts any referenced uobjects. It is the central trust boundary between userspace and all `DECLARE_UVERBS_*` method handlers in the standard type files and provider extensions.

## Important APIs, Types, and Functions

- `struct bundle_priv` is the private backing storage for `struct uverbs_attr_bundle`; it tracks the selected method, radix lookup cache, copied user attributes, per-call allocation blocks, output/finalize bitmaps, and the inline `internal_buffer`.
- `uapi_compute_bundle_size()` precomputes whether a method can use on-stack storage or needs a kmalloc-backed bundle, based on method bitmap length and expected attribute count.
- `_uverbs_alloc()` is the bundle-scoped allocator used by handlers and parser helpers. Allocations live only for the syscall and are freed by `bundle_destroy()`.
- `ib_uverbs_ioctl()` is the file operation entry point. It accepts only `RDMA_VERBS_IOCTL`, validates length/reserved fields, and runs the command under `device->disassociate_srcu`.
- `ib_uverbs_cmd_verbs()` resolves the method by `object_id` and `method_id`, creates the bundle, and calls `ib_uverbs_run_method()`.
- `uverbs_process_attr()`, `uverbs_set_attr()`, and `uverbs_process_idrs_array()` implement the attribute type parser for pointer, enum, idr, fd, raw fd, and object-array attributes.
- `ib_uverbs_run_method()` copies the user attribute descriptors, rejects duplicates, checks mandatory attributes, builds `ib_udata`, handles special destroy ordering, calls the handler, and marks UHW output as valid.
- Exported helpers such as `uverbs_get_flags64()`, `uverbs_get_flags32()`, `uverbs_fill_udata()`, `uverbs_copy_to()`, `uverbs_copy_to_struct_or_zero()`, `_uverbs_get_const_*()`, `uverbs_finalize_uobj_create()`, `_ib_copy_validate_udata_in()`, and `_ib_respond_udata()` are consumed by standard object handlers and provider code.

## Control Flow

The ioctl path is: userspace ioctl -> copy and validate `ib_uverbs_ioctl_hdr` -> SRCU read lock -> radix lookup of object/method -> allocate `bundle_priv` -> copy the `ib_uverbs_attr` array -> parse each attribute against its `uverbs_attr_spec` -> enforce mandatory bitmap -> synthesize `driver_udata` if the method declares `UVERBS_ATTR_UHW` -> optionally pre-destroy an object for destroy methods -> invoke the method handler -> mark valid outputs -> finalize all uobjects and IDR arrays with commit on success or abort on failure -> free bundle memory.

Attribute parsing is deliberately strict. Unknown optional attributes are ignored, unknown mandatory attributes return `-EPROTONOSUPPORT`, duplicate attributes return `-EINVAL`, trailing non-zero bytes in extensible input structs return `-EOPNOTSUPP`, and object NEW/DESTROY references are recorded for later finalization. This makes ABI probing predictable and keeps object lifetime changes centralized.

## State and Persistence Behavior

The file does not persist durable state. Its important state is per-call bundle memory, bitmaps describing which attributes and uobjects were seen, and references acquired from the file's uobject tables. Commit/abort is delegated to `uverbs_finalize_object()` and `uobj_destroy()` in `rdma_core`. Output state is communicated to userspace by setting `UVERBS_ATTR_F_VALID_OUTPUT` in the original userspace attribute descriptor after a successful write.

## Dependencies and Integration Points

It depends on `rdma_user_ioctl.h` for ABI structures, `rdma/uverbs_ioctl.h` for attribute helpers/macros, `rdma_core.h` for uobject lookup/finalization, and `uverbs.h` for file/device structures. It integrates with `uverbs_uapi.c` through `struct uverbs_api_ioctl_method`, with `uverbs_main.c` through `ib_uverbs_ioctl` in the file operations, and with every standard/provider method handler through `struct uverbs_attr_bundle`.

## Risks and Edge Cases

The highest-risk behavior is ABI parsing and lifetime finalization. Bugs in bitmap indexing, inline pointer handling, object-array cleanup, or the NEW/DESTROY single-object contract can leak uobjects, destroy live objects, or expose stale output. The code mitigates this with fixed key bitmap limits, strict mandatory checks, radix-key validation done during API finalization, and centralized `bundle_destroy()`. Disassociation races are controlled by `disassociate_srcu`; provider handlers are fetched with SRCU and may be nulled during teardown.

Other risk areas include copied vs inline pointer attributes, zero-trailing compatibility checks, raw fd range checking, and the special `-EPROTONOSUPPORT` rule, where handlers must not return that value except framework-level unsupported paths.

## Test Signals

Useful test signals include ioctl fuzzing for duplicate/unknown/mandatory attributes, zero-trailing extensible struct tests, invalid header length/reserved field tests, uobject create failure rollback, destroy failure behavior, UHW input/output size tests, compatibility of 32-bit and 64-bit flags, and device disassociation while ioctl handlers are running.
