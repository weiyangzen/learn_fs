<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/gic.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/gic.h

Purpose: this header defines the common arm64 GIC selftest interface and address layout used by guest code and VM setup helpers.

Important APIs, types, and functions: `enum gic_type` currently exposes `GIC_V3`. GPA/GVA constants place ITS, distributor, and redistributor regions at fixed identity-mapped guest addresses: `GITS_BASE_GPA`, `GICD_BASE_GPA`, and `GICR_BASE_GPA`. Interrupt ID constants define SGI, PPI, SPI ranges and `IAR_SPURIOUS`. Macros classify intids. Function declarations cover GIC init, IRQ enable/disable, acknowledge, EOI, DIR, EOI split, priority mask/priority, active/pending/config/group state, and LPI redistributor enablement.

Control flow: this file is declarations and macros only; implementation is in arm64 GIC helper sources. Downstream tests call these APIs from guest code after VGIC setup.

State, persistence, and dependencies: no direct state. Dependencies include `<asm/kvm.h>` for KVM VGIC sizes and selftest VM setup that maps the GIC MMIO regions at the declared addresses.

Risks and edge cases: fixed GIC base addresses must not collide with test memory. `MAX_SPI` is 1019 and `IAR_SPURIOUS` is 1023, leaving reserved IDs. LPI use requires separate ITS/GICv3 setup.

Test signals: used by VGIC IRQ and LPI tests for delivery, active/pending state, priorities, and LPI configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/gic.h -->
