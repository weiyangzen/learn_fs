# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/loongarch/processor.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/loongarch/processor.h

Purpose: LoongArch processor support header for KVM selftests. It defines register names for assembly, page-table/PTE bits, CSR IDs, exception register save layout, exception handler registration, vCPU setup, and local interrupt helpers.

Important APIs/types/functions: assembly register aliases (`a0`-`a7`, `t0`-`t8`, `s0`-`s8`), PTE bits (`_PAGE_VALID`, `_PAGE_PRESENT`, `_PAGE_WRITE`, `_PAGE_USER`), CSR constants (`LOONGARCH_CSR_CRMD`, `ESTAT`, `ERA`, `TCFG`, `TINTCLR`, etc.), `read_cpucfg`, `csr_read`, `csr_write`, `struct ex_regs`, `struct handlers`, `handle_tlb_refill`, `handle_exception`, `loongarch_vcpu_setup`, `vm_init_descriptor_tables`, `vm_install_exception_handler`, `cpu_relax`, `local_irq_enable`, and `local_irq_disable`.

Control flow and state: guest exception entry code saves general registers and CSR state into `struct ex_regs`, dispatches to handlers installed in a guest handler table, and returns according to architecture exception flow. VM setup initializes descriptor/exception tables and vCPU state. CSR helpers mutate virtual CPU state and interrupt enable bits.

Dependencies and integration: includes `ucall_common.h` for guest assertion/ucall behavior and integrates with `kvm_util.h` architecture hooks. Timer and PMU headers build on its CSR definitions.

Risks: save-area offsets are shared with assembly and must remain exact. CSR constants and PTE bit layouts must track LoongArch architecture and kernel headers. Interrupt enable/disable uses fixed temporary register constraints and can break if compiler/assembler expectations change.

Test signals: LoongArch exception, page-table, timer, PMU, and ucall tests exercise this header. Offset mismatches usually appear as bad exception reports or crashes very early in guest execution.
