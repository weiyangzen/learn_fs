# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_ptr_util.h

## Purpose

`i915_ptr_util.h` provides low-level pointer tagging and conversion helpers used by i915 code that stores small bitfields in naturally aligned pointers or needs sparse-friendly container calculations for `__user` pointers.

## Important APIs, types, and functions

The macro API includes `ptr_mask_bits()`, `ptr_unmask_bits()`, `ptr_unpack_bits()`, `ptr_pack_bits()`, `ptr_dec()`, `ptr_inc()`, page-specific wrappers `page_mask_bits()`, `page_unmask_bits()`, `page_pack_bits()`, `page_unpack_bits()`, `u64_to_ptr(T, x)`, and `container_of_user()`. The only function is `static __always_inline ptrdiff_t ptrdiff(const void *a, const void *b)`.

## Control flow

All helpers expand inline at call sites. Pack/unpack helpers cast through `unsigned long`, mask low bits using `BIT(n)`, and cast back to the original pointer type. `ptr_pack_bits()` asserts with `GEM_BUG_ON()` if the supplied bits do not fit in the low `n` bits. `container_of_user()` performs compile-time member type checks and returns a `type __user *`.

## State and persistence behavior

The header stores no state. It defines reversible encodings where low pointer bits carry flags and the remaining high bits carry the aligned pointer. The correctness depends on callers only packing bits into alignment-guaranteed zero bits, especially page-aligned addresses for the page wrappers.

## Dependencies

It depends on Linux types and standard kernel helper macros such as `BIT`, `typecheck`, `BUILD_BUG_ON_MSG`, `__same_type`, `typeof_member`, `offsetof`, and i915 `GEM_BUG_ON` from included contexts.

## Integration points

This is a utility header for i915 internals. It is suitable for GEM/VM data structures that tag flags in object or page pointers, uAPI conversion code that receives 64-bit pointer values, and sparse-checked user-pointer container calculations.

## Risks

Pointer tagging is architecture- and alignment-sensitive. Packing too many bits, passing unaligned pointers, or applying `ptr_inc()`/`ptr_dec()` to tagged pointers can corrupt addresses. `ptrdiff()` subtracts `void *`, which is accepted as a kernel/GNU extension but should not be treated as portable ISO C. `u64_to_ptr()` should not be used for unchecked userspace addresses when `u64_to_user_ptr()` is the correct API.

## Test signals

Build coverage with sparse is important for `container_of_user()`. Unit-style checks should round-trip pack/unpack for aligned pointers, assert rejection of out-of-range tag bits in debug builds, and verify page tag helpers preserve page addresses.
