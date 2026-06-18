# sources/distributed-fs/ceph-client/drivers/irqchip/irq-sg2042-msi.c

## Purpose
Implements the Sophgo SG2042/SG2044 MSI parent/middle irq domain used to terminate PCI MSI/MSI-X writes into SoC general-purpose interrupt registers and forward them to the RISC-V PLIC parent domain. It is a platform irqchip driver, not a Ceph-specific component.

## Important APIs, Types, And Functions
`struct sg204x_msi_chipdata` stores the clear register, doorbell physical address, first parent IRQ, vector count, interrupt type, allocation bitmap, mutex, and SoC-specific `sg204x_msi_chip_info`. The middle-domain callbacks are `sg204x_msi_middle_domain_alloc()` and `sg204x_msi_middle_domain_free()`, backed by bitmap allocation helpers. SG2042 and SG2044 have separate `irq_chip` instances and MSI parent ops because SG2044 supports multi-MSI/MSI-X and uses per-vector doorbell/clear semantics.

## Control Flow
Probe reads match data, maps the `clr` MMIO resource, records the `doorbell` resource start, parses `msi-ranges` to find the PLIC fwnode, base IRQ, type, and vector count, allocates the vector bitmap, then creates a parent MSI irq domain. MSI allocation finds a free contiguous bitmap region, allocates one parent PLIC IRQ per vector, installs the middle chip, and composes MSI messages using either SG2042 bit data or SG2044 doorbell-bank plus bit-index data. Ack clears the controller latch and then acks the parent.

## State And Persistence
Mutable state is the in-memory MSI allocation bitmap protected by `msi_map_lock`; hardware state is the clear register write, parent PLIC enable/type state, and MSI doorbell target programmed into PCI devices. Managed allocation keeps chipdata and bitmap alive for device lifetime.

## Dependencies And Integration Points
Depends on generic MSI parent-domain support, `irq-msi-lib`, Linux irqdomain hierarchy APIs, platform resource parsing, firmware properties, and the PLIC parent domain. Integration is through `sophgo,sg2042-msi` and `sophgo,sg2044-msi` compatible strings plus `msi-ranges`, `clr`, and `doorbell` resources.

## Risks
`1 << d->hwirq` limits SG2042-style operations to word-sized vector positions and depends on DT-provided vector count matching hardware. `msi-ranges` parsing is subtle because the code reads separate base and count reference entries. Allocation failure cleanup must release both parent IRQs and bitmap regions. Incorrect supported MSI flags can make PCI endpoints request unsupported MSI-X or multi-MSI modes.

## Test Signals
Build with the Sophgo MSI driver enabled, boot on SG2042 and SG2044 DTs, verify the MSI parent domain registers, and exercise PCI endpoints with single MSI, multi-MSI, and MSI-X where supported. Useful failures include PLIC parent lookup errors, exhausted vector bitmap paths, correct interrupt ack/clear behavior, and endpoint stress with repeated enable/disable cycles.
