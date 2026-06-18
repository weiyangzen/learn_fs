# sources/distributed-fs/ceph-client/arch/powerpc/mm/init_64.c

Purpose: handles 64-bit PowerPC early MMU feature selection, vmemmap population/freeing, memory-block-size probing, and radix/hash devicetree initialization.

Important APIs and control flow: sparse vmemmap paths allocate backing pages, track mappings in `vmemmap_list`, create/remove mappings, and delegate to radix-specific implementations when radix is active. `mmu_early_init_devtree()` parses `disable_radix`, DT PID/LPID bit widths, hypervisor vector-5 MMU/GTSE support, memory block size, invokes radix or hash early setup, initializes HugeTLB defaults, and panics if no supported MMU type remains.

State and dependencies: persistent state includes `vmemmap_list`, backing free-list counters, `mmu_lpid_bits`, `mmu_pid_bits`, `disable_radix`, and `memory_block_size`. Dependencies include flat DT scanning, memblock/altmap allocation, sparsemem subsection validity, pseries/powernv memory layout, radix/hash setup functions, and KVM LPID export. Risks include vmemmap backing leaks on mapping failure, wrong altmap boundary checks, radix forced/disabled mismatch under a hypervisor, and memory block sizes incompatible with hotplug. Test signals include memory hotplug add/remove, devdax altmap, pseries guests with vector-5 variants, radix-disabled boots, and sparsemem subsection tests.
