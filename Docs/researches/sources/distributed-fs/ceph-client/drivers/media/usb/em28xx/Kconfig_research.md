# sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/Kconfig

## Purpose
This Kconfig file defines build options for Empia EM28xx USB media devices: core device support, analog/V4L2 support, ALSA audio, DVB/ATSC support, and remote-control support.

## Important APIs, types, and functions
The important symbols are `VIDEO_EM28XX`, `VIDEO_EM28XX_V4L2`, `VIDEO_EM28XX_ALSA`, `VIDEO_EM28XX_DVB`, and `VIDEO_EM28XX_RC`. Dependency and select clauses pull in core media, I2C, tuner, TV EEPROM, videobuf2, audio, rc-core, many demod/tuner frontends, and legacy GPIO support when needed.

## Control flow and state
There is no runtime control flow. The file controls kernel configuration resolution: selecting modules enables corresponding object builds in the Makefile and auto-selects subdevice drivers when `MEDIA_SUBDRV_AUTOSELECT` is enabled.

## Dependencies and integration
It integrates with the media Kconfig tree and the EM28xx Makefile. The DVB symbol selects a broad list of frontend/tuner dependencies such as LGDT, ZL10353, TDA10023, DRX, CXD2820R, TDA18271, M88DS3103, TS2020, SI2168, SI2157, and others.

## Risks and test signals
Risks include over-selecting unavailable dependencies, modular dependency conflicts, and missing selects for new boards. Test with `allmodconfig`, `allyesconfig`, minimal `VIDEO_EM28XX_DVB=m`, `VIDEO_EM28XX_RC=y/m`, and configurations where `MEDIA_SUBDRV_AUTOSELECT` is disabled.
