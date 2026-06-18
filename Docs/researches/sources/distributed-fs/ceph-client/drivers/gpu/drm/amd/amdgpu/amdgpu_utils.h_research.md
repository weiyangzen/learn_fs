# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_utils.h

## Purpose

`amdgpu_utils.h` provides a generic macro framework for declaring small capability classes whose capabilities have two-bit access attributes: invalid, read-only, write-only, or read-write. In this subset it is used by virtualization capability declarations in `amdgpu_virt.h`, but the macros are generic for any AMDGPU subsystem that wants compact capability metadata.

## Important APIs And Types

`enum amdgpu_cap_attr` defines the encoded values: `AMDGPU_CAP_ATTR_INVALID`, `AMDGPU_CAP_ATTR_RO`, `AMDGPU_CAP_ATTR_WO`, and `AMDGPU_CAP_ATTR_RW`. `AMDGPU_CAP_ATTR_BITS` fixes the storage width at two bits and `AMDGPU_CAP_ATTR_MAX` bounds validation.

`DECLARE_ATTR_CAP_CLASS(NAME, LIST_MACRO)` is the public macro. It expands an X-macro list into `enum NAME_cap_id { ... NAME_COUNT }` and then emits helpers via `DECLARE_ATTR_CAP_CLASS_HELPERS(NAME)`. The helpers define `struct NAME_caps` with a bitmap sized to `NAME_COUNT * 2`, `NAME_attr_init()`, `NAME_attr_set()`, `NAME_attr_get()`, and convenience predicates `NAME_cap_is_ro/wo/rw()`.

The implementation uses kernel bitmap helpers `bitmap_zero`, `bitmap_write`, and `bitmap_read`. It validates null pointers, out-of-range capability ids, and attributes wider than the two-bit field, returning `-EINVAL` on invalid inputs.

## Control Flow, State, And Integration

Callers define a list macro such as `AMDGPU_VIRT_CAPS_LIST(X)`, invoke `DECLARE_ATTR_CAP_CLASS(amdgpu_virt, AMDGPU_VIRT_CAPS_LIST)`, initialize a caps object, then set or query per-capability access attributes. The state is a compact bitmap embedded in the caller's object; there is no allocation, locking, persistence, or IO.

This header depends on bitmap APIs and error constants being available through includers. It integrates with any subsystem that needs generated capability enums plus consistent accessors without duplicating boilerplate.

## Risks And Test Signals

Risks are macro-related: namespace collisions, passing a non-enum value, forgetting to initialize the bitmap, using capability lists with too many entries for expected storage, or assuming these helpers are atomic. The code does not lock, so concurrent set/get requires caller-side synchronization if the capability object is mutable.

Test signals can be simple compile-time users plus unit-style checks: generated enum count, init zeroes all attributes, set/get each legal attribute, invalid cap id returns `-EINVAL`, invalid attribute value returns `-EINVAL`, null input handling, and predicate correctness for RO/WO/RW/invalid values.
