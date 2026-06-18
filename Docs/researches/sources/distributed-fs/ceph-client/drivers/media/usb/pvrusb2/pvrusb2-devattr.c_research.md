<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-devattr.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-devattr.c

Purpose: static per-device attribute database for pvrusb2. It maps USB IDs to hardware descriptions, firmware file names, I2C client sets, analog/digital capabilities, routing schemes, IR/LED schemes, default tuner/std values, and DVB frontend/tuner attach callbacks.

Important APIs/types/functions: `pvr2_device_table[]` is the USB match table and stores `driver_info` pointers to `struct pvr2_device_desc`. Static descriptors cover Hauppauge 29xxx/24xxx/73xxx/750xx/751xx/160000/160111, GotView variants, Terratec AV400, and OnAir devices. DVB helper callbacks attach LGDT330x, S5H1409/S5H1411, TDA10048/TDA18271/TDA829x, LGDT3306A, SI2168, SI2157, and simple tuner components when enabled. `MODULE_FIRMWARE()` advertises required FX2 firmware.

Control flow: USB probe matches an entry in `pvr2_device_table`, then the hardware layer consumes the descriptor to load firmware, instantiate subdevices, choose routing logic, expose inputs, handle IR/LED/digital control schemes, and optionally create DVB frontends. DVB attach callbacks are referenced through `struct pvr2_dvb_props`.

State and persistence: the file defines static read-only descriptors and config structs. Runtime state is created elsewhere based on these descriptors. Firmware file names refer to persistent files in the system firmware path but this file does not write them.

Dependencies and integration: depends on USB IDs, tuner type IDs, pvrusb2 device descriptor types, and optional DVB frontend/tuner driver APIs. It is the central integration point between product variants and the generic pvrusb2 hardware logic.

Risks: descriptor accuracy is critical; wrong routing, tuner type, firmware name, or digital scheme can make a product partially unusable. Conditional DVB code changes descriptor contents by build config. Some newer devices use I2C client module probing and must release demod/tuner clients on failures. `MODULE_FIRMWARE(PVR2_FIRMWARE_75xxx)` advertises the same filename as 73xxx through a separate macro, which is intentional but easy to misread.

Test signals: enumerate every USB ID; verify firmware request names; analog input availability and routing per product; IR scheme behavior; DVB frontend attach for each digital-capable model; module autoload aliases; build with and without DVB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-devattr.c -->
