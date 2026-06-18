# sources/distributed-fs/ceph-client/tools/perf/util/print_insn.h

## Purpose
This header declares instruction printing helpers for perf samples and direct byte buffers.

## Important APIs, Types, and Functions
It declares `sample__fprintf_insn_asm`, `sample__fprintf_insn_raw`, and `fprintf_insn_asm`, and defines `PRINT_INSN_IMM_HEX`. Forward declarations cover `perf_sample`, `thread`, `machine`, and `perf_insn`.

## Control Flow
There is no header control flow. Implementations choose raw versus assembly output and capstone fallback behavior.

## State and Persistence
No state is declared. All formatting uses caller-supplied sample and machine context.

## Dependencies and Integration Points
The header depends on standard size and file types and is included by perf reporting/script code that needs instruction display.

## Risks
The prototypes mention `struct addr_location` without a forward declaration in this header, relying on includer context. That can be fragile if included standalone.

## Test Signals
Build tests with minimal includers can catch missing forward declarations. Functional tests should use the implementation through this API for raw and disassembled output.
