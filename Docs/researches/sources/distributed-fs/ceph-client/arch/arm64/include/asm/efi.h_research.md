## sources/distributed-fs/ceph-client/arch/arm64/include/asm/efi.h

Purpose: arm64 EFI boot and runtime-services integration.

Important APIs/types/functions: declares `efi_init`, `efi_runtime_fixup_exception`, `efi_create_mapping`, `efi_set_mapping_permissions`, `arch_efi_call_virt`, `efi_rt_stack_top`, `__efi_rt_asm_wrapper`, runtime setup/teardown, `current_in_efi`, EFI DAIF save/restore macros, `efi_get_max_initrd_addr`, `efi_get_kimg_min_align`, `efi_set_pgd`, `efi_virtmap_load/unload`, capsule cache flushing, corrupted-x18 handling, and `efi_icache_sync`.

Control flow: boot code initializes EFI memory maps and runtime mappings. Runtime calls switch stacks/page tables, call firmware through an assembly wrapper, and restore kernel state afterward.

State and persistence: runtime page tables, `efi_rt_stack_top`, firmware virtual mappings, and EFI runtime-services enablement persist after boot.

Dependencies and integration: depends on boot constraints, cpufeature, FPSIMD/NEON, IO, memory management, TLB, ptrace, and TTBR0 PAN handling.

Risks: EFI calls run untrusted firmware in fragile CPU state; wrong DAIF, page-table, x18, cache, or FP handling can corrupt kernel execution. Test signals are EFI boot, runtime variable access, capsule update, kexec, KASLR/no-KASLR alignment, and fault injection during runtime calls.
