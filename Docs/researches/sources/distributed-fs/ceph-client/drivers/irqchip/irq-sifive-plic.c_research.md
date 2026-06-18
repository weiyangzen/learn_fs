# sources/distributed-fs/ceph-client/drivers/irqchip/irq-sifive-plic.c

## Purpose
Implements the RISC-V Platform-Level Interrupt Controller for DT and ACPI systems. It maps external device interrupt sources to per-hart contexts, handles claim/complete cycles, supports edge-capable variants, saves state for suspend, and carries a workaround path for the UltraRISC CP100 claim-register erratum.

## Important APIs, Types, And Functions
`struct plic_priv` owns MMIO base, fwnode, irqdomain, local CPU mask, quirk bits, priority-save bitmap, interrupt count, and ACPI GSI metadata. Per-CPU `struct plic_handler` owns hart context base, enable bitmap registers, saved enable words, and a lock. Core operations include `plic_irq_enable()`, `plic_irq_disable()`, `plic_irq_eoi()`, `plic_set_affinity()`, `plic_irq_set_type()`, `plic_handle_irq()`, `plic_handle_irq_cp100()`, and `plic_probe()`.

## Control Flow
Probe maps registers, parses interrupt counts and contexts from DT or ACPI, creates one handler per usable `RV_IRQ_EXT` context, disables per-source enables, sets priorities, and creates a linear domain. Once all online CPUs have handlers, it maps the parent RISC-V external interrupt, installs the chained handler, registers CPU hotplug callbacks, and registers syscore suspend/resume. Runtime handling repeatedly reads the claim register, dispatches the domain hwirq, and completes in EOI. CP100 handling temporarily isolates one pending enabled interrupt before reading claim.

## State And Persistence
State is split between global setup flags, the parent IRQ, per-CPU handler data, enable-save arrays, and priority-save bitmap. Suspend saves priority and enable registers; resume restores them for all present handlers. Hardware priorities are hardwired to one when unmasked and zero when masked.

## Dependencies And Integration Points
Depends on RISC-V hart/INTC helpers, CPU hotplug, syscore PM, DT `riscv,ndev` and interrupt-parent data, ACPI RINTC/GSI helpers, and generic irqdomain allocation. Compatible strings include SiFive, generic RISC-V, Andes, T-Head, UltraRISC, and Allwinner early PLIC declarations.

## Risks
Context parsing is platform-critical: wrong hart/context IDs leave CPUs without interrupt handlers. Hardware IRQ 0 is reserved and must stay unmapped. Affinity changes write multiple context enable registers and rely on saved masks being coherent. CP100 isolation temporarily rewrites enables and must restore them exactly. M-mode/S-mode context ordering is acknowledged as fragile in comments.

## Test Signals
Boot DT and ACPI RISC-V systems, confirm the logged interrupt/context counts, verify per-CPU external interrupts, affinity changes, CPU hotplug, suspend/resume, and edge-versus-level triggering on quirked controllers. Erratum coverage should stress simultaneous pending interrupts on CP100-compatible hardware.
