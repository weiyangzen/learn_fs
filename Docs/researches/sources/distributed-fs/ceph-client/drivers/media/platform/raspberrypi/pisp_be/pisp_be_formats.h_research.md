# sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/pisp_be/pisp_be_formats.h

Purpose: static format capability table for the PiSP Back End driver.

Important APIs/types/functions: defines `PISPBE_MAX_PLANES`, `struct pisp_be_format`, colorspace mask helpers, `supported_formats[]`, and `meta_out_supported_formats[]`. Each image format records V4L2 FourCC, bytes-per-line alignment, bit depth, fixed-point plane factors, number of memory planes, allowed colorspaces, and default colorspace.

Control flow: no executable functions, but `pisp_be.c` iterates `supported_formats[]` for enum/try/set format and uses the table for plane sizing and address translation.

State and persistence: immutable compile-time data.

Dependencies and integration: depends on V4L2 pixel formats and PiSP compressed pixel format definitions. Supports single-plane and multiplane YUV, RGB, Bayer, unpacked Bayer, PiSP compressed Bayer/mono, greyscale, and config metadata.

Risks: plane factors use a fixed-point convention via `P3(x)`, and several entries use fractional macro arguments; mistakes directly affect buffer sizes and computed plane offsets. Colorspace masks constrain userspace negotiation. Missing formats here are invisible to all PiSP BE nodes.

Test signals: enumerate every format, try/set each format on relevant nodes, verify bytesperline alignment and sizeimage for single-plane and multiplane variants, and run DMA with non-mplane YUV formats that require derived plane addresses.
