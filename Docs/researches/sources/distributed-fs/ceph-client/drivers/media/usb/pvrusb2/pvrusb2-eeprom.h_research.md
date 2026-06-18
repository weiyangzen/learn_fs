<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-eeprom.h -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-eeprom.h

Purpose: declaration for pvrusb2 EEPROM analysis.

Important APIs/types/functions: forward-declares `struct pvr2_hdw` and declares `pvr2_eeprom_analyze()`.

Control flow: hardware initialization calls this helper when the device descriptor indicates a Hauppauge ROM.

State and persistence: no state; implementation stores parsed EEPROM results in hardware state.

Dependencies and integration: private pvrusb2 hardware initialization API.

Risks: callers must ensure I2C adapter and EEPROM address are initialized before calling.

Test signals: compile hardware initialization path and run on EEPROM-equipped devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-eeprom.h -->
