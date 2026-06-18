# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/mmap.c

Purpose: Provides formatters for memory-management syscall arguments: mmap protections, mmap flags, mremap flags, and madvise behavior.

Important APIs/types/functions: Static formatters `syscall_arg__scnprintf_mmap_prot`, `syscall_arg__scnprintf_mmap_flags`, `syscall_arg__scnprintf_mremap_flags`, and `syscall_arg__scnprintf_madvise_behavior` are exposed via `SCA_MMAP_PROT`, `SCA_MMAP_FLAGS`, `SCA_MREMAP_FLAGS`, and `SCA_MADV_BHV` macros. It consumes generated arrays for `PROT_`, `MAP_`, `MREMAP_`, and `MADV_` names.

Control flow: Protection value zero is printed as `PROT_NONE`; otherwise flags go through `strarray__scnprintf_flags`. `MAP_ANONYMOUS` masks the ignored fd and offset syscall arguments. `MREMAP_FIXED` controls whether the new-address argument is displayed. `madvise` indexes directly into its generated advice table and falls back to a numeric string.

State and persistence: No persistent state; display state is changed by setting bits in `arg->mask`.

Dependencies and integration points: Integrated through perf trace syscall argument macros and the shared `strarray` flag formatter from this beauty subsystem.

Risks: The generated flag arrays require power-of-two indexing. Non-bitmask advice values use direct array indexes, so sparse values need NULL-safe fallback.

Test signals: Trace `mmap`, `mremap`, and `madvise` combinations, verifying argument masking for anonymous mappings and non-fixed remaps.
