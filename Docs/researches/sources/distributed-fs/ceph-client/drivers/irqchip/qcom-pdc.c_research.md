# sources/distributed-fs/ceph-client/drivers/irqchip/qcom-pdc.c

## Purpose
Implements Qualcomm Power Domain Controller wakeup interrupts as a hierarchy above the GIC. It maps GPIO/PDC wake pins to parent GIC SPIs, controls PDC enable bits, converts polarity/edge types for the GIC, and handles version- and X1E-specific register layouts.

## Important APIs, Types, And Functions
`struct pdc_pin_region` maps PDC pin ranges to parent hwirq ranges. Global state stores PDC MMIO bases, region table, version, and X1E quirk flag. `qcom_pdc_gic_set_type()` programs PDC type bits and converts low/falling/both to parent-supported high/rising. `pdc_setup_pin_mapping()` parses `qcom,pdc-ranges` and disables all mapped PDC interrupts.

## Control Flow
Platform probe maps the current PDC region and, on X1E, the previous DRV region needed for an enable-bank write workaround. It reads PDC version, finds the parent domain, parses pin mappings, creates a wakeup hierarchy domain, and marks it `DOMAIN_BUS_WAKEUP`. Allocation translates two-cell child specifiers, handles `GPIO_NO_WAKE_IRQ` disconnects, installs the PDC chip, finds the pin region, normalizes parent trigger type, and allocates the parent GIC IRQ.

## State And Persistence
State is global because the PDC is treated as a singleton: MMIO bases, region table, version, lock, and quirk. Hardware state is IRQ enable banks or per-IRQ config enable bits plus type bits. There is no explicit PM cache; wake behavior is represented by irqchip flags and the wakeup domain token.

## Dependencies And Integration Points
Depends on OF platform irqchip probing, GIC parent domain, Qualcomm GPIO wake constants, raw spinlock protection, `qcom,pdc-ranges`, compatible `qcom,pdc`, and special compatible `qcom,x1e80100-pdc`.

## Risks
Pin-region mappings are safety-critical; missing regions disconnect hierarchy allocation. Hardware versions before and after 3.2 use different enable layouts. X1E remaps enable-bank writes across DRV regions, and incorrect bank shifting can enable the wrong wake line. Type changes may generate phantom interrupts, so pending parent state is cleared after reconfiguration.

## Test Signals
Validate old and new PDC versions, X1E quirk bank remapping, GPIO wake/no-wake allocations, all trigger types, suspend wake from PDC lines, `qcom,pdc-ranges` parsing failures, and phantom interrupt clearing after type changes.
