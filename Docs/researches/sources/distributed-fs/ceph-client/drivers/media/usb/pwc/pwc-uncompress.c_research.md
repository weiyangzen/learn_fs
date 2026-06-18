## sources/distributed-fs/ceph-client/drivers/media/usb/pwc/pwc-uncompress.c

### Purpose
`pwc-uncompress.c` is the frame conversion frontend. It turns captured raw PWC frame data into either userspace raw PWC metadata+payload or planar YUV420 output.

### Important APIs, Types, And Functions
The single public function is `pwc_decompress(struct pwc_device *, struct pwc_frame_buf *)`. It uses `struct pwc_raw_frame`, vb2 plane helpers, codec macros, and `pwc_dec23_decompress()`.

### Control Flow
The function obtains the output plane address and skips the camera-specific frame header in the captured buffer. For raw PWC1/PWC2 output, it writes type, band length, last mode command, and raw frame bytes into the vb2 plane. For YUV420, it sets the payload to width*height*3/2. If `vbandlength` is zero, it byte-shuffles native uncompressed camera data into Y, U, and V planes. If compressed and codec1, it returns `-ENXIO`. Otherwise it invokes codec23 decompression.

### State, Persistence, And Dependencies
The function reads `struct pwc_device` fields such as type, width, height, pixfmt, command buffer, frame sizes, header size, and band length. It writes only the vb2 output payload. Dependencies include videobuf2, PWC decompressor headers, and format constants.

### Integration Points
`pwc-if.c` calls this from `buffer_finish()` when a completed buffer is dequeued by userspace. Mode setup in `pwc-ctrl.c` determines whether the path is raw, uncompressed YUV, codec1, or codec23.

### Risks
Codec1 YUV output is unsupported despite mode initialization. The uncompressed byte-shuffle assumes the captured payload size and layout match width/height. Raw output size uses `struct_size()` and must fit the allocated vb2 plane.

### Test Signals
Test raw PWC1/PWC2 capture, uncompressed YUV420 modes, compressed codec23 YUV420 modes, unsupported codec1 YUV handling, payload sizes, and output-plane contents for small known frames.
