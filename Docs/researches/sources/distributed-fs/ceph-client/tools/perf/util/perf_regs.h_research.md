# sources/distributed-fs/ceph-client/tools/perf/util/perf_regs.h

## Purpose
This header defines the register decoding contract used by perf sample display, SDT probe parsing, and DWARF integration. It exposes generic dispatch APIs and declares architecture-specific helper entry points.

## Important APIs, Types, and Functions
Public functions include `perf_sdt_arg_parse_op`, `perf_intr_reg_mask`, `perf_user_reg_mask`, `perf_reg_name`, `perf_reg_value`, `perf_arch_reg_ip`, and `perf_arch_reg_sp`. It defines `SDT_ARG_VALID`, `SDT_ARG_SKIP`, and `DWARF_MINIMAL_REGS(e_machine)`, which builds a minimal IP/SP sample mask.

## Control Flow
The header itself has no control flow except the `DWARF_MINIMAL_REGS` inline expression. Implementations are dispatched by `perf_regs.c` to per-architecture helpers such as arm64, arm, csky, loongarch, mips, powerpc, riscv, s390, and x86.

## State and Persistence
No state is declared here. Callers pass a `struct regs_dump` whose ownership and lifetime remain outside this header.

## Dependencies and Integration Points
It depends on Linux integer types and compiler annotations. It is included by code that decodes sampled registers, names registers for output, and converts SDT operand syntax into perf-compatible probe arguments.

## Risks
Adding a new architecture requires updating both declarations here and switch dispatch in `perf_regs.c`. `DWARF_MINIMAL_REGS` assumes IP and SP IDs fit in a 64-bit mask.

## Test Signals
Build matrix coverage across supported architectures is the primary signal. Unit tests can verify that `DWARF_MINIMAL_REGS` contains exactly the architecture IP and SP bits and that declarations stay aligned with implementations.
