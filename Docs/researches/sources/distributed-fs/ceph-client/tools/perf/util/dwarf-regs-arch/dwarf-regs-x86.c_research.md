# sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-x86.c

Purpose: Provides x86/i386 register-name to DWARF-number conversion and perf-register to DWARF-register mapping. `__get_dwarf_regnum_i386` and `__get_dwarf_regnum_x86_64` parse names with a required leading `%` and accept aliases such as full, partial, stack, flags, segment, SIMD, PC, and base registers. Perf-register functions translate enum values to architecture-specific DWARF numbers.

Control flow and state: Stateless lookup through alias tables and sparse mapping arrays. Mapping functions special-case valid perf register zero because unsupported entries also default to zero.

Dependencies and integration: Depends on x86 perf register uapi, Linux `ARRAY_SIZE`, and `dwarf-regs.h`. `dwarf-regs.c` dispatches to these functions for `EM_386` and `EM_X86_64`.

Risks: Alias table correctness directly affects probe argument parsing. A visible table typo maps x86-64 `"edx"` to DWARF register 3 in the RBX row, which should be reviewed because `"edx"` already appears in the RDX row. Sparse zero sentinel handling has the usual future-maintenance risk.

Test signals: Reverse lookup tests for `%rax/%eax/%al`, `%rip/%eip/%ip`, `%fs.base`, i386 `%esp/%stack`, invalid names without `%`, and perf enum mappings for GPRs, IP, flags, segments, and XMM registers.
