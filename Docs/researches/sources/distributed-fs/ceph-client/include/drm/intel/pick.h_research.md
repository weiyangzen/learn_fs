# sources/distributed-fs/ceph-client/include/drm/intel/pick.h

Purpose: supplies compact compile-time macros for selecting indexed MMIO offsets or constants from evenly spaced ranges or explicit value lists.

Important APIs/types/functions: `_PICK_EVEN(index, a, b)` computes an arithmetic progression. `_PICK_EVEN_2RANGES(index, c_index, a, b, c, d)` selects from one even range before `c_index` and a second after it, requiring `c_index` to be constant. `_PICK(index, ...)` indexes an anonymous constant `u32` array for irregular values.

Control flow: macro expansion performs constant or runtime arithmetic/indexing inside register definitions. There are no functions or side effects except build-time validation in the two-range form.

State and persistence: none.

Dependencies and integration: uses `BUILD_BUG_ON_ZERO` and `__is_constexpr`; integrated by Intel register headers for pipe/port/transcoder indexed MMIO address generation.

Risks and test signals: risks include nonconstant cutoff in two-range use, out-of-range array indexing in `_PICK`, and unintended multiple evaluation of index expressions. Test by compiling register headers for all platforms and checking generated MMIO addresses against hardware specs.
