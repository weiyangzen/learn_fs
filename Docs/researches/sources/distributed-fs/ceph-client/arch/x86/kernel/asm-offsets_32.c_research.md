# sources/distributed-fs/ceph-client/arch/x86/kernel/asm-offsets_32.c

## Purpose
This file contributes 32-bit x86-specific generated offsets to `asm-offsets.c`. It is included by the main generator and explicitly rejects direct builds.

## Important APIs, Types, and Functions
The only function, `foo()`, emits offsets for 32-bit `pt_regs` fields, `saved_context.gdt_desc`, the `TSS_entry2task_stack` delta from CPU entry stack to task stack, and the EFI runtime `set_virtual_address_map` offset.

## Control Flow
When `CONFIG_X86_32` is selected, `asm-offsets.c` includes this file. The generator emits constants from the `OFFSET()` and `DEFINE()` macros and kbuild post-processing turns them into assembly-visible definitions.

## State and Persistence
No runtime state exists. The generated constants persist as build artifacts used by 32-bit entry, resume, and EFI assembly.

## Dependencies and Integration Points
It depends on `linux/efi.h`, `asm/ucontext.h`, `pt_regs`, `saved_context`, `cpu_entry_area`, `tss_struct`, and EFI runtime service layouts. The TSS delta is tightly coupled to entry-stack switching code.

## Risks and Test Signals
Layout drift can break trap/syscall entry, resume, or EFI runtime transitions on 32-bit builds. Test signals are successful 32-bit build, correct generated offset names, and boot tests covering entry stack and EFI runtime paths.
