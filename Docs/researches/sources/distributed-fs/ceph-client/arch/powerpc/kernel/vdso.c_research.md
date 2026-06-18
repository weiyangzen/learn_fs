# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso.c

## Purpose
Installs and initializes the PowerPC vDSO and vvar mappings for each userspace process, prepares vDSO runtime data, applies CPU/MMU/firmware fixups, and sets up getcpu support.

## Important APIs, Types, And Functions
Key functions are `arch_setup_additional_pages`, `__arch_setup_additional_pages`, `vdso_mremap`, `vdso_close`, `vdso_fixup_features`, `vdso_setup_syscall_map`, `vdso_getcpu_init`, `vdso_setup_pages`, and `vdso_init`. It uses `vdso32_spec` and `vdso64_spec` `vm_special_mapping` objects, external `vdso32_start/end` and `vdso64_start/end`, and `vdso_k_arch_data`.

## Control Flow
At exec time, `arch_setup_additional_pages` locks the mm, clears the previous vDSO pointer, chooses 32-bit or 64-bit vDSO based on the task, reserves enough unmapped space for vvar plus aligned vDSO, installs vvar first, installs executable vDSO text, and records `mm->context.vdso`. At boot, `vdso_init` fills cache block sizes, builds syscall bitmaps, patches feature-dependent alternatives in embedded vDSOs, converts embedded vDSO pages to page lists, and publishes with an SMP write barrier.

## State And Persistence
Per-mm state is `mm->context.vdso`, updated on install, mremap, and close. Boot state includes vDSO page lists in `vdso*_spec.pages`, syscall maps, cache metadata, and on 64-bit the per-CPU SPRG value used by vDSO getcpu.

## Dependencies And Integration Points
Integrates with `binfmt_elf`, special mappings, generic vDSO data pages, PowerPC feature fixup machinery, syscall tables, CPU topology, PACA, and embedded vDSO images from `vdso32_wrapper.S` and `vdso64_wrapper.S`.

## Risks And Edge Cases
Mapping order and alignment matter for ABI stability and for `AT_SYSINFO_EHDR`. COW of vvar by ptrace can break live time updates for a process. mremap only accepts exact vDSO text size. Feature fixup symbol ranges must match linker script symbols, and getcpu only stores 16-bit CPU/node values.

## Test Signals
Useful signals include `gettimeofday`, `clock_gettime`, `clock_getres`, `time`, `getcpu`, `getrandom`, and signal trampoline tests in 32-bit and 64-bit tasks, `mremap`/`munmap` behavior, `/proc/self/maps` vvar/vdso placement, feature-fixup boot logs, and cross-builds with and without `CONFIG_VDSO32`.
