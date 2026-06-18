# sources/distributed-fs/ceph-client/arch/powerpc/kexec/core_32.c

## Purpose
Implements the default 32-bit PowerPC machine kexec handoff by copying relocation code to the control page and jumping to it with interrupts masked.

## Important APIs, Types, And Functions
Defines `default_machine_kexec(struct kimage *image)` and `machine_kexec_prepare(struct kimage *image)`. Uses `relocate_new_kernel`, `relocate_new_kernel_size`, and function pointer type `relocate_new_kernel_t`.

## Control Flow
The default handoff disables local IRQs, masks interrupt sources, locates the image indirection list and control code page, copies relocation code into the control page, flushes I-cache over that page, prints "Bye!", and jumps either directly to the original relocation symbol on most systems or through the copied control page on 85xx/44x. `machine_kexec_prepare` accepts all images.

## State And Persistence
Mutates the control code page and hardware interrupt state. It does not persist data.

## Dependencies And Integration Points
Depends on generic `struct kimage`, interrupt masking, cache flushing, physical/virtual address helpers, and `relocate_32.S`.

## Risks And Edge Cases
This path runs after reboot commitment. The relocation code size must fit in the control page, I-cache flushing must cover the copied code, and effective versus physical addresses must be correct for the target platform.

## Test Signals
32-bit kexec boot tests, crash-dump handoff where applicable, cache coherency checks around copied relocation code, and board coverage for 85xx/44x versus other PPC32 platforms are needed.
