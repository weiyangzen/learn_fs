# sources/distributed-fs/ceph-client/drivers/ptp/ptp_pch.c

Purpose: implements a PCI PTP clock for the Intel EG20T/LAPIS PCH IEEE 1588 timer. It also exports helper functions used by companion Ethernet/CAN logic to access channel control/event, station UUID, and RX/TX snapshot registers.

Important APIs/types/functions: `struct pch_ts_regs` maps the hardware register block. `struct pch_dev` stores the mapped regs, registered PHC, external timestamp enable flags, IRQ, PCI device, and register spinlock. Exported APIs include `pch_ch_control_write()`, `pch_ch_event_read/write()`, `pch_src_uuid_lo_read()`, `pch_src_uuid_hi_read()`, `pch_rx_snap_read()`, `pch_tx_snap_read()`, and `pch_set_station_address()`. `ptp_pch_caps` wires `adjfine`, `adjtime`, `gettime64`, `settime64`, and EXTS enable.

Control flow: PCI probe enables the device with managed PCI helpers, maps BAR1, registers the PHC, requests a shared IRQ, stores drvdata, resets the hardware, writes the default addend, clears the target-time pending bit, enables Ethernet timestamp selection, and optionally programs the `station=` module parameter. The ISR reads event bits, emits `PTP_CLOCK_EXTTS` for enabled SNS/SNM channels, acknowledges handled bits, and ignores the always-set TTIPEND except for acking.

State and persistence: external timestamp enables are runtime booleans only. System time and addend live in hardware registers. The station address module parameter is read-only after load and programs hardware at probe; it is not persisted by the driver.

Dependencies and integration: uses PCI, MMIO, PTP core, shared IRQs, MAC string parsing, and exported symbols for other PCH-related drivers. Time registers store ticks shifted by `TICKS_NS_SHIFT`, so all public helpers convert to nanoseconds.

Risks and test signals: `ptp_pch_adjfine()` writes the addend without taking `register_lock`, unlike get/set/adjtime. The ISR uses the same ASMS timestamp register for both external timestamp channels, which should match hardware expectations. Station parsing stores a parsed MAC into a `u64` and writes it little-endian through `iowrite64_lo_hi`; byte order should be tested with real hardware. Test module load/unload, IRQ sharing, both EXTS channels, settime/adjtime frequency adjustment, exported snapshot readers, invalid station parameter handling, and probe failure after PHC registration.
