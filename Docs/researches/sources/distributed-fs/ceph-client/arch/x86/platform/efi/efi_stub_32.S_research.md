<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi_stub_32.S -->
# sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi_stub_32.S

## Purpose
`efi_stub_32.S` provides the 32-bit assembly stub used to call EFI `SetVirtualAddressMap()` in physical addressing mode with interrupts disabled.

## Important APIs, types, and functions
The sole symbol is `efi_call_svam`. It receives the runtime-services-table pointer and arguments from the C wrapper in `efi_32.c`, switches to a flat physical alias of itself, disables paging, calls `EFI_svam`, captures the remapped runtime-services pointer, re-enables paging, and returns.

## Control flow
The stub saves frame state and `%ebx`, pushes the call arguments, jumps to the physical alias of label `1`, clears CR0.PG, converts `%esp` from kernel virtual to physical by subtracting `__PAGE_OFFSET`, calls firmware, stores the new `efi.runtime` pointer through the supplied physical output argument, sets CR0.PG again, restores stack/frame state, and returns.

## State and persistence behavior
It directly mutates CR0 paging state for the duration of the call and writes the C-visible runtime-services pointer. It does not allocate memory or retain local state.

## Dependencies and integration points
It depends on the IA32 calling convention, `EFI_svam` offset from asm offsets, `__PAGE_OFFSET`, the C wrapper having installed suitable CR3/GDT state, and firmware accepting physical-mode execution.

## Risks and edge cases
Any missing identity/flat mapping, wrong stack conversion, or invalid GDT/segment state can crash during early boot. Interrupts must remain disabled because handlers are not valid while paging and address interpretation are changed.

## Test signals
32-bit EFI boot reaching successful `SetVirtualAddressMap()`, runtime variable access after virtual-mode entry, and fault-free transition with EFI debug page-table dumps provide validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi_stub_32.S -->
