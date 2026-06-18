<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/apple-aic.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/apple-aic.h

## Purpose
This header defines Apple AIC interrupt specifier constants for IRQ/FIQ selection and built-in per-CPU sources such as timers and PMUs.

## Important APIs, types, and functions
It includes the generic `irq.h` flags and exports `AIC_IRQ`, `AIC_FIQ`, timer IDs `AIC_TMR_HV_PHYS`, `AIC_TMR_HV_VIRT`, `AIC_TMR_GUEST_PHYS`, `AIC_TMR_GUEST_VIRT`, and PMU IDs `AIC_CPU_PMU_E` and `AIC_CPU_PMU_P`.

## Control flow
Apple SoC DTS files use these constants in interrupt specifiers. They are preprocessed into integers and consumed by the Apple AIC irqchip driver when it creates Linux IRQ mappings.

## State and persistence
The header is stateless. Values become stable DT ABI in compiled Apple platform DTBs.

## Dependencies and integration points
It depends on generic interrupt trigger flags from `irq.h` and integrates with Apple Silicon AIC/AIC2 interrupt-controller nodes, ARM timer nodes, and PMU descriptions.

## Risks and test signals
Risks include confusing IRQ and FIQ cells, mapping PMU E/P cores incorrectly, or applying AIC constants to a different controller binding. Test signals include DTS schema checks, timer interrupts, PMU overflow interrupts, and boot logs from the Apple AIC driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/apple-aic.h -->
