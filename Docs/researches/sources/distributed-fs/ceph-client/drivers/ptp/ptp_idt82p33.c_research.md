# sources/distributed-fs/ceph-client/drivers/ptp/ptp_idt82p33.c Research

## Purpose
`ptp_idt82p33.c` is the Renesas/IDT 82P33xxx PHC driver. It loads firmware, exposes selected PLLs as PTP clocks, implements time/frequency/phase adjustment, supports 1-PPS output enable, and polls for external timestamp events.

## Important APIs, Types, And Functions
Important helpers include regmap wrappers, ToD byte-array conversions, DPLL mode/trigger programming, external timestamp arm/check flows, `_idt82p33_gettime()`, `_idt82p33_settime()`, immediate and internally triggered adjtime paths, double-DCO small adjustment helpers, overhead measurement helpers, channel/caps initialization, firmware parsing, and `idt82p33_probe()/remove()`. PTP ops are `idt82p33_adjwritephase()`, `idt82p33_adjfine()`, `idt82p33_adjtime()`, `idt82p33_gettime()`, `idt82p33_settime()`, `idt82p33_enable()`, and `idt82p33_work_handler()`.

## Control Flow
Probe initializes defaults, cold-resets the chip, loads firmware if available, soft-resets, then enables each PLL selected by firmware/default `pll_mask`. Enabling a channel initializes register addresses, caps and pins, registers the PTP clock, puts the DPLL in DCO mode, measures ToD write overhead, zeroes the ToD, and enables ToD sync. Gettime temporarily disables EXTTS polling, triggers a ToD status read, reads the timestamp, and re-arms EXTTS as needed. Settime writes a triggered ToD configuration. Adjtime uses double-DCO for deltas below `phase_snap_threshold`; otherwise it prefers an internal 1-PPS-triggered write and may fall back to immediate write for larger positive deltas. EXTTS enable maps configured pins to hardware triggers and starts a 95 ms delayed polling loop.

## State And Persistence
Device state tracks PLL mask, output masks, delayed EXTTS work, event-channel routing, overhead timing, and one channel per possible PHC. Channel state includes PLL register addresses, current frequency, double-DCO state, output mask, trigger state, and delayed adjtime workaround work. Hardware state includes loaded firmware, DPLL modes, ToD counters, output squelch, and trigger selection.

## Dependencies And Integration Points
The driver depends on RSMU MFD parent data, regmap, firmware loader (`idt82p33xxx.bin` or module override), PTP core, delayed work, and IDT 82P33 register definitions. Userspace reaches it through `/dev/ptpN`, pin config, EXTTS, PEROUT, and clock adjustment ioctls.

## Risks
Firmware parsing drives PLL/output masks and skips some page offsets; malformed firmware can disable all PHCs or mis-map outputs. Polling-based EXTTS can miss events or race with gettime, which temporarily disables/re-arms triggers. The double-DCO worker suppresses adjfine while active and returns `-EBUSY` for adjtime. There is a suspicious loop in `idt82p33_measure_tod_write_9_byte_overhead()` that uses `i` instead of `j` for register offset/buffer index, worth targeted review.

## Test Signals
Test cold/soft reset and firmware load paths, default masks when firmware is missing, both PLL registrations, ToD overhead measurement, get/set/adjtime thresholds, double-DCO scheduling and restoration, adjphase range and register encoding, perout 1-PPS validation, EXTTS pin mapping/polling/single-shot behavior, and remove canceling delayed work before clock teardown.
