<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mtk-cirq.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-mtk-cirq.c

### Purpose
`irq-mtk-cirq.c` implements the MediaTek CIRQ low-power interrupt recorder. It mirrors a configured external IRQ range from a parent controller and records edge interrupts during suspend so they can be flushed back on resume.

### Important APIs, Types, And Functions
`struct mtk_cirq_chip_data` stores MMIO base, external IRQ start/end, register-offset table, and domain. `mtk_cirq_domain_translate()` maps GIC SPI numbers in the configured range to local CIRQ hwirqs. `mtk_cirq_set_type()` programs polarity/sensitivity and delegates to the parent. `mtk_cirq_suspend()` acks safe recorded state and enables edge recording; `mtk_cirq_resume()` flushes then disables CIRQ.

### Control Flow
OF init finds the parent domain, maps registers, reads `mediatek,ext-irq-range`, selects v1/v2 register offsets, creates a hierarchy domain, and registers syscore PM. Allocation validates a single SPI in range, installs `mtk_cirq_chip`, and allocates the unchanged parent fwspec. Suspend walks every supported CIRQ line, checks parent pending/masked state to avoid losing interrupts that arrived after global IRQ disable, acks safe lines, then enables edge-only CIRQ recording. Resume sets `CIRQ_FLUSH`, then clears `CIRQ_EDGE` and `CIRQ_EN`.

### State, Persistence, And Dependencies
Persistent state is the singleton `cirq_data`, external range, offset table, hierarchy domain, and CIRQ control registers. It depends on parent irqchip state queries, OF bindings, syscore suspend ordering, and MediaTek CIRQ register layouts.

### Integration Points
The CIRQ domain is a transparent child of the GIC for supported external SPIs. It mainly matters in system suspend/resume paths.

### Risks
Only one global CIRQ instance is supported. `mtk_cirq_set_type()` defaults through unsupported types rather than returning `-EINVAL` before delegating, so parent rejection is important. Suspend correctness depends on parent pending/masked state support. Range translation rejects PPIs and out-of-range SPIs.

### Test Signals
Test both offset-table versions, valid and out-of-range SPIs, each trigger type, parent state query failures, interrupts arriving between `arch_suspend_disable_irqs()` and CIRQ suspend, resume flush delivery, and malformed DT range properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mtk-cirq.c -->
