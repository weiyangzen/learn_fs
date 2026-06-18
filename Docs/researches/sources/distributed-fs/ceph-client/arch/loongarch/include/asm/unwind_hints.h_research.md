<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/unwind_hints.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/unwind_hints.h

Purpose: supplies assembly unwind hint macros for LoongArch entry and low-level code.
Important APIs and types: defines macros such as `UNWIND_HINT_UNDEFINED`, `UNWIND_HINT_REGS`, and `UNWIND_HINT_END_OF_STACK`, with objtool/CFI-aware behavior where configured.
Control flow: assembly code emits hints at entry, exception, idle, and return sites so unwinder tools can understand non-standard frames.
State and persistence: no runtime state, but emitted metadata persists in object/debug sections.
Dependencies and integration: used by `entry.S`, `head.S`, `genex.S`, FPU/idle assembly, objtool, stacktrace, and ORC/CFI-like validation flows.
Risks and test signals: bad hints produce unreliable stack traces or build-time validation failures. Signals include objtool warnings, stack unwinding through exceptions, and livepatch reliable-stack checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/unwind_hints.h -->
