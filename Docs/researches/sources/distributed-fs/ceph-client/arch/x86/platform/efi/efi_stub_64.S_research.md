<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi_stub_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi_stub_64.S

## Purpose
`efi_stub_64.S` adapts Linux x86_64 function calling to the EFI x86_64 ABI for native firmware runtime calls.

## Important APIs, types, and functions
The sole symbol is `__efi_call`. It is an assembly ABI shim used by the `arch_efi_call_virt()` machinery.

## Control flow
The stub saves `%rbp`, aligns the stack to 16 bytes, reserves EFI shadow/home space, moves Linux register arguments into EFI-required registers, stores stack arguments, and performs an indirect no-speculation call through the function pointer in `%rdi`. It then restores the frame and returns.

## State and persistence behavior
No persistent state is kept. The only mutations are transient stack/register ABI conversions during the firmware call.

## Dependencies and integration points
It depends on x86_64 Linux and Microsoft/EFI ABI differences, `CALL_NOSPEC`, no-CFI annotation for firmware code, and C wrappers that already switched into `efi_mm` and prepared FPU/speculation state.

## Risks and edge cases
Stack alignment and home-space layout must exactly match EFI firmware expectations. Indirect calls into firmware lack kernel CFI metadata, hence explicit annotations are needed to avoid objtool/CFI issues.

## Test signals
Native 64-bit EFI runtime service calls such as GetVariable/SetVariable/ResetSystem under CFI, retpoline/no-spec, and page-table switching configurations validate this shim.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/efi/efi_stub_64.S -->
