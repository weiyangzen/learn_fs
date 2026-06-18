# sources/distributed-fs/ceph-client/drivers/staging/media/av7110/Kconfig

## Purpose
Defines kernel configuration entries for the legacy AV7110 full-featured DVB card driver, optional IR/OSD support, and the SP8870 frontend dependency used by this driver family.

## Important APIs, Types, and Functions
Key symbols are `DVB_AV7110_IR`, `DVB_AV7110`, `DVB_AV7110_OSD`, and nested `DVB_SP8870`. `DVB_AV7110` depends on DVB core, PCI, I2C, and video device support, selects TTPCI EEPROM and SAA7146 video support, and auto-selects several DVB frontends/tuners when `MEDIA_SUBDRV_AUTOSELECT` is enabled.

## Control Flow
Kconfig selection determines whether `dvb-ttpci.o`, OSD code, IR code, and `sp8870.o` are built. Help text also documents required external firmware.

## State and Persistence Behavior
No runtime state. Configuration choices persist in the kernel build config and determine module availability.

## Dependencies and Integration Points
Integrates the av7110 directory with DVB core, media frontend drivers, RC core, SAA7146, and firmware-loading expectations.

## Risks
Missing selects/dependencies cause link errors or runtime probe failures. The driver requires external firmware, so enabling the module does not guarantee usable hardware without firmware files.

## Test Signals
Build matrix for built-in/module `DVB_AV7110`, OSD enabled/disabled, IR enabled when RC core is available, `MEDIA_SUBDRV_AUTOSELECT` on/off, and SP8870 firmware path.
