# sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-kvm-device.c

## Purpose
`vgic-kvm-device.c` is the KVM device API bridge for ARM VGIC models. It validates userspace configuration, exposes model-specific attribute groups, serializes migration register access, registers v2/v3/v5 device ops, and delegates actual register emulation to the MMIO and sysreg helpers.

## Important APIs, Types, And Functions
`vgic_check_iorange()` validates alignment, duplicate assignment, overflow, and IPA size limits. `kvm_set_legacy_vgic_v2_addr()` supports the legacy v2 address API. `kvm_vgic_addr()` handles distributor, CPU interface, redistributor, and redistributor-region address attributes. `vgic_set_common_attr()` and `vgic_get_common_attr()` implement shared address, IRQ-count, and control attributes. Model-specific accessors are `vgic_v2_attr_regs_access()`, `vgic_v3_attr_regs_access()`, and the limited v5 attribute handlers. The exported registrations are `kvm_arm_vgic_v2_ops`, `kvm_arm_vgic_v3_ops`, `kvm_arm_vgic_v5_ops`, and `kvm_register_vgic_device()`.

## Control Flow
Userspace creates a VGIC device, sets address and sizing attributes, then issues `KVM_DEV_ARM_VGIC_CTRL_INIT`. The common setter validates `KVM_DEV_ARM_VGIC_GRP_NR_IRQS` before VGIC initialization and delegates `CTRL_INIT` to `vgic_init()` under `config_lock`. Address writes take `slots_lock` first because v3 redistributor registration may touch the MMIO bus, then take `config_lock` around state mutation.

Register migration access parses CPU IDs or MPIDRs from `attr->attr`, stops all VCPUs using `kvm_trylock_all_vcpus()`, takes `config_lock`, verifies initialization rules, and delegates to `vgic_v2_dist_uaccess()`, `vgic_v2_cpuif_uaccess()`, `vgic_v3_dist_uaccess()`, `vgic_v3_redist_uaccess()`, or v3 CPU sysreg access. v3 allows a small pre-init read/write set for ID-like registers (`GICD_IIDR`, `GICD_TYPER2`) so userspace can discover and select features before final init.

## State And Persistence
The file mutates persistent VM configuration in `kvm->arch.vgic`: model, base addresses, redistributor regions, number of SPIs, maintenance interrupt PPI, implementation revision, and v5 userspace PPI exposure. Migration register access persists distributor, redistributor, CPU interface, level-info, and sysreg state through the common uaccess path. v2 register access may initialize the VGIC on demand, while v3 mostly requires prior initialization except for the pre-init ID registers.

## Dependencies And Integration Points
It depends on KVM device-core callbacks, user copy helpers, `kvm_get_vcpu_by_id()`, `kvm_mpidr_to_vcpu()`, all-vCPU locking, VGIC init/map helpers, MMIO uaccess functions from v2/v3 MMIO files, v3 CPU sysreg helpers, and v5 PPI state in `gicv5_vm`. It also registers the ITS device when the v3 VGIC device registration succeeds.

## Risks
The main risks are ABI regressions in error codes, lock ordering around `slots_lock` and `config_lock`, accepting address ranges that overlap or exceed IPA limits, permitting register writes after initialization when the ABI forbids it, and partial v5 support confusing userspace because most legacy address/sysreg attributes intentionally return `-ENXIO`. The save-pending-tables control path must hold KVM and all-vCPU locks because it writes guest memory and samples LPI state.

## Test Signals
Exercise KVM device `has_attr`, `set_attr`, and `get_attr` for every supported group; invalid alignment and out-of-range address tests; v3 redistributor region indexing and count validation; v2/v3 migration register round trips; pre-init v3 IIDR/TYPER2 access; maintenance IRQ PPI validation; v5 userspace PPI readback; and concurrent access tests that confirm running VCPUs cause `-EBUSY`.
