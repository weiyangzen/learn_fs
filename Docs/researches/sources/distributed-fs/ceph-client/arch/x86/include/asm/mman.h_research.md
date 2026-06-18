# sources/distributed-fs/ceph-client/arch/x86/include/asm/mman.h

## Purpose
Adds x86 memory-management protection-key VM flag translation before including the UAPI mmap definitions.

## Important APIs, Types, And Functions
When `CONFIG_X86_INTEL_MEMORY_PROTECTION_KEYS` is enabled, `arch_calc_vm_prot_bits(prot, key)` maps low four bits of a protection key to `VM_PKEY_BIT0` through `VM_PKEY_BIT3`. It then includes `uapi/asm/mman.h`.

## Control Flow
Compile-time macro expansion attaches pkey bits to VMA protection flags during mmap/mprotect handling.

## State And Persistence
No state in this header. Pkey state lives in mm context and VMA flags.

## Dependencies And Integration Points
Integrates with generic mm pkey handling, x86 PKU support, and user-visible mmap/mprotect constants.

## Risks And Edge Cases
Incorrect bit mapping would assign the wrong protection key to VMAs. Disabled configs must leave generic behavior unchanged.

## Test Signals
Protection key selftests, mmap/mprotect tests, and builds with PKU enabled and disabled are useful.
