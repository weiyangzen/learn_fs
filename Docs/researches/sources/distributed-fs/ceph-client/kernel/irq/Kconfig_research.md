# sources/distributed-fs/ceph-client/kernel/irq/Kconfig

## Purpose
`irq/Kconfig` defines feature switches for the generic IRQ subsystem. It lets architecture and subsystem code select generic probing, sparse descriptors, IRQ domains, generic chips, simulated IRQs, IPI support, MSI hierarchy, debugfs, migration, statistics snapshots, forced threading, and KUnit tests.

## Important APIs, types, and functions
This is declarative Kconfig, not C code. Important symbols include `MAY_HAVE_SPARSE_IRQ`, `GENERIC_IRQ_PROBE`, `GENERIC_IRQ_SHOW`, `GENERIC_IRQ_EFFECTIVE_AFF_MASK`, `GENERIC_PENDING_IRQ`, `GENERIC_IRQ_MIGRATION`, `GENERIC_IRQ_CHIP`, `IRQ_DOMAIN`, `IRQ_SIM`, `IRQ_DOMAIN_HIERARCHY`, `GENERIC_IRQ_IPI`, `GENERIC_IRQ_IPI_MUX`, `GENERIC_MSI_IRQ`, `GENERIC_IRQ_STAT_SNAPSHOT`, `IRQ_FORCED_THREADING`, `SPARSE_IRQ`, `GENERIC_IRQ_DEBUGFS`, `GENERIC_IRQ_KEXEC_CLEAR_VM_FORWARD`, `IRQ_KUNIT_TEST`, `GENERIC_IRQ_MULTI_HANDLER`, and `DEPRECATED_IRQ_CPU_ONOFFLINE`.

## Control flow
Kconfig selection controls which files are built and which conditional paths compile in the IRQ core. For example `GENERIC_IRQ_CHIP` selects `IRQ_DOMAIN`, `IRQ_SIM` selects `IRQ_WORK` and `IRQ_DOMAIN`, `GENERIC_IRQ_IPI` depends on SMP and selects hierarchy domains, and `IRQ_KUNIT_TEST` depends on built-in KUnit and sparse IRQ support.

## State and persistence
The file contributes build-time configuration only. Its choices become persistent for a built kernel through `.config`, generated headers, and compiled code paths, but it maintains no runtime state itself.

## Dependencies and integration points
This file drives `irq/Makefile` object inclusion and preprocessor paths in the IRQ implementation. It is selected by architecture Kconfig files, irqchip drivers, MSI/IOMMU code, debugfs, procfs, PM, SMP, and KUnit.

## Risks and test signals
Risks include missing `select` dependencies causing link errors, enabling options on unsupported architectures, stale deprecated options, and test configs that cannot satisfy CPU/hotplug assumptions. Test signals include allmodconfig/allyesconfig builds, architecture defconfigs with sparse and non-sparse IRQs, debugfs and simulated IRQ configs, IPI hierarchy builds, and KUnit `irq_test_cases`.
