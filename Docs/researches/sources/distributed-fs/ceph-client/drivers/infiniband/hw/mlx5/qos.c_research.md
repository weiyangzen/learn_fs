# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/qos.c

## Purpose

`qos.c` exposes mlx5 packet pacing rate-limit objects through the RDMA uverbs named-ioctl API. It lets DEVX-capable userspace allocate a packet pacing object, receive a hardware rate-limit table index, and later destroy that object. QPs can then use the returned index when configuring packet pacing.

The file is intentionally small: it provides capability gating, one allocation handler, one cleanup handler, uverbs object/method declarations, and the `mlx5_ib_qos_defs` uAPI definition chain consumed by mlx5 device setup.

## Important APIs, Types, and Functions

- `pp_is_supported()` gates the uAPI object on general QoS support, packet pacing support, and packet pacing UID support.
- `UVERBS_HANDLER(MLX5_IB_METHOD_PP_OBJ_ALLOC)` handles object allocation. It obtains the caller ucontext, requires `devx_uid`, copies the raw mlx5 rate-limit context, parses allocation flags, chooses either the caller DEVX UID or shared resource UID, calls `mlx5_rl_add_rate_raw()`, finalizes the uobject, and returns the allocated index.
- `pp_obj_cleanup()` removes the raw rate with `mlx5_rl_remove_rate_raw()` and frees the `struct mlx5_ib_pp` object.
- `DECLARE_UVERBS_NAMED_METHOD`, `DECLARE_UVERBS_NAMED_METHOD_DESTROY`, and `DECLARE_UVERBS_NAMED_OBJECT` define the object ABI around `MLX5_IB_OBJECT_PP`.
- `mlx5_ib_qos_defs[]` chains the object tree into the mlx5 uAPI only when `pp_is_supported()` returns true.

The main persistent kernel object is `struct mlx5_ib_pp`, which stores the mlx5 core device pointer and the allocated rate-limit index. The userspace ABI identifiers come from `rdma/mlx5_user_ioctl_cmds.h` and `rdma/mlx5_user_ioctl_verbs.h`.

## Control Flow

Allocation begins when userspace calls the named uverbs method `MLX5_IB_METHOD_PP_OBJ_ALLOC`. The handler resolves the `MLX5_IB_ATTR_PP_OBJ_ALLOC_HANDLE` uobject and the mlx5 ucontext. Non-DEVX contexts are rejected because the allocated entry can be used only by DEVX flows. The handler allocates `struct mlx5_ib_pp`, copies the bounded raw `set_pp_rate_limit_context` input into a fixed-size buffer, parses `MLX5_IB_UAPI_PP_ALLOC_FLAGS_DEDICATED_INDEX`, and chooses a UID. A dedicated index uses the calling context's `devx_uid`; otherwise the shared resource UID is used.

`mlx5_rl_add_rate_raw()` programs or reserves the rate-limit entry and returns the hardware index. On success, the object stores `mdev` and index, assigns `uobj->object`, finalizes creation, and copies the index to the mandatory output attribute. Destroying the uobject invokes `pp_obj_cleanup()`, which removes the raw rate by index and frees the allocation.

## State and Persistence Behavior

State is runtime-only. Each uverbs PP object owns one `struct mlx5_ib_pp` and one hardware rate-limit index. Lifetime is tied to the uobject IDR entry: finalize publishes the object to userspace, and destroy or ucontext cleanup calls the cleanup callback. No file-backed or persistent state is written.

The hardware rate-limit table is external state managed by mlx5 core rate-limit helpers. The cleanup path assumes `pp_entry->index` was successfully allocated before object publication; allocation failures before publication free memory locally and do not install a cleanup-visible object.

## Dependencies and Integration Points

The file depends on RDMA uverbs named-ioctl infrastructure, mlx5 user ioctl ABI headers, mlx5 capability macros, mlx5 core rate-limit helpers, and the mlx5 ucontext DEVX UID. `main.c` chains `mlx5_ib_qos_defs` into the device uAPI tree. Query-device code advertises packet pacing caps, and QP modification code uses packet pacing rate-limit indices in SQ context fields.

## Risks and Edge Cases

The input context is copied into a fixed-size stack buffer after uverbs enforces an attribute size range from 1 byte to `MLX5_ST_SZ_BYTES(set_pp_rate_limit_context)`. Correctness depends on uverbs validation and mlx5 core parsing of partially supplied raw contexts. A failure after `uverbs_finalize_uobj_create()` but before copying the index to userspace would leave a live object even though the method returns an error; callers must handle ordinary uverbs semantics for finalized objects, and this path is worth testing.

Capability gating must stay aligned with hardware requirements. Exposing the object without packet pacing UID support would allow contexts to allocate entries they cannot safely own. Cleanup assumes `uobject->object` is valid and initialized, which is true only for finalized allocations.

## Test Signals

Test with devices that both support and do not support QoS packet pacing UID capabilities. Exercise allocation with shared and dedicated flags, invalid flags, non-DEVX contexts, short and full-size raw contexts, allocation failure injection in `mlx5_rl_add_rate_raw()`, destroy after successful allocation, and ucontext teardown with live PP objects. Integration tests should verify a QP can consume the returned index and that rate entries are removed after object destruction.
