# sources/distributed-fs/ceph-client/arch/powerpc/kexec/vmcore_info.c

## Purpose
Adds PowerPC-specific metadata to the crash vmcore information block so dump tools can interpret memory layout, MMU mode, KASLR offset, CPU features, and vmemmap backing structures after a crash.

## Important APIs, Types, And Functions
Defines `arch_crash_save_vmcoreinfo`. It emits entries with `VMCOREINFO_SYMBOL`, `VMCOREINFO_LENGTH`, `VMCOREINFO_STRUCT_SIZE`, `VMCOREINFO_OFFSET`, and `vmcoreinfo_append_str`. Important exported facts include `node_data`, `contig_page_data`, `vmemmap_list`, `mmu_vmemmap_psize`, `mmu_psize_defs`, `cur_cpu_spec`, `cpu_spec.cpu_features`, `cpu_spec.mmu_features`, `RADIX_MMU`, and `KERNELOFFSET`.

## Control Flow
At crash metadata construction time the function conditionally records NUMA or contiguous page-data symbols, optional PPC64 sparse-vmemmap details, CPU-spec offsets, the early radix mode state, and the KASLR offset. There is no loop or dynamic allocation.

## State And Persistence
The function appends text metadata to the vmcore info note that persists into the crash dump. It reads current architecture globals and does not mutate runtime state beyond the vmcoreinfo buffer.

## Dependencies And Integration Points
Depends on `linux/vmcore_info.h`, PPC page allocation/MMU definitions, NUMA configuration, sparse vmemmap configuration, `early_radix_enabled()`, and `kaslr_offset()`. It integrates with makedumpfile/crash tooling and the generic crash core.

## Risks And Edge Cases
Missing or wrong offsets break postmortem tools rather than normal runtime. Conditional emission must match the crashed kernel configuration; NUMA and sparse-vmemmap mismatches can cause dump tools to walk invalid structures. Radix/hash mode and KASLR offset are essential for correct address translation in modern PPC64 dumps.

## Test Signals
Validate by booting NUMA and non-NUMA kernels, hash and radix PPC64 kernels, collecting vmcores, and confirming `makedumpfile` or `crash` resolves page metadata, CPU feature flags, vmemmap backing, and kernel virtual addresses.
