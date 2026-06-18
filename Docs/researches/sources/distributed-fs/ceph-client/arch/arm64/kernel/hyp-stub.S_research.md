# sources/distributed-fs/ceph-client/arch/arm64/kernel/hyp-stub.S

Purpose: Supplies the minimal EL2 hypervisor stub vectors used before KVM installs its own hyp code and during EL2 finalization/resume.

Important symbols: `__hyp_stub_vectors`, `elx_sync`, `__finalise_el2`, `enter_vhe`, `__hyp_set_vectors`, `__hyp_reset_vectors`, and `finalise_el2`. The vector table handles selected HVC commands: set vectors, reset vectors, finalize EL2, read `ICH_VTR_EL2`, and soft restart.

Control flow: synchronous EL2/EL1 entries dispatch on x0 command. `__finalise_el2` checks MMU-off state and VHE capability/overrides, transfers EL1 system state to EL2, configures HCR for VHE, copies stack/percpu/FP/vector/MMU state, rewrites return state to EL2h, and enters `enter_vhe` in idmap text. `__hyp_set_vectors()` and `__hyp_reset_vectors()` are thin HVC wrappers.

Dependencies and integration: used by `head.S`, KVM hyp initialization, hibernation, kexec, and soft restart. It depends on EL2 setup macros, feature override storage, KVM ABI command constants, and idmapped execution for enabling VHE translations.

Risks and test signals: risks include finalizing EL2 with MMU still on, losing system register state when switching to VHE, wrong vector alignment, unexpected `kvm_call_hyp()` against the stub, and broken hibernate/kexec EL2 recovery. Test EL1 boot, EL2 nVHE boot, VHE finalization, KVM load/unload, kexec, hibernate, and protected/nVHE command-line overrides.
