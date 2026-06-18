# sources/distributed-fs/ceph-client/drivers/mfd/qcom-pm8xxx.c

## Purpose
`qcom-pm8xxx.c` is the core/IRQ controller for older Qualcomm PM8xxx SSBI PMICs. It creates an SSBI-backed regmap, exposes a linear IRQ domain, handles PM8058/PM8921-style and PM8821-style interrupt topologies, and populates child devices.

## Important APIs, Types, And Functions
`struct pm_irq_chip` holds regmap, spinlock, IRQ domain, topology counts, variant data, and per-hwirq config bytes. `pm8xxx_irq_handler()` walks root/master/block status registers. `pm8821_irq_handler()` handles PM8821's two-master layout. IRQ chip callbacks include mask/ack, unmask, set_type, and get line-level state. `pm8xxx_probe()` initializes regmap, revision logging, IRQ domain, physical IRQ, wake, and children.

## Control Flow
Probe selects `pm_irq_data` by compatible, gets the parent IRQ, initializes SSBI regmap using `ssbi_reg_read/write`, reads two hardware revision registers, allocates `pm_irq_chip`, creates a fwnode-backed linear IRQ domain, requests the physical IRQ with the variant handler, marks it wake-capable, and calls `of_platform_populate()`. Runtime IRQ handling reads root status, selects blocks, reads bit status, and dispatches nested hwirqs through `generic_handle_domain_irq()`.

## State And Persistence
State includes the regmap, spinlock, IRQ domain, and cached per-IRQ configuration. Hardware interrupt configuration is persistent until rewritten. Child devices are DT-populated under the PMIC node.

## Dependencies And Integration Points
It depends on SSBI, regmap custom bus callbacks, IRQ domains, chained/nested IRQ infrastructure, OF population, compatibles `qcom,pm8058`, `qcom,pm8821`, and `qcom,pm8921`, plus child nodes that consume two-cell IRQ specifiers.

## Risks
The PM8821 unmask path uses `regmap_update_bits(..., BIT(irq_bit), ~BIT(irq_bit))`, which relies on regmap masking semantics and is easy to misread. IRQ type programming only exists for PM8xxx, not PM8821. Block/master arithmetic differs by variant. Error paths after IRQ-domain creation rely on remove or explicit cleanup. Spinlocked SSBI block select and status/config reads must stay serialized.

## Test Signals
Validate revision reads, interrupt dispatch for every master/block, two-cell IRQ translation, edge/level type programming, line-level reads, PM8821-specific topology, wake from PMIC IRQ, child node population, and IRQ-domain removal on probe failure/remove.
