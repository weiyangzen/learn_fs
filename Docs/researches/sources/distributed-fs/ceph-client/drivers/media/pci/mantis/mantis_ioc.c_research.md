# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_ioc.c

- Purpose: Miscellaneous board I/O control helpers: EEPROM MAC read, GPIF GPIO bit updates, and stream routing between HIF and CAM.
- Important APIs/types/functions: `mantis_get_mac()`, `mantis_gpio_set_bits()`, `mantis_stream_control()`, and internal `read_eeprom_bytes()`.
- Control flow: MAC read performs an I2C register read from EEPROM address 0x50 at offset 0x08 and logs it. GPIO helper updates `MANTIS_GPIF_ADDR` bit state and clears DOUT. Stream control toggles `MANTIS_BYPASS` in `MANTIS_CONTROL` to route TS toward HIF or CAM.
- State and persistence: Tracks current GPIO bitfield in `mantis->gpio_status`; EEPROM contents are persistent hardware data but this file only reads/logs them.
- Dependencies and integration points: Used by probe, DVB frontend power/reset, board LNB voltage callbacks, and CAM stream routing; depends on Mantis I2C and GPIF registers.
- Risks: `mantis_get_mac()` does not copy the read MAC into `mantis->mac_address`. GPIO updates read current GPIF address register and may mix address/control bits with GPIO state. Stream-control bit math uses `0xff - MANTIS_BYPASS` instead of a conventional mask.
- Test signals: Test EEPROM read success/failure, frontend power GPIO transitions, stream routing before DMA/CAM operation, and regression for MAC propagation expectations.
