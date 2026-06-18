# sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zoran_card.c

## Purpose
`zoran_card.c` is the PCI/card binding layer for the Zoran driver. It owns module parameters, PCI IDs, board database, bit-banged I2C setup, codec registration/attachment orchestration, V4L2 device allocation, default capture/JPEG settings, debugfs, probe, and remove.

## Important APIs, Types, And Functions
Module parameters include `card[]`, `default_input`, `default_mux`, `default_norm`, `video_nr[]`, and `pass_through`. Board data lives in the static `zoran_cards[]` table of `struct card_info`, including I2C decoder/encoder names, codec IDs, inputs, norms, timing tables, interrupts, GPIO/GPCS maps, VFE polarity, and board init hooks. Important functions are the guest-bus codec read/write callbacks (`zr36060_read/write`, `zr36050_read/write`, `zr36016_read`, exported `zr36016_write()`), `videocodec_init/exit()`, `zoran_check_jpg_settings()`, `zoran_i2c_init/exit()`, `zoran_open_init_params()`, `zr36057_init()`, `zoran_setup_videocodec()`, `zoran_probe()`, and `zoran_remove()`.

## Control Flow
Probe validates DMA mask and vb2 segment size, allocates `struct zoran`, registers V4L2/control state, enables PCI, selects a card by module parameter or PCI subsystem, maps MMIO, requests IRQ, adjusts PCI latency, restarts the chip, registers I2C and subdevices, registers codec templates, resets the JPEG codec, attaches codec and optional VFE via `videocodec_attach()`, initializes hardware resources/video node/status DMA buffers, creates debugfs, and returns bound. Remove reverses this by removing debugfs, releasing queues, detaching codecs/VFE, unregistering codec templates and I2C, disabling bus mastering, resetting GPIO, freeing IRQ/DMA/status buffers, releasing PCI, unregistering video/V4L2, and freeing controls.

## State And Persistence
Card-level settings persist in `struct zoran`: selected card info, norm/input, timing pointer, V4L/JPEG settings, status command buffers (`stat_com`, `stat_comb`) with DMA addresses, attached subdevs/codecs, initialized flag, and debugfs directory. Module parameters persist for the loaded module and affect all probes.

## Dependencies And Integration Points
The file integrates with PCI, DMA, V4L2 core/controls/video devices, debugfs, I2C algo-bit and media I2C subdevs, the videocodec registry, codec files, and low-level ZR36057 helpers from `zoran_device.c`. Kconfig controls which codec init paths compile.

## Risks
Manual error unwinding is long and cross-layered; missing an unwind step can leak IRQs, I2C adapters, DMA buffers, or codec attachments. `zoran_check_jpg_settings()` mutates settings while validating, so callers must distinguish try versus commit behavior. Some old board timing entries include documented U/V shift workarounds. Autodetect cannot identify older ZR36057 boards, requiring `card=X`. Probe failure paths generally return `-ENODEV`, which can hide the precise earlier error.

## Test Signals
Test each supported card selection path, invalid `card[]`, invalid defaults, missing I2C subdevice, missing codec support, debugfs output, and remove after partial probe failures. JPEG settings tests should verify decimation 1/2/4, custom crop alignment, quality clamping, APP/COM length clamping, and DC10_NEW horizontal-decimation restrictions.
