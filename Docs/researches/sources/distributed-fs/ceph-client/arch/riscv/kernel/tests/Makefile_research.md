<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/Makefile

Purpose: Selects RISC-V kernel self-test subdirectories for module-linking and kprobes KUnit tests.

Important APIs/types/functions: Uses `obj-$(CONFIG_RISCV_MODULE_LINKING_KUNIT)` and `obj-$(CONFIG_RISCV_KPROBES_KUNIT)`.

Control flow: Kbuild descends into enabled test subdirectories based on config.

State and persistence: No runtime state; affects test build composition.

Dependencies and integration points: Integrates RISC-V architecture KUnit tests into the kernel build.

Risks: Wrong config guards silently omit architecture tests.

Test signals: KUnit builds with either or both configs enabled and confirms subdirectory objects are linked.

Source read size: 2 lines, 104 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/tests/Makefile -->
