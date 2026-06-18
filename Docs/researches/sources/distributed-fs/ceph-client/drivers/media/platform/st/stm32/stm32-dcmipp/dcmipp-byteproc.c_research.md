# sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/stm32-dcmipp/dcmipp-byteproc.c

Purpose: implements the DCMIPP byte processor subdevice. It is a two-pad media entity that propagates mbus formats, exposes compose/crop selections, and programs hardware decimation and crop registers before forwarding stream enable to the upstream input entity.

Important APIs and functions: format helpers include `dcmipp_byteproc_pix_map_by_code`, `dcmipp_byteproc_adjust_fmt`, `dcmipp_byteproc_adjust_compose`, and `dcmipp_byteproc_adjust_crop`. Subdevice operations include init state, enum mbus code, enum frame size, set/get format, get/set selection, enable/disable streams, and s_stream helper integration. Hardware programming is `dcmipp_byteproc_configure_scale_crop`. Entity lifecycle is `dcmipp_byteproc_ent_init`, release callback, and `dcmipp_byteproc_ent_release`.

Control flow: init registers a scaler-function subdevice with sink and source pads. Format setting on the sink validates mbus code, clamps dimensions/colorimetry, resets compose/crop to full frame, and mirrors the format to the source. Source format is derived from sink format and current source crop dimensions. Compose on the sink represents decimation before crop; crop on the source represents the crop after decimation. Stream enable finds the upstream subdev connected to the sink, programs decimation and crop registers based on sink format, compose, crop, and bytes-per-pixel, then enables upstream streaming. Disable forwards stream disable upstream.

State and persistence: state is held in V4L2 subdev state for pad formats, compose, and crop, plus hardware registers programmed on stream enable. The entity has no persistent storage.

Dependencies and integration points: depends on DCMIPP common registration and register helpers, V4L2 subdev selection/state APIs, media pad links, and the DCMIPP input and bytecap entities. It does not convert pixel format; output mbus code remains the input code.

Risks and test signals: risks include restricted decimation ratios, bytes-per-pixel assumptions for crop register units, no compose for JPEG/Bayer or non-1/2-byte formats, source pad selection validity, format changes blocked only while streaming, and needing upstream/downstream formats to remain synchronized. Test via media-ctl selection operations, crop/compose boundary cases, JPEG and Bayer no-scale behavior, Y8 1/4 width decimation, YUV/RGB 1/2 decimation, stream enable register programming, and link validation through bytecap.
