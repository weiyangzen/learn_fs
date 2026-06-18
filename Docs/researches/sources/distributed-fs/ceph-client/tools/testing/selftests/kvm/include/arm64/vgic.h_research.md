# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/vgic.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/vgic.h

Purpose: arm64 VGIC helper declarations for KVM selftests. It packages VGICv3 setup, IRQ line manipulation, device attribute access, and ITS creation behind test-friendly APIs.

Important APIs/types/functions: `REDIST_REGION_ATTR_ADDR`, `kvm_supports_vgic_v3`, `__vgic_v3_setup`, `__vgic_v3_init`, `vgic_v3_setup`, `kvm_irq_set_level_info`, `_kvm_irq_set_level_info`, `kvm_arm_irq_line`, `_kvm_arm_irq_line`, `kvm_irq_write_ispendr`, `kvm_irq_write_isactiver`, `KVM_IRQCHIP_NUM_PINS`, and `vgic_its_setup`.

Control flow and state: tests create a VM, initialize the virtual interrupt controller, optionally configure redistributor regions and ITS state, then inject interrupts either through irq-line ioctls or direct VGIC device attributes. The underscore-prefixed helpers return errors for negative tests; the non-underscore forms assert success.

Dependencies and integration: depends on `<linux/kvm.h>` device attributes and `kvm_util.h` device/ioctl wrappers. It integrates with arm64 interrupt and timer selftests, and with common IRQFD or KVM interrupt routing helpers where arm64 support is needed.

Risks: GIC redistributor layout, reserved interrupt ranges, and ITS capabilities vary by kernel and host support. Tests must avoid assuming VGICv3 availability without `kvm_supports_vgic_v3()`.

Test signals: VGIC setup tests, timer interrupt tests, IRQ injection tests, and ITS-specific selftests validate the helper surface. Return-code helpers enable negative-path validation for unsupported attributes or invalid interrupt IDs.
