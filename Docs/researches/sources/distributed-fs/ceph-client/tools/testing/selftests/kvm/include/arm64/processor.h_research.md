# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/processor.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/arm64/processor.h

Purpose: arm64 processor support contract for KVM selftests. It defines KVM one-reg encodings for core and system registers, default MAIR/TCR/PTE constants, exception-vector metadata, MMIO accessors, interrupt masking helpers, SMCCC call wrappers, EL2-aware register aliasing, and vCPU setup hooks.

Important APIs/types/functions: `ARM64_CORE_REG`, `KVM_ARM64_SYS_REG`, `struct ex_regs`, `handler_fn`, `aarch64_vcpu_setup`, `aarch64_vcpu_add`, `vm_install_exception_handler`, `vm_install_sync_handler`, `virt_get_pte_hva_at_level`, `smccc_hvc`, `smccc_smc`, `wfi`, `test_wants_mte`, `test_disable_default_vgic`, `vm_supports_el2`, `ctxt_reg_alias`, and `kvm_get_default_vcpu_target`. Inline helpers expose `cpu_relax`, `isb`, `dsb`, `dmb`, `readl/writeq` families, IRQ/SERROR DAIF toggles, and current EL detection.

Control flow and state: the file is header-only except for external declarations. Tests create VMs/vCPUs through common `kvm_util.h`, then arm64 setup code initializes target features, descriptor tables, exception handlers, and page tables. `ctxt_reg_alias()` rewrites selected EL1 sysreg IDs to EL2 IDs when a vCPU has `KVM_ARM_VCPU_HAS_EL2`, so callers can use context-sensitive register access without duplicating EL checks.

Dependencies and integration: depends on Linux arm64 headers (`asm/sysreg.h`, `asm/esr.h`, `asm/brk-imm.h`), KVM uAPI IDs, `kvm_util.h`, and `ucall_common.h`. It integrates with arm64 KVM selftest libraries that implement VM creation, descriptor table setup, interrupt routing, and guest exception dispatch.

Risks: the register-alias switch intentionally build-fails for unsupported encodings, which is useful but brittle when new EL1/EL2 aliases are needed. MAIR/TCR/PTE constants must track architectural and kernel uAPI behavior, especially LPA2 address-bit packing. The raw MMIO helpers assume correct endian conversions and barrier placement; misuse can hide ordering bugs.

Test signals: selftests that install guest exception handlers, use VGIC/MMIO, exercise MTE, run EL2 guests, or perform SMCCC calls validate this header indirectly. Compile failures around missing sysreg names or KVM one-reg IDs are early signals of kernel/uapi drift.
