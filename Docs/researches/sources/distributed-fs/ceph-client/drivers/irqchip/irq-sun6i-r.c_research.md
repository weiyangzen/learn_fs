# sources/distributed-fs/ceph-client/drivers/irqchip/irq-sun6i-r.c

## Purpose
Implements Allwinner R_INTC wakeup/NMI interrupt control for A31/H6-class SoCs as a hierarchical domain above the GIC. It handles NMI trigger conversion, wake-enabled direct and muxed IRQs during suspend/shutdown, and old two-cell NMI bindings.

## Important APIs, Types, And Functions
`struct sun6i_r_intc_variant` describes mux range and valid mux bitmap. Global bitmaps track wake-enabled top-level and mux interrupts. `sun6i_r_intc_nmi_chip` manages NMI-specific ack/eoi/type/state; `sun6i_r_intc_wakeup_chip` forwards regular IRQ operations to the parent while providing wake programming.

## Control Flow
Initialization parses the parent NMI GIC SPI, seeds wake bitmaps from variant data, maps MMIO, creates a zero-size hierarchy domain, registers syscore ops, clears NMI pending state, and enables normal NMI-only operation. Allocation accepts either old two-cell NMI specifiers or GIC-style three-cell specifiers, allocates the parent GIC IRQ, and installs the NMI or wakeup chip. Suspend writes wake bitmaps into IRQ and mux enable registers; resume restores normal NMI-only enables.

## State And Persistence
Persistent state consists of global base pointer, NMI hwirq, wake bitmaps, valid mux bitmap, and syscore PM hooks. NMI level ack may be deferred in `chip_data` until unmask/EOI for oneshot behavior.

## Dependencies And Integration Points
Depends on OF parent domain, GIC binding constants, hierarchical irqdomain APIs, syscore suspend/resume/shutdown, and compatible `allwinner,sun6i-a31-r-intc` or `allwinner,sun50i-h6-r-intc`.

## Risks
Wake capability is constrained by variant bitmaps; invalid wake requests return `-EPERM`. NMI parent specifier must be level-high GIC SPI. Deferred NMI ack logic must avoid losing oneshot-level wake interrupts. The domain accepts old and new bindings, so translation must remain compatible.

## Test Signals
Test NMI rising/falling/level modes, old two-cell binding, GIC-style child specifiers, suspend/shutdown wake from direct and muxed sources, and H6 full 128-bit mux coverage.
