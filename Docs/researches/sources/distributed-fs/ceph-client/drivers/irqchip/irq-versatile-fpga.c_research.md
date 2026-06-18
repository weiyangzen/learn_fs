# sources/distributed-fs/ceph-client/drivers/irqchip/irq-versatile-fpga.c

## Purpose
Supports ARM Versatile FPGA-based interrupt controllers, either as primary root controllers or cascaded secondary controllers. It registers valid interrupt masks, dispatches pending status, and supports the Versatile SIC pass-through register.

## Important APIs, Types, And Functions
`struct fpga_irq_data` stores MMIO base, valid mask, domain, and active IRQ count. Static `fpga_irq_devices` avoids allocation during early init. The irq chip masks by writing enable-clear, unmasks by writing enable-set, and prints the OF node name.

## Control Flow
OF init maps MMIO, reads `clear-mask` and `valid-mask`, clears IRQ/FIQ enables, maps an optional parent IRQ, and either installs a chained handler or the global root `fpga_handle_irq()`. Registration creates a linear domain sized by `fls(valid)`, pre-creates mappings for valid bits, and enables SIC pass-through bits for `arm,versatile-sic`.

## State And Persistence
State is static per-controller array entries and hardware enable registers. There is no PM state. Valid mask determines which hwirqs can map for the controller lifetime.

## Dependencies And Integration Points
Depends on early OF irqchip init, ARM exception handling, chained irq helpers, `CONFIG_VERSATILE_FPGA_IRQ_NR`, and compatible `arm,versatile-fpga-irq` or `arm,versatile-sic`.

## Risks
The static controller array can overflow if Kconfig is too small. Invalid-mask mistakes produce `-EPERM` mappings or missing child interrupts. Root-mode polling loops over all registered FPGA controllers until none is pending, so stale status can spin.

## Test Signals
Boot primary and cascaded configurations, confirm valid-mask mapping count, test mask/unmask, trigger simultaneous child bits, verify SIC pass-through behavior, and validate Kconfig controller-count coverage.
