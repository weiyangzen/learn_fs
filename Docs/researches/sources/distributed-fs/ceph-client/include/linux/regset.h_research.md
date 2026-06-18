# sources/distributed-fs/ceph-client/include/linux/regset.h

## Purpose

`regset.h` defines the architecture-neutral interface for exposing user-mode machine state to ptrace, core dumps, and related process inspection APIs. It models CPU or ABI state as register sets with get/set/active/writeback callbacks.

## Important APIs, Types, and Functions

`struct membuf` and helpers `membuf_zero()`, `membuf_write()`, `membuf_at()`, and `membuf_store()` provide bounded kernel-buffer output for regset getters. Callback types include `user_regset_active_fn`, `user_regset_get2_fn`, `user_regset_set_fn`, and `user_regset_writeback_fn`.

`struct user_regset` describes one register set: slot count, slot size, alignment, bias, ELF core note type/name, and callbacks. `USER_REGSET_NOTE_TYPE()` fills note metadata from `NT_*`/`NN_*` symbols. `struct user_regset_view` groups regsets for an ABI view and supplies ELF machine flags, machine ID, and OS ABI.

Runtime APIs include `task_user_regset_view()`, `user_regset_copyin()`, `user_regset_copyin_ignore()`, `regset_get()`, `regset_get_alloc()`, `copy_regset_to_user()`, and inline `copy_regset_from_user()`.

## Control Flow

Inspection code obtains a task's native `user_regset_view`, selects a regset by index, and invokes get/set helpers. Getters write into `struct membuf` with truncation-aware helpers. Setters receive byte offsets and counts that the caller has already validated for alignment and size. Copy-in helpers advance position/count and either copy from kernel buffers or user buffers with `__copy_from_user()`.

Regset callbacks must be called only for the current thread or stopped/traced inactive targets, with `wait_task_inactive()` synchronization as documented. Optional writeback callbacks flush hardware-backed or user-memory-backed register windows immediately or before the next context switch.

## State and Persistence Behavior

The header defines descriptors, not storage. Actual state is architecture thread state, FPU/vector state, TLS/GDT-like state, or user-memory-backed register windows. Core-dump note metadata determines how much state persists into core files.

## Dependencies and Integration Points

It depends on compiler annotations, uaccess, task structures, ELF note constants, and architecture implementations of regset views. It integrates with ptrace, coredump generation, signal/user context handling, and process memory access code.

## Risks

Callbacks are not responsible for validating alignment or bounds, so callers must enforce the documented preconditions. Accessing a running target can capture inconsistent or corrupted state. `membuf_store()` requires proper alignment for scalar stores. User copies can fault. Backward compatibility requires padding/default data for inactive parts of variable-sized regsets.

## Test Signals

Tests should cover ptrace get/set for each architecture regset, partial offset/count copies, inactive/default regset areas, core note generation, compat ABI views, user-copy faults, writeback behavior, and stopped-task synchronization under SIGKILL races.
