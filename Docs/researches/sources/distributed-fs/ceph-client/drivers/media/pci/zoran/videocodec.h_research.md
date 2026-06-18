# sources/distributed-fs/ceph-client/drivers/media/pci/zoran/videocodec.h

## Purpose
`videocodec.h` defines the internal master/slave API used by the Zoran driver to attach hardware JPEG codecs and video front ends to the ZR36057/ZR36067 PCI controller. It documents expected usage, command IDs, flags, mode IDs, data structures, and helper casts back to `struct zoran`.

## Important APIs, Types, And Functions
Core types are `struct videocodec`, `struct videocodec_master`, `struct vfe_settings`, `struct vfe_polarity`, `struct tvnorm`, `struct jpeg_com_marker`, and `struct jpeg_app_marker`. Flags describe codec capabilities such as JPEG, hardware, VFE, encoder, decoder, IRQ, and picture I/O. Commands include status/mode/VFE/MMAP operations and JPEG target-size, scale, Huffman, quantization, APP, and COM data controls. Function prototypes expose attach/detach/register/unregister and debugfs display. Inline helpers `videocodec_master_to_zoran()` and `videocodec_to_zoran()` recover the owning `struct zoran`.

## Control Flow
The header describes callback control flow: masters provide `readreg()` and `writereg()` callbacks; slaves provide `setup()`, `unset()`, `set_mode()`, `set_video()`, and `control()` plus optional IRQ/image hooks. The Zoran card code constructs masters; codec source files define static `struct videocodec` templates; `videocodec.c` matches and duplicates templates during attach.

## State And Persistence
`struct videocodec` stores registered template fields and live attachment fields including `master_data` and private `data`. `struct videocodec_master` stores the master name, flags, opaque `data`, and register callbacks. JPEG marker structures cap APP/COM payloads at 60 bytes. State is kernel-only and per attachment.

## Dependencies And Integration Points
The header includes Linux debugfs and V4L2 definitions and then includes `zoran.h` for helper casts. It is consumed by all Zoran codec files, `videocodec.c`, `zoran_card.c`, and `zoran_device.c`. The API is explicitly not a userspace ABI; V4L2 ioctls eventually influence it through `zoran_driver.c` settings.

## Risks
The API is loosely typed: `control()` takes integer command IDs plus void pointers and size checks must be correct in every codec implementation. The header itself notes that master/slave data structures are device-dependent. Including `zoran.h` from this header couples the generic-looking codec API back to one driver. Deprecated comments mention procfs even though the implementation now exposes debugfs, a documentation drift signal.

## Test Signals
Build coverage across all codec configurations is the first signal. Runtime signals are correct codec attach, VFE setup, JPEG quality/APP/COM propagation, and debugfs display. Fuzzing or negative ioctl tests around JPEG controls should not pass wrong-size buffers to codec `control()` callbacks.
