# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/vgic.c

## Purpose
This host-side arm64 helper creates and manages VGICv3 and ITS KVM devices for selftest VMs, maps their MMIO regions into the guest, and offers interrupt injection/state helpers.

## Important APIs, Types, and Functions
`kvm_supports_vgic_v3()` probes device creation. `__vgic_v3_setup()` creates a VGICv3 device, sets IRQ count, distributor address, redistributor region, and guest mappings. `__vgic_v3_init()` initializes the device. `vgic_v3_setup()` validates vCPU count before setup. IRQ helpers include `_kvm_irq_set_level_info()`, `kvm_arm_irq_line()`, `kvm_irq_write_ispendr()`, `kvm_irq_write_isactiver()`, and `vgic_its_setup()`.

## Control Flow
The default VM hook in arm64 `processor.c` calls setup after VM creation and initialization after all vCPUs are created. Explicit callers can use `vgic_v3_setup()` to create and initialize in one path. ITS setup creates a separate device, assigns its GPA, initializes it, and maps the ITS window.

## State, Dependencies, and Integration
State lives in KVM device file descriptors and guest MMIO mappings. The helpers depend on KVM device attributes, ARM VGIC constants, `virt_map()`, and the GIC register layout expected by guest-side `gic_v3.c`.

## Risks and Test Signals
Private interrupt poking is limited to vCPU 0. Incorrect setup order, mismatched vCPU counts, or unsupported VGIC/ITS devices lead to assertions, negative setup returns, or failed interrupt delivery.
