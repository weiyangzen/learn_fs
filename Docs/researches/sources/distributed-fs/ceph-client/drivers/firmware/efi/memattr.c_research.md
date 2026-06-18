
# sources/distributed-fs/ceph-client/drivers/firmware/efi/memattr.c

Purpose: validates, reserves, and applies the EFI Memory Attributes Table so runtime service mappings can be tightened with firmware-provided permissions.

Important APIs/types/functions: exports `efi_memattr_init()` and `efi_memattr_apply_permissions()`. Internal `entry_is_valid()` verifies table descriptors against the EFI memory map and computes virtual addresses.

Control flow: early init maps the table header, rejects unexpected versions/descriptors/counts, reserves the full table with memblock, and sets `EFI_MEM_ATTR`. Permission application memremaps the full table, detects BTI/forward-control-flow-guard support, iterates entries, validates runtime code/data coverage against current EFI memmap virtual addresses, logs invalid entries, and calls the architecture-provided permission setter until failure.

State and persistence behavior: global `efi_mem_attr_table` holds the physical address and `tbl_size` stores validated size. Reserved table memory persists for runtime permission setup.

Dependencies and integration points: depends on early memremap/memblock, EFI memory map, `efi_memattr_perm_setter`, architecture page-table permission code, and EFI flags.

Risks and test signals: corrupted table sizes can exhaust memory without caps, descriptors may not align to kernel page size, and missing virtual addresses mean no stub virtual map was installed. Test signals include valid/invalid table versions, descriptor size mismatches, more than 64k entries, runtime code/data permission changes, BTI flag propagation, and kexec-loaded maps.
