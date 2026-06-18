# sources/distributed-fs/ceph-client/drivers/iio/adc/axp20x_adc.c

## Purpose
This driver exposes ADC channels from several X-Powers PMIC families through IIO: AXP192, AXP20x/AXP209, AXP22x/AXP221, AXP717, and AXP813. The channels represent PMIC temperature, AC input, VBUS, battery voltage/current, GPIO/TS pins, VMID, backup battery, and similar PMIC measurements. It is a direct-mode regmap-backed IIO provider for sibling power-supply and charger drivers.

## Important APIs, Types, And Functions
`struct axp20x_adc_iio` holds the parent PMIC regmap and selected `struct axp_data`. `struct axp_data` supplies the per-chip `iio_info`, channel table, ADC enable register masks, optional sample-rate setter, and IIO consumer maps. Channel macros define `IIO_CHAN_INFO_RAW`, `SCALE`, and optional `OFFSET` support. Read paths are chip-specific: `axp192_adc_raw()`, `axp20x_adc_raw()`, `axp22x_adc_raw()`, `axp717_adc_raw()`, and `axp813_adc_raw()`. Scale and offset are split by chip and type; only AXP192/AXP20x GPIO offsets are writable.

## Control Flow
Probe obtains the parent `struct axp20x_dev`, allocates the IIO device, chooses `axp_data` from firmware match data or platform ID, binds channels and `iio_info`, enables ADC blocks by writing `adc_en1` and optional `adc_en2`, optionally programs 100 Hz sampling, registers IIO consumer maps, and registers the IIO device. Remove unregisters the IIO device/maps and clears ADC enable registers.

Raw reads use PMIC register helpers. Most chips use `axp20x_read_variable_width()` with 12-bit or 13-bit widths depending on current-channel quirks. AXP717 is special: several channels share a generic ADC data register, so `axp717_adc_raw()` first selects TS, die temperature, VMID, or backup-battery input in `AXP717_ADC_DATA_SEL`, bulk-reads two bytes, and extracts the 14-bit value. Scale and offset callbacks return fixed values based on datasheet channel type and chip family; temp channels have fixed offsets for older families.

## State And Persistence
The driver has minimal state: a regmap pointer and immutable chip data. Hardware ADC enable bits persist in the PMIC while the driver is bound and are cleared on error/remove. Writable GPIO offset state is stored in PMIC registers (`AXP192_GPIO30_IN_RANGE` or `AXP20X_GPIO10_IN_RANGE`) and therefore persists at hardware register level until changed or reset by PMIC/firmware.

## Dependencies And Integration Points
It depends on the AXP20x MFD core for regmap and register definitions, IIO core, IIO machine maps, Linux bitfield helpers, unaligned access helpers, platform bus, and OF/platform ID matching. IIO maps connect ADC labels to `axp20x-usb-power-supply`, `axp20x-ac-power-supply`, and `axp20x-battery-power-supply` consumers.

## Risks And Test Signals
Risks include enabling/disabling the full ADC mask without preserving firmware state, chip-specific raw width mistakes, AXP717 mux selection races if multiple consumers read generic data channels concurrently, missing scale/offset for channels explicitly marked unknown, and assuming `platform_get_device_id()` is valid for `indio_dev->name` even in firmware-matched contexts. Test signals include chip-specific channel count/name exposure, raw reads for 12/13/14-bit channels, GPIO offset read/write acceptance only for valid values, IIO map registration rollback clearing ADC enables, and remove clearing both enable registers where present.
