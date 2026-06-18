<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/quirks.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/efi/quirks.c

## Purpose
Implements x86-specific EFI firmware workarounds for variable-store safety, boot-services memory lifetime, kexec configuration table reuse, reduced-hardware reset/poweroff selection, Quark capsule headers, and runtime-service fault containment.

## Important APIs, Types, And Functions
`efi_query_variable_store()` and `efivar_reserved_space()` protect nonvolatile EFI variable storage; `efi_arch_mem_reserve()`, `efi_reserve_boot_services()`, `efi_unmap_boot_services()`, and `efi_free_boot_services()` manage EFI boot-services memory; `efi_reuse_config()` repairs kexec configuration tables; `efi_reboot_required()` and `efi_poweroff_required()` select EFI reset/poweroff fallbacks; `efi_capsule_setup_info()` handles Quark security headers when enabled; `efi_crash_gracefully_on_page_fault()` disables broken runtime services after firmware page faults.

## Control Flow
Early parameters can disable storage paranoia. Variable writes first query firmware free space, optionally force garbage collection through a dummy variable, and return EFI errors before callers write. EFI boot-services descriptors are reserved during init, runtime-tagged if not safely owned, unmapped after virtual mapping setup, queued in `ranges_to_free`, and finally released by an `arch_initcall`. Runtime faults in the EFI workqueue either redirect reset to BIOS or abort the waiting caller and park the worker forever.

## State And Persistence
The file touches persistent EFI NVRAM variables through `set_variable*`. It rewrites the in-kernel EFI memory map and E820 reservations during boot and stores freeable ranges until `efi_free_boot_services()`. Quark capsule setup mutates `capsule_info` metadata, and runtime-service fault handling clears `EFI_RUNTIME_SERVICES`.

## Dependencies And Integration Points
Depends on EFI core services, x86 E820/memblock, ACPI reduced-hardware state, DMI, UV headers, real-mode trampoline allocation, kexec setup data, capsule update code, and the EFI runtime workqueue. Drivers needing boot-services data integrate through `efi_mem_reserve()`, which this file supports by splitting descriptors.

## Risks And Edge Cases
Incorrect descriptor splitting or ownership tagging can free firmware, kernel, crash-kernel, or driver-owned memory. Variable-store arithmetic is sensitive to firmware reporting bugs and underflow-style cases around `remaining_size - size`. Runtime page-fault recovery is intentionally drastic and must avoid running in interrupt/NMI context. Quark capsule pointer adjustments assume the first buffer contains enough signed-header bytes.

## Test Signals
Boot logs for EFI boot-services freeing, NVRAM write failures, kexec boot across EFI, capsule update on Quark, and fault-injection around EFI runtime calls are the main signals. Memory-map regressions show up as early boot crashes, missing SMBIOS after kexec, or firmware reset/poweroff failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/quirks.c -->
