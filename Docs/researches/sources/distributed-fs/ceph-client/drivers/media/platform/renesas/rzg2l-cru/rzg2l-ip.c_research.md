<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/rzg2l-ip.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/rzg2l-ip.c

Purpose: implements the internal CRU image-processing V4L2 subdevice. It defines supported CRU media bus and memory formats, propagates sink format to source format, validates codes and sizes, and sequences CRU image processing around the upstream CSI-2 subdevice.

Important APIs, types, and functions: `rzg2l_cru_ip_formats[]` maps UYVY and Bayer RAW8/10/12/14 media bus codes to V4L2 pix formats, CSI-2 datatypes, ICnDMR values, and YUV/raw classification. Lookup helpers `rzg2l_cru_ip_code_to_fmt()`, `format_to_fmt()`, `index_to_fmt()`, and `fmt_supports_mbus_code()` are consumed by video/DMA code. Subdev operations are `rzg2l_cru_ip_s_stream()`, `rzg2l_cru_ip_set_format()`, `enum_mbus_code`, `enum_frame_size`, and `init_state`. Registration helpers create a two-pad pixel formatter entity.

Control flow: on format set, source pad requests are read-only, while sink pad requests are validated, clamped to CRU variant bounds, forced to progressive field, and copied to the source pad. Stream-on calls remote `pre_streamon`, waits briefly, starts CRU image processing, then calls remote `s_stream(1)`. On failures it calls remote `post_streamoff` and stops image processing. Stream-off calls remote `s_stream(0)`, remote `post_streamoff`, then stops CRU image processing.

State and persistence: active subdev state stores sink/source media-bus formats. `cru->ip.remote` points to the bound CSI-2 subdevice. There is no persistent state.

Dependencies and integration points: V4L2 subdev state API, media-controller link validation, MIPI CSI-2 datatype constants, `rzg2l-video.c` image-processing start/stop, and `rzg2l-core.c` media graph registration.

Risks: `rzg2l_cru_ip_get_src_fmt()` returns a pointer from active subdev state after unlocking it, which may be fragile if callers assume long-lived stable storage. Format table grouping maps all RAW10 patterns to one packed CRU10 pixelformat, similarly RAW12/14, so media-code compatibility must be validated by video link validation. Stream sequencing is tightly coupled to CSI-2 `pre_streamon/post_streamoff` semantics.

Test signals: enumerate media bus codes and frame sizes; set each supported sink code and verify source propagation; validate media links against CRU video formats; inject remote `pre_streamon`, `s_stream`, and `post_streamoff` failures; stream each supported raw/YUV format through the full pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/rzg2l-ip.c -->
