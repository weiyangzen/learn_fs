<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/smp.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/smp.h

Purpose: Declares RISC-V SMP CPU bring-up, IPI, hart ID, and remote operation interfaces.

Important APIs/types/functions: Key items include `cpuid_to_hartid_map()`, `riscv_hartid_to_cpuid()`, `arch_send_call_function_ipi_mask()`, `arch_send_call_function_single_ipi()`, `handle_IPI()`, `smp_callin()`, `riscv_ipi_set_virq_range()`, and SMP/non-SMP fallbacks.

Control flow: SMP code maps logical CPUs to hart IDs, sends IPIs through selected backends, and handles call-function/reschedule events; UP builds collapse to local-only helpers.

State and persistence: Persistent state includes hart ID mappings, possible CPU masks, and IPI virq allocation.

Dependencies and integration points: Integrates with SBI IPI, irqchip backends, CPU hotplug, scheduler, TLB shootdown, and ACPI/DT CPU discovery.

Risks: Bad hart mapping or IPI routing can hang secondary CPUs or miss reschedules/TLB flushes.

Test signals: SMP boot, CPU hotplug, scheduler IPI stress, TLB shootdown tests, ACPI and DT platforms, and UP build coverage.

Source read size: 117 lines, 2553 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/smp.h -->
