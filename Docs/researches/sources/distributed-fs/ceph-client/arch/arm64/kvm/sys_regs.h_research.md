<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/sys_regs.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/sys_regs.h

## Purpose
This private KVM arm64 header defines the common data model and lookup helpers for system register emulation. It is shared by the main sysreg implementation and smaller integrations such as VGIC system register userspace access.

## Important APIs, Types, And Functions
- `struct sys_reg_params` carries decoded Op0/Op1/CRn/CRm/Op2, the transferred value, and access direction.
- `struct sys_reg_desc` describes one trapped or userspace-visible register: name, AArch32 mapping, encoding, trap access callback, reset callback, backing `enum vcpu_sysreg`, value/writable mask, custom get/set callbacks, and visibility callback.
- Encoding helpers include `reg_to_encoding()`, `encoding_to_params()`, `esr_sys64_to_params()`, and `esr_cp1x_32_to_params()`.
- `in_feat_id_space()` identifies the AArch64 feature-ID encoding space.
- Visibility flags `REG_HIDDEN`, `REG_RAZ`, and `REG_USER_WI` distinguish hidden, read-as-zero, and userspace-write-ignore behavior.
- Inline helpers include `print_sys_reg_msg()`, `print_sys_reg_instr()`, `ignore_write()`, `read_zero()`, `reset_unknown()`, `reset_val()`, `sysreg_visibility()`, `sysreg_hidden()`, `sysreg_visible_as_raz()`, `sysreg_user_write_ignore()`, `cmp_sys_reg()`, `match_sys_reg()`, and `find_reg()`.
- Exported declarations include `get_reg_by_id()`, `kvm_arm_sys_reg_get_reg()`, `kvm_arm_sys_reg_set_reg()`, generic sysreg get/set helpers, `triage_sysreg_trap()`, and `kvm_finalize_sys_regs()`.
- Descriptor initializer macros include `AA32()`, `Op0()`, `Op1()`, `CRn()`, `CRm()`, `Op2()`, `SYS_DESC()`, and `CP15_SYS_DESC()`.

## Control Flow
Callers decode ESR or KVM register IDs into `sys_reg_params`, then use `find_reg()` over a sorted descriptor table. The comparator uses a packed sysreg encoding and inline binary search, so the descriptor arrays must be sorted and unique. Access handlers and userspace accessors then use the descriptor’s callback fields and visibility flags to choose emulation behavior.

## State And Persistence Behavior
The header itself owns no persistent state. It defines how descriptors point at persistent vCPU or VM state through `.reg`, `.reset`, `.get_user`, `.set_user`, `.val`, and `.visibility`. The reset helpers write into `vcpu->arch` sysreg storage and deliberately use a recognizable poison-like value for architecturally unknown resets.

## Dependencies And Integration Points
It depends on Linux `bsearch` and arm64/KVM types supplied by included translation units. It is a contract between sysreg trap dispatch, VGIC sysreg user attributes, nested virtualization trap triage, debugfs, and KVM one-reg UAPI code.

## Risks And Edge Cases
- The comparator calls `BUG_ON(i1 == i2)` and assumes valid descriptor inputs.
- Tables must be sorted by encoding for `find_reg()` to work.
- `reset_unknown()` and `reset_val()` require a valid nonzero `.reg` index below `NR_SYS_REGS`.
- Visibility flags have distinct guest and userspace semantics; mixing `REG_HIDDEN`, `REG_RAZ`, and `REG_USER_WI` can change migration ABI.

## Test Signals
- Table validation during KVM init catches ordering and missing reset callbacks.
- One-reg enumeration and get/set tests verify descriptor lookup.
- Negative tests for hidden, RAZ, and userspace write-ignore registers validate visibility semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/sys_regs.h -->
