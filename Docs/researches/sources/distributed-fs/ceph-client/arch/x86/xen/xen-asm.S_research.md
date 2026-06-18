<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/xen-asm.S -->
# sources/distributed-fs/ceph-client/arch/x86/xen/xen-asm.S

## Purpose
Provides low-level Xen PV x86 assembly entry points for hypercalls, interrupt enable/disable/save flags, CR2 reads, trap stubs, early IDT handlers, IRET, syscall/sysenter callbacks, and return-to-usermode paths.

## Important APIs, Types, And Functions
Important symbols include `xen_hypercall_pv`, `xen_irq_disable_direct`, `xen_irq_enable_direct`, `xen_save_fl_direct`, `xen_read_cr2`, `xen_read_cr2_direct`, generated `xen_asm_exc_*` trap labels, `xen_early_idt_handler_array`, `xen_iret`, `xenpv_restore_regs_and_return_to_usermode`, `xen_entry_SYSCALL_64`, `xen_entry_SYSCALL_compat`, and `xen_entry_SYSENTER_compat`.

## Control Flow
The IRQ helpers directly manipulate Xen vCPU event masks and call `check_events` to force callback processing when unmasking reveals pending events. Trap stubs push vector/error-code shape expected by common x86 handlers. `xen_iret` and syscall entry wrappers use the Xen `iret` hypercall path rather than native return where PV privilege rules require it. Compatibility entry points normalize `%rsp` and branch into common x86 syscall handling.

## State And Persistence
No C-visible data persists, but the assembly reads/writes per-CPU Xen vCPU info fields, CR2, and CPU registers. The symbols become callback targets registered in `setup.c` and SMP bringup.

## Dependencies And Integration Points
Depends on x86 calling conventions, Xen PV ABI, IDT entry macros, paravirt patching, syscall entry code, and callback registration in `xen_enable_syscall`/`xen_pvmmu_arch_setup`.

## Risks And Edge Cases
Register save/restore, stack shape, flags semantics, event-mask pending checks, and 32/64-bit conditional code are extremely sensitive. Missing callback processing after enabling events can lose interrupts. Callback targets must match Xen's expected code segment and privilege model.

## Test Signals
Signals include PV boot, syscall and compat-syscall tests, exception/fault handling, interrupt storm tests, preemption/return-to-user stress, and objtool/unwind validation where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/xen-asm.S -->
