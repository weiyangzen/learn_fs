# sources/distributed-fs/ceph-client/include/uapi/linux/media/raspberrypi/pisp_common.h

## Purpose
Provides common Raspberry Pi PiSP UAPI definitions shared by front-end and back-end configuration headers: image format descriptors, Bayer order encodings, image format bitfields, compression/decompression parameters, black-level/white-balance blocks, and AXI bus configuration.

## Important APIs, Types, And Functions
Important types are `pisp_image_format_config`, `pisp_bayer_order`, `pisp_image_format`, `pisp_bla_config`, `pisp_wbg_config`, `pisp_compress_config`, `pisp_decompress_config`, and `pisp_axi_config`. Helper macros decode bits-per-sample, shift, channel count, compression, sampling, order, planarity, wallpaper layout, 32-bit pixels, and HOG mode.

## Control Flow
This header has no runtime branches; it encodes the decision table that front-end/back-end drivers and userspace use when parsing formats. Userspace chooses format bitfields, dimensions, strides, offsets, and AXI flags; drivers interpret those flags to program bus transfers and pixel pipeline format paths.

## State, Persistence, And Dependencies
State is fully caller-owned and passed in packed structs. Compression and decompression structs carry mode and offset, but no persistent memory is owned here. Dependencies are limited to `linux/types.h`.

## Integration Points
Included by `pisp_fe_config.h` and `pisp_be_config.h`. It is the common ABI vocabulary for camera pipeline formats and is expected to match userspace camera stack assumptions about Bayer order, planar layout, compression mode, and AXI behavior.

## Risks
Format values are bitfield composites, so invalid combinations can pass C type checks. Packed layouts and signed stride fields must be identical in userspace and kernel. Plane stride handling is a risk for semi-planar/planar formats, and AXI burst flags share the byte with burst length.

## Test Signals
Validate macro decoding for representative formats, packed struct sizes, RGB/Bayer greyscale handling, compression mode acceptance, stride/stride2 interpretation, and AXI maxlen flag masking.
