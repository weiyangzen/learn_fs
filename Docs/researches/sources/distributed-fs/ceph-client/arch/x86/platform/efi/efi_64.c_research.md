<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi_64.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi_64.c

## Purpose
`efi_64.c` implements 64-bit x86 EFI page-table management, runtime virtual mappings, permission updates, native runtime-call context switching, and mixed-mode thunk wrappers for calling 32-bit firmware from a 64-bit kernel.

## Important APIs, types, and functions
Core mapping APIs are `efi_alloc_page_tables()`, `efi_sync_low_kernel_mappings()`, `efi_setup_page_tables()`, `efi_map_region()`, `efi_map_region_fixed()`, `parse_efi_setup()`, `efi_runtime_update_mappings()`, `efi_set_virtual_address_map()`, and `efi_dump_pagetable()`. Runtime-call setup uses `arch_efi_call_virt_setup()`, `arch_efi_call_virt_teardown()`, `efi_enter_mm()`, LASS toggles, and `efi_runtime_lock`. Mixed-mode services include `efi_thunk_*` variable/reset/query wrappers and `efi_thunk_runtime_setup()`.

## Control flow
EFI setup allocates a private `efi_mm` page-table root and shares only non-EFI parts of the kernel address space. Runtime descriptors are first 1:1 mapped, then assigned top-down virtual addresses below `EFI_VA_START` unless mixed mode forces physical virtual addresses. `efi_setup_page_tables()` identity maps the new memory map, page zero, SEV-ES GHCBs, and, for mixed mode, low 32-bit stack/text/rodata/trampoline pages. Runtime calls synchronize low mappings, save FPU state, apply speculation restrictions, borrow `efi_mm`, disable LASS if needed, call firmware, and restore state. Mixed-mode wrappers convert kernel virtual pointers to 32-bit physical addresses before `efi64_thunk()`.

## State and persistence behavior
State includes top-down `efi_va`, previous borrowed mm pointer, saved CR4.LASS bit, `efi_runtime_lock`, `efi_disable_ibt_for_runtime`, and `efi_mixed_mode_stack_pa` from assembly. EFI descriptors persist 1:1 and virtual mappings. Runtime permission updates honor EFI memory attributes for RO/NX and encrypted memory.

## Dependencies and integration points
It integrates with x86 page-table allocation, temporary-mm switching, SEV-ES, confidential-computing encryption bits, LASS, IBT policy, EFI memory attributes table, mixed-mode assembly thunks, FPU/speculation wrappers, UCS-2 variable names, and generic EFI runtime dispatch.

## Risks and edge cases
Firmware may still use stale physical pointers, requiring 1:1 mappings. Mixed mode requires all callable code/data/stack addresses to fit in 32-bit physical space. Pointer conversion rejects buffers crossing page boundaries. Runtime calls are serialized for mixed-mode variable/reset paths. Permission tightening must wait until after `SetVirtualAddressMap()`.

## Test signals
Native 64-bit EFI runtime variables, mixed 32-bit firmware boots, kexec, SEV-ES guests, LASS-capable CPUs, EFI memory attribute tables, IBT-enabled kernels, capsule/query-variable behavior, and page-table dump inspection are key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi_64.c -->
