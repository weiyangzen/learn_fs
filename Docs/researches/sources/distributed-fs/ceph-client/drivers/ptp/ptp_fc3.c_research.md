# sources/distributed-fs/ceph-client/drivers/ptp/ptp_fc3.c Research

## Purpose
`ptp_fc3.c` is the Renesas/IDT FemtoClock3 Wireless PHC driver. It loads register firmware, calibrates timing hardware, maintains a software timecounter over a hardware sub-sync counter, supports frequency/phase adjustments, and reports external phase-offset measurements.

## Important APIs, Types, And Functions
Key helpers convert between nanoseconds and sub-sync counters, convert TDC measurements to offsets, configure LPF/TDC blocks, manage the TOD subcounter, and implement PTP ops: `idtfc3_gettime()`, `idtfc3_settime()`, `idtfc3_adjtime()`, `idtfc3_adjphase()`, `idtfc3_adjfine()`, `idtfc3_enable()`, and `idtfc3_aux_work()`. Probe uses `idtfc3_check_device_compatibility()`, `idtfc3_load_firmware()`, `idtfc3_configure_hw()`, and `idtfc3_enable_ptp()`.

## Control Flow
Probe obtains the parent RSMU regmap and lock, verifies device ID, loads firmware or defers if the firmware is missing, then enables the PTP clock. Firmware loading initializes default hardware parameters, parses firmware records, updates derived parameters for recognized addresses, writes valid register records, calibrates TDC/APLL, enables LPF, disables TDC, determines TDC sign, and reads clock parameters. Time reads update a software `ns` value from the current hardware subcounter. Settime programs a future subcounter load so the software time aligns at the next sync. Adjtime similarly computes a counter load from the delta. Adjfine and adjphase write LPF frequency/phase control words. EXTTS with `PTP_EXT_OFFSET` enables continuous TDC measurement; aux work periodically updates the timecounter and emits EXTOFF events from TDC FIFO measurements.

## State And Persistence
`struct idtfc3` stores parent regmap/lock, derived hardware parameters, TDC frequencies/sign, sub-sync counts, software timecounter fields, update periods, and measured write overhead. Hardware firmware and register settings persist in the chip until reset.

## Dependencies And Integration Points
The driver integrates with RSMU MFD data, regmap, firmware loader (`idtfc3.bin` or module override), PTP core, delayed aux worker scheduling, and FC3 register definitions from `idtRC38xxx_reg.h`.

## Risks
Timekeeping depends on periodic aux work; if it is delayed beyond counter wrap, software time can drift or jump. Firmware failure other than missing firmware is warned but probe can continue, so default configuration must be valid. EXTTS supports only external offset semantics, not ordinary edge timestamps. The static `tdc_get` in aux work is shared at function scope, which is safe for a single device but questionable for multiple instances.

## Test Signals
Test firmware defer and successful load, device ID rejection, derived parameter calculations, timecounter wrap, settime and adjtime around negative and large deltas, adjfine/adjphase control-word writes, EXTTS offset enable/disable, TDC FIFO overrun recovery, aux worker cadence, and remove while worker activity is pending.
