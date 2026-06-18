<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/irq-st.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/irq-st.h

## Purpose
This header defines STMicroelectronics syscfg interrupt selector constants and inversion flags for ST irqchip bindings.

## Important APIs, types, and functions
It exports `ST_IRQ_SYSCFG_EXT_0..2`, `ST_IRQ_SYSCFG_CTI_0..1`, `ST_IRQ_SYSCFG_PMU_0..1`, `ST_IRQ_SYSCFG_pl310_L2`, `ST_IRQ_SYSCFG_DISABLED`, and inversion flags `ST_IRQ_SYSCFG_EXT_1_INV`, `ST_IRQ_SYSCFG_EXT_2_INV`, `ST_IRQ_SYSCFG_EXT_3_INV`.

## Control flow
DTS nodes use the constants in syscfg interrupt routing properties. After preprocessing, the ST irqchip/syscfg code interprets the selector and optional inversion bits while configuring hardware routing.

## State and persistence
The header has no runtime state. Numeric selectors persist in compiled DTBs.

## Dependencies and integration points
It integrates with ST interrupt controller/syscfg drivers, external interrupt lines, CTI, PMU, and PL310 L2 interrupt routes.

## Risks and test signals
Risks include treating `ST_IRQ_SYSCFG_DISABLED` as a valid selector, confusing `EXT_3_INV` naming with the available `EXT_0..2` selectors, and incorrect polarity inversion. Test signals include DT validation, external interrupt edge tests, PMU/CTI interrupt delivery, and syscfg register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/irq-st.h -->
