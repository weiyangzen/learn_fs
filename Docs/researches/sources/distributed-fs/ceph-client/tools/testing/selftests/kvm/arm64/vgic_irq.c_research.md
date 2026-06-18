<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/vgic_irq.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/vgic_irq.c

Purpose: this functional VGICv3 interrupt injection selftest validates userspace injection paths, priority/preemption behavior, active-state restoration, invalid intid handling, EOI split behavior, level versus edge interrupt behavior, and selected two-vCPU corner cases.

Important APIs, types, and functions: `struct test_args` carries IRQ count, EOI split, level sensitivity, routing and irqfd capabilities, and shared data. `enum kvm_inject_cmd` and `struct kvm_inject_args` encode guest-to-host injection requests over ucalls. Injection descriptions separate supported SGI/PPI/SPI targets for edge, level, and active-state operations. Guest handlers call `gic_get_and_ack_irq()`, `gic_irq_get_active()`, `gic_irq_get_pending()`, `gic_set_eoi()`, and optionally `gic_set_dir()`. Host handlers use `kvm_arm_irq_line()`, `kvm_irq_set_level_info()`, `kvm_gsi_routing_*()`, irqfd/eventfd, and direct ISPENDR/ISACTIVER device-register writes.

Control flow: `test_vgic()` creates a one-vCPU VM, maps guest args, sets up VGICv3 with the requested IRQ count, installs an IRQ handler matching EOI split and level mode, and loops on guest ucalls to perform injection commands. Guest code initializes GICv3, configures SPI level/edge state, enables all interrupts, sets priority mask, and runs injection, preemption, failure, and active-restore tests. Default `main()` runs four edge/level by EOI-split combinations plus three two-vCPU tests: asymmetric DIR, group enable gating, and timer PPI/SPI interaction.

State, persistence, and dependencies: interrupt state lives in the emulated GIC and guest globals `irq_handled` and `irqnr_received`. Host state includes eventfds and routing tables for irqfd tests. Dependencies include arm64 GIC helpers, selftest descriptor table setup, pthreads for two-vCPU runs, and `KVM_CAP_IRQ_ROUTING`/`KVM_CAP_IRQFD` capability checks.

Risks and edge cases: invalid interrupt IDs exercise inconsistent UAPI behavior across `KVM_IRQ_LINE`, level-info attributes, routing, irqfd, and register writes. Timer PPIs are excluded from userspace PPI injection tests. Preemption tests manually poll IAR with IRQs masked, so priority programming and AP1R state must be correct. Active-state restoration models live migration where interrupts are active but not deactivated. The two-vCPU asymmetric DIR test checks deactivation from a different vCPU.

Test signals: guest assertions verify exact intid delivery counts, active/pending state transitions, no spurious pending after handling, AP1R returning to zero, expected failure for bad intids, and successful two-vCPU completion. Host assertions verify expected ioctl failures and routing behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/vgic_irq.c -->
