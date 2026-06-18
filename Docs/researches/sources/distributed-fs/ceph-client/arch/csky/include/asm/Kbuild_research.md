# sources/distributed-fs/ceph-client/arch/csky/include/asm/Kbuild

## Purpose

selects generated and generic C-SKY asm headers exported through Kbuild

## Important APIs, Types, and Functions

Source read size: 14 lines, 346 bytes. Build selections: `syscall-y -> syscall_table_32.h`,
`generic-y -> asm-offsets.h`, `generic-y -> extable.h`, `generic-y -> kvm_para.h`, `generic-y ->
mcs_spinlock.h`, `generic-y -> qrwlock.h`, `generic-y -> qrwlock_types.h`, `generic-y ->
qspinlock.h`, `generic-y -> parport.h`, `generic-y -> user.h`, `generic-y -> vmlinux.lds.h`,
`generic-y -> text-patching.h`.

## Control Flow and Behavior

the header provides macros, inline functions, declarations, or generic-header selections used by
C-SKY core kernel code

## State and Persistence

state is normally compile-time definitions; inline helpers may manipulate CPU registers, page
tables, TLBs, interrupt flags, or task state when used

## Dependencies and Integration Points

integrates with ABI-specific headers, asm-generic fallbacks, MM, scheduler, tracing, IRQ, syscall,
and user-access subsystems depending on the declarations present

## Risks and Test Signals

header changes have wide compile-time and runtime blast radius; allmodconfig builds plus subsystem
selftests matching the declared interface are the main signals
