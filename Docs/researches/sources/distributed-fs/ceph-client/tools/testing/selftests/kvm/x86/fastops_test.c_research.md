# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/fastops_test.c

Purpose: Exercises KVM's x86 emulator fastop paths for common arithmetic, bit-test, shift, and divide instructions. It compares normal and forced-emulation execution for correctness of result values and EFLAGS.

Important APIs/types/functions: Macro families `guest_execute_fastop_*()`, `guest_test_fastop_*()`, `guest_execute_fastop_cl()`, and `guest_execute_fastop_div()` generate inline assembly for many operand sizes and instruction forms. `vals[]` supplies edge-case input values; `guest_test_fastops()` expands the matrix; `guest_code()` runs it; `main()` creates a one-vCPU VM.

Control flow: The guest runs a deterministic matrix of fastop instruction tests. For each instruction/input pair, it executes the operation without forced emulation and with KVM forced-emulation prefix where applicable, then asserts output registers and flags are identical or architecturally expected.

State and persistence behavior: All state is guest register/flag state within a single vCPU run. No host persistence exists.

Dependencies and integration points: Depends on the KVM instruction emulator, selftest forced-emulation prefix support, compiler inline assembly constraints, and x86 arithmetic flag semantics.

Risks and maintenance notes: Inline assembly constraints are fragile and instruction encodings are hand-driven by macros. Compiler changes may expose constraint issues. Divide tests must handle faulting/overflow cases carefully.

Test signals: Passing means emulator fastop shortcuts match hardware behavior for the tested instruction matrix, including EFLAGS. Failures identify arithmetic, shift, bit-test, divide, or forced-emulation discrepancies.
