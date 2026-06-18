# sources/distributed-fs/ceph-client/arch/s390/include/asm/module.h

Purpose: This header defines s390 module-loader architecture state for GOT/PLT management, per-symbol offsets, and optional ftrace hotpatch trampolines.

Important APIs/types/functions: `struct mod_arch_syminfo`, `struct mod_arch_specific`, and `find_section()` are defined. The arch state records GOT/PLT offsets and sizes, symbol-specific initialization, and ftrace trampoline allocation pointers when function tracing is enabled.

Control flow: The module loader scans ELF sections, allocates or initializes GOT/PLT entries per symbol, and reserves/consumes ftrace trampoline slots for module text patching.

State and persistence: Persistent state is attached to each loaded module in `mod_arch_specific` and lives until module unload.

Dependencies and integration points: It depends on generic module ELF types, ftrace hotpatch structures, and s390 relocation code.

Risks and test signals: Incorrect GOT/PLT offsets or ftrace trampoline ranges can break module calls or tracing. Tests should include module load/unload, symbols needing PLT/GOT, ftrace on modules, and missing-section handling.
