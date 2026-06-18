# sources/distributed-fs/ceph-client/drivers/input/touchscreen/hp680_ts_input.c

## Purpose
`hp680_ts_input.c` is a board-specific touchscreen driver for the HP Jornada 680. It uses SuperH board registers, ADC channels, and a delayed work item to sample a resistive touchscreen after the pen-down IRQ fires.

## Important APIs, types, and functions
- Global `hp680_ts_dev` holds the input device and `DECLARE_DELAYED_WORK(work, do_softint)` defers ADC sampling.
- `hp680_ts_interrupt()` disables the pen IRQ and schedules `do_softint()` after `HZ / 20`.
- `do_softint()` checks pen-down state, drives scan GPIO bits for Y then X measurement, reads `ADC_CHANNEL_TS_Y` and `ADC_CHANNEL_TS_X`, reports touch/coordinates, syncs input, and re-enables the IRQ.
- `hp680_ts_init()` allocates input, sets fixed ABS ranges, requests `HP680_TS_IRQ`, and registers the device.
- `hp680_ts_exit()` frees IRQ, cancels delayed work, and unregisters input.

## Control flow
Module init creates one global input device. The interrupt path does no sampling directly; it masks the IRQ and schedules delayed work. The work function performs the settle delays and ADC reads, then reports either a contact with X/Y or a release and reenables interrupts.

## State and persistence
State is global and module-lifetime only. Hardware state is manipulated through memory-mapped board registers during each sample. There is no persistence.

## Dependencies and integration points
The driver is tightly tied to SuperH HP6xx platform headers, raw I/O, the platform ADC API, the input subsystem, and a board-defined IRQ.

## Risks
- Global state and hard-coded physical addresses make this unsuitable outside the HP680 platform.
- Exit frees the IRQ before canceling delayed work; any already-running work must not race with device unregister.
- IRQ handler passes `NULL` dev_id while work uses global device state, limiting multi-instance support.
- Sampling constants and axis ranges are fixed and hardware-calibration-sensitive.

## Test signals
- Build on the target architecture with HP6xx headers.
- Hardware tests should validate pen-down IRQ, release reporting, ADC channel order, scan GPIO sequencing, and module unload under active touches.
