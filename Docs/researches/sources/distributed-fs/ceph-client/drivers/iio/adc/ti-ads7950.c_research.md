# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads7950.c

Purpose: SPI IIO driver for the ADS7950/7951/7952/7953/7954/7955/7956/7957/7958/7959/7960/7961 family, supporting 4/8/12/16 channel variants, 8/10/12-bit scan formats, triggered buffers, direct reads, and a four-line GPIO provider.

Important APIs/types/functions: `struct ti_ads7950_state` stores SPI messages, scan/direct transfer buffers, mutex, gpio_chip, vref regulator/default, and ADC/GPIO command bitmasks. `ti_ads7950_update_scan_mode()` builds pipelined manual-mode commands for active channels. `ti_ads7950_trigger_handler()` pushes buffered scans. `ti_ads7950_scan_direct()` performs the three-transfer pipeline for a single channel. GPIO methods manipulate command/config bitmasks and synchronize SPI writes.

Control flow: probe sets 16-bit SPI words and `SPI_CS_WORD`, selects chip info from match data, builds reusable ring and direct messages, enables vref or ACPI default voltage, sets up a triggered buffer, initializes manual/GPIO command registers, registers IIO, then registers the gpiochip. Direct raw reads send a manual channel command through the pipeline, verify the returned channel tag, and extract shifted sample bits. Buffered scans issue the prepared ring message and skip the first two pipeline words.

State and persistence: `cmd_settings_bitmask` and `gpio_cmd_settings_bitmask` mirror chip settings for range, GPIO data, direction, and output values. SPI buffers are shared under `slock`; no persistent storage. Remove unregisters GPIO/IIO/buffer and disables regulator.

Dependencies and integration: SPI, regulator, optional ACPI, IIO triggered buffer, and gpiolib. OF and SPI IDs cover the whole ADS795x/ADS796x family.

Risks: SPI conversion is pipelined, so scan buffers include dummy latency words; direct reads reject mismatched channel tags; GPIO reads temporarily change ADC command settings and then restore them. Test signals include all variant channel counts/bit widths, GPIO input/output direction, vref scale including range-doubling, triggered buffer layout, and cleanup on partial probe failures.
