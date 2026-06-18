# sources/distributed-fs/ceph-client/drivers/media/spi/cxd2880-spi.c

Purpose: SPI adapter and DVB glue for the Sony CXD2880 DVB-T2/T tuner/demodulator. It powers the chip, attaches the CXD2880 frontend, registers DVB adapter/frontend/demux devices, manages PID filtering, and runs a kernel thread to pull MPEG-TS packets over SPI.

Important APIs and functions: `struct cxd2880_dvb_spi` owns DVB frontend/adapter/demux/dmxdev/frontend, SPI device, mutex, feed counters, optional regulator, TS buffer, and PID filter config. SPI helpers include `cxd2880_write_spi`, `cxd2880_write_reg`, `cxd2880_spi_read_ts`, `cxd2880_spi_read_ts_buffer_info`, and `cxd2880_spi_clear_ts_buffer`. DVB feed callbacks are `cxd2880_start_feed` and `cxd2880_stop_feed`; lifecycle is `cxd2880_spi_probe` and `cxd2880_spi_remove`.

Control flow: probe allocates state, optionally enables `vcc`, sets SPI drvdata and mutex, registers a DVB adapter, attaches/registers the frontend, initializes demux and dmxdev, adds/connects a hardware frontend, then leaves feeds idle. Starting the first feed allocates a DMA-capable TS buffer and starts `cxd2880_ts_read`; PID feeds update the 32-entry hardware filter unless all-PID feed `0x2000` is active. The read thread clears the TS buffer, polls buffer info, reads large batches immediately or smaller batches after 500 ms, and passes TS bytes to `dvb_dmx_swfilter`. Stopping the last feed stops the thread and frees the TS buffer.

State and persistence: runtime state tracks feed counts, all-PID count, PID filter table, read thread, regulator state, and transient TS buffer. Hardware PID filter and TS buffer state are volatile. No persistent storage exists.

Dependencies and integration points: depends on SPI core, optional regulator framework, DVB adapter/frontend/demux/dmxdev APIs, the CXD2880 frontend attach function and config, kthreads, mutexes, and OF/SPI device IDs.

Risks and edge cases: feed_count/filter updates are not protected by a dedicated mutex, so concurrent DVB feed start/stop calls could race. `cxd2880_spi_read_ts_buffer_info` fills `info` even when `spi_write_then_read` fails, using possibly stale stack data. The read thread returns on SPI errors; subsequent stop may see a nonzero `kthread_stop` result. Remove does not explicitly stop active feeds before tearing down DVB structures, relying on DVB core shutdown ordering. Large `pkt_num` is split by integer division, leaving a remainder for later polling.

Test signals: SPI probe with and without `vcc`, frontend attach and tuning, DVB demux open/close, PID filter updates for normal and all-PID feeds, TS packet continuity under high bitrate, SPI error injection, concurrent feed start/stop stress, remove while feeds are active, and regulator disable on probe/remove failure paths.
