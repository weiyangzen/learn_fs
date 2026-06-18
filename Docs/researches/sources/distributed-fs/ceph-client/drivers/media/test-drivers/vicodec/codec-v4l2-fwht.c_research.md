# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vicodec/codec-v4l2-fwht.c

Purpose: V4L2-facing adapter for the raw FWHT codec. It maps V4L2 pixel formats to component pointers/strides, writes and validates FWHT headers, manages colorspace metadata, and bridges stateful/stateless encode/decode calls to `codec-fwht.c`.

Important APIs/types/functions: exported helpers include `v4l2_fwht_find_pixfmt()`, `v4l2_fwht_get_pixfmt()`, `v4l2_fwht_validate_fmt()`, `v4l2_fwht_find_nth_fmt()`, `v4l2_fwht_encode()`, and `v4l2_fwht_decode()`. `v4l2_fwht_pixfmts[]` describes packed, planar, semiplanar, RGB, HSV, alpha, and GREY layouts. `prepare_raw_frame()` translates a single V4L2 buffer pointer into luma/Cb/Cr/alpha pointers and component step sizes.

Control flow: encode validates `state->info`, prepares raw-frame pointers for the input buffer, adjusts chroma stride for three-plane and NV24/NV42 formats, calls `fwht_encode_frame()` using GOP state to decide intra/next-intra behavior, updates GOP count, and writes a `fwht_cframe_hdr` plus payload to output. Decode validates state info, FWHT version, magic, dimensions, pixel encoding, component count, chroma subsampling flags, and then prepares destination and reference raw frames before calling `fwht_decode_frame()`. Decoded header colorspace/xfer/ycbcr/quantization values are copied back into state.

State and persistence: `struct v4l2_fwht_state` owns visible/coded geometry, strides, GOP/QP state, colorspace metadata, reference-frame descriptor/buffer, compressed frame storage pointer, and a cached header for decode. Encoded headers persist per compressed frame.

Dependencies and integration points: depends on V4L2 pixel-format constants and FWHT flags from `videodev2.h`, raw FWHT functions from `codec-fwht.c`, and is used by `vicodec-core.c` for actual mem2mem processing.

Risks: all buffer pointer derivation assumes q_data sizeimage/stride are consistent with the selected pixel format. Version >=2 enforces pixel encoding and component counts; older versions default to three components, so compatibility paths must remain tested. Decode explicitly rejects resolution changes, leaving dynamic-resolution handling to the stateful decoder wrapper before calling this function.

Test signals: per-format pointer-layout round trips, GREY/RGB/HSV/alpha cases, header version/magic/flags rejection tests, GOP count behavior, and dynamic resolution rejection at this layer with acceptance in `vicodec-core.c` reconfiguration flow.
