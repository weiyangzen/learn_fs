## sources/distributed-fs/ceph-client/arch/arm64/include/asm/el2_setup.h

Purpose: assembly-only macro library for initializing EL2 state before the kernel or KVM relies on it.

Important APIs/types/functions: exports macros `init_el2_hcr`, `init_el2_state`, `finalise_el2_state`, and many internal setup macros for SCTLR, HCRX, timers, debug/SPE/TRBE/BRBE, LOR, stage-2, GICv3/v5, HSTR, virtual CPU ID registers, CPTR, fine-grained traps, MPAM, GCS, SVE, and SME.

Control flow: early assembly probes ID registers, handles VHE-only behavior, disables traps, zeros stage-2 translation, enables timer/GIC access, configures debug ownership, and later finalizes feature-specific EL2 access based on overrides or sanitized values.

State and persistence: writes EL2 system registers such as HCR_EL2, SCTLR_EL2, HCRX_EL2, CNTHCTL_EL2, MDCR_EL2, VTTBR_EL2, ICC/ICH registers, CPTR_EL2, FGT registers, ZCR_EL2, SMCR_EL2, and MPAM/GCS state. These persist as CPU-local control state.

Dependencies and integration: used by early head/KVM assembly. Depends on KVM register definitions, sysreg encodings, cpufeature overrides, GIC definitions, and VHE/nVHE build modes.

Risks: EL2 setup bugs prevent boot, break KVM, expose traps to guests/host, or misconfigure security-sensitive features. Test signals are VHE and nVHE boots, pKVM/KVM selftests, nested virtualization probes, SVE/SME/GCS/MPAM boots, GICv3/v5 interrupt tests, and CPU hotplug through EL2 initialization.
