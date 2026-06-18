
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad3552r-hs.c

## Purpose
`ad3552r-hs.c` is the high-speed platform/IIO-backend variant of the AD354x/AD355x DAC driver. It configures a backend-assisted DSPI/QSPI DDR streaming path, exposes raw/scale/offset/sample-frequency IIO attributes, provides debugfs data-source controls, and sequences the DAC/backend between safe SPI-SDR register access and high-speed buffered streaming.

## Important APIs, types, and functions
- `struct ad3552r_hs_state` stores model data, reset GPIO, device, IIO backend, single-channel mode, channel calibration data, platform bus hooks, cached `INTERFACE_CONFIG_D`, and a mutex.
- Platform hooks in `struct ad3552r_hs_platform_data` perform backend bus register read/write and IO mode changes.
- `ad3552r_hs_buffer_postenable()` programs streaming loop length, DDR mode, target/bus DSPI/QSPI mode, backend data address/format, and enables data stream.
- `ad3552r_hs_buffer_predisable()` disables stream and unwinds to simple SPI SDR.
- `ad3552r_hs_setup()` resets, disables backend DDR, validates scratch pad, reads ID, clears reset status, sets reference/drive strength, parses channel nodes, and computes IIO scale/offset.
- `ad3552r_hs_reg_access()` backs debugfs register access with range checks.
- Debugfs files `data_source` and `data_source_available` switch backend external data vs internal ramp.
- `ad3552r_hs_probe()` obtains platform data and backend, requests backend buffer, runs setup, registers IIO device, initializes mutex, and creates debugfs entries.

## Control flow
Probe gets platform bus hooks, enables the backend, matches model data, configures IIO metadata and backend buffer, then initializes the DAC. Buffered enable validates active scan mask, disables single-instruction mode, programs stream loop length and DDR, switches target and bus to dual/quad high-speed mode, tells backend the data register address and format, and starts streaming. Buffered disable reverses the stream, bus mode, DDR bit, backend DDR, target mode, and single-instruction state so debugfs/raw register access works again.

## State and persistence behavior
The driver caches `config_d` because DDR mode cannot be read back. Channel range/gain data lives in `ch_data`. `single_channel` reflects the current active scan mask. Hardware state changes persist until predisable/reset: stream mode, transfer mode, DDR config, reference config, drive strength, output range/custom gain, and backend data source.

## Dependencies and integration points
Depends on platform driver core, IIO backend API, IIO buffers, debugfs, GPIO, firmware child nodes, `ad3552r-common.c` exports, and platform data callbacks from the backend bus provider. It imports namespaces `IIO_BACKEND` and `IIO_AD3552R`.

## Risks and edge cases
- In `ad3552r_hs_setup()`, after `ad3552r_get_ref_voltage(st->dev, &val)`, the code assigns `val = ret`; on success this programs reference selection as zero instead of the parsed value, likely ignoring external/internal-vref selection.
- Probe initializes `st->lock` after registering the IIO device and after debugfs-capable setup paths; debugfs is created after mutex init, but registered IIO callbacks could theoretically run before the mutex is initialized.
- Product ID mismatch only warns and continues, unlike the standard driver that fails probe.
- DDR mode disallows reads; any error unwind that fails to restore `config_d`/backend DDR can leave debugfs/raw reads unsafe.
- `ad3552r_hs_show_data_source_avail()` uses `PAGE_SIZE - len` with a 128-byte local buffer; current strings fit, but the bound is conceptually wrong.

## Test signals
Use backend simulation or hardware to test probe with external/internal vref, scratch-pad mismatch, ID mismatch, active scan masks for channel 0/channel 1/both, postenable error unwind at each backend step, predisable restoration, raw reads before/after streaming, debugfs data-source switching, and sample-frequency calculation from backend clock/lane count/realbits.
