<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/sys_parisc.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/sys_parisc.c

### Purpose
`sys_parisc.c` supplies PA-RISC-specific syscall wrappers for mmap placement, 64-bit argument splitting, personality compatibility, legacy flag translation, and madvise compatibility.

### Important APIs, Types, And Functions
Core functions include `calc_max_stack_size()`, `mmap_upper_limit()`, `arch_get_unmapped_area()`, `arch_get_unmapped_area_topdown()`, `sys_mmap2()`, `sys_mmap()`, `parisc_truncate64()`, `parisc_ftruncate64()`, `parisc_pread64()`, `parisc_pwrite64()`, `parisc_readahead()`, `parisc_fadvise64_64()`, `parisc_sync_file_range()`, `parisc_fallocate()`, `parisc_personality()`, `FIX_O_NONBLOCK()` wrappers, and `parisc_madvise()`.

### Control Flow
Mmap allocation handles PA-RISC shared mapping cache coloring, fixed-address validation, top-down first search with bottom-up fallback, stack limit calculation, and randomization room. Split-64 wrappers reconstruct `loff_t`/`u64` arguments from high/low words. Legacy wrappers mask the old `O_NONBLOCK` bit after one warning per thread. `parisc_madvise()` remaps old PA-RISC advice constants to generic values.

### State, Persistence, And Dependencies
State is per-mm VMA layout and one thread warning flag for deprecated nonblock values. Dependencies include generic mmap search, file mapping identity, rlimits, personality, compat mode, syscall helpers, and legacy ABI constants.

### Integration Points
Called from the PA-RISC syscall table and ELF mmap layout selection.

### Risks
Cache coloring affects ABI-visible mmap addresses. Legacy compatibility wrappers must remain in sync with userland expectations. Top-down fallback changes allocation direction under pressure.

### Test Signals
Mmap fixed/shared/color-aligned mappings, large stack rlimits, compat stack defaults, 64-bit file-offset syscalls, old `O_NONBLOCK` binaries, and legacy madvise constants should be exercised.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/sys_parisc.c -->
