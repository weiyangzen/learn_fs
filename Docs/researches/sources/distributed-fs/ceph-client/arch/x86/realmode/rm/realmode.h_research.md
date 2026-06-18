<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/realmode.h -->
# sources/distributed-fs/ceph-client/arch/x86/realmode/rm/realmode.h

## Purpose
`realmode.h` provides small shared definitions for real-mode assembly, primarily the handcrafted 16-bit far jump macro and end-of-blob signature.

## Important APIs, types, and functions
The important API is `LJMPW_RM(to)`, used where gas cannot encode a relocatable segment operand, and `REALMODE_END_SIGNATURE` for integrity checking.

## Control flow
Assembly code uses `LJMPW_RM()` when switching CS to the relocated real-mode segment. Wakeup code compares the signature after entering the blob.

## State and persistence behavior
No runtime state is stored; the constants influence encoded instruction bytes and signature data.

## Dependencies and integration points
It depends on `real_mode_seg` being supplied by the realmode linker script and included only in the blob assembly context for the macro.

## Risks and edge cases
Incorrect far-jump encoding breaks all real-mode transitions. Signature drift must match `header.S` and `wakeup_asm.S` checks.

## Test signals
Signals include objdump inspection of far jumps, real-mode relocation validation, and S3/reboot/SMP startup smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/rm/realmode.h -->
