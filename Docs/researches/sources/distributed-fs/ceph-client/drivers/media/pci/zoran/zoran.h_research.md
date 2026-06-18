# sources/distributed-fs/ceph-client/drivers/media/pci/zoran/zoran.h

## Purpose
`zoran.h` is the central private header for the Zoran MJPEG driver. It defines card identities, formats, settings, card capability tables, the main `struct zoran` device state, register access macros, logging helpers, and queue entry types shared by card, device, driver, and codec code.

## Important APIs, Types, And Functions
Important enums are `card_type`, `zoran_codec_mode`, `zoran_map_mode`, GPIO IDs, and guest-bus IDs. Important structures are `struct zr_buffer`, `struct zoran_format`, `struct zoran_v4l_settings`, `struct zoran_jpg_settings`, `struct card_info`, and `struct zoran`. Helpers include `vb2_to_zr_buffer()`, `to_zoran()`, `ZR_DEVNAME()`, `btread()`, `btwrite()`, `btand()`, `btor()`, and `btaor()`. It declares `zoran_queue_init()`, `zoran_queue_exit()`, and `zr_set_buf()`.

## Control Flow
This header shapes nearly all Zoran control flow. `zoran_card.c` fills `struct zoran` and `struct card_info`, `zoran_driver.c` manipulates map mode and vb2 queues, `zoran_device.c` reads/writes ZR36057 registers through `btread`/`btwrite`, and codec files use `struct tvnorm` and JPEG settings through the videocodec layer. `struct zr_buffer` is embedded in vb2 buffer allocations.

## State And Persistence
`struct zoran` contains persistent runtime state for one PCI card: V4L2 device, controls, video node, vb2 queue, bit-banged I2C adapter, decoder/encoder subdevs, attached codec/VFE, locks, card info, norm/input/timing, raw and JPEG settings, queue counters, DMA status rings, interrupt counters, running/map modes, in-use buffers, and debugfs dentry. State persists while the kernel device object is bound and is reset/reinitialized on stream transitions.

## Dependencies And Integration Points
The header depends on PCI, I2C bit algorithm, V4L2 core/control/device APIs, videobuf2 core/V4L2/DMA-contig, debugfs, and the ZR36057 register map. The `card_info` structure integrates external media I2C decoder/encoder names and addresses with GPIO/GPCS mappings and codec IDs.

## Risks
Register access macros assume a local variable named `zr`, which makes them concise but context-sensitive. `struct zoran` is large and shared across IRQ, vb2, ioctl, probe, and remove paths; correct lock choice is essential. Several queue counters are unsigned longs used as ring indices and rely on masks such as `BUZ_MASK_STAT_COM`. Debug counters and operational counters coexist, so regressions can hide if tests only inspect one set.

## Test Signals
Signals include successful probe for each supported `card_type`, correct I2C subdevice discovery, valid debugfs contents, raw and MJPEG queue operation, no leaked `inuse[]` buffers after stream stop, and interrupt counters changing as expected during capture/playback. Static build checks should cover macro users because `btread`/`btwrite` depend on local naming.
