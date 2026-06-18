# sources/distributed-fs/ceph-client/arch/parisc/math-emu/fpudispatch.c

Purpose: decodes trapped PA-RISC floating-point instructions and dispatches them to the appropriate software emulation routine. It is the integration hub between trap handling, the FP register image, and arithmetic helpers.

Important APIs and functions: public entry points are `fpudispatch(ir, excp_code, holder, fpregs)` for hardware unimplemented exceptions and `emfpudispatch(ir, dummy1, dummy2, fpregs)` for full coprocessor emulation. Static decoders handle major opcodes `0x0c`, `0x0e`, `0x06`, `0x26`, and `0x2e`; `update_status_cbit()` updates compare status or compare queue bits.

Control flow: the dispatcher derives class and subop fields, considering PA1.1 versus PA2.0 subop layouts. Major decoders compute register offsets, map source `fr0` to a constant zero slot, reject illegal destination `fr0`, align double registers, then call conversion, compare, add, subtract, multiply, divide, remainder, sqrt, round, fused, or multi-op helpers.

State and persistence: it updates `fpregs[0]` as the FP status register and stores results directly into `fpregs`. It also writes `fpregs[FPU_TYPE_FLAG_POS]` from CPU type for Linux callers.

Dependencies and integration: called by `decode_exc.c` and trap paths behind `handle_fpe()`. Depends on `float.h`, arithmetic files, Linux `boot_cpu_data`, and PA-RISC register encodings.

Risks: decode field positions are dense and architecture-specific. Misaligned double or right-half register handling can corrupt adjacent register slots. Several unsupported paths use `BUG()` after nominally unreachable switch cases; fuzzed instruction streams must return unimplemented exceptions before reaching them.

Test signals: use instruction-encoding tests for every major opcode, source zero mapping, destination zero rejection, PA1.1 versus PA2.0 compare status, Timex/Rolex special cases, fused op `0x2e`, and crashme-style malformed double register operands.
