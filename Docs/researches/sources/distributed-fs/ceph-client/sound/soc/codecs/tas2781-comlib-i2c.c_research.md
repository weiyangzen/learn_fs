<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2781-comlib-i2c.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/tas2781-comlib-i2c.c

## Purpose

This file provides I2C-specific common support for TAS2563/TAS2781-style multi-amplifier drivers used by both HDA and ASoC front ends. It creates the shared paged regmap, switches the active I2C address/book per channel, implements multi-device volume helpers, resets devices, and starts asynchronous RCA firmware loading.

## Important APIs, types, and functions

Important exported APIs are `tasdev_chn_switch()`, `tasdevice_dev_update_bits()`, `tasdevice_kzalloc()`, `tasdevice_init()`, `tasdevice_amp_putvol()`, `tasdevice_amp_getvol()`, `tasdevice_digital_getvol()`, `tasdevice_digital_putvol()`, `tasdevice_reset()`, and `tascodec_init()`. Internal helpers include `tasdevice_change_chn_book()` and `tasdevice_clamp()`. The regmap uses `TASDEVICE_PAGE_SELECT` as selector, spans 256 pages, and disables caching (`REGCACHE_NONE`).

## Control flow

`tasdevice_kzalloc()` allocates shared private state and records device/client pointers. `tasdevice_init()` initializes the shared I2C regmap, resets current program/config/book trackers to -1, wires function pointers for update/read/bulk-read/book switching, and initializes `codec_lock`. Channel switching mutates the live `i2c_client->addr` to the target amplifier address, resets page selection when crossing devices, and writes the book-control register when needed. Volume put helpers clamp/invert one control value and apply it to every device; get helpers read device 0. `tasdevice_reset()` either toggles reset GPIO or writes per-device software reset. `tascodec_init()` builds the RCA binary name from optional prefix, device name, and `ndev`, populates the CRC8 table, stores the codec pointer, and calls `request_firmware_nowait()`.

## State and persistence behavior

Persistent state lives in `tasdevice_priv`: shared regmap, current program/config, per-device current book/program/config, CRC table, firmware filenames, codec pointer, and mutex. Because all devices share one regmap and the I2C client address is mutated, `cur_book` and page reset behavior are essential. No regcache is used, so reads/writes go directly to hardware.

## Dependencies and integration points

The file depends on I2C, regmap, firmware loading, GPIOs, CRC8, ALSA SoC mixer controls, and public TAS2781 headers `<sound/tas2781.h>` and `<sound/tas2781-comlib-i2c.h>`. Higher-level ASoC/HDA drivers supply `tasdevice_priv` fields such as `ndev`, device addresses, `dev_name`, reset GPIO, and firmware callbacks.

## Risks and test signals

Risks include mutable `client->addr` races if callers do not hold `codec_lock`, surprising success return semantics in volume puts (`0` when all devices fail, `1` otherwise), lack of regcache, and book/page state corruption if external code accesses the same client. Test signals include multi-amplifier register reads/writes on each I2C address, page/book transitions, reset via GPIO and software reset, mixer get/put across all devices, asynchronous RCA firmware request naming, and lock coverage during codec probe/firmware loading.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/tas2781-comlib-i2c.c -->
