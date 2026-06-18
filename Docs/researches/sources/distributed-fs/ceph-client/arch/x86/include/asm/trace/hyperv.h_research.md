# sources/distributed-fs/ceph-client/arch/x86/include/asm/trace/hyperv.h

Purpose: Hyper-V tracepoint definitions for TLB flush, nested guest mapping flush, and IPI send operations on x86 guests.

Important APIs/types/functions: `hyperv_mmu_flush_tlb_multi`, `hyperv_nested_flush_guest_mapping`, `hyperv_nested_flush_guest_mapping_range`, `hyperv_send_ipi_mask`, and `hyperv_send_ipi_one`.

Control flow: tracepoints are compiled only when `CONFIG_HYPERV` is enabled. TLB flush tracing records CPU mask weight plus `flush_tlb_info` memory range and mm pointer. Nested flush events record address space and return code. IPI events record target CPU count or single CPU plus vector.

State/persistence: no owned state; events snapshot arguments from Hyper-V MMU and interrupt calls. Return codes are captured for diagnosing hypercall failures.

Dependencies/integration: depends on `linux/tracepoint.h`, `cpumask`, `flush_tlb_info`, Hyper-V MMU and IPI implementation files, and the generated trace header path `asm/trace/hyperv`.

Risks/test signals: incorrect trace fields would mislead virtualization debugging but should not alter behavior. Test by enabling tracepoints on Hyper-V guests under TLB shootdown, nested virtualization mapping flush, and synthetic IPI traffic; verify CPU counts, ranges, vectors, and return codes match the caller paths.
