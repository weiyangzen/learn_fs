# sources/distributed-fs/ceph-client/arch/s390/kernel/fpu.c

## Purpose
Implements s390 in-kernel FPU/vector save and restore helpers. It lets kernel code temporarily use floating point or vector registers while preserving task state according to requested register masks.

## Important APIs, Types, And Functions
Exports `__kernel_fpu_begin()`, `__kernel_fpu_end()`, and `save_fpu_state()`. Also provides `load_fpu_state()`. These operate on `struct kernel_fpu` or `struct fpu` and flags such as `KERNEL_FPC`, `KERNEL_VXR`, `KERNEL_VXR_LOW`, `KERNEL_VXR_HIGH`, and subranges like `KERNEL_VXR_V0V7`.

## Control Flow
Begin/save paths mask requested flags by state mask, save FPC when requested, then choose legacy FP save/load helpers on systems without vector facility or vector load/store multiple instructions for full, mid, low, high, and subrange register sets. End/load paths mirror the same mask decisions to restore saved state.

## State And Persistence
State is copied between hardware FPC/vector registers and caller-provided memory. No global state is owned.

## Dependencies And Integration Points
Depends on CPU vector facility detection and low-level FPU instruction wrappers. Used by crypto, checksum, and other kernel code that uses vector registers.

## Risks And Edge Cases
Incorrect masks can clobber user or kernel FPU state. Legacy non-VX machines only preserve low FP-compatible registers. FPC safe loading is used for task state to avoid invalid-control faults.

## Test Signals
Signals include kernel vector selftests, crypto tests using kernel FPU regions, context-switch stress with user vector workloads, non-VX build/runtime coverage, and invalid FPC restore tests.
