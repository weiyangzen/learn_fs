# sources/distributed-fs/ceph-client/include/linux/mman.h

## Purpose
`mman.h` bridges user `mmap()`/`mprotect()` flags to kernel VMA flags and declares VM overcommit accounting helpers. It also provides architecture override points for protection validation, flag validation, and architecture-specific VMA flag calculation.

## Important APIs, Types, And Functions
Important symbols are `LEGACY_MAP_MASK`, `sysctl_overcommit_memory`, `vm_committed_as`, `vm_committed_as_batch`, `mm_compute_batch()`, `vm_memory_committed()`, `vm_acct_memory()`, `vm_unacct_memory()`, `arch_calc_vm_prot_bits()`, `arch_calc_vm_flag_bits()`, `arch_validate_prot()`, `arch_validate_flags()`, `_calc_vm_trans()`, `calc_vm_prot_bits()`, `calc_vm_flag_bits()`, `vm_commit_limit()`, and `arch_memory_deny_write_exec_supported()`.

## Control Flow And State
The control path is inline translation and accounting. `vm_acct_memory()` and `vm_unacct_memory()` update the global committed-address-space percpu counter using the SMP batch size. `calc_vm_prot_bits()` maps `PROT_READ`, `PROT_WRITE`, `PROT_EXEC`, and architecture pkey bits into `VM_*` flags. `calc_vm_flag_bits()` maps supported `MAP_*` bits such as grow-down, locked, sync, and stack/nohugepage into internal flags. Legacy or undefined architecture map flags default to zero so common code can mask them uniformly.

## Dependencies And Integration Points
The header depends on `fs.h`, `mm.h`, percpu counters, atomics, and UAPI `linux/mman.h`. It integrates with `mmap()`, `mprotect()`, overcommit policy, transparent hugepage stack handling, architecture protection keys, MDWE support, and file operations that either provide or omit `->mmap_validate()`.

## Risks And Test Signals
Risks include accepting unsupported mapping bits, dropping architecture protection semantics, incorrect overcommit accounting batch sizes, and treating ignored historical flags as meaningful. Test signals include mmap/mprotect flag validation tests, overcommit limit and accounting tests, architecture pkey and W+X policy tests, THP stack mapping tests, and builds for architectures with custom `MAP_*` flags.
