
# sources/distributed-fs/ceph-client/arch/x86/include/asm/desc.h

Purpose: x86 descriptor-table manipulation helpers for GDT, IDT, LDT, TSS, TLS, and entry stack mappings.

Important APIs and control flow: `fill_ldt()` converts `user_desc` to an LDT descriptor. GDT helpers return writable per-CPU GDT, read-only CPU entry-area GDT, or physical addresses. `pack_gate()`/`idt_init_desc()` build IDT gates. Native load/store functions issue `lgdt`, `lidt`, `ltr`, `lldt`, `sgdt`, `sidt`, and `str`. TSS/LDT descriptor setup writes GDT entries; `native_load_tr_desc()` temporarily swaps from RO fixmap GDT to writable GDT on 64-bit. TSS limit helpers reload or invalidate TR around IO bitmap behavior.

State, dependencies, and risks: state is per-CPU GDT/TSS/TLS/IDT and cached TSS limit flags. Dependencies include descriptor definitions, CPU entry area, paravirt, thread flags, and entry setup. Risks include descriptor layout corruption, preemption-sensitive TSS limit updates, RO/RW GDT mismatch, and user LDT corner cases. Test signals include boot/entry tests, modify_ldt tests, IO bitmap tests, CPU hotplug, and virtualization exits.
