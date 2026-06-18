<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic-sys-reg-v3.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic-sys-reg-v3.c

## Purpose
This file provides userspace access descriptors for GICv3 CPU interface system registers. It lets KVM device attributes and the generic sysreg one-reg helpers save, restore, and validate ICC_* and selected ICH_* virtual interrupt controller state.

## Important APIs, Types, And Functions
- `vgic_v3_get_sysreg_table()` returns the local `gic_v3_icc_reg_descs[]` table to sysreg table validation.
- `vgic_v3_has_cpu_sysregs_attr()` checks whether a VGIC sysreg device attribute names a visible descriptor.
- `vgic_v3_cpu_sysregs_uaccess()` maps a `kvm_device_attr` to a `kvm_one_reg` and delegates to generic sysreg get/set helpers.
- ICC VMCR-backed accessors include `set/get_gic_ctlr`, `set/get_gic_pmr`, `set/get_gic_bpr0`, `set/get_gic_bpr1`, `set/get_gic_grpen0`, and `set/get_gic_grpen1`.
- APR accessors include `set/get_gic_ap0r`, `set/get_gic_ap1r`, and shared `set_apr_reg()` / `get_apr_reg()`.
- EL2/ICH accessors include `set/get_gic_ich_reg`, `set/get_gic_ich_apr`, `set/get_gic_icc_sre`, and `set/get_gic_ich_vtr`.

## Control Flow
Userspace supplies a VGIC sysreg attribute encoding. `attr_to_id()` converts it to an ARM64 sysreg one-reg ID. Lookup uses the same `get_reg_by_id()` and descriptor visibility semantics as the main sysreg ABI. Reads and writes then call `kvm_sys_reg_get_user()` or `kvm_sys_reg_set_user()` against the VGIC descriptor table.

## State And Persistence Behavior
ICC_* user-visible state is stored in VGIC CPU state, mostly `struct vgic_vmcr` and `vcpu->arch.vgic_cpu.vgic_v3`. ICH_* EL2 state is stored in vCPU sysreg backing slots when nested virtualization exposes it. Host capability-derived values such as `ICH_VTR_EL2`, SRE, priority bits, ID bits, SEIS, and A3V are validated rather than blindly restored.

## Dependencies And Integration Points
The file depends on GICv3 register definitions, KVM host types, `asm/kvm_emulate.h`, `sys_regs.h`, and VGIC internals. It is called by VGIC device attribute handlers and checked by the main sysreg table initialization.

## Risks And Edge Cases
- Restored `ICC_CTLR_EL1` values must not claim more priority/ID bits or different SEIS/A3V support than host virtual hardware.
- APR indexes are limited by `vgic_v3_max_apr_idx()`; invalid indexes return `-EINVAL`.
- `ICC_SRE_EL1` restore requires SRE set; `ICC_SRE_EL2` and `ICH_VTR_EL2` are fixed values.
- EL2 descriptors are hidden unless nested virtualization is enabled for the vCPU.
- `get_gic_grpen1()` uses `FIELD_GET` rather than `FIELD_PREP` for the returned value, which is worth scrutinizing if behavior looks asymmetric.

## Test Signals
Migration/save-restore tests for VGICv3 CPU sysregs are direct coverage. Negative tests should try invalid priority bits, ID bits, APR indexes, disabled SRE, and hidden EL2 attributes without NV. Nested virtualization tests should verify ICH_* exposure and values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic-sys-reg-v3.c -->
