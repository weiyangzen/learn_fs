<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/asm_pure_loop/asm_pure_loop.S -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/asm_pure_loop/asm_pure_loop.S

## Purpose

This arm64 assembly workload creates a predictable branch-heavy loop for CoreSight ETM trace validation.

## Research

The `_start` entry sets `x0` to `0x0000ffff` as loop count and `x1` to zero. Each iteration executes nops, conditionally branches around more nops via `cbnz`, computes the `skip` address with `adrp/add`, performs an indirect `br`, decrements `x0`, and loops until zero. It exits through syscall 93 with status 0 and declares an empty GNU-stack note. There is no libc, heap, or persistent state; execution state is registers and instruction flow. Dependencies are arm64 instruction set and Linux syscall ABI. Integration provides a stable ETM packet source for `asm_pure_loop.sh`. Risks include assembler/linker differences affecting layout, branch predictor/trace compression variability, and being arm64-only. Test signals are sufficient branch/async/trace-info packets in the recorded AUX dump.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/asm_pure_loop/asm_pure_loop.S -->
