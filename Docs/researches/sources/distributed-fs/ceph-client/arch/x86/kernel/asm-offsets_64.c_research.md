# sources/distributed-fs/ceph-client/arch/x86/kernel/asm-offsets_64.c

## Purpose
This file contributes 64-bit x86-specific generated offsets to `asm-offsets.c`.

## Important APIs, Types, and Functions
`main()` emits paravirt patch offsets when configured, KVM steal-time `preempted`, selected `pt_regs` register offsets, and `saved_context` control-register/GDT descriptor offsets.

## Control Flow
For non-`CONFIG_X86_32` builds, `asm-offsets.c` includes this file. The function body is compiled only for its offset-emitting side effects in generated assembly.

## State and Persistence
No runtime state exists. Generated definitions persist into headers consumed by 64-bit assembly and low-level paravirt/KVM code.

## Dependencies and Integration Points
The file depends on IA32 emulation headers, optional KVM paravirt structures, paravirt patch templates, `pt_regs`, and `saved_context`. It integrates with entry code, KVM steal-time checks, paravirt patching, and suspend/resume save areas.

## Risks and Test Signals
Wrong offsets can corrupt register save/restore, paravirt patching, KVM steal-time logic, or resume. Test signals are successful 64-bit build and runtime coverage of entry, KVM guest, paravirt, and suspend paths.
