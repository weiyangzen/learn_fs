# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/vector.h

Purpose: Declares a small dynamic-array abstraction used inside DAL/DC code where kernel allocation needs to be tied to `dc_context`. It stores fixed-size elements in a byte container.

Important APIs and types: `struct vector` contains `container`, `struct_size`, `count`, `capacity`, and `ctx`. Lifecycle functions include `dal_vector_construct`, `dal_vector_create`, `dal_vector_presized_create`, `dal_vector_destruct`, and `dal_vector_destroy`. Operations include count/capacity, insert, append, index get/set, clone, remove, reserve, and clear. Macros generate typed wrappers for insert/append/at/set.

Control flow: Callers construct/create with capacity and element size, append or insert elements, access elements by index, optionally clone/reserve/clear, and destruct/destroy. Insert and append can reallocate the backing container. Remove shifts trailing elements left.

State and persistence: The vector owns heap-allocated `container` memory and tracks element count/capacity. It is not persistent outside process lifetime and has no synchronization; callers must serialize concurrent access.

Dependencies and integration points: Depends on `dc_context` allocation conventions and common integer/bool types. Used by DAL components needing generic collections without C++ templates.

Risks: The API comments say some index bounds are not checked because callers calculate private indices; misuse can cause memory corruption. Typed wrapper macros are only shallow casts and do not enforce element size at runtime. Reallocation invalidates pointers returned by `dal_vector_at_index`.

Test signals: Allocation failure paths, append/insert growth, remove shifting, clone independence, presized initialization with/without initial values, reserve shrink/grow behavior, index bounds assertions in implementation, and typed wrapper compile coverage.
