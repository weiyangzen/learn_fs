# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/riscv/processor.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/riscv/processor.h

Purpose: RISC-V processor support header for KVM selftests. It defines KVM register ID builders, ISA/SBI extension checks, saved exception register layout, vector/exception handler APIs, page-table bit geometry, local interrupt helpers, and SATP mode discovery.

Important APIs/types/functions: `__kvm_reg_id`, `RISCV_CONFIG_REG`, `RISCV_CORE_REG`, `RISCV_GENERAL_CSR_REG`, `RISCV_TIMER_REG`, `RISCV_ISA_EXT_REG`, `RISCV_SBI_EXT_REG`, `__vcpu_has_ext`, `__vcpu_has_isa_ext`, `__vcpu_has_sbi_ext`, `struct pt_regs`, `vm_init_vector_tables`, `vcpu_init_vector_tables`, `vm_install_exception_handler`, `vm_install_interrupt_handler`, page-table masks/shifts, `local_irq_enable`, `local_irq_disable`, and `riscv64_get_satp_mode`.

Control flow and state: tests query or set vCPU registers using composed KVM one-reg IDs, initialize guest vector tables, install handlers, then execute guest code that reports traps through `struct pt_regs`. Page-table helpers use the defined masks to map guest memory. Interrupt enable/disable mutates supervisor status CSR bits.

Dependencies and integration: depends on Linux RISC-V CSR and KVM uAPI headers plus common `kvm_util.h`. It integrates with RISC-V timer, SBI, ucall, page-table, and extension capability tests.

Risks: register ID composition must match KVM RISC-V uAPI exactly. Page-table constants assume supported 64-bit RISC-V modes and may need updates for new address modes. Extension checks should be used before tests depend on optional ISA/SBI features.

Test signals: RISC-V exception tests, SATP/page-table tests, timer tests, and extension-gated SBI tests validate this header.
