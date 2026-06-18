# sources/distributed-fs/ceph-client/arch/riscv/kernel/efi.c

Purpose: Creates and protects RISC-V EFI runtime service mappings with architecture-specific page attributes.

Important APIs/types/functions: Implements `efimem_to_pgprot_map()`, `efi_create_mapping()`, and `efi_set_mapping_permissions()`.

Control flow: EFI memory descriptors are translated into RISC-V page protections, runtime mappings are installed page by page with global-bit clearing, and later permission updates walk PTEs to apply RO/XN policy from EFI attributes.

State and persistence: Mutates EFI runtime page tables for the life of the kernel. No file-local persistent state.

Dependencies and integration points: Depends on generic EFI runtime services, RISC-V page-table helpers, memory descriptor attributes, and early boot EFI setup.

Risks and test signals: Incorrect executable/read-only handling can break runtime services or weaken W+X protections. Test EFI variable/runtime calls, mixed RO/XP descriptors, MMIO descriptors, page table attribute inspection, and boot under UEFI firmware.
