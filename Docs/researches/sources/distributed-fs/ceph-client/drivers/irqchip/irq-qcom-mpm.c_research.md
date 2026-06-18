<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-qcom-mpm.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-qcom-mpm.c

## Purpose
`irq-qcom-mpm.c` implements the Qualcomm MSM Power Manager wakeup interrupt controller. It programs a shared vMPM register image used by the application processor while awake and handed to RPM firmware during deep power collapse.

## Important APIs, Types, and Functions
`struct qcom_mpm_priv` stores the vMPM base, lock, mailbox client/channel, MPM-to-GIC pin map, register stride, wakeup domain, and generic PM domain. Register helpers `qcom_mpm_read()` and `qcom_mpm_write()` access enable, edge, polarity, and status banks. IRQ operations are `qcom_mpm_mask()`, `qcom_mpm_unmask()`, and `qcom_mpm_set_type()`. Allocation is handled by `qcom_mpm_alloc()`, wake status by `qcom_mpm_handler()`, power-collapse notification by `mpm_pd_power_off()`, and platform setup by `qcom_mpm_probe()`.

## Control Flow
Probe reads `qcom,mpm-pin-count` and `qcom,mpm-pin-map`, maps either RPM message RAM or local MMIO, clears all MPM register banks, initializes a GENPD, acquires a mailbox channel, creates a wakeup irqdomain above the parent GIC domain, and requests the MPM wake IRQ. Allocation translates a two-cell MPM pin, handles `GPIO_NO_WAKE_IRQ` disconnection, installs the MPM chip, maps the pin to its GIC hwirq, normalizes parent trigger type to high/rising, and allocates the parent IRQ. On deep sleep entry, status registers are cleared and RPM is notified by mailbox. On wake, the handler scans enabled pending MPM pins and marks non-level mapped IRQs pending.

## State and Persistence
vMPM register contents are the meaningful state: enable bits, edge selections, polarity bits, and status bits. A raw spinlock serializes register updates. The GENPD power-off path transfers state to RPM; there is no filesystem persistence.

## Dependencies and Integration Points
The driver depends on mailbox/RPM firmware, generic PM domains, OF platform irqchip matching, IRQ wakeup domains, parent GIC hierarchy, and Qualcomm `GPIO_NO_WAKE_IRQ` semantics.

## Risks and Edge Cases
Duplicate GIC hwirq map entries are warned and skipped, which can leave an MPM pin disconnected. `qcom_mpm_handler()` assumes `irq_resolve_mapping()` returns a descriptor for pending pins; malformed maps can expose null descriptor risk. Missing MSI/message RAM mailbox prevents deep-sleep programming.

## Test Signals
Validate suspend/resume wake from each mapped pin, parent GIC type normalization, `GPIO_NO_WAKE_IRQ` paths, duplicate map handling, RPM mailbox notification on GENPD power-off, and status-to-pending replay for edge-triggered interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-qcom-mpm.c -->
