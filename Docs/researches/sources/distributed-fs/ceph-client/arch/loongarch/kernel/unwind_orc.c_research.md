# sources/distributed-fs/ceph-client/arch/loongarch/kernel/unwind_orc.c

Purpose: implements the LoongArch ORC unwinder, including table lookup, module ORC registration, ftrace trampoline mapping, stack safety checks, and frame-step logic.

Important APIs, types, and functions: exported interfaces are `unwind_get_return_address()`, `unwind_start()`, and `unwind_next_frame()`. `unwind_init()` validates and initializes vmlinux ORC tables and lookup blocks. `unwind_module_init()` sorts module ORC tables and attaches them to `struct module`. Internal helpers include `orc_find()`, `__orc_find()`, `orc_module_find()`, `orc_ftrace_find()`, `stack_access_ok()`, and `bt_address()`.

Control flow: lookup first handles `ip == 0`, then uses the fast `orc_lookup` block table for core text, a full binary search for init text, module tables when enabled, and dynamic ftrace fallback if needed. `unwind_next_frame()` obtains an ORC entry under RCU protection, falls back to a fake frame-pointer entry for generated code, computes the previous SP/FP/RA according to the ORC entry, handles saved `pt_regs` frames, translates exception-vector addresses via `bt_address()`, and marks the trace done or errored on invalid state.

State and persistence: persistent state includes `orc_init`, `lookup_num_blocks`, mutable lookup table entries, module ORC pointers, and module sort scratch globals protected by `sort_mutex`. The unwinder mutates per-call `unwind_state` fields `sp`, `fp`, `ra`, `pc`, `stack_info`, and `error`.

Dependencies and integration points: depends on objtool-generated `.orc_unwind`/`.orc_unwind_ip` sections, linker `ORC_UNWIND_TABLE`, module loader ORC plumbing, dynamic ftrace trampolines, exception handlers, stack metadata, RCU, and function graph return address translation.

Risks: corrupt or unsorted ORC tables can disable unwinding or produce bad stack walks. The module sort swap must keep relative IP encodings aligned with entries. Stack access validation is critical for crash safety. Fallback frame-pointer unwinding intentionally marks `state->error`.

Test signals: ORC table validation warnings at boot, stacktrace correctness through modules, ftrace-enabled traces, NULL function pointer crash unwinding, IRQ/exception stack traces, and objtool/sorttable build checks are the strongest signals.
