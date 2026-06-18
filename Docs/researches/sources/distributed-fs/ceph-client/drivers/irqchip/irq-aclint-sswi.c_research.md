# sources/distributed-fs/ceph-client/drivers/irqchip/irq-aclint-sswi.c

Purpose: Implements RISC-V ACLINT S-mode software interrupt support as an IPI provider for compatible MIPS P8700, Nuclei UX900, and T-HEAD C900 variants.

Important APIs/types/functions: `sswi_ipi_virq`, per-CPU `sswi_cpu_regs`, `aclint_sswi_ipi_send()`, `aclint_sswi_ipi_handle()`, `aclint_sswi_parse_irq()`, `aclint_sswi_probe()`, CPU hotplug callbacks, generic/T-HEAD probe wrappers, and `IRQCHIP_DECLARE` entries.

Control flow: Probe maps the SSWI MMIO region, parses each interrupt context to associate parent hart IDs and hart indexes with per-CPU set/clear registers, creates a mapping for `RV_IRQ_SOFT` in the RISC-V INTC domain, creates muxed IPIs, chains the soft IRQ handler, installs CPU hotplug callbacks, and publishes the virtual IPI range.

State and persistence: Persistent state is the global SSWI virq and per-CPU MMIO register pointers. CPU online/offline paths enable or disable the percpu IRQ and clear pending software interrupts.

Dependencies/integration: Uses OF IRQ parsing, RISC-V hart ID/index helpers, SBI/vendor IDs, CSR operations, `ipi_mux`, percpu IRQs, CPU hotplug, and `riscv_ipi_set_virq_range()`.

Risks and test signals: Test multiple SSWI nodes, malformed context lists, non-soft parent IRQs, missing hart indexes, offline/online clear behavior, T-HEAD CLINTEE gating, and IPI delivery under SMP stress.
