# sources/distributed-fs/ceph-client/arch/m68k/mac/via.c

## Purpose
Manages Macintosh VIA/RBV chips for interrupts, NuBus dispatch, RTC/ADB-related lines, L2 cache flush, and the VIA1 timer clocksource.

## APIs, Flow, And State
Public state includes `volatile __u8 *via1`, `via2`, `int rbv_present`, and exported `via_alt_mapping`. Internal state tracks RBV clear semantics, generic register offsets, `nubus_disabled`, and clock counters. `via_init()` maps VIA1/VIA2 or RBV based on `macintosh_config`, disables and clears interrupts, initializes timers, configures RTC lines, selects alternate Quadra interrupt mapping, initializes NuBus, and configures VIA2 PCR. Interrupt dispatchers read IFR/IER masks and call `generic_handle_irq()`. NuBus dispatch reads active-low slot lines and applies RBV SIER or VIA DirA masking. `via_irq_enable/disable()` manipulate VIA/RBV IER/SIER and manage the NuBus umbrella interrupt. `via_init_clock()` installs the timer IRQ and clocksource; `mac_read_clk()` derives continuous ticks from VIA T1 high byte and wrap flags.

## Dependencies And Integration
Depends on Mac model data, VIA/RBV register definitions, OSS/PSC presence, generic IRQ, clocksource, and legacy timer tick. It is the default IRQ and timing backend for non-OSS Macs and is also used by OSS for VIA1.

## Risks And Test Signals
NuBus masking on genuine VIA hardware is constrained by electrical behavior, so the `nubus_disabled` workaround must be preserved. Clocksource accuracy trades low overhead for high-byte-only reads. Test signals include timer ticks, monotonic clocksource behavior, VIA/RBV IRQ routing, NuBus cards, SCSI DRQ, floppy head select export, and IIci L2 cache flush behavior.
