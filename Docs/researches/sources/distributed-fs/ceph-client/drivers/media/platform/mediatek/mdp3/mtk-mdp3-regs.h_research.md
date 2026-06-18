# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-regs.h

## Purpose
This header defines MDP3 color encoding, pixel-format metadata, scaling limits, stream types, frame state, and the public helpers used by the M2M pipeline.

## Important APIs, Types, And Functions
`MDP_COLOR()` packs color attributes, while `MDP_COLOR_*` macros decode compression, 10-bit packing, block mode, plane count, subsampling, bits-per-pixel, group, swap, and hardware format ID. `enum mdp_color` covers raw Bayer, RGB, packed YUV, planar YUV, NV formats, block/tile/UFO formats, and 10-bit variants. Inline helpers compute minimum strides and plane sizes. `struct mdp_format`, `struct mdp_limit`, `struct mdp_frame`, and `struct mdp_frameparam` model V4L2-visible and hardware-visible state. Public functions cover enumeration, try-format, color profile mapping, crop validation, scaling checks, PP enable, source/destination config, and frameparam initialization.

## Control Flow
The header provides declarations and inline calculations used during format negotiation and job setup. The main flow is V4L2 format/selection input to validated `mdp_frameparam`, then to firmware image descriptors.

## State, Persistence, And Dependencies
State is stored in caller-owned `mdp_frameparam` and `mdp_frame` structures. Dependencies include Linux V4L2 types, vb2 core, and the image IPI ABI.

## Integration Points
Used by `mtk-mdp3-m2m.c`, `mtk-mdp3-regs.c`, VPU processing, and platform config format tables.

## Risks
The packed color bit layout is a driver/firmware/hardware ABI. Mistakes in bit fields can produce wrong stride or unsupported hardware formats. `MDP_VPU_INIT` and `MDP_M2M_CTX_ERROR` live in an atomic state field and must remain unique.

## Test Signals
Compile-time coverage of platform format tables, per-format bytesperline/sizeimage tests, 10-bit/block format validation, and V4L2 try/s_fmt compliance.
