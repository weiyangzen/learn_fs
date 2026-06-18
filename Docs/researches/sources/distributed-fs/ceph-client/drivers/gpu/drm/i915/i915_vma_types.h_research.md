# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_vma_types.h

Purpose: defines `struct i915_vma` and documents GGTT view semantics for normal, partial, rotated, and remapped object mappings.

Important APIs/types: `assert_i915_gem_gtt_types()` enforces view union layout assumptions. `struct i915_vma` contains address-space node state, object/VM pointers, backend ops, SG pages, iomap, fencing, page sizes, guard and display alignment, open/pin/bind flags, active tracking, page binding counts, view metadata, object/VM/eviction/closed list links, and current async resource. It also defines VMA flag bits and `I915_VMA_PAGES_ACTIVE`.

Control flow: this header is consumed by the implementation and callers that need direct state. The documentation describes adding new GGTT views: extend view type/metadata and implement SG-table construction in VMA page acquisition.

State and persistence: the VMA is an in-memory object whose lifetime is bounded by its GEM object. It persists while present in object rb-tree/list or VM lists, then is destroyed after unbind/close. It is not serialized across driver reloads.

Dependencies and integration: depends on GEM object types, GTT view types, rb-trees, `drm_mm`, and active/resource subsystems. Display, execbuf, eviction, and mmap code all interpret the flag bits defined here.

Risks: flags multiplex pin counts and state bits into one atomic, so masks must remain non-overlapping. Page-count high bits encode active binds; incorrect arithmetic can leak or prematurely release pages. View layout assertions are essential because `i915_vma_compare()` uses compact `memcmp` over union branches.

Test signals: build-time `BUILD_BUG_ON` assertions, i915 VMA selftests, and broad compile coverage through most GEM and GTT paths.
