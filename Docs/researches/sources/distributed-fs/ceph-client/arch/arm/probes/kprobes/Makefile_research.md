<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/Makefile

Purpose: selects ARM kprobe objects for normal, Thumb-2, optimized-probe, and self-test builds.

Important build entries: disables KASAN instrumentation for `actions-common.o`, `actions-arm.o`, and `actions-thumb.o`, which is important because these files contain low-level probe emulation paths and inline assembly that run in exception-sensitive contexts. `obj-$(CONFIG_KPROBES)` always includes `core.o`, `actions-common.o`, and `checkers-common.o`. `obj-$(CONFIG_ARM_KPROBES_TEST)` builds `test-kprobes.o` from `test-core.o` plus the ISA-specific test file.

Control flow: build selection branches on `CONFIG_THUMB2_KERNEL`. Thumb-2 kernels compile `actions-thumb.o`, `checkers-thumb.o`, and `test-thumb.o`. Non-Thumb2 ARM kernels compile `actions-arm.o`, `checkers-arm.o`, optional `opt-arm.o` under `CONFIG_OPTPROBES`, and `test-arm.o`.

State and persistence: no runtime state; this file determines which object files and test cases are linked into the kernel or module.

Dependencies and integration: integrates with Kbuild and architecture Kconfig symbols. The object split mirrors runtime dispatch in `core.c`, where Thumb-2 selects T16/T32 decode/action/checker arrays and non-Thumb ARM selects ARM arrays and optimized kprobe support.

Risks: an incorrect `CONFIG_THUMB2_KERNEL` branch would compile action/checker arrays incompatible with the instruction set used by `arch_prepare_kprobe()`. Enabling KASAN here could perturb register/stack assumptions in probe handlers.

Test signals: `CONFIG_ARM_KPROBES_TEST` links either `test-arm.o` or `test-thumb.o`; successful build and boot/module test execution indicate correct object selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/Makefile -->
