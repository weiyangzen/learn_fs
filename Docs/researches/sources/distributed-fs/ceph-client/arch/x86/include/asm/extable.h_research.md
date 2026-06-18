
# sources/distributed-fs/ceph-client/arch/x86/include/asm/extable.h

Purpose: x86 exception table entry format and fixup handler declarations.

Important APIs and control flow: `struct exception_table_entry` stores relative instruction, fixup, and data/type fields. `ARCH_HAS_RELATIVE_EXTABLE` declares relative-entry semantics. `swap_ex_entry_fixup()` swaps sort entries while adjusting relative offsets. Declarations expose `fixup_exception()`, `ex_get_fixup_type()`, `early_fixup_exception()`, optional MCE MSR handler, and optional BPF JIT exception handler.

State, dependencies, and risks: persistent state is the sorted exception table emitted by assembly/inline asm. Runtime state is fault context in `pt_regs`. Dependencies include extable fixup types, fault handling, MCE, and BPF JIT. Risks include relative offset miscalculation during sorting, wrong fixup type data, and early exception handling before full infrastructure is ready. Test signals are uaccess/MSR fault injection, BPF JIT fault tests, machine-check paths, and extable sort validation.
