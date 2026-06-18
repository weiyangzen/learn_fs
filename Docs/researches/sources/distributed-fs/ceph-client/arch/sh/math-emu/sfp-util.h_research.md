# sources/distributed-fs/ceph-client/arch/sh/math-emu/sfp-util.h

Purpose: adapts generic Linux soft-fp support to SH software FPU emulation.

Important content: soft-fp word/type definitions, exception/rounding glue, and architecture-specific macros consumed by `math.c`.

Control flow: header-only macro layer used during compile-time expansion of floating-point operations.

State and persistence: does not own state directly; macros operate on soft-fp temporaries and caller-provided FPU state.

Dependencies and integration: included before `<math-emu/soft-fp.h>`, `<math-emu/single.h>`, and `<math-emu/double.h>`.

Risks: mismatch between SH FPSCR rounding/exception semantics and soft-fp macros causes subtle arithmetic differences.

Test signals: soft-FPU arithmetic conformance tests across rounding modes and exception cases.
