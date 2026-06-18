# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp1034.c

- Purpose: Board-specific frontend glue for the Mantis VP-1034 DVB-S/DSS card.
- Important APIs/types/functions: Exports `struct mantis_hwconfig` for the PCI table; frontend init attaches MB86A16 frontend at 0x08 with board voltage callback.
- Control flow: Frontend init powers the board, toggles reset, waits for hardware settle, probes the demod/tuner stack over the Mantis I2C adapter, assigns `mantis->fe`, and returns failure if attachment fails. The config tells common DVB/DMA code TS packet size and board GPIO choices; drives polarization using GPIO 13/14 and writes GPIF DOUT after SEC voltage changes.
- State and persistence: Persistent data is limited to EEPROM or frontend chip registers read/written over I2C; driver state is the `mantis->fe` pointer and hardware register configuration.
- Dependencies and integration points: Integrated by `mantis_cards.c` through PCI driver data, `mantis_dvb.c` through `frontend_init`, and Linux DVB frontend/tuner helper modules.
- Risks: Board init relies on fixed delays and exact I2C addresses. Tuner callbacks can fail after frontend registration if I2C gates or GPIO voltage lines misbehave. Wrong TS size breaks demux filtering.
- Test signals: Test probe on VP-1034 hardware, scan/tune for DVB-S/DSS, frontend detach failure handling, power-cycle recovery, and PCI ID matching for MANTIS_VP_1034_DVB_S.
