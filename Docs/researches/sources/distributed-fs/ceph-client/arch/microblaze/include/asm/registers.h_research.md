# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/registers.h

## Purpose

names MicroBlaze special-purpose registers and MSR bit definitions

## Important APIs, Types, and Functions

Source read size: 45 lines, 1508 bytes. Key macros/defines: `_ASM_MICROBLAZE_REGISTERS_H`, `MSR_BE`,
`MSR_IE`, `MSR_C`, `MSR_BIP`, `MSR_FSL`, `MSR_ICE`, `MSR_DZ`, `MSR_DCE`, `MSR_EE`, `MSR_EIP`,
`MSR_CC`, `FSR_IO`, `FSR_DZ`, `FSR_OF`, `FSR_UF`, `FSR_DO`, `MSR_UM`, `MSR_UMS`, `MSR_VM`,
`MSR_VMS`, `MSR_KERNEL`, `MSR_KERNEL_VMS`, `ESR_DIZ`; plus 1 more.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
