# sources/distributed-fs/ceph-client/tools/perf/util/dwarf-regs-arch/dwarf-regs-s390.c

Purpose: Converts s390 perf register numbers to DWARF register numbers, including the non-linear floating-point register order. `__get_dwarf_regnum_for_perf_regnum_s390(int perf_regnum)` maps GPRs, FPRs, mask, and PC using a sparse table.

Control flow and state: Stateless table lookup with bounds checking and `-ENOENT` for unsupported entries. Perf register zero is specially accepted because zero is otherwise the unsupported sentinel.

Dependencies and integration: Uses s390 uapi perf register definitions and is selected by the generic dispatcher for `EM_S390`.

Risks: Sparse-table sentinel handling can misclassify future valid zero mappings unless special-cased. Floating-point numbering is non-contiguous and easy to regress.

Test signals: Mapping tests for R0/R15, FP0-FP15 reordered numbers, mask, PC, and unsupported/out-of-range registers; callchain/register tests on s390 samples.
