<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/llvm-c-helpers.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/llvm-c-helpers.h

## Purpose

`llvm-c-helpers.h` exposes a C ABI for perf code to call LLVM C++ symbolization helpers.

## Important APIs, Types, and Functions

It defines `struct llvm_a2l_frame` with heap-owned filename, function name, and line fields. It declares `llvm_addr2line()`, `llvm_name_for_code()`, and `llvm_name_for_data()` inside `extern "C"` for C++ compatibility.

## Control Flow

Callers request source lookup with optional inline unwinding. A positive return from `llvm_addr2line()` is the number of frames; if inline unwinding is enabled, `inline_frames` receives a newly allocated array. Name helpers return a newly allocated symbol string or NULL.

## State and Persistence Behavior

The header defines no global state. It documents caller ownership of returned strings and arrays.

## Dependencies and Integration Points

It depends on `linux/compiler.h` for `u64` and C/C++ linkage macros. It integrates C perf symbolization paths with the C++ implementation file.

## Risks and Edge Cases

Callers must free nested frame strings and the frame array. Return value 1 can mean either no inline expansion or a one-frame inline result. Passing NULL output pointers must match implementation expectations, especially for `inline_frames` when unwinding.

## Test Signals

Build tests should include the header from C and C++ translation units. Runtime tests should validate ownership, NULL returns, inline-frame counts, and code/data name helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/llvm-c-helpers.h -->
