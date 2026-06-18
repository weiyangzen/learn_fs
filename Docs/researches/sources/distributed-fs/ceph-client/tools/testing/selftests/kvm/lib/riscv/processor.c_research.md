# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/riscv/processor.c

## Purpose
This is the RISC-V processor backend for KVM selftests. It implements page-table construction, SATP setup, vCPU initialization, register dumps, exception routing, SBI calls, guest-mode probing, and default IRQ-chip detection.

## Important APIs, Types, and Functions
Important helpers include `__vcpu_has_ext()`, `virt_arch_pgd_alloc()`, `virt_arch_pg_map()`, `addr_arch_gva2gpa()`, `riscv_vcpu_mmu_setup()`, `vm_arch_vcpu_add()`, `vcpu_args_set()`, `route_exception()`, `vm_init_vector_tables()`, `vm_install_exception_handler()`, `vm_install_interrupt_handler()`, `sbi_ecall()`, `guest_sbi_probe_extension()`, `get_host_sbi_spec_version()`, and `riscv64_get_satp_mode()`.

## Control Flow
Mapping starts at the top-level page table and lazily allocates child tables until the leaf, where it writes a valid permission PTE. VCPU setup allocates stack, creates the vCPU, programs SATP based on selected mode and KVM-supported max SATP mode, sets MP state runnable, copies host `gp`, sets stack and `sscratch`, and installs a default unexpected-trap vector. Custom vector tables can later route through `handlers.S`.

## State, Dependencies, and Integration
Static `exception_handlers` stores the guest handler table GVA. The file depends on RISC-V KVM register namespaces, SBI extension IDs, generic `guest_modes`, ucall, and KVM capability probing.

## Risks and Test Signals
Risks include unsupported SATP modes, assumptions about 4K page tables, default unexpected trap behavior via SBI, and register ID mismatches. Signals are register dumps, `UCALL_UNHANDLED`, SBI exits, and KVM ioctl assertions.
