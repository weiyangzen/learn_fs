# sources/distributed-fs/ceph-client/include/rdma/uverbs_ioctl.h

Purpose: Defines the RDMA uverbs ioctl description DSL, radix-tree key encoding, parsed attribute bundle, and helper accessors for safely moving data and object references between userspace and RDMA drivers.

Important APIs/types/functions: `struct uverbs_attr_spec`, `uverbs_attr_def`, `uverbs_method_def`, `uverbs_object_def`, and `uapi_definition` describe objects, methods, write commands, attributes, support predicates, and chained definitions. Macros such as `DECLARE_UVERBS_OBJECT`, `DECLARE_UVERBS_WRITE`, `UAPI_DEF_*`, `UVERBS_ATTR_PTR_IN/OUT`, `UVERBS_ATTR_IDR`, `UVERBS_ATTR_FD`, `UVERBS_ATTR_ENUM_IN`, and `UVERBS_ATTR_UHW` build compile-time API tables. `uapi_key_*` helpers compress object/method/attr IDs. Runtime helpers include `uverbs_attr_get()`, object and length accessors, `uverbs_copy_from()`, `uverbs_copy_from_or_zero()`, allocation helpers, flag/const getters, and `ib_copy_validate_udata_in*()`.

Control flow and state: The parser validates mandatory attributes, object access mode, user pointer sizes, extension zeroing, and driver udata. Parsed data is stored in `struct uverbs_attr_bundle`, whose header carries `ib_udata`, user file, context, current uobject, and an attr-present bitmap. Object attributes refer to looked-up `ib_uobject`s; pointer attributes may be inline or user pointers. Compatibility helpers zero-pad or reject non-zero extension bytes depending on the declared ABI shape.

Dependencies and integration: Depends on uverbs object types, RDMA UAPI ioctl IDs, userspace copy helpers, `ib_uverbs_file`, `ib_ucontext`, and `ib_device_ops` feature detection. Driver method handlers receive `struct uverbs_attr_bundle`.

Risks and test signals: Risks include key-space overflow, wrong namespace/core ID encoding, missing mandatory attributes, insufficient zero-trailing checks, copying less/more than declared, stale uobject access mode, and disabled-user-access stubs returning `-EINVAL`. Tests should cover every attr type, old/new struct compatibility, invalid comp masks, object create/destroy lifetimes, driver UHW passthrough, and fuzzed ioctl payloads.
