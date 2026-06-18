# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads124s08.c

Purpose: SPI IIO driver for TI ADS124S06/ADS124S08 delta-sigma ADCs. It exposes 6 or 12 voltage channels, performs direct raw reads by programming the input mux and starting/stopping conversion, and supports triggered buffering over active channels.

Important APIs/types/functions: `struct ads124s_private` stores chip info, optional reset GPIO, SPI device, mutex, aligned scan buffer, and shared command/data buffer. Core functions are `ads124s_write_cmd()`, `ads124s_write_reg()`, `ads124s_reset()`, `ads124s_read()`, `ads124s_read_raw()`, trigger handler, and probe.

Control flow: probe allocates IIO, gets optional reset GPIO, selects chip info from SPI ID, initializes mutex, sets direct-mode channel table, installs triggered buffer support, resets the chip by GPIO or RESET command, and registers IIO. Direct raw read locks, writes `INPUT_MUX` to the requested channel, sends START, sends RDATA with NOP clocks through a two-transfer SPI sequence, reads a 24-bit big-endian result, sends STOP, returns the value, and unlocks. Triggered buffer repeats mux/start/read/stop for each active scan channel and pushes the aligned buffer with timestamp.

State and persistence: persistent state is chip variant, optional reset line, mutex, and command buffer. Hardware state includes selected input mux and conversion start/stop state; most configuration registers are otherwise left at reset defaults.

Dependencies and integration: depends on SPI, optional GPIO reset, unaligned big-endian helpers, IIO direct and triggered-buffer APIs, and OF/SPI IDs for ADS124S06/S08.

Risks: channel scan metadata declares unsigned 32-bit samples while `ads124s_read()` returns a 24-bit value without sign extension, which may not match bipolar ADC expectations. Trigger handler does not hold the mutex used by direct reads, relying on IIO mode exclusion. It does not wait on DRDY, so conversion timing depends on command/read behavior and device defaults. Optional reset GPIO errors are logged as info but not returned.

Test signals: ADS124S06 and ADS124S08 channel counts, raw reads across all channels, reset GPIO and command reset paths, mux register write failures, start/read/stop error handling, triggered buffer with multiple active channels, sign/format validation against hardware, and concurrent direct/buffer exclusion.
