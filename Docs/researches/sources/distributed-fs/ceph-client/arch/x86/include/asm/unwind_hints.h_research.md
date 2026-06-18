# sources/distributed-fs/ceph-client/arch/x86/include/asm/unwind_hints.h

Purpose: assembler and C macros that emit ORC/objtool unwind hints for hand-written x86 assembly.

Important APIs/types/functions: assembler macros `UNWIND_HINT_END_OF_STACK`, `UNWIND_HINT_UNDEFINED`, `UNWIND_HINT_ENTRY`, `UNWIND_HINT_REGS`, `UNWIND_HINT_IRET_REGS`, `UNWIND_HINT_IRET_ENTRY`, `UNWIND_HINT_FUNC`, `UNWIND_HINT_SAVE`, `UNWIND_HINT_RESTORE`, and C-side `UNWIND_HINT_*` macro forms.

Control flow: assembler macros validate base registers, calculate ORC stack register/offset/type fields, distinguish full vs partial register frames, mark signal frames, and pair entry hints with unret validation. C-side macros provide equivalent static annotations for objtool-visible code.

State/persistence: no runtime state. Hints are persisted into object metadata consumed by objtool and the ORC unwinder.

Dependencies/integration: depends on `linux/objtool.h` and x86 `orc_types.h`. Used by entry code, interrupt/exception assembly, context switch code, and any hand-coded stack manipulation.

Risks/test signals: incorrect hints lead to broken stack traces or objtool warnings, especially around interrupt frames and special stacks. Test with `objtool` validation, ORC unwinder enabled, all entry/exit paths, NMI/IST frames, retbleed/unret validation, and oops stack traces through annotated assembly.
