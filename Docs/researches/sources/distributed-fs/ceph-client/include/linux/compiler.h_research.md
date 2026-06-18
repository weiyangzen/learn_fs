## sources/distributed-fs/ceph-client/include/linux/compiler.h

Purpose: This is the shared kernel compiler abstraction layer used by C code. It defines branch prediction and profiling hooks, barriers, unreachable markers, symbol retention, data-race annotations, compile-time type checks, constant-expression helpers, and pointer offset helpers.

Important APIs, types, and functions: Branch APIs include `likely`, `unlikely`, `likely_notrace`, `unlikely_notrace`, and `ftrace_likely_update()` when branch profiling is active. `barrier()` and `barrier_data(ptr)` prevent compiler reordering or dead-store elimination. `unreachable()`, `KENTRY(sym)`, `RELOC_HIDE`, `absolute_pointer`, `OPTIMIZER_HIDE_VAR`, `__UNIQUE_ID`, `data_race(expr)`, `__BUILD_BUG_ON_ZERO_MSG`, array/string validation helpers, `TYPEOF_UNQUAL`, `KCFI_REFERENCE`, `offset_to_ptr`, `__ADDRESSABLE`, `__is_constexpr`, `is_signed_type`, `is_unsigned_type`, `statically_true`, `const_true`, and `prevent_tail_call_optimization()` are key exports.

Control flow: In branch profiling builds, `likely()` and `unlikely()` allocate static profiling records in special sections and call `ftrace_likely_update()` around the evaluated condition. `data_race()` disables KCSAN and context analysis around a single expression and restores both after evaluation. `offset_to_ptr()` turns a 32-bit relative offset stored at an address into an absolute pointer.

State and persistence: Runtime state appears only through instrumentation records placed in sections such as `_ftrace_annotated_branch`, `_ftrace_branch`, `___kentry+sym`, or `.discard.addressable`. Most macros are compile-time or codegen controls. `data_race()` temporarily changes current-task sanitizer state.

Dependencies and integration points: It includes `compiler_types.h` and `asm/rwonce.h`, integrates with ftrace, KCSAN, context analysis, objtool jump-table annotations, KCFI, linker scripts, and architecture memory-barrier definitions.

Risks and test signals: Risks include evaluating macro arguments more than intended, weakening memory/compiler barriers, hiding real data races, or losing symbols needed by assembly/linker discovery. Test signals include branch-profiling boots, KCSAN reports, objtool validation, KCFI builds, compile-time assertion failures, and all-compiler build coverage.
