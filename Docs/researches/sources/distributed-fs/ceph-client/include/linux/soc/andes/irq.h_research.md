# sources/distributed-fs/ceph-client/include/linux/soc/andes/irq.h

Purpose: This Andes RISC-V header publishes SoC-specific interrupt and CSR numbers used by Andes PMU and supervisor local interrupt code.

Important APIs/types/functions: It defines `ANDES_RV_IRQ_PMOVI` as interrupt 18, `ANDES_RV_IRQ_LAST`, `ANDES_SLI_CAUSE_BASE`, and PMU-related CSRs `ANDES_CSR_SLIE`, `ANDES_CSR_SLIP`, and `ANDES_CSR_SCOUNTEROF`.

Control flow: There is no executable flow. Low-level irqchip or perf/PMU code uses these constants to map counter overflow and SLI causes to Linux IRQ handling.

State and persistence: State exists in CPU CSRs and interrupt pending/enable registers. The header only names those hardware resources.

Dependencies and integration: It is standalone and integrates with RISC-V arch code, Andes irqchip support, and performance counter overflow handling.

Risks and test signals: Wrong CSR or IRQ numbering breaks PMU overflow interrupts or local interrupt dispatch. Test perf counter overflow, IRQ domain mapping, and boot on Andes cores with SLI enabled.
