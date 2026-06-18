# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_vp1033.c

- Purpose: Board-specific frontend glue for the Mantis VP-1033 DVB-S/DSS card.
- Important APIs/types/functions: Exports `struct mantis_hwconfig` for the PCI table; frontend init attaches STV0299 demod at 0x68 plus LG TDQ-CS001F tuner programming and symbol-rate callback.
- Control flow: Frontend init powers the board, toggles reset, waits for hardware settle, probes the demod/tuner stack over the Mantis I2C adapter, assigns `mantis->fe`, and returns failure if attachment fails. The config tells common DVB/DMA code TS packet size and board GPIO choices; uses a 204-byte TS path, power GPIF_A12, reset GPIF_A13, 9600-N UART, and a large STV0299 init table.
- State and persistence: Persistent data is limited to EEPROM or frontend chip registers read/written over I2C; driver state is the `mantis->fe` pointer and hardware register configuration.
- Dependencies and integration points: Integrated by `mantis_cards.c` through PCI driver data, `mantis_dvb.c` through `frontend_init`, and Linux DVB frontend/tuner helper modules.
- Risks: Board init relies on fixed delays and exact I2C addresses. Tuner callbacks can fail after frontend registration if I2C gates or GPIO voltage lines misbehave. Wrong TS size breaks demux filtering.
- Test signals: Test probe on VP-1033 hardware, scan/tune for DVB-S/DSS, frontend detach failure handling, power-cycle recovery, and PCI ID matching for MANTIS_VP_1033_DVB_S.
