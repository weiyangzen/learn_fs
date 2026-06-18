# sources/distributed-fs/ceph-client/arch/arm/kernel/hyp-stub.S

Purpose: installs a minimal ARMv7 HYP-mode stub during early boot or zImage transitions so the kernel can leave CPUs in a known SVC/HYP relationship and service a tiny set of HVC requests.

Important APIs/types/functions: assembly entry points are `__hyp_stub_install`, `__hyp_stub_install_secondary`, `__hyp_set_vectors`, `__hyp_soft_restart`, and vector table `__hyp_stub_vectors`. Writable `__boot_cpu_mode` records the primary boot mode and mismatch bit for later `hyp_mode_check`.

Control flow: primary install stores CPSR mode, secondaries compare their mode against it, abort on mismatch, and only install vectors when currently in HYP mode. Installation programs HVBAR, clears HCR/HCPTR/HSTR traps, configures HSCTLR, mirrors MIDR/MPIDR into virtual registers, opens physical timer access, and optionally enables GICv3 system registers. Trap handling accepts vector updates for zImage, soft restart jumps, and returns `HVC_STUB_ERR` otherwise.

State and persistence: persistent state is the boot-mode word and EL2/HYP register configuration. The stub vectors persist until replaced by KVM or firmware paths.

Dependencies and integration: called from early head/resume paths with MMU/cache off; `setup.c` reads the boot-mode state through virtualization helpers; reboot and suspend paths can invoke soft restart through HVC.

Risks: CPU mode mismatches indicate broken firmware and disable virtualization assumptions; these routines are not ABI-compliant and require exact register/boot-state contracts. Test signals include boot logs from `hyp_mode_check`, secondary CPU bring-up under HYP, KVM availability, and soft restart behavior.
