
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/systable.c

Purpose: provides the global EFI system table pointer definition for stub builds that need a shared `efi_system_table` object.

Important APIs/types/functions: defines `const efi_system_table_t *efi_system_table`.

Control flow: no executable flow. Architecture entry code writes this pointer before using `efi_bs_call()` or other table-based helpers.

State and persistence behavior: the pointer is process-global boot state. It remains valid until ExitBootServices for boot services and into runtime if the kernel retains runtime mappings.

Dependencies and integration points: depends on EFI type definitions and is referenced by nearly every libstub helper.

Risks and test signals: duplicate definitions are architecture-sensitive; x86 provides its own definition. Test signals are link success for each EFI stub target and early entry setting the pointer before any helper call.
