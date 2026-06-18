# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600_buffer.c

Purpose: owns shared FIFO setup, enable/disable sequencing, watermark computation, FIFO reads, packet decoding, parse dispatch, and hardware FIFO flush for ICM45600 accel/gyro children.

Important APIs and functions: `inv_icm45600_fifo_decode_packet()` identifies one-sensor versus two-sensor packets, temp, timestamp, and ODR-change flags. `inv_icm45600_buffer_set_fifo_en()`, `update_fifo_period()`, and `update_watermark()` maintain FIFO configuration. `inv_icm45600_buffer_ops` supplies IIO buffer preenable/postenable/predisable/postdisable callbacks. `inv_icm45600_buffer_fifo_read()`, `fifo_parse()`, `hwfifo_flush()`, and `buffer_init()` are used by IRQ handlers and child hwfifo hooks.

Control flow: preenable runtime-resumes and resets timestamp state. Postenable flushes FIFO, enables FIFO threshold/full IRQs, switches FIFO to stream mode, then enables FIFO interface writes. Predisable reverses stream mode and interrupts, with `fifo.on` as a reference count for the two child devices. Postdisable clears per-sensor FIFO enable bits, zeroes watermarks, powers the sensor off, sleeps for hardware stop time, and drops runtime PM.

State and persistence: `st->fifo` stores reference count, enabled sensor bits, effective watermarks, counts, total bytes, and DMA buffer. Hardware state persists in FIFO config, watermark, and interrupt enable registers.

Risks and tests: packet-size assumptions use the two-sensor packet size for reads/watermarks, extended headers are unsupported and stop parsing, watermark math depends on ODR periods being multiples, and regmap noinc reads may need sample-by-sample fallback. Test signals include simultaneous accel/gyro buffers, single-sensor buffers, overflow/full IRQ logging, flush counts, active suspend/resume, and regmap backends that reject large noinc reads.
