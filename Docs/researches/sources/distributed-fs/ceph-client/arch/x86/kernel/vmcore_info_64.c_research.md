# sources/distributed-fs/ceph-client/arch/x86/kernel/vmcore_info_64.c

Purpose: exports 64-bit x86 crash dump metadata so vmcore analysis tools can translate addresses, page tables, NUMA data, KASLR offsets, and memory encryption masks.

Important APIs/functions: implements `arch_crash_save_vmcoreinfo()`.

Control flow: the function records `phys_base`, `init_top_pgt`, five-level paging enablement, optional NUMA `node_data` symbol and length, `KERNELOFFSET`, `KERNEL_IMAGE_SIZE`, and SME mask value. It snapshots `sme_me_mask` locally before emitting it.

State and persistence: no private state is retained. The function appends architecture values into the vmcoreinfo note for later crash dump consumers.

Dependencies and integration: depends on vmcoreinfo infrastructure, x86 setup symbols, page-table helpers such as `pgtable_l5_enabled()`, KASLR offset reporting, NUMA globals, and SME memory encryption state.

Risks: incorrect metadata causes post-mortem tools to misinterpret virtual-to-physical mappings, encrypted memory bits, KASLR relocation, or node topology. Five-level paging and SME values are especially important for modern 64-bit dumps.

Test signals: generated vmcoreinfo from kdump should include these numbers and symbols. Crash utility validation across 4-level/5-level paging, KASLR on/off, SME on/off, and NUMA/non-NUMA configurations is the main coverage signal.
