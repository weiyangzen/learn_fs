<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/llvm-c-helpers.cpp -->
# sources/distributed-fs/ceph-client/tools/perf/util/llvm-c-helpers.cpp

## Purpose

`llvm-c-helpers.cpp` bridges perf C code to LLVM's C++ symbolizer APIs for addr2line, inline-frame lookup, and code/data symbol naming.

## Important APIs, Types, and Functions

It defines a process-lifetime `LLVMSymbolizer` from `get_symbolizer()`, `extract_file_and_line()`, exported C functions `llvm_addr2line()`, `llvm_name_for_code()`, and `llvm_name_for_data()`, and helper `make_symbol_relative_string()`.

## Control Flow

The symbolizer is lazily allocated with demangling disabled so perf's own demangler produces consistent names. `llvm_addr2line()` either calls `symbolizeInlinedCode()` and converts every frame into a heap-allocated `llvm_a2l_frame` array, or calls `symbolizeCode()` for a single file/line result. Name helpers call LLVM code/data symbolization and format `name+offset` when LLVM provides a start address distinct from the queried address.

## State and Persistence Behavior

The LLVM symbolizer instance is intentionally leaked until process exit to retain its cache. Returned strings and inline-frame arrays are heap allocated and caller-owned. No files are written.

## Dependencies and Integration Points

It depends on LLVM DebugInfo/Symbolize C++ APIs, Linux compiler/zalloc compatibility, perf DSO demangling, and the C header `llvm-c-helpers.h`. It lets C symbolization code use LLVM features without including LLVM C++ headers.

## Risks and Edge Cases

Memory ownership is strict: every filename/function string and frame array must be freed by the caller. On partial allocation failure the function frees frames allocated so far. `<invalid>` filenames map to NULL to match libbfd conventions. LLVM API behavior and warning profiles vary by version, reflected by diagnostic suppression for LLVM <= 15.

## Test Signals

Tests should cover simple addr2line, inline stacks, invalid addresses, allocation-failure cleanup, demangled C++ symbols through perf demangler, data symbol names, and LLVM version build compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/llvm-c-helpers.cpp -->
