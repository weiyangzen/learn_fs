# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/asm-offsets.h

Purpose: hard-coded constants for arm64 FP assembly selftests, covering signal structure sizes/offsets and signal constants.

Important APIs/types/functions: defines `sa_sz`, `sa_flags`, `sa_handler`, `sa_mask_sz`, signal numbers, `SA_NODEFER`, `SA_SIGINFO`, and `ucontext_regs`.

Control flow: no runtime flow.

State and persistence: none.

Dependencies/integration: included by assembly tests that need signal/ucontext layout without C-generated offsets.

Risks and test signals: hard-coded ABI offsets must match the target kernel/userspace ABI; drift causes assembly signal handling failures.
