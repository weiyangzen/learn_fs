# sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-cards.c

Purpose: board database and board-specific setup helpers for SAA7164-based cards, primarily Hauppauge HVR2200/HVR2250/HVR2255/HVR2205 variants.

Important APIs, types, and functions: `saa7164_boards[]` maps internal board IDs to names, chip revisions, port roles (`SAA7164_MPEG_DVB`, encoder, VBI), and firmware unit/I2C mappings for EEPROMs, tuners, analog demods, and digital demods. `saa7164_subids[]` maps PCI subsystem IDs to board IDs. `saa7164_card_list()` prints valid card choices. `saa7164_gpio_setup()` resets demodulators using firmware GPIO controls. `hauppauge_eeprom()` decodes Hauppauge EEPROM data via `tveeprom_hauppauge_analog()`. `saa7164_card_setup()` reads EEPROM and applies board-specific decode. `saa7164_i2caddr_to_unitid()`, `saa7164_i2caddr_to_reglen()`, and `saa7164_unitid_name()` translate virtual I2C addresses and unit IDs.

Control flow: core probe selects a board from subsystem IDs or module parameters, then uses this file's tables for chip revision, port creation, firmware unit mapping, and I2C emulation. GPIO setup resets attached demods by clearing then setting bridge GPIO bits. Card setup reads EEPROM from bus 0 when available and logs known/unknown Hauppauge models. Virtual I2C calls scan the selected board's `unit[]` array for address and register-width translation.

State and persistence: board tables are static read-mostly data. Runtime state affected here includes selected `dev->board`, EEPROM buffer contents during setup, GPIO line state, and firmware I2C unit translation. EEPROM contents are read but not written.

Dependencies and integration points: integrates with `saa7164-api.c` for EEPROM and GPIO firmware commands, `tveeprom`, tuner/frontend drivers through virtual I2C address mapping, PCI subsystem matching, and core port setup.

Risks: incorrect unit IDs or register lengths break all virtual I2C access for that chip. Static EEPROM assumptions still hardcode bus 0/address `0xa0` in the API. Unknown models only warn, so unsupported board variants may proceed with a close-but-wrong profile. GPIO reset unit ID is a TODO constant (`PCIEBRIDGE_UNITID 2`). Duplicate board names with different revisions make logs less specific.

Test signals: autodetect each listed subsystem ID; compare selected board/chiprev/ports to hardware; read EEPROM and verify logged Hauppauge model; attach tuner and demod drivers on all virtual buses; check GPIO reset with frontend probe success; run `card=<n>` override and verify `saa7164_card_list()` output for unknown IDs.
