## sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-dec23.c

### Purpose
`pwc-dec23.c` implements software decompression for PWC codec versions 2 and 3. It converts compressed Timon/Kiara camera bands into planar YUV420 output using reverse-engineered ROM tables, bitstream decoding, block reconstruction, and clamp/copy helpers.

### Important APIs, Types, And Functions
Public entry points are `pwc_dec23_init(struct pwc_device *, const unsigned char *cmd)` and `pwc_dec23_decompress(struct pwc_device *, const void *src, void *dst)`. Key internals include table builders `build_table_color()`, `build_subblock_pattern()`, `build_bit_powermask_table()`, `fill_table_dc00_d800()`, bit reservoir macros, `decode_block()`, `copy_image_block_Y()`, `copy_image_block_CrCb()`, and `DecompressBand23()`.

### Control Flow
Initialization checks whether the command byte changed; if so it derives codec bit depth and ROM version from the mode command, selects Kiara or Timon ROM tables, builds pass-one/pass-two color tables, scaling tables, subblock patterns, bit masks, and the clamp table. Decompression locks the decoder state, splits the destination into Y, U, and V planes, and processes one four-line band at a time. Each band skips the first stream byte, reads a compression index, decodes Y blocks first, then U and V blocks, and advances plane pointers to the next band.

### State, Persistence, And Dependencies
Decoder state lives in `struct pwc_dec23_private`: mutex, last command cache, bit reservoir, current stream pointer, temporary colors, and large lookup tables. The static `pwc_crop_table` is shared for clamping. The file depends on `pwc-timon.h`, `pwc-kiara.h`, and the camera mode command format established by `pwc-ctrl.c`.

### Integration Points
`pwc_set_video_mode()` initializes the decoder for compressed YUV420 modes. `pwc_decompress()` calls `pwc_dec23_decompress()` from the vb2 buffer-finish path after a full frame has been captured.

### Risks
The bitstream parser assumes valid compressed data and advances `stream` without explicit frame-length bounds inside decode macros. Decode table correctness depends on opaque reverse-engineered constants. The shared clamp table is rebuilt during init and could be touched by multiple devices, although decompression uses a per-device lock. Any mismatch between `vbandlength`, width, height, and command bytes can corrupt output or overread frame data.

### Test Signals
High-value tests include compressed YUV output for codec2 and codec3 devices at each supported resolution/fps/compression level, repeated mode changes that rebuild tables, parallel devices with different commands, malformed or short frames, and visual comparison against known-good decoded frames.
