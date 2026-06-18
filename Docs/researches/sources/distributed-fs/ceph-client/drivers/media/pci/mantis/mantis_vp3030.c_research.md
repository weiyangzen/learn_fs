# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp3030.c

- Purpose: Board-specific frontend glue for the Mantis VP-3030 DVB-T card.
- Important APIs/types/functions: Exports `struct mantis_hwconfig` for the PCI table; frontend init attaches ZL10353 demod plus TDA665x tuner.
- Control flow: Frontend init powers the board, toggles reset, waits for hardware settle, probes the demod/tuner stack over the Mantis I2C adapter, assigns `mantis->fe`, and returns failure if attachment fails. The config tells common DVB/DMA code TS packet size and board GPIO choices; uses byte-mode I2C, custom reset/power order, 188-byte TS, and ENV57H12D5 tuner limits.
- State and persistence: Persistent data is limited to EEPROM or frontend chip registers read/written over I2C; driver state is the `mantis->fe` pointer and hardware register configuration.
- Dependencies and integration points: Integrated by `mantis_cards.c` through PCI driver data, `mantis_dvb.c` through `frontend_init`, and Linux DVB frontend/tuner helper modules.
- Risks: Board init relies on fixed delays and exact I2C addresses. Tuner callbacks can fail after frontend registration if I2C gates or GPIO voltage lines misbehave. Wrong TS size breaks demux filtering.
- Test signals: Test probe on VP-3030 hardware, scan/tune for DVB-T, frontend detach failure handling, power-cycle recovery, and PCI ID matching for MANTIS_VP_3030_DVB_T.
