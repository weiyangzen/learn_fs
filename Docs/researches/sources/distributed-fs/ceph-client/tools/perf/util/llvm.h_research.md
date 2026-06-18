# sources/distributed-fs/ceph-client/tools/perf/util/llvm.h

## Purpose

`llvm.h` declares perf's optional LLVM integration surface for source-line lookup and disassembly. It keeps LLVM details out of callers by exposing only perf-native types and two entry points.

## Important APIs, Types, and Functions

The header forward-declares `struct annotate_args`, `struct dso`, `struct inline_node`, and `struct symbol`. `llvm__addr2line()` resolves a DSO-relative address to file/line information and, when requested, populates inline frame data. `symbol__disassemble_llvm()` disassembles one symbol into perf's annotation structures.

## Control Flow

There is no local control flow. Callers include this header and call the functions; runtime behavior is selected inside `llvm.c` based on compile-time LLVM support and runtime annotate options.

## State and Persistence Behavior

The header defines no state. Ownership contracts are implicit in the implementation: `file` may receive allocated storage, `node` may receive inline entries, and `annotate_args` is mutated during disassembly.

## Dependencies and Integration Points

It depends on `<stdbool.h>` and `<linux/types.h>` for `bool` and `u64`. It is consumed by annotation, symbol, and srcline users that want LLVM support without including LLVM C headers directly.

## Risks and Edge Cases

The API is compiled in regardless of whether LLVM is linked, so callers must handle negative or zero returns. The header's forward declarations mean type contract changes in annotation, symbol, or DSO code must stay synchronized with the implementation.

## Test Signals

Compile tests should cover builds with and without LLVM development headers. Functional tests should verify callers degrade when `llvm__addr2line()` or `symbol__disassemble_llvm()` returns failure.
