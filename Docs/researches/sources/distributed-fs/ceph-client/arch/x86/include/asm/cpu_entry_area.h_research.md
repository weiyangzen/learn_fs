
# sources/distributed-fs/ceph-client/arch/x86/include/asm/cpu_entry_area.h

Purpose: defines the per-CPU entry-area virtual layout used by x86 entry, exception, GDT/TSS, and debug-store code.

Important APIs and control flow: 64-bit exception stack macros build guarded IST stack layout, including optional VC stacks for AMD memory encryption. `struct cpu_entry_area` maps GDT, entry stack, optional 32-bit doublefault stack, TSS, 64-bit exception stacks, debug store, and debug buffers. APIs declare setup and PTE mapping functions, `get_cpu_entry_area()`, `cpu_entry_stack()`, and helpers to find current IST top/bottom addresses.

State, dependencies, and risks: persistent state is per-CPU virtual aliases to backing storage; the struct itself is layout contract, not directly allocated. Dependencies include processor/TSS types, pgtable areas, Intel DS, percpu, and entry assembly offsets. Risks include layout changes breaking assembly, guard-page mistakes, RO/RW mapping mismatch, and confidential-computing VC stack sizing. Test signals are boot entry paths, NMI/DF/MCE/#VC handling, debug-store use, and objtool/offset checks.
