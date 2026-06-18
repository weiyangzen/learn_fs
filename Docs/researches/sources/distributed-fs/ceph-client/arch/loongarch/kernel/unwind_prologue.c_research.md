# sources/distributed-fs/ceph-client/arch/loongarch/kernel/unwind_prologue.c

Purpose: implements prologue-analysis stack unwinding for LoongArch by scanning function prologues for stack allocation and RA-save instructions.

Important APIs, types, and functions: exports `unwind_get_return_address()`, `unwind_start()`, and `unwind_next_frame()`. Core helpers are `unwind_by_prologue()`, `next_frame()`, `scan_handlers()`, `fix_exception()`, `fix_ftrace()`, and `unwind_state_fixup()`.

Control flow: `unwind_start()` initializes state as `UNWINDER_PROLOGUE`, or downgrades to guess mode if the initial PC is not kernel text. `unwind_by_prologue()` looks up the current symbol, scans from symbol start to current PC for stack allocation, then scans for RA save before branches. It computes caller SP/PC, handles first-frame leaf functions via saved RA, and resets from `pt_regs` when it recognizes exception/ftrace handler hints. `next_frame()` also handles IRQ stack transitions and falls back through stack segments.

State and persistence: persistent inputs are exception unwind hint symbols and per-CPU exception handlers. Runtime state is held in `unwind_state` flags `type`, `first`, and `reset` plus SP/RA/PC and stack info.

Dependencies and integration points: depends on instruction recognizers from `asm/inst.h`, kallsyms size/offset lookup, exception vector layout, dynamic ftrace, function graph tracing, and stack metadata. It integrates with stacktrace and dump paths through exported GPL symbols.

Risks: compiler prologue variations, hand-written assembly, unusual control flow, or missing kallsyms data can break analysis. Leaf-function handling is necessarily approximate. Exception-vector hint offsets must stay synchronized with low-level exception assembly.

Test signals: compare traces under normal C call chains, leaf functions, ftrace, exceptions, IRQ stacks, and NUMA per-CPU handlers. Build changes affecting prologues should be validated with stacktrace and unwinder tests.
