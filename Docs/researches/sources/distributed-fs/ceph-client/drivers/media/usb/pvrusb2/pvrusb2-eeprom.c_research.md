<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-eeprom.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-eeprom.c

Purpose: reads and interprets Hauppauge EEPROM metadata for pvrusb2 devices, using the common `tveeprom` parser to determine tuner type, serial number, and supported standards.

Important APIs/types/functions: `pvr2_eeprom_analyze()` is the exported entry point. `pvr2_eeprom_fetch()` reads the last 128 bytes of the EEPROM through the pvrusb2 I2C adapter, handling 8-bit or 16-bit addressing based on the controller-reported EEPROM address.

Control flow: analysis allocates a 128-byte buffer, normalizes the EEPROM I2C address, selects address width and total size, reads 16-byte chunks from the end of the EEPROM through a two-message I2C transfer, then calls `tveeprom_hauppauge_analog()`. Parsed fields are copied into `hdw->tuner_type`, `tuner_updated`, `serial_number`, and `std_mask_eeprom`.

State and persistence: temporary EEPROM data is heap allocated and freed. Persistent runtime results are stored in `struct pvr2_hdw`; EEPROM contents are read-only hardware persistence.

Dependencies and integration: depends on pvrusb2 hardware internals, Linux I2C, trace flags, and `media/tveeprom.h`.

Risks: only the last 128 bytes are read, assuming Hauppauge layout compatibility. I2C transfer failure aborts parsing. Address normalization for high-bit-set addresses and odd-address 16-bit mode is based on observed FX2 behavior and could mis-handle unusual EEPROMs.

Test signals: devices with Hauppauge ROM; trace EEPROM output; tuner type/std mask/serial propagation; fault injection of I2C transfer failures; compare parsed values with known labels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-eeprom.c -->
