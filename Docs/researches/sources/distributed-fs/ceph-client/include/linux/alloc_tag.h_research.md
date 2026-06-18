<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/alloc_tag.h -->
# sources/distributed-fs/ceph-client/include/linux/alloc_tag.h

## Purpose
`alloc_tag.h` defines allocation callsite tagging for memory allocation profiling. It creates codetag-backed records in a special ELF section and updates per-CPU byte/call counters around allocations.

## Important APIs, types, and functions
Types include `struct alloc_tag_counters`, `struct alloc_tag`, `alloc_tag_kernel_section`, `alloc_tag_module_section`, and `struct codetag_bytes`. With profiling enabled, `DEFINE_ALLOC_TAG()` emits a static tag in `alloc_tags`; `mem_alloc_profiling_enabled()` checks the static key; `alloc_tag_read()` sums per-CPU counters; `alloc_tag_ref_set()`, `alloc_tag_add()`, and `alloc_tag_sub()` maintain references and counts; inaccurate flags can be set/tested; `alloc_hooks()` and `alloc_hooks_tag()` wrap allocation expressions. Debug builds add codetag-empty checks and early PFN tagging.

## Control flow
Allocation wrappers define or use a tag, save it into current allocation context, execute the allocation expression, restore the old tag, and record bytes/calls on success. Free paths subtract bytes/calls through the stored codetag reference and clear it.

## State and persistence behavior
Each callsite tag persists in an ELF section. Counters are per-CPU and accumulate runtime allocation statistics. Object references remember which tag owns their allocation accounting until freed.

## Dependencies and integration points
The header depends on codetag infrastructure, per-CPU variables, current task allocation tag, static keys, preemption/IRQ assumptions, and module section handling. It integrates slab/page allocation profiling and top-user reporting.

## Risks and test signals
Risks include counter imbalance on split/free paths, missing ref clearing, weak per-CPU module behavior, preemption-sensitive counter updates, and disabled stubs changing coverage. Test signals include allocation profiling selftests, debug warnings for stale tags, module load/unload sections, top-user reports, and builds with profiling on/off/debug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/alloc_tag.h -->
