# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/tas2781_hda_spi.c

## Purpose
This is the SPI HDA side-codec driver for HP-style TAS2781 smart amplifiers. It implements the TAS2781 SPI register-access quirks, ACPI amp-index discovery, component binding, RCA/DSP firmware loading, per-amp ALSA controls, EFI calibration, playback hooks, and runtime/system PM.

## Important APIs, types, and functions
SPI-specific regmap setup uses `tasdevice_ranges[]` and `tasdevice_regmap`. Access wrappers `tasdevice_spi_dev_read()`, `tasdevice_spi_dev_bulk_read()`, and `tasdevice_spi_dev_update_bits()` handle the dummy-byte requirement for non-book-zero or high-page reads. `tasdevice_spi_change_chn_book()` restricts operations to the current amp index. `tas2781_spi_reset()`, `tascodec_spi_init()`, and `tasdevice_spi_init()` prepare reset, firmware request, and TAS library callbacks. Volume/control helpers include analog and digital get/put callbacks, force-fwload callbacks, and per-amp control creation functions. Firmware/component flow is handled by `tasdev_fw_ready()`, `tas2781_hda_bind()`, and `tas2781_hda_unbind()`. Probe/remove/PM are `tas2781_hda_spi_probe()`, `tas2781_hda_spi_remove()`, and TAS2781 runtime/system PM callbacks.

## Control flow
Probe allocates the wrapper, SPI-private state, and `tasdevice_priv`, limits SPI speed, creates the SPI regmap, accepts only `TXNW2781`, reads ACPI `ti,dev-index` to map chip select to amp index and optional shared reset GPIO, initializes SPI-specific TAS callbacks, enables runtime PM, and registers as a component. Bind runtime-resumes, fills the component slot, starts asynchronous RCA firmware loading with a name based on device name and amp count, installs the playback hook on success, and marks category as HP. The firmware callback parses RCA, adds profile and volume controls, removes stale DSP data, builds a per-subsystem/per-index coefficient filename, parses DSP firmware, adds program/config controls, resets the amp, loads program 0, initializes current state, and imports calibration.

Playback open resumes and switches tuning on only when firmware state is `TASDEVICE_DSP_FW_ALL_OK`; close switches tuning off and autosuspends. Runtime suspend switches tuning off if active and invalidates cached book/config. System resume force-resumes, reads a reset-detection register, and if the device reset, invalidates cached state, reloads program 0, marks firmware OK, and restores tuning.

## State and persistence
State includes one SPI amp index, per-index cached book/program/config fields, reset GPIO for index 0/shared reset, firmware state, current profile/program/config, ALSA controls, playback flag, and calibration data in `tasdevice_priv`. Unlike I2C, this transport uses a single-device regmap window and explicit dummy-byte handling.

## Dependencies and integration points
Dependencies include Linux SPI/regmap/property/ACPI/runtime PM, HDA component and codec APIs, TAS2781 firmware library, TLV control data, EFI calibration from the shared TAS HDA library, and ALSA control APIs. It imports `SND_SOC_TAS2781_FMWLIB` and `SND_HDA_SCODEC_TAS2781`.

## Risks and edge cases
The dummy-byte read rule is central; missing it corrupts register reads outside early book/page ranges. `tasdevice_spi_dev_update_bits()` writes `TASDEVICE_PAGE_REG(reg)` after reading the full logical register, so register-window mapping assumptions must hold. `tasdevice_spi_change_chn_book()` returns `-EXDEV` for other channels and logs it as an ignored non-error. Control name "Froce Speaker-%d FW Load" contains a typo that may be user visible. Resume reloads firmware only when the clock-config reset value indicates a reset, so reset detection must be reliable.

## Test signals
Test SPI register reads for book 0/page 0-1 and for dummy-byte paths, ACPI `ti,dev-index` mapping for multiple chip selects, shared reset behavior, RCA/DSP firmware naming and load, per-index controls, playback open/close around firmware failure and success, runtime suspend/resume cache invalidation, system resume after hardware reset, and calibration import on HP category devices.
