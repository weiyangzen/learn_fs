<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ubsan.c -->
# sources/distributed-fs/ceph-client/lib/ubsan.c

## Purpose
Kernel UBSAN runtime reporting implementation. It maps compiler-emitted sanitizer handlers to kernel warnings, KUnit failures, stack dumps, optional panic-on-warn, and trap-mode failure strings.

## APIs, Types, and Functions
When trap support is enabled, `report_ubsan_failure()` maps Clang sanitizer handler codes to short reason strings based on enabled `CONFIG_UBSAN_*` checks. Without `CONFIG_UBSAN_TRAP`, the file exports compiler ABI handlers such as `__ubsan_handle_add_overflow()`, `__ubsan_handle_sub_overflow()`, `__ubsan_handle_mul_overflow()`, `__ubsan_handle_negate_overflow()`, `__ubsan_handle_implicit_conversion()`, `__ubsan_handle_divrem_overflow()`, `__ubsan_handle_type_mismatch()`, `__ubsan_handle_type_mismatch_v1()`, `__ubsan_handle_out_of_bounds()`, `__ubsan_handle_shift_out_of_bounds()`, `__ubsan_handle_builtin_unreachable()`, `__ubsan_handle_load_invalid_value()`, and `__ubsan_handle_alignment_assumption()`. Helpers decode type descriptors, values, source locations, and suppression state.

## Control Flow, State, and Persistence
Reports are suppressed when the current task is already in UBSAN or when the `source_location` has its `REPORTED_BIT` set via `test_and_set_bit()`. `ubsan_prologue()` increments `current->in_ubsan`, prints a cut marker and source location, and fails the current KUnit test. Handlers format type/value-specific diagnostics, then `ubsan_epilogue()` dumps the stack, decrements `in_ubsan`, and honors panic-on-warn. Type mismatch and shift/invalid-value paths wrap reporting with `user_access_save()`/`user_access_restore()` to avoid user access state issues. `__ubsan_handle_builtin_unreachable()` panics after reporting because it cannot return safely.

## Dependencies and Integration
Depends on compiler-emitted UBSAN metadata structures from `ubsan.h`, task state, printk/warn infrastructure, stack dumps, KUnit bug integration, bitops, user access controls, and sanitizer config options. It exports ABI symbols expected by instrumented kernel code.

## Risks and Test Signals
Risks include ABI drift with Clang sanitizer handler metadata, endian-specific packing of `source_location.reported`, recursive reporting suppression hiding secondary issues, formatting 128-bit values only when supported, and panic behavior for unreachable reports. Test signals include KUnit tests that intentionally trigger each handler, trap-mode code-to-string mapping for enabled configs, duplicate-location suppression, user-access-state restoration, signed/unsigned value formatting, and panic-on-warn behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ubsan.c -->
