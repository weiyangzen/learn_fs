# sources/distributed-fs/ceph-client/tools/perf/util/include/asm/dwarf2.h

Purpose: supplies no-op DWARF CFI annotation macros needed when perf tools include kernel x86 assembly such as `memcpy` or `memset` implementations. Userspace perf does not need the kernel's assembler CFI macro implementation for these imported files.

Important APIs and types: defines `CFI_STARTPROC`, `CFI_ENDPROC`, `CFI_REMEMBER_STATE`, and `CFI_RESTORE_STATE` as empty macros under guard `PERF_DWARF2_H`.

Control flow: compile-time macro expansion only. It strips CFI annotations from assembly sources in the tools context.

State and persistence: none.

Dependencies and integration: used by architecture assembly pulled into perf. It deliberately avoids depending on the kernel's full `asm/dwarf2.h`.

Risks: because CFI macros are empty, generated object unwind metadata may differ from kernel builds. That is acceptable for the imported helper usage but risky if broader assembly code starts relying on these macros for unwind correctness.

Test signals: assembler builds of imported x86 library code, plus smoke tests that exercise the copied routines if they are linked into tools.
