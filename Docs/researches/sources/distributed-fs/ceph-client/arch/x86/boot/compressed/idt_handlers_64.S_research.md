## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/idt_handlers_64.S

### Purpose
`compressed/idt_handlers_64.S` defines early 64-bit exception entry stubs for compressed boot.

### Important APIs, Types, And Functions
The `EXCEPTION_HANDLER` macro emits handlers for `boot_page_fault`, `boot_nmi_trap`, and, under AMD memory encryption, `boot_stage1_vc` and `boot_stage2_vc`.

### Control Flow
Each handler optionally synthesizes a zero error code, pushes general-purpose registers into a `pt_regs`-like layout, passes `%rsp` as the first C argument and the saved error code as the second, calls the target C function, restores registers, removes the error code, and returns with `iretq`.

### State, Persistence, And Dependencies
The only state is the interrupt stack frame and saved registers on the current boot stack. It depends on `ORIG_RAX` layout from `entry/calling.h`, kernel code segment expectations, and handler prototypes.

### Integration Points
`idt_64.c` installs these symbols into the boot IDT. C handlers live in `ident_map_64.c` and SEV code.

### Risks
The synthetic `pt_regs` layout must match what C handlers expect. Error-code handling differs by vector and is encoded in macro arguments. Any stack alignment or register-save mismatch can corrupt early boot.

### Test Signals
Trigger page faults before identity mapping, inject or observe NMI handling, boot SEV-ES/SNP to exercise #VC paths, and inspect register preservation across handlers.
