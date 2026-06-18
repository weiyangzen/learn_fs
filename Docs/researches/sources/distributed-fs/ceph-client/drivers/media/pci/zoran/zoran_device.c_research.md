# sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zoran_device.c

## Purpose
`zoran_device.c` contains low-level ZR36057/ZR36067 hardware programming. It drives GPIO, guest-bus post-office access, JPEG codec sleep/reset/start, VFE geometry, raw memory grab, MJPEG engine setup, status-command queue feed/reap, interrupt handling, PCI bus mastering, hardware initialization, and chip restart.

## Important APIs, Types, And Functions
Public functions include `GPIO()`, `post_office_wait()`, `post_office_write()`, `post_office_read()`, `jpeg_codec_sleep()`, `jpeg_codec_reset()`, `zr36057_set_memgrab()`, `clear_interrupt_counters()`, `jpeg_start()`, `zr36057_enable_jpg()`, `zoran_feed_stat_com()`, `zoran_irq()`, `zoran_set_pci_master()`, `zoran_init_hardware()`, and `zr36057_restart()`. Key private helpers include `zr36057_init_vfe()`, `zr36057_set_vfe()`, `zr36057_adjust_vfe()`, `zr36057_set_jpg()`, `init_jpeg_queue()`, `count_reset_interrupt()`, and `zoran_reap_stat_com()`.

## Control Flow
Hardware init enables PCI mastering, runs a board init hook, initializes decoder/encoder subdevices, toggles JPEG sleep, initializes VFE, sets the JPEG engine idle, and clears interrupts. Raw capture start arms VSync interrupts, snapshot capture, VFE geometry, DMA target registers, and frame grab. MJPEG start configures decoder/encoder routing, codec/VFE callbacks, JPEG marker/target-size data, ZR36057 JPEG registers, status command rings, interrupts, and codec start pulse. IRQ handling clears interrupt sources; raw mode advances one buffer on VSync, while JPEG mode reaps completed status-command entries and feeds new queued buffers.

## State And Persistence
The file mutates `struct zoran` fields for codec mode, queue heads/tails, sequence/error counters, status rings, interrupt counters, running mode, `inuse[]`, and buffer reserve counts. Hardware register state is repeatedly reset and rebuilt at stream start. Status command memory is coherent DMA shared with the device.

## Dependencies And Integration Points
It depends on ZR36057 register definitions, card GPIO/GPCS metadata, V4L2 subdev decoder/encoder calls, videocodec callbacks for JPEG/VFE programming, vb2 DMA-contig buffer addresses, and PCI chipset quirk flags. It is called by probe/init and vb2 start/stop paths in `zoran_driver.c`.

## Risks
`post_office_wait()` busy-waits without a timeout; the source contains a TODO for this. Raw and JPEG paths manipulate hardware and queue state across IRQ and process contexts, so locking around `queued_bufs_lock` and assumptions around held spinlocks are important. Several legacy comments document hardware-specific color/polarity/timeout quirks. If no buffer is available, raw capture disables interrupts and marks the queue error. Endian conversion of status-command entries is required.

## Test Signals
Signals include raw capture frame delivery, MJPEG capture/playback status ring turnover, interrupt counters, correct encoder/decoder routing under `pass_through`, GPIO-driven codec reset/sleep, no queue leaks after stop, and recovery from empty queue. Hardware fault tests should target post-office timeout behavior and JPEG IRQs arriving in unexpected modes.
