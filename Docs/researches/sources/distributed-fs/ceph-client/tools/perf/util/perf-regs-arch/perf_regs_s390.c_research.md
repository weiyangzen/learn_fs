
# sources/distributed-fs/ceph-client/tools/perf/util/perf-regs-arch/perf_regs_s390.c

Purpose: provides s390 register names, masks, IP/SP IDs, and SDT operand validation/conversion.

Important APIs/types/functions: `__perf_reg_mask_s390` returns `PERF_REGS_MASK`. `__perf_reg_name_s390` maps R0-R15, FP0-FP15, MASK, and PC. `__perf_reg_ip_s390` returns PC and `__perf_reg_sp_s390` returns R15. `__perf_sdt_arg_parse_op_s390` accepts `%r0`-`%r15` and signed displacement forms like `+48(%r1)`, returning the same syntax when valid and skipping unsupported operands.

Control flow: regexes compile lazily with a two-step initialized state. SDT parsing matches either direct register or displacement form, duplicates the matched operand, and returns valid/skip/error.

State and persistence: static compiled regexes and initialized flag.

Dependencies: regex, s390 arch register definitions, zalloc, debug logging.

Integration points: s390 perf register sampling, sample display, and SDT probe argument setup.

Risks: regex initialized state must reset correctly on second-regex failure. Register names are uppercase for display while SDT syntax is lowercase `%rN`. Test signals include SDT operand cases, register list output, and sample decoding.
