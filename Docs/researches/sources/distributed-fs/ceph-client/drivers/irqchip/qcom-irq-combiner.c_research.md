# sources/distributed-fs/ceph-client/drivers/irqchip/qcom-irq-combiner.c

## Purpose
Implements an ACPI-only Qualcomm TCSR interrupt combiner. It ORs read-only status registers behind one parent interrupt and exposes individual child status bits as Linux IRQs with software-maintained enable masks.

## Important APIs, Types, And Functions
`struct combiner` stores the child domain, parent IRQ, total IRQ count, register count, and flexible array of `combiner_reg` entries. Each register stores an MMIO address and enabled bitmask. ACPI helpers count and map Generic Register resources from `_CRS`.

## Control Flow
Probe counts ACPI generic-register resources, allocates the combiner, maps each register, sums bit widths into `nirqs`, obtains the parent IRQ, creates a linear domain, and installs a chained handler. The handler reads each status register, ANDs with the software enabled mask, warns for unexpected disabled pending bits, and dispatches each enabled child bit.

## State And Persistence
Mutable state is only the per-register `enabled` bitmask; hardware status registers are read-only. There is no suspend/resume state. Device-managed allocation covers mappings and combiner storage.

## Dependencies And Integration Points
Depends on ACPI `_CRS` generic-register resources, platform IRQ acquisition, chained irqchip helpers, irqdomain translation for ACPI fwspecs, and HID `QCOM80B1`.

## Risks
Only ACPI fwspecs are accepted; DT is intentionally unsupported. Resource validation rejects non-memory, nonzero bit-offset, or wider-than-32-bit registers. Since masking is software-only, disabled hardware sources can still assert the parent and produce warnings. Edge trigger flags are rejected.

## Test Signals
Boot ACPI systems with QCOM80B1, validate register count/mapping, child IRQ translation, software mask/unmask behavior, warning path for disabled pending bits, and level-trigger dispatch for all declared register bits.
