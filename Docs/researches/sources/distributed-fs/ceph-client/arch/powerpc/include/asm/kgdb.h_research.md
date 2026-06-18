# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kgdb.h

Purpose: Defines PowerPC KGDB breakpoint instruction, register buffer sizing, and architecture breakpoint helper for kernel debugging.

Important APIs, types, and functions: Defines `BREAK_INSTR_SIZE`, `BUFMAX`, `BREAK_INSTR`, `arch_kgdb_breakpoint()`, `CACHE_FLUSH_IS_SAFE`, `DBG_MAX_REG_NUM`, `NUMREGBYTES`, `NUMCRITREGBYTES`, and `MAXREG` with PPC64, PPC32, and e500 differences.

Control flow: KGDB inserts/executes the trap instruction, collects architecture register state into protocol buffers sized by these constants, and communicates with a remote debugger.

State and persistence: KGDB session state is external. The header defines register serialization sizes and emits a trap instruction when requested.

Dependencies and integration points: Integrates KGDB core, ptrace register numbering, exception handling, and cache flush/text patching safety.

Risks: Register buffer sizes must match GDB protocol expectations and architecture register sets. Wrong breakpoint instruction or cache flush assumptions can fail to stop or resume correctly.

Test signals: KGDB break-in, software breakpoint hit/resume, register read/write packets on PPC32/PPC64/e500, single-step if supported, and module/text breakpoint cache coherency.
