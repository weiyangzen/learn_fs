# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp2040.c

- Purpose: Board-specific frontend glue for the Mantis VP-2040 DVB-C card.
- Important APIs/types/functions: Exports `struct mantis_hwconfig` for the PCI table; frontend init attaches TDA10021 fallback to TDA10023 CU1216 frontend and CU1216 tuner programming.
- Control flow: Frontend init powers the board, toggles reset, waits for hardware settle, probes the demod/tuner stack over the Mantis I2C adapter, assigns `mantis->fe`, and returns failure if attachment fails. The config tells common DVB/DMA code TS packet size and board GPIO choices; similar to VP-2033 with separate PCI IDs for Cinergy/CableStar, 204-byte TS.
- State and persistence: Persistent data is limited to EEPROM or frontend chip registers read/written over I2C; driver state is the `mantis->fe` pointer and hardware register configuration.
- Dependencies and integration points: Integrated by `mantis_cards.c` through PCI driver data, `mantis_dvb.c` through `frontend_init`, and Linux DVB frontend/tuner helper modules.
- Risks: Board init relies on fixed delays and exact I2C addresses. Tuner callbacks can fail after frontend registration if I2C gates or GPIO voltage lines misbehave. Wrong TS size breaks demux filtering.
- Test signals: Test probe on VP-2040 hardware, scan/tune for DVB-C, frontend detach failure handling, power-cycle recovery, and PCI ID matching for MANTIS_VP_2040_DVB_C plus CINERGY_C/CABLESTAR_HD2.
