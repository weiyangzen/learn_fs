<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi_thunk_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi_thunk_64.S

## Purpose
`efi_thunk_64.S` implements the long-mode-to-compatibility-mode thunk used by 64-bit kernels to call 32-bit EFI runtime services after ExitBootServices in mixed-mode EFI.

## Important APIs, types, and functions
The main symbol is `__efi64_thunk`; return support is in read-only data symbol `__efi64_thunk_ret_tramp`; `efi_mixed_mode_stack_pa` is a BSS variable holding the physical low-memory stack top allocated by `efi_setup_page_tables()`.

## Control flow
The thunk saves `%rbp/%rbx`, switches to the 1:1 mapped 32-bit stack, copies stack-passed arguments into 32-bit layout, computes physical addresses for return labels by subtracting the kernel physical mapping delta, builds a 32-bit return frame and argument area, then uses `lretq` to enter `__KERNEL32_CS` at the EFI runtime service address. The 32-bit trampoline returns through a far return to 64-bit code, restores the original stack and saved registers, and returns to C.

## State and persistence behavior
Persistent state is only `efi_mixed_mode_stack_pa`, set by C code. Runtime mutations are limited to stack switching and far control transfers.

## Dependencies and integration points
It depends on mixed-mode C wrappers in `efi_64.c`, identity mappings for kernel text/rodata/trampoline and low stack, `phys_base`, segment descriptors `__KERNEL32_CS`/`__KERNEL_CS`, and objtool annotations for nonstandard stack frames.

## Risks and edge cases
All firmware-call targets, arguments, stack, and trampoline addresses must be representable to 32-bit firmware. Incorrect identity mappings or segment descriptors would fault in compatibility mode. The dummy return instruction exists for objtool, not runtime behavior.

## Test signals
64-bit kernel booted via 32-bit EFI, variable service calls, ResetSystem, query-variable-info, and mixed-mode runtime calls under interrupt-capable paths are the key checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi_thunk_64.S -->
