# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/lib/reg.S

## Purpose
Assembly implementation of common register load/store helpers declared in `include/reg.h`.

## Important APIs, Types, and Functions
Exports `load_gpr`, `store_gpr`, `store_fpr`, `loadvsx`, and `storevsx` via `FUNC_START`/`FUNC_END`.

## Control Flow
Each helper sequentially loads or stores a register class from/to caller-provided buffers: r14-r31 for GPRs, f0-f31 for FPR stores, and vs0-vs63 for VSX load/store.

## State and Persistence
Mutates register files and caller-provided memory only. No persistent state.

## Dependencies and Integration Points
Depends on `<ppc-asm.h>` and `reg.h` raw VSX load/store macros. Linked into PowerPC tests needing register state setup/inspection.

## Risks and Test Signals
Risk is ABI register numbering or buffer sizing mistakes. Downstream tests signal failures through register mismatch checks.
