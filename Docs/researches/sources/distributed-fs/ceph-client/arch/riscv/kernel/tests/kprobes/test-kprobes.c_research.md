<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/kprobes/test-kprobes.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/kprobes/test-kprobes.c

Purpose: Implements the KUnit harness that registers kprobes on the assembly test sites and verifies each target function still returns the magic result.

Important APIs/types/functions: Defines `kprobe_dummy_handler()`, `test_kprobe_riscv()`, KUnit case array, and suite `kprobes_riscv`.

Control flow: The test counts address entries, allocates matching `struct kprobe` objects, registers probes with a dummy pre-handler, calls each assembly function, asserts the expected return value, then unregisters probes and frees memory.

State and persistence: Test-local allocations and registered kprobes are cleaned up before return.

Dependencies and integration points: Depends on KUnit, generic kprobes, and assembly symbols from `test-kprobes-asm.S`.

Risks: Registration failure can leave later expectations noisy; cleanup must unregister every successfully registered probe. The test assumes probe sites are safe for current simulator coverage.

Test signals: KUnit suite result, kprobe registration errors, and function-specific failure messages indicating the broken instruction class.

Source read size: 59 lines, 1252 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/kprobes/test-kprobes.c -->
