# sources/distributed-fs/ceph-client/arch/riscv/kvm/isa.c

Purpose: This file maps KVM RISC-V ISA extension IDs to kernel RISC-V extension IDs and centralizes host availability plus guest enable/disable policy. It is the policy source used by one-reg ISA configuration and vCPU default ISA setup.

Important APIs/types/functions: `kvm_isa_ext_arr` maps `KVM_RISCV_ISA_EXT_*` IDs to `RISCV_ISA_EXT_*` IDs. `kvm_riscv_base2isa_ext` converts legacy single-letter base extension indices into KVM extension IDs. `__kvm_riscv_isa_check_host` validates an extension ID, handles host-side aliasing such as guest Smnpm backed by host Ssnpm, and returns the guest extension bit. `kvm_riscv_isa_enable_allowed` and `kvm_riscv_isa_disable_allowed` encode guest policy restrictions.

Control flow: Callers validate a KVM extension ID against array bounds, use nospec indexing, translate any special host availability case, then query host ISA availability. Enable policy rejects exposing H to guests, requires SSAIA for Sscofpmf interrupt filtering, requires hardware PTE young support for Svadu, and checks vector user control for V. Disable policy marks many architectural extensions as non-disableable because no architectural control exists, while allowing selected extensions where Smstateen or hardware ADUE controls can enforce behavior.

State and persistence: This file is mostly static data and pure policy. Guest ISA bitmaps persist in each vCPU and are modified by `vcpu_onereg.c`; this file decides which requested transitions are legal before the first vCPU run.

Dependencies and integration points: It depends on kernel cpufeature helpers, `asm/kvm_isa.h`, page-table young/dirty capability, and vector state control. It feeds vCPU creation, KVM_GET/SET_ONE_REG ISA extension handling, and configuration of HENVCFG/HSTATEEN in `vcpu_config.c`.

Risks and test signals: A wrong mapping or permissive disable decision can advertise an extension that KVM cannot virtualize or cannot hide. Tests should enumerate all `KVM_RISCV_ISA_EXT_MAX` IDs, compare GET_REG_LIST with host capabilities, verify pre-run enable/disable restrictions, confirm post-run changes are rejected by callers, and cover special cases for SSAIA/Sscofpmf, Svadu/Svade, Smstateen, V, and pointer masking.
