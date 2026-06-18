# sources/distributed-fs/ceph-client/drivers/irqchip/irq-bcm7120-l2.c

## Purpose
Implements Broadcom BCM7120/BCM3380-style Level 2 cascaded interrupt controllers with one or more status/enable word pairs and optional multiple parent IRQ map masks.

## Important APIs, Types, and Functions
`struct bcm7120_l2_intc_data` stores word count, mapped register bases, offsets, domain, wake/fwd masks, parent count, and per-parent L1 data. `bcm7120_l2_intc_probe()` is the common probe; variant iomap functions handle 7120 and 3380 layouts. Generic-chip suspend/resume callbacks restore masks.

## Control Flow
Probe counts parent IRQs, maps registers, parses forwarding and map masks, attaches a chained handler per parent, creates a generic-chip domain, sets each generic chip's register base and enable/status offsets, initializes the enable register with forwarded-mask defaults, and configures wake support if requested.

## State and Persistence
Persistent state includes per-parent `irq_map_mask[]`, `irq_fwd_mask[]`, generic-chip `mask_cache`, wake masks, and mapped register arrays. The handler intersects status with `mask_cache` and the parent-specific map mask before dispatch.

## Dependencies and Integration Points
Uses platform irqchip registration, OF property parsing (`brcm,int-fwd-mask`, `brcm,int-map-mask`, `brcm,irq-can-wake`), generic irqchip, and chained IRQ dispatch. It cascades below parent L1 or CPU interrupt lines.

## Risks and Test Signals
Risks include invalid map-mask dimensions, confusion between enable-as-mask semantics and generic-chip naming, forwarded lines exposed to Linux, and missing cleanup after chained handlers are installed. Test signals are correct per-parent demultiplexing, generic-chip mask cache restoration, wake propagation, and no interrupts from invalid/unmapped bits.
