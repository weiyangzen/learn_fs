# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp1041.c

- Purpose: Board-specific frontend glue for the Mantis VP-1041 DVB-S/S2 card.
- Important APIs/types/functions: Exports `struct mantis_hwconfig` for the PCI table; frontend init attaches STB0899 demod, STB6100 tuner, and optional LNBP21 attach.
- Control flow: Frontend init powers the board, toggles reset, waits for hardware settle, probes the demod/tuner stack over the Mantis I2C adapter, assigns `mantis->fe`, and returns failure if attachment fails. The config tells common DVB/DMA code TS packet size and board GPIO choices; uses extensive STB0899 register tables, 188-byte TS, and shared power/reset GPIOs.
- State and persistence: Persistent data is limited to EEPROM or frontend chip registers read/written over I2C; driver state is the `mantis->fe` pointer and hardware register configuration.
- Dependencies and integration points: Integrated by `mantis_cards.c` through PCI driver data, `mantis_dvb.c` through `frontend_init`, and Linux DVB frontend/tuner helper modules.
- Risks: Board init relies on fixed delays and exact I2C addresses. Tuner callbacks can fail after frontend registration if I2C gates or GPIO voltage lines misbehave. Wrong TS size breaks demux filtering.
- Test signals: Test probe on VP-1041 hardware, scan/tune for DVB-S/S2, frontend detach failure handling, power-cycle recovery, and PCI ID matching for MANTIS_VP_1041_DVB_S2 plus TechniSat/TerraTec aliases.
