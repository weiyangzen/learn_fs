<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ubsan.h -->
# sources/distributed-fs/ceph-client/lib/ubsan.h

## Purpose
Private UBSAN runtime ABI header defining Clang sanitizer check IDs, metadata layouts, max integer types, calling convention adjustments, and handler prototypes used by `ubsan.c`.

## APIs, Types, and Functions
Defines `enum ubsan_checks`, type-kind constants, `struct type_descriptor`, `struct source_location`, and per-check metadata structures: `overflow_data`, `implicit_conversion_data`, `type_mismatch_data`, `type_mismatch_data_v1`, `type_mismatch_data_common`, `nonnull_arg_data`, `out_of_bounds_data`, `shift_out_of_bounds_data`, `unreachable_data`, `invalid_value_data`, and `alignment_assumption_data`. Typedefs `s_max` and `u_max` use `__int128` when available. `ubsan_linkage` handles old Clang i386 calling convention quirks. Prototypes cover all exported handlers.

## Control Flow, State, and Persistence
This header has no executable control flow. Its key state contract is the `source_location` union that overlays an atomic-like reported bit with line/column fields, and the exact field order expected by compiler-emitted metadata.

## Dependencies and Integration
Depends on kernel integer types, config macros for architecture int128 support, x86/Clang version checks, and the Clang CodeGen sanitizer ABI. It is included by `ubsan.c` and must match compiler output.

## Risks and Test Signals
Risks include sanitizer enum ordering drift, calling convention mismatch on older Clang/i386, source-location bit overlay bugs on endian/word-size combinations, and unused metadata structs becoming stale. Test signals include building UBSAN-instrumented kernels with supported Clang versions, 32-bit x86 builds with old Clang, big-endian 64-bit builds, and handler invocation tests validating field decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/ubsan.h -->
