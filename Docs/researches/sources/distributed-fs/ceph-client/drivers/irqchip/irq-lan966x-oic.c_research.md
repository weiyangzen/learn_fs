<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-lan966x-oic.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-lan966x-oic.c

## Purpose
Implements the Microchip LAN966x outbound interrupt controller, mapping up to 86 source interrupts to one destination interrupt and exposing them through domain generic chips.

## Important APIs, Types, And Functions
`struct lan966x_oic_data` stores MMIO base and parent IRQ. `struct lan966x_oic_chip_regs` describes each 32-source register bank. Important functions include `lan966x_oic_probe()`, `lan966x_oic_chip_init()`, `lan966x_oic_irq_startup()`, `lan966x_oic_irq_shutdown()`, `lan966x_oic_irq_handler()`, and `lan966x_oic_irq_handler_domain()`.

## Control Flow
Probe maps registers, gets the parent IRQ, instantiates an irqdomain with destroyable generic chips, and its domain init chains the parent IRQ. Each generic-chip bank sets enable, disable, ack, map, and ident register offsets. Startup maps the source to destination 0, acknowledges sticky state, and unmasks. Shutdown masks and unmaps. The chained handler checks ident registers for banks 0, 32, and 64 and dispatches set bits.

## State And Persistence
Per-source mapping state lives in the destination map registers and is changed at IRQ startup/shutdown. Enable state is in atomic set/clear registers; sticky status is acknowledged through sticky registers. No explicit PM save/restore exists.

## Dependencies And Integration Points
It depends on platform devices, OF compatible `microchip,lan966x-oic`, `devm_irq_domain_instantiate()`, domain generic-chip init/exit callbacks, and chained IRQ support. Child consumers use the irqdomain as a normal interrupt controller.

## Risks
Only level-high flow type is supported. The third bank has only 22 valid IRQs although the generic chip handles 32-bit registers, so domain size and hwirq max must stay at 86. Startup/shutdown map updates must be serialized under the generic-chip lock.

## Test Signals
Test hwirqs across all three banks including 85, startup mapping, shutdown unmapping, sticky ACK, level-high type enforcement, parent chained dispatch with multiple banks pending, and devm domain teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-lan966x-oic.c -->
