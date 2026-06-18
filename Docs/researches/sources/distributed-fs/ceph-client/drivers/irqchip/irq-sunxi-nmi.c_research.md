# sources/distributed-fs/ceph-client/drivers/irqchip/irq-sunxi-nmi.c

## Purpose
Implements standalone Allwinner NMI controllers for several SoC generations. It exposes a single child interrupt and configures controller-specific control, pending, and enable offsets using generic irq chips.

## Important APIs, Types, And Functions
`struct sunxi_sc_nmi_data` supplies register offsets and optional enable value. The generic chip has separate level and edge chip types. `sunxi_sc_nmi_set_type()` converts Linux trigger flags to hardware source-type values and switches between level and edge handlers.

## Control Flow
Initialization creates a one-IRQ domain, allocates two generic chip types, maps the parent IRQ and MMIO resource, programs level and edge chip callbacks/register offsets, disables the NMI, clears pending state, then installs a chained handler that always dispatches child hwirq 0.

## State And Persistence
State lives in generic irq chip register and mask caches plus MMIO state. There is no custom suspend/resume storage. Hardware source type, mask, and pending registers persist while powered.

## Dependencies And Integration Points
Depends on OF early irqchip init, generic irq chips, chained IRQ helpers, and compatible strings for sun6i A31, sun7i A20, sun9i A80, and sun55i A523 NMI blocks.

## Risks
Register offset ordering differs by generation, and sun55i uses a nonzero enable disable value. Unsupported mixed trigger modes return `-EBADR`. Since only one child hwirq exists, parent mapping failures make the entire controller unusable.

## Test Signals
Validate each compatible's offsets, single child IRQ mapping, all supported trigger types, pending clear, enable/disable polarity, and chained dispatch under repeated NMI assertion.
