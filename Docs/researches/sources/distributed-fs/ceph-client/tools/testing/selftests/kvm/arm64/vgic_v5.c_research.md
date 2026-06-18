<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/vgic_v5.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/vgic_v5.c

Purpose: this arm64 test probes KVM VGICv5 device creation and verifies userspace-driven software PPI delivery through the GICv5 current-domain instruction interface.

Important APIs, types, and functions: `struct vm_gic` wraps VM and GIC fd. Guest code enables GICv5 CPU interrupts with `gicv5_cpu_enable_interrupts()`, enables software PPI 3 via `SYS_ICC_PPI_ENABLER0_EL1`, and reports readiness with ucalls. The IRQ handler reads `CDIA` via `gicr_insn(CDIA)`, uses `GICV5_GICR_CDIA_VALID()` and `GICV5_GICR_CDIA_INTID`, acknowledges with `gsb_ack()`, drops/deactivates with `gic_insn(..., CDDI)` and `gic_insn(..., CDEOI)`, and completes after two interrupts. Host code creates `KVM_DEV_TYPE_ARM_VGIC_V5`, initializes it, reads `KVM_DEV_ARM_VGIC_USERSPACE_PPIS`, and toggles PPI level with `_kvm_irq_line()`.

Control flow: `main()` disables default VGIC setup, computes max physical size, probes GICv5 device support through trial create, skips if absent, and runs the PPI test. The test creates a one-vCPU VM manually, installs an IRQ handler, initializes the GIC, verifies SW_PPI is userspace-drivable, and loops on guest ucalls to raise/lower PPI level at readiness and EOI points.

State, persistence, and dependencies: all state is VM-local. Dependencies include `arm64/gic_v5.h`, KVM VGIC device creation, guest exception tables, `KVM_ARM_IRQ_TYPE_PPI`, and GICv5 sysreg/instruction definitions.

Risks and edge cases: GICv5 support is optional and new relative to GICv3. The test assumes SW_PPI 3 should always be userspace-drivable and that pending interrupts cause WFI to be skipped. It uses `__vcpu_run()` so run failures can be checked without immediate selftest assertion.

Test signals: unsupported device returns skip. Passing signals include device create errors behaving as expected, SW_PPI present in userspace PPI mask, two interrupt acknowledgements/deactivations from the guest, and final `KVM_RUN` success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/vgic_v5.c -->
