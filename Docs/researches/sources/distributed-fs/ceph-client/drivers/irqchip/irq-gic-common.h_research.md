# sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-common.h

## Purpose
Declares shared ARM GIC helper APIs and the quirk descriptor structure used by GIC implementations.

## Important APIs, Types, and Functions
`struct gic_quirk` combines description, OF compatible/property selectors, IIDR mask/value selectors, and an init callback. The header declares `gic_configure_irq()`, `gic_dist_config()`, `gic_cpu_config()`, `gic_enable_quirks()`, and `gic_enable_of_quirks()`. It also defines redistributor flag bits for property-base flushing, preallocated tables, and non-shareable forcing.

## Control Flow
No executable flow lives here. It defines the contract for shared helper calls and quirk tables consumed by GIC source files.

## State and Persistence
No storage is defined. Redistributor flags are bit constants to be stored by consumers in their own state.

## Dependencies and Integration Points
Includes OF, irqdomain, MSI, and ARM GIC common headers. It is a compile-time integration point among ARM GIC drivers and platform-specific quirk implementations.

## Risks and Test Signals
Risks are interface drift and mismatched flag semantics across GIC versions. Test signals are successful builds of all GIC consumers and runtime quirk/redistributor behavior matching the consuming driver expectations.
