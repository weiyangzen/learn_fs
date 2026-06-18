# sources/distributed-fs/ceph-client/kernel/irq/irq_test.c

## Purpose
`irq_test.c` is a KUnit suite for IRQ management behavior, focused on descriptor disable depth, free/re-request behavior, managed IRQ shutdown/startup depth, and CPU hotplug interaction.

## Important APIs, types, and functions
The suite defines a fake `irq_chip` with no-op callbacks and an affinity setter that updates effective affinity. Test helpers include `irq_test_setup_fake_irq()`, `noop_handler()`, and chip no-op callbacks. Test cases are `irq_disable_depth_test()`, `irq_free_disabled_test()`, `irq_shutdown_depth_test()`, and `irq_cpuhotplug_test()`, registered in `irq_test_suite`.

## Control flow
Each test allocates one sparse IRQ descriptor, assigns the fake chip and `handle_simple_irq`, clears no-request state, requests the IRQ, manipulates disable/free/shutdown/hotplug operations, and asserts descriptor depth and irqdata state. Managed shutdown tests create managed affinity descriptors, call `irq_shutdown_and_deactivate()` under descriptor lock, reactivate/start managed IRQs, then verify disabled depth is preserved until `enable_irq()`. The hotplug test removes and re-adds CPU1 for a managed IRQ affine to CPU1.

## State and persistence
State is temporary test state in dynamically allocated IRQ descriptors and a fake chip. Tests may affect CPU hotplug state but restore CPU1 by calling `add_cpu(1)` after removal. No state should persist after the suite beyond normal KUnit lifecycle cleanup assumptions.

## Dependencies and integration points
The suite depends on built-in KUnit, sparse IRQ support, IRQ domains/descriptor allocation, CPU hotplug APIs, SMP for managed tests, and internal IRQ helpers via `internals.h`. Kconfig gates it behind `IRQ_KUNIT_TEST`.

## Risks and test signals
Risks include CPU1 availability/hotpluggability assumptions causing skips, allocated descriptors not explicitly freed in some paths, architecture defaults requiring no-request clearing, and test behavior that is too tied to internal depth semantics. Passing test signals are preserved disable depth across disable/enable, free/re-request after disabled free, managed shutdown depth balance, and hotplug not re-enabling a manually disabled managed IRQ.
