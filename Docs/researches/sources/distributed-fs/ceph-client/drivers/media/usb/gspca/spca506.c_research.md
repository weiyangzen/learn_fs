# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/spca506.c

## Purpose
`spca506.c` drives SPCA506 USB video capture devices using an SAA7113-like video decoder. It produces raw `V4L2_PIX_FMT_SPCA505` frames, initializes bridge and decoder registers, tracks TV standard/input selection internally, configures resolution, assembles raw frames from isochronous packets, and exposes brightness, contrast, saturation, and hue controls through decoder I2C writes.

## Important APIs, types, and functions
`struct sd` stores `norme` and `channel` in addition to the GSPCA base. `reg_r` and `reg_w` are USB vendor control helpers. `spca506_Initi2c` sets the SAA7113 write address, and `spca506_WriteI2c` writes a decoder register through USB register `0x07`, polling status index `0x0003` up to 60 times. `spca506_SetNormeInput` programs NTSC/PAL/SECAM and composite/S-video channel bits, writes decoder register `0x02`, and chooses chrominance control register `0x0e`. `spca506_GetNormeInput` returns the cached copy, because reading the chip is considered unreliable. `spca506_Setsize` writes compression/image-size registers.

## Control flow
`sd_config` enables five raw modes from 160x120 to 640x480. `sd_init` writes bridge setup, sets default PAL/composite input, initializes CCDSP-like registers, and writes a long SAA7113 register sequence. `sd_start` repeats much of the decoder setup, configures the current resolution through `spca506_Setsize`, enables compression/size registers, reads a status register for diagnostics, retrieves the cached TV standard/channel, and reapplies it. `sd_stopN` disables streaming and clears bridge registers.

Packet scanning follows the SPCA raw convention: `0` starts a frame and skips the 10-byte header, `0xff` drops, and other packets skip one byte and append payload. Controls call `spca506_Initi2c`, write the relevant SAA7113 register (`0x0a`, `0x0b`, `0x0c`, or `0x0d`), and then write decoder register `0x09` with `0x01` to apply or latch the update.

## State and persistence
The driver caches only TV standard and input channel in `struct sd`. It does not persist settings outside memory and does not currently expose standard/input controls through this file's V4L2 control setup. Hardware state is volatile and reprogrammed on init/start. The I2C write polling loop has no sleep or error return, so timeout behavior is silent.

## Dependencies and integration points
The driver depends on GSPCA, USB control transfers, V4L2 standards constants, and userspace support for `V4L2_PIX_FMT_SPCA505`. It shares packet framing style with SPCA501/SPCA505 and maps three USB IDs in `device_table`, with comments noting possible overlap with SPCA505 devices.

## Risks
The standard/input state is stored as `char` even though V4L2 standard masks can exceed 8 bits, so values may truncate. `sd_init` calls `spca506_SetNormeInput(gspca_dev, 0, 0)`, making "PAL" the implicit else path rather than an explicit V4L2 standard. `spca506_WriteI2c` busy-polls without delay and never reports failure to callers. Short packets are not guarded before header skips. Large repeated magic register sequences make maintenance risky, and comments mark uncertain device classification for one USB ID.

## Test signals
Test decoder initialization with PAL, NTSC, and SECAM standard masks, channel boundary normalization, resolution mode selection, repeated start/stop, raw frame packet parsing including drop markers, control I2C writes and latch register behavior, and USB IDs that might otherwise bind to SPCA505.
