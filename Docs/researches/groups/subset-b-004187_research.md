# subset-b-004187 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/spi/gs1662.c -->
# sources/distributed-fs/ceph-client/drivers/media/spi/gs1662.c

Purpose: V4L2 SPI subdevice driver for the Gennum GS1662 HD/SD-SDI serializer. It exposes one V4L2 subdev pad, enumerates a fixed set of SDI/CEA digital-video timings, detects the incoming standard from device registers, and forces a selected standard when streaming starts.

Important APIs/types/functions: `struct gs` stores the SPI device, subdev, current timings, and stream-enabled flag. `struct gs_reg_fmt`, `fmt_cap`, and `reg_fmt` map GS1662 standard status/force register values to `struct v4l2_dv_timings`. `gs_read_register()` and `gs_write_register()` issue two-transfer 16-bit SPI messages, with read addresses ORed by `0x8000`. `gs_status_format()` decodes `REG_STATUS` standard bits, and `get_register_timings()` performs the inverse mapping for forced output. V4L2 pad/video callbacks are `gs_s_dv_timings()`, `gs_g_dv_timings()`, `gs_query_dv_timings()`, `gs_enum_dv_timings()`, `gs_dv_timings_cap()`, `gs_s_stream()`, and `gs_g_input_status()`. Probe/remove are `gs_probe()` and `gs_remove()` under `module_spi_driver()`.

Control flow: probe allocates `struct gs`, configures SPI mode 0, 16 bits per word, 10 MHz max speed, initializes the subdev with `v4l2_spi_subdev_init()`, sets default 720p60 timings, and writes `0x300` to register 0 to select SMPTE timing behavior. Timing query first rejects nonzero pads and active streaming, checks four activity registers (`REG_LINES_PER_FRAME` through active-line/word counters) for any signal, then reads `REG_STATUS` and requires H lock, V lock, and standard lock before translating the standard field. Starting a stream writes the forced-format register with the selected timing plus `MASK_FORCE_STD`; stopping writes zero to re-enable autodetection.

State and persistence: state is entirely runtime and per SPI device. `current_timings` is updated only by successful `s_dv_timings()` and defaults at probe. `enabled` gates timing query and avoids redundant stream register writes. No persistent storage or firmware state is used beyond device registers.

Dependencies and integration points: integrates with Linux SPI, V4L2 subdev, V4L2 DV timings, and optional `CONFIG_VIDEO_ADV_DEBUG` register access. It is selected/loaded as an SPI driver named `gs1662`; upstream bridge drivers are expected to bind and route the subdev.

Risks: SPI read/write helpers assign output even if `spi_sync()` fails, and several callers ignore read failures during timing query. `gs_s_dv_timings()` validates that a timing can be forced but does not program hardware until streaming, which is correct but can surprise callers that expect immediate state. `gs_g_input_status()` ORs into `*status` without clearing it first, relying on caller initialization. Timing coverage is limited to `reg_fmt`; several hardware formats are compiled out because matching DV timing definitions are missing. Endianness of raw 16-bit SPI buffer values depends on controller/device convention and should be verified on real hardware.

Test signals: useful tests are V4L2 subdev compliance for pad 0 validation, timing enum/capability consistency, forcing each listed timing through `s_dv_timings()` and `s_stream(1)`, no-signal/no-lock register simulations returning `-ENOLINK`, `-ENOLCK`, or `-ERANGE`, and ADV_DEBUG register read/write smoke tests when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/spi/gs1662.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/Kconfig

Purpose: top-level Kconfig menu for virtual V4L and DVB media test drivers. It groups memory-to-memory V4L test devices under `V4L_TEST_DRIVERS` and virtual DVB devices under `DVB_TEST_DRIVERS`.

Important APIs/types/functions: defines `menuconfig V4L_TEST_DRIVERS`, `config VIDEO_VIM2M`, and `menuconfig DVB_TEST_DRIVERS`, and sources child Kconfig files for `vicodec`, `vimc`, `vivid`, `visl`, and `vidtv`.

Control flow: if `V4L_TEST_DRIVERS` is enabled and `VIDEO_DEV` is available, child V4L virtual driver menus become visible. `VIDEO_VIM2M` selects `VIDEOBUF2_VMALLOC`, `V4L2_MEM2MEM_DEV`, and `MEDIA_CONTROLLER`. If `DVB_TEST_DRIVERS` is enabled and DVB/media/I2C dependencies exist, `vidtv/Kconfig` is sourced.

State and persistence: no runtime state; it controls build-time symbol visibility and dependency propagation.

Dependencies and integration points: depends on media core symbols (`VIDEO_DEV`, `DVB_CORE`, `MEDIA_SUPPORT`, `I2C`) and includes downstream test-driver Kconfig fragments.

Risks: parent menu dependency changes affect many test drivers. `DVB_TEST_DRIVERS` requires I2C because vidtv models tuner/demod attachment through virtual I2C clients.

Test signals: `make menuconfig` visibility checks, `scripts/kconfig/conf` dependency checks, and allmodconfig/randconfig builds with and without `VIDEO_DEV`, `DVB_CORE`, and `I2C`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/Makefile

Purpose: build dispatcher for media test drivers.

Important APIs/types/functions: maps config symbols to objects/subdirectories: `CONFIG_DVB_VIDTV` to `vidtv/`, `CONFIG_VIDEO_VICODEC` to `vicodec/`, and other virtual V4L drivers to their objects/directories.

Control flow: Kbuild descends into subdirectories or builds objects when each config symbol is enabled. The file notes entries should remain alphabetically sorted by Kconfig name.

State and persistence: no runtime state; it is Kbuild metadata.

Dependencies and integration points: integrates with the top-level media driver build and child Makefiles for `vidtv` and `vicodec`.

Risks: symbol/object mismatches silently drop a driver from builds. Ordering is cosmetic but helps maintainability.

Test signals: compile with each affected config as `m` and `y`, and check generated modules include `vicodec.ko`, `dvb-vidtv-bridge.ko`, `dvb-vidtv-demod.ko`, and `dvb-vidtv-tuner.ko` as appropriate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vicodec/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vicodec/Kconfig

Purpose: Kconfig definition for the virtual codec driver.

Important APIs/types/functions: defines `CONFIG_VIDEO_VICODEC` as a tristate "Virtual Codec Driver". It selects `VIDEOBUF2_VMALLOC`, `V4L2_MEM2MEM_DEV`, and `MEDIA_CONTROLLER`.

Control flow: when enabled, it builds a virtual memory-to-memory codec that exposes stateful encoder, stateful decoder, and stateless decoder behavior implemented in the vicodec sources.

State and persistence: build-time only.

Dependencies and integration points: depends on `VIDEO_DEV`; selected symbols provide vb2 vmalloc buffers, V4L2 mem2mem scheduling, and media-controller integration expected by `vicodec-core.c`.

Risks: omitting selected dependencies would break compilation or runtime registration. The help text positions the driver as a test/reference device and recommends `N` for normal systems.

Test signals: Kconfig dependency resolution, module build as `m`, built-in build as `y`, and V4L2 compliance once loaded.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vicodec/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vicodec/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vicodec/Makefile

Purpose: Kbuild recipe for the vicodec module.

Important APIs/types/functions: `vicodec-objs := vicodec-core.o codec-fwht.o codec-v4l2-fwht.o`; `obj-$(CONFIG_VIDEO_VICODEC) += vicodec.o`.

Control flow: Kbuild links the V4L2 mem2mem core wrapper, raw FWHT codec, and V4L2 FWHT adapter into one module.

State and persistence: build metadata only.

Dependencies and integration points: ensures internal symbols from the FWHT codec and wrapper resolve inside the single `vicodec` module.

Risks: changing object order or omitting one object breaks exported-internal functions such as `v4l2_fwht_encode()`/`decode()` or `fwht_encode_frame()`/`decode_frame()`.

Test signals: module link success and `modinfo vicodec`/device registration smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vicodec/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vicodec/codec-fwht.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vicodec/codec-fwht.c

Purpose: raw Fast Walsh Hadamard Transform codec engine used by vicodec. It compresses/decompresses luma, chroma, and optional alpha planes using 8x8 FWHT blocks, quantization, run-length coding, inter-frame deltas, duplicate macroblock runs, and uncompressed-plane fallback.

Important APIs/types/functions: external entry points are `fwht_encode_frame()` and `fwht_decode_frame()`. Internal primitives include `fwht()`, `fwht16()`, `ifwht()`, `quantize_intra()`, `quantize_inter()`, `dequantize_intra()`, `dequantize_inter()`, `rlc()`, `derlc()`, `encode_plane()`, and `decode_plane()`. `zigzag`, `quant_table`, and `quant_table_p` shape coefficient ordering and quantization. `PFRAME_BIT`, `DUPS_MASK`, `ALL_ZEROS`, and FWHT flag bits define stream semantics.

Control flow: encoding rounds each plane to 8-pixel block boundaries. For each block, I/P choice defaults to I on intra frames and otherwise compares intra variance against delta variance. I blocks transform raw samples with an intra offset; P blocks transform signed deltas against the reference. Quantized coefficients are RLE-encoded in zigzag order, and consecutive identical RLE blocks are collapsed by incrementing duplicate counts in the prior block header. If encoded output approaches the per-plane raw-size budget, the plane is copied uncompressed into the output and marked with the appropriate uncompressed flag. Decoding walks the planes in the same order, expands RLE blocks with `derlc()`, dequantizes according to P/I state, inverse-transforms, adds reference deltas for P blocks, and writes saturated 8-bit samples.

State and persistence: `struct fwht_cframe` carries scratch coefficient arrays, QP values, RLE output pointer, and compressed size per frame. `struct fwht_raw_frame` supplies component pointers/steps and subsampling geometry. Reference frames are supplied by the caller and updated by the higher V4L2 layer, not persisted here.

Dependencies and integration points: uses kernel byteorder helpers, V4L2 FWHT flag definitions from videodev2, and layout metadata from `codec-fwht.h`. It is called by `codec-v4l2-fwht.c`, which supplies headers, pixel-format mapping, strides, and reference buffers.

Risks: malformed streams are partly contained by end-of-buffer checks and overflow signaling, but decoder correctness depends on accurate `cf->size` and caller-validated geometry. `encode_plane()` uses raw fallback to avoid expansion, but fallback replaces byte `0xff` with `0xfe` to preserve the magic sync invariant, which can alter full-range data. Duplicate macroblock encoding manipulates prior output in-place and relies on size equality and P/I bit compatibility. Rounding beyond visible dimensions means callers must provide coded buffers large enough for rounded accesses.

Test signals: round-trip tests across all supported pixel layouts, intra/P GOP tests, malformed RLE truncation tests returning false, uncompressed fallback by forcing incompressible input, duplicate-block compression using generated color bars, and sanitizer/KASAN-style checks around odd visible dimensions rounded to 8.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vicodec/codec-fwht.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vicodec/codec-fwht.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vicodec/codec-fwht.h

Purpose: public raw FWHT codec contract shared by the codec engine and V4L2 adapter.

Important APIs/types/functions: defines `FWHT_MAGIC1`, `FWHT_MAGIC2`, `vic_round_dim()`, `struct fwht_cframe_hdr`, `struct fwht_cframe`, `struct fwht_raw_frame`, raw codec flag bits, and prototypes for `fwht_encode_frame()` and `fwht_decode_frame()`. The header documents the compressed stream layout in detail.

Control flow: the header itself has no control flow, but it defines how encoded frames are structured: an 8-byte magic sequence, big-endian metadata, compressed-frame size, then per-plane RLE or raw payloads. Macroblock headers carry P-coded state and duplicate counts, and coefficient words carry zero-run length plus quantized coefficient.

State and persistence: `fwht_cframe_hdr` is serialized into compressed buffers. `fwht_cframe` and `fwht_raw_frame` are transient caller-owned structures for scratch and frame component layout.

Dependencies and integration points: includes Linux types, bitops, byteorder, and is consumed by `codec-fwht.c`, `codec-v4l2-fwht.h`, and `vicodec-core.c`. The serialized header interoperates with V4L2 FWHT userspace controls/formats.

Risks: the serialized ABI depends on big-endian fields and magic values; any extension must preserve sync and version handling. `vic_round_dim()` rounds dimensions after subsampling division and multiplication, so callers must understand coded versus visible dimensions.

Test signals: compile-time users of struct layout, encoded stream parser tests validating magic/version/size, and cross-endian encode/decode compatibility checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vicodec/codec-fwht.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vicodec/codec-v4l2-fwht.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vicodec/codec-v4l2-fwht.c

Purpose: V4L2-facing adapter for the raw FWHT codec. It maps V4L2 pixel formats to component pointers/strides, writes and validates FWHT headers, manages colorspace metadata, and bridges stateful/stateless encode/decode calls to `codec-fwht.c`.

Important APIs/types/functions: exported helpers include `v4l2_fwht_find_pixfmt()`, `v4l2_fwht_get_pixfmt()`, `v4l2_fwht_validate_fmt()`, `v4l2_fwht_find_nth_fmt()`, `v4l2_fwht_encode()`, and `v4l2_fwht_decode()`. `v4l2_fwht_pixfmts[]` describes packed, planar, semiplanar, RGB, HSV, alpha, and GREY layouts. `prepare_raw_frame()` translates a single V4L2 buffer pointer into luma/Cb/Cr/alpha pointers and component step sizes.

Control flow: encode validates `state->info`, prepares raw-frame pointers for the input buffer, adjusts chroma stride for three-plane and NV24/NV42 formats, calls `fwht_encode_frame()` using GOP state to decide intra/next-intra behavior, updates GOP count, and writes a `fwht_cframe_hdr` plus payload to output. Decode validates state info, FWHT version, magic, dimensions, pixel encoding, component count, chroma subsampling flags, and then prepares destination and reference raw frames before calling `fwht_decode_frame()`. Decoded header colorspace/xfer/ycbcr/quantization values are copied back into state.

State and persistence: `struct v4l2_fwht_state` owns visible/coded geometry, strides, GOP/QP state, colorspace metadata, reference-frame descriptor/buffer, compressed frame storage pointer, and a cached header for decode. Encoded headers persist per compressed frame.

Dependencies and integration points: depends on V4L2 pixel-format constants and FWHT flags from `videodev2.h`, raw FWHT functions from `codec-fwht.c`, and is used by `vicodec-core.c` for actual mem2mem processing.

Risks: all buffer pointer derivation assumes q_data sizeimage/stride are consistent with the selected pixel format. Version >=2 enforces pixel encoding and component counts; older versions default to three components, so compatibility paths must remain tested. Decode explicitly rejects resolution changes, leaving dynamic-resolution handling to the stateful decoder wrapper before calling this function.

Test signals: per-format pointer-layout round trips, GREY/RGB/HSV/alpha cases, header version/magic/flags rejection tests, GOP count behavior, and dynamic resolution rejection at this layer with acceptance in `vicodec-core.c` reconfiguration flow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vicodec/codec-v4l2-fwht.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vicodec/codec-v4l2-fwht.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vicodec/codec-v4l2-fwht.h

Purpose: V4L2 FWHT adapter interface and state definitions.

Important APIs/types/functions: `struct v4l2_fwht_pixfmt_info` captures pixel-format ID, bytes-per-line/sizeimage factors, component steps, subsampling, component/plane counts, and FWHT pixel encoding. `struct v4l2_fwht_state` stores selected format, geometry, stride/reference stride, GOP/QP values, colorspace metadata, reference frame, header, compressed buffer, and reference timestamp. Function prototypes expose pixel-format lookup/validation and encode/decode.

Control flow: no executable flow in the header; it defines the data contract used by vicodec core and the FWHT adapter.

State and persistence: `v4l2_fwht_state` is per vicodec context and persists across frames while queues stream. It carries the reference frame and GOP count that make stateful P-frame decoding/encoding possible. The `header` field is filled either from bytestream headers or stateless controls.

Dependencies and integration points: includes `codec-fwht.h` and uses V4L2 enum types. It is the interface between high-level V4L2 mem2mem code and the raw codec.

Risks: adding pixel formats requires keeping size multipliers, component counts, and subsampling flags consistent with both V4L2 queue sizing and raw codec pointer math.

Test signals: compile-time coverage through vicodec, per-format enumeration consistency, and stateless decode controls matching `v4l2_fwht_validate_fmt()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vicodec/codec-v4l2-fwht.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vicodec/vicodec-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vicodec/vicodec-core.c

Purpose: V4L2 mem2mem virtual codec driver exposing stateful encoder, stateful decoder, and stateless decoder video nodes backed by the FWHT codec.

Important APIs/types/functions: device/context types are `struct vicodec_dev`, `struct vicodec_dev_instance`, `struct vicodec_ctx`, and `struct vicodec_q_data`. Processing paths are `device_process()`, `device_run()`, `job_ready()`, and `get_next_header()`. V4L2 operations cover format enumeration/try/set/get, selection, encoder/decoder commands, event subscription, queue setup/prepare/queue/start/stop, controls, file open/release, request validation/queueing, and platform probe/remove. Controls include GOP size, I/P QP, min buffers, and `V4L2_CID_STATELESS_FWHT_PARAMS`.

Control flow: module init registers a platform device and driver. Probe registers a V4L2 device, optionally media controller, and three video-device instances. Open creates a filehandle context, initializes controls and q_data defaults, and creates an m2m context. For stateful encode, output raw frames are encoded into capture FWHT buffers. For stateful decode, `job_ready()` scans a continuous bytestream for FWHT magic/header, accumulates compressed payload across source buffers, raises source-change events when frame geometry/subsampling changes, and `device_run()` decodes into capture buffers. For stateless decode, each output buffer must be in a media request with FWHT params; `device_process()` imports request controls, resolves the reference capture buffer by timestamp for P frames, and decodes one frame.

State and persistence: per-filehandle state includes source/capture q_data, `v4l2_fwht_state`, compressed-frame scan offsets/counts, header matching progress, source-change flags, and reference buffers. Streaming allocates `ref_frame.buf` and compressed staging memory for stateful paths, then frees on stop/release. No disk persistence exists.

Dependencies and integration points: depends on V4L2 mem2mem, vb2-vmalloc, V4L2 controls/events/ioctls, media requests for stateless decode, media controller registration, and the FWHT adapter. Userspace sees `/dev/video*` nodes named `stateful-encoder`, `stateful-decoder`, and `stateless-decoder`.

Risks: bytestream parsing is complex and must preserve offsets across buffers; invalid headers intentionally advance one byte after magic to resync. Dynamic-resolution flow sets source-change, emits LAST on capture, and requires userspace reconfiguration. Stateless decode requires exactly one buffer and required controls per request; missing or extra request objects fail validation. Buffer size calculations must match format descriptors and FWHT rounded dimensions to avoid rejection or overflow. Reference buffers in stateless mode are obtained from capture queue timestamps and must not be in error state.

Test signals: `v4l2-compliance` for all three nodes, encode/decode round trips, stateful decoder bytestream split across many source buffers, source-change event and restart flow, EOS behavior for encoder/decoder commands, stateless media-request validation failures/success, all supported pixfmt enumeration in single- and multi-planar module modes, and fault injection for allocation failures in stream start/probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vicodec/vicodec-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/Kconfig

Purpose: Kconfig definition for the virtual DVB test driver.

Important APIs/types/functions: defines `CONFIG_DVB_VIDTV` as tristate "Virtual DVB Driver (vidtv)", depending on DVB core, media support, and I2C, and selecting CRC32.

Control flow: when enabled, Kbuild includes the virtual tuner, demodulator, and bridge/mux modules from the vidtv Makefile.

State and persistence: build-time only.

Dependencies and integration points: depends on DVB and I2C frameworks because vidtv models bridge-to-demod/tuner attachment via virtual I2C clients. CRC32 supports PSI table CRC generation in non-listed PSI code used by the listed channel/mux files.

Risks: missing CRC32 selection breaks PSI table generation; missing I2C prevents virtual module probing.

Test signals: Kconfig dependency tests and module build/load of `dvb_vidtv_*` components.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/Makefile

Purpose: Kbuild recipe for vidtv's virtual DVB modules.

Important APIs/types/functions: builds `dvb-vidtv-tuner.o`, `dvb-vidtv-demod.o`, and `dvb-vidtv-bridge.o`; the bridge module links `vidtv_bridge.o`, `vidtv_common.o`, `vidtv_ts.o`, `vidtv_psi.o`, `vidtv_pes.o`, `vidtv_s302m.o`, `vidtv_channel.o`, and `vidtv_mux.o`.

Control flow: enabling `CONFIG_DVB_VIDTV` builds all three modules. The bridge module depends on the mux, channel, PES, PSI, TS, and S302M pieces for transport stream generation.

State and persistence: build metadata only.

Dependencies and integration points: module names match `dvb_module_probe()` calls in `vidtv_bridge.c` for `dvb_vidtv_tuner` and `dvb_vidtv_demod`.

Risks: object/module naming mismatches prevent bridge probe from loading its virtual tuner/demod clients. Bridge object omissions break runtime stream generation.

Test signals: module link/load, `modprobe dvb_vidtv_bridge` causing tuner/demod probe, and symbol resolution for all vidtv helper objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_bridge.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_bridge.c

Purpose: platform bridge for vidtv. It registers a virtual DVB adapter, creates virtual I2C tuner/demod clients, wires DVB demux/dmxdev/frontends, and starts/stops the MPEG-TS mux when demux feeds are active.

Important APIs/types/functions: module parameters control lock-loss probabilities, tune/power delays, valid DVB-T/C/S frequencies, frequency tolerance, SI/PCR periods, mux rate, PCR PID, mux buffer size, and adapter number. Major functions include `vidtv_start_streaming()`, `vidtv_stop_streaming()`, `vidtv_start_feed()`, `vidtv_stop_feed()`, `vidtv_bridge_i2c_register_adap()`, `vidtv_bridge_probe_demod()`, `vidtv_bridge_probe_tuner()`, `vidtv_bridge_dvb_init()`, `vidtv_bridge_probe()`, and `vidtv_bridge_remove()`. `vidtv_bridge_on_new_pkts_avail()` injects packets into `dvb_dmx_swfilter_packets()` when demod lock is present.

Control flow: module init registers a platform device and driver. Probe allocates `struct vidtv_dvb`, initializes optional media controller data, registers a virtual I2C adapter and DVB adapter, probes demod/tuner modules using `dvb_module_probe()`, registers frontends, initializes DVB demux and demux device, connects demux frontends, and registers media device if configured. Starting the first demux feed grabs `feed_lock`, increments `nfeeds`, creates a mux with configured timing/network IDs, starts its work thread, and returns the active feed count. Stopping the last feed stops and destroys the mux. Packet callbacks drop TS packets if the demod reports loss of full lock.

State and persistence: `struct vidtv_dvb` holds platform device, frontend/client pointers, DVB adapter/demux/dmxdev, feed count, feed lock, streaming flag, mux pointer, and optional media device. Runtime state is reset on module remove; no persistence exists.

Dependencies and integration points: integrates with platform driver core, I2C adapter/client model, DVB adapter/frontend/demux/dmxdev APIs, media controller, virtual tuner/demod modules, and `vidtv_mux`. Satellite frequency module parameters are translated from Ku-band kHz to tuner IF Hz before tuner probe.

Risks: `NUM_FE` is fixed at one. Virtual I2C `master_xfer()` is a stub, acceptable for platform-data probing but not real bus IO. `vidtv_stop_feed()` decrements `nfeeds` without an explicit underflow guard. Mux buffer sizing is derived from mux rate/sleep interval and clamped; too small a module parameter may still stress overflow guards in TS writers. Cleanup paths must keep tuner/demod/frontend unregister order correct.

Test signals: `modprobe dvb_vidtv_bridge`, DVB adapter/frontend/demux node creation, tuning to configured frequencies, starting/stopping demux feeds, packet flow through `dvb_dmx_swfilter_packets()`, lock-loss simulation by module params, and media-controller graph registration when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_bridge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_bridge.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_bridge.h

Purpose: bridge state definition for vidtv.

Important APIs/types/functions: defines `NUM_FE` as 1, `VIDTV_PDEV_NAME` as `vidtv`, and `struct vidtv_dvb` containing platform, frontend, DVB adapter, demux/dmxdev, demux frontends, I2C adapter/clients, feed count/lock, streaming flag, mux pointer, and optional media device.

Control flow: no executable flow; `vidtv_bridge.c` uses this structure across probe, feed start/stop, streaming, and remove.

State and persistence: all bridge runtime state is centralized in `struct vidtv_dvb`. The feed lock protects feed-count and streaming transitions.

Dependencies and integration points: includes Linux I2C/platform types and DVB/media demux/frontend/media-device headers, plus `vidtv_mux.h`.

Risks: fixed one-frontend layout limits scaling; the include guard closing comment contains a typo but the macro itself is correct.

Test signals: build coverage and runtime bridge probe/start/stop paths exercising every field.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_bridge.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_channel.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_channel.c

Purpose: defines vidtv's hardcoded channel abstraction and builds PSI/SI table inputs from channels. The current implementation creates an audio-only Beethoven channel with an S302M encoder, PAT/PMT/SDT/EIT/NIT entries, and service descriptors.

Important APIs/types/functions: exported functions are `vidtv_channel_s302m_init()`, `vidtv_channel_si_init()`, `vidtv_channel_si_destroy()`, `vidtv_channels_init()`, and `vidtv_channels_destroy()`. Internal helpers clone/concatenate channel EIT events, SDT services, PAT programs, match PMT sections to channels, build NIT service lists, and destroy encoder chains.

Control flow: channel init allocates a `struct vidtv_channel`, duplicates the service name, creates SDT service plus service descriptor, PAT program, PMT stream plus registration descriptor for S302M, initializes the S302M encoder, and creates an EIT event plus short-event descriptor. `vidtv_channel_si_init()` creates PAT and SDT tables, concatenates programs/services/events from all channels, builds a service list for NIT, creates NIT and EIT tables, assigns program/service/event lists, creates PMT sections for each PAT entry, and attaches cloned stream descriptors to matching PMTs. Destructors walk allocated linked lists and call PSI/encoder destroy functions.

State and persistence: channel state lives under `m->channels` in the mux and owns linked PSI fragments plus encoder chains. SI table state lives under `m->si` until mux destruction.

Dependencies and integration points: relies on `vidtv_psi` constructors/destructors and descriptor cloning, `vidtv_s302m_encoder_init()`, and mux fields such as transport stream ID, network ID/name, PCR PID, and device for warnings.

Risks: error paths are allocation-heavy and must avoid leaks/double frees across partially built linked lists. `vidtv_channel_build_service_list()` uses `s->descriptor->type` inside a descriptor loop instead of `desc->type`, so additional descriptor chains could be mishandled. `vidtv_channel_pat_prog_cat_into_new()` adds a NIT PAT entry after the loop but does not check the return value. Only one hardcoded channel exists, limiting coverage of multi-channel concatenation unless tests add more channels.

Test signals: load/start stream and verify PAT/PMT/SDT/NIT/EIT packets, KASAN/leak checks on mux init failure injection, multi-channel test injection for concatenation, and DVB userspace scans seeing the Beethoven service/event metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_channel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_channel.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_channel.h

Purpose: channel abstraction interface for vidtv.

Important APIs/types/functions: `struct vidtv_channel` contains name, transport stream ID, SDT service, PAT program number/program, PMT streams, encoder chain, EIT events, and next pointer. Prototypes expose SI init/destroy, hardcoded channel init/destroy, and S302M channel construction.

Control flow: no executable flow; implementations build linked channel lists and derive PSI tables/encoder polling from them.

State and persistence: channel instances persist for the lifetime of a mux and own PSI fragments plus encoders.

Dependencies and integration points: includes `vidtv_encoder.h`, `vidtv_mux.h`, and `vidtv_psi.h`, making it the bridge between service metadata, mux operation, and elementary stream encoders.

Risks: ownership is pointer-heavy; callers must use the matching destroy helpers. Adding channel types requires careful PAT/PMT/SDT/EIT descriptor consistency and encoder/PID uniqueness.

Test signals: compile coverage, mux init/destroy, and service scan output for generated channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_channel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_common.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_common.c

Purpose: safe bounded memory helpers for vidtv's in-kernel MPEG-TS generator.

Important APIs/types/functions: `vidtv_memcpy()` and `vidtv_memset()` validate `to_offset + len <= to_size` before writing, log ratelimited overflow errors, and return the number of bytes actually written.

Control flow: each helper checks the target bounds, returns 0 on overflow, otherwise delegates to `memcpy()`/`memset()` and returns `len`.

State and persistence: no state; helpers are pure wrappers except for logging.

Dependencies and integration points: used by PES, TS, and PSI writers to prevent buffer overruns while constructing MPEG-TS packets in kernel memory. Uses `pr_err_ratelimited()`.

Risks: `to_offset + len` can theoretically wrap `size_t` before comparison; callers mostly use bounded TS sizes, but overflow-safe addition would be stronger. Returning 0 lets writers continue with shorter-than-expected output, so callers must validate packet alignment/byte counts.

Test signals: unit-style boundary tests at exact fit, one-byte overflow, zero length, and writer-level tests verifying mis-sized mux buffers log and avoid writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_common.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_common.h

Purpose: shared constants and bounded memory helper declarations for vidtv.

Important APIs/types/functions: defines 90 kHz and 27 MHz clock constants, mux sleep intervals, and prototypes for `vidtv_memcpy()`/`vidtv_memset()`.

Control flow: header only.

State and persistence: no state.

Dependencies and integration points: included by TS/PES/mux/common code for timing constants and safe writer helpers.

Risks: changing clock constants affects PCR/PTS calculations across mux and PES code. Sleep interval changes affect mux rate buffer sizing and output cadence.

Test signals: build coverage and transport stream timing validation through PCR/PTS analysis.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_demod.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_demod.c

Purpose: virtual DVB demodulator I2C driver. It exposes a `dvb_frontend` supporting DVB-T/T2/C/S/S2, delegates tuning to the virtual tuner, simulates lock and signal statistics, and provides frontend callbacks used by the bridge.

Important APIs/types/functions: CNR threshold tables map delivery system/modulation/FEC to "ok" and "good" values. Core functions include `vidtv_match_cnr_s()`, `vidtv_clean_stats()`, `vidtv_demod_update_stats()`, `vidtv_demod_read_status()`, `vidtv_demod_set_frontend()`, `vidtv_demod_release()`, `vidtv_demod_i2c_probe()`, and `vidtv_demod_i2c_remove()`. `vidtv_demod_ops` defines supported delivery systems, frontend caps, and callback table.

Control flow: probe allocates `vidtv_demod_state`, copies frontend ops and bridge-provided config, stores the frontend in I2C client data, and initializes stats. Tuning calls tuner `set_params()`, reads RF strength/CNR, sets full lock if CNR is nonzero, updates stats, and closes the I2C gate if present. Status reads may randomly drop lock when CNR is below threshold or recover lock when signal improves, based on module-provided probabilities. Stats report strength/CNR with slight random variation and expose BER/block counters only when locked.

State and persistence: `vidtv_demod_state` holds frontend, config, current `enum fe_status`, and latest tuner CNR. State is per I2C client and freed on frontend release/remove.

Dependencies and integration points: integrates with I2C driver core, DVB frontend ops, tuner ops supplied by virtual tuner, random number helpers, and bridge platform data. Bridge retrieves the frontend pointer from I2C client data.

Risks: `vidtv_demod_i2c_probe()` names platform data as `struct vidtv_tuner_config *` even though it copies into `vidtv_demod_config`; this works only if the pointer actually points to compatible demod config from the bridge, and the type is misleading. Random lock-loss behavior can make tests flaky unless probabilities are controlled. `read_signal_strength()` returns `uvalue` while strength is filled via `svalue`, which may be semantically odd for signed dBm-like values.

Test signals: tune to valid/invalid virtual frequencies via tuner, frontend status transitions with probabilities set to 0/100, stats scale changes with lock, delivery-system threshold matching, module probe/remove, and DVB scan behavior through the bridge.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_demod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_demod.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_demod.h

Purpose: data contracts for the virtual DVB demodulator.

Important APIs/types/functions: defines `struct vidtv_demod_cnr_to_qual_s`, `struct vidtv_demod_config`, and `struct vidtv_demod_state`.

Control flow: header only; used by bridge and demod implementation to pass simulation parameters and store frontend state.

State and persistence: `vidtv_demod_state` persists for the I2C client/frontend lifetime and stores current status and tuner CNR. Config probabilities are copied at probe.

Dependencies and integration points: includes DVB frontend types from Linux and media headers. Bridge supplies `vidtv_demod_config` as platform data and reads the resulting frontend from client data.

Risks: config fields are `u8`; module params are unsigned int in bridge and truncate when assigned, so values over 255 are not meaningful and probability logic expects 0-100.

Test signals: compile checks, bridge-to-demod platform data propagation, and frontend status behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_demod.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_encoder.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_encoder.h

Purpose: generic encoder abstraction for vidtv elementary streams.

Important APIs/types/functions: defines `enum vidtv_encoder_id` with `S302M`, `struct vidtv_access_unit` for payload slices with PTS/DTS/size/offset, note-frequency enum for generated audio sources, and `struct vidtv_encoder` with buffers, source offsets, encoder callbacks, stream IDs/PIDs, timing, sync pointer, and linked-list chaining.

Control flow: no executable flow; concrete encoders such as S302M implement `encode`, `clear`, and `destroy`, and the mux polls each encoder and packetizes its access units.

State and persistence: encoder instances persist under channel objects during mux lifetime. They own encoded buffers, access-unit lists, source state, sample count, and encoder-specific context.

Dependencies and integration points: used by `vidtv_channel.c`, `vidtv_mux.c`, `vidtv_pes.c`, and concrete S302M code.

Risks: callback and ownership contracts are manual. Mux assumes `encode()` populates access units and `clear()` resets state after packetization. Adding encoders requires PID/stream ID correctness and cleanup symmetry.

Test signals: S302M stream generation, mux polling of chained encoders, access-unit packetization, and destroy-path leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_mux.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_mux.c

Purpose: MPEG-TS muxer for vidtv. It periodically emits PCR, PSI/SI sections, encoder payloads packetized as PES, and null packets into a mux buffer, then hands complete TS packets to the bridge callback.

Important APIs/types/functions: exported functions are `vidtv_mux_init()`, `vidtv_mux_destroy()`, `vidtv_mux_start_thread()`, and `vidtv_mux_stop_thread()`. Internal pieces manage per-PID continuity counters (`vidtv_mux_get_pid_ctx()`, `vidtv_mux_create_pid_ctx_once()`, `vidtv_mux_pid_ctx_init()`), timing (`vidtv_mux_update_clk()`, `vidtv_mux_should_push_pcr()`, `vidtv_mux_should_push_si()`), SI output (`vidtv_mux_push_si()`), PCR output (`vidtv_mux_push_pcr()`), encoder packetization (`vidtv_mux_packetize_access_units()`), polling (`vidtv_mux_poll_encoders()`), null padding, and the workqueue loop `vidtv_mux_tick()`.

Control flow: init allocates mux state and buffer, copies config, initializes channels if none supplied, builds SI tables, initializes work item, and builds PID contexts for PCR/null/PAT/SDT/NIT/EIT/PMT PIDs. Starting sets streaming, records start jiffies, and schedules work. Each tick updates a 27 MHz clock, emits PCR/SI if due, polls encoders and packetizes access units into PES/TS packets, pads 256 null packets, validates TS alignment, invokes the bridge callback with packet count, clears the buffer, updates DVB frontend counters, simulates low pre-BER, and sleeps. Stop clears streaming and cancels work; destroy stops and frees PID contexts, SI/channels, network name, buffer, and mux.

State and persistence: `struct vidtv_mux` owns timing counters, PID continuity hash table, mux buffer/offset, channel list, SI tables, streamed PCR/SI counts, work item, streaming flag, network IDs/name, and callback private data. State is per active stream and recreated when feeds restart.

Dependencies and integration points: depends on channel/SI constructors, PSI/TS/PES writers, encoder abstraction, DVB frontend stats, Linux workqueue/jiffies/vmalloc/hash APIs, and bridge callbacks.

Risks: `vidtv_mux_poll_encoders()` adds `au_nbytes` to `m->mux_buf_offset` after `vidtv_mux_packetize_access_units()` already advanced the offset, which appears to double-count encoder bytes. TS writer overflow guards may mask rather than fail buffer exhaustion. Workqueue loop is cooperative via `streaming`; long writer paths delay stop. PID context creation must include every PID used or null dereferences are possible. Timing and mux-rate padding are approximate, not broadcast-grade.

Test signals: transport stream packet alignment, continuity counter monotonicity per PID, PCR/SI cadence, DVB stats increments, service scan success, mux start/stop under repeated feed changes, buffer-overflow log tests with small buffers, and review/test around encoder offset accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_mux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_mux.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_mux.h

Purpose: muxer data structures and public interface for vidtv.

Important APIs/types/functions: defines `struct vidtv_mux_timing`, `struct vidtv_mux_si`, `struct vidtv_mux_pid_ctx`, `struct vidtv_mux`, `struct vidtv_mux_init_args`, and prototypes for init/destroy/start/stop.

Control flow: header only; implementation uses timing fields to decide PCR/SI cadence, SI fields to write PAT/PMT/SDT/NIT/EIT, PID contexts for continuity counters, and callback fields to deliver generated TS packets.

State and persistence: all mux runtime state is in `struct vidtv_mux` for the lifetime of a stream. `pid_ctx` hash table persists continuity counters per PID.

Dependencies and integration points: includes Linux hashtable/workqueue, DVB frontend, and `vidtv_psi.h`. Referenced by bridge and channel code.

Risks: initialization args pass raw pointers/callbacks; lifetime must outlive mux. Adding more channels/encoders must ensure PID contexts and SI metadata remain consistent.

Test signals: build coverage, mux init/destroy with and without supplied channels, and TS analyzer validation of emitted streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_mux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_pes.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_pes.c

Purpose: packetizes one encoder access unit into a PES packet split across MPEG-TS packets, including optional PTS/DTS fields, adaptation-field stuffing, optional PCR, and payload copying.

Important APIs/types/functions: public entry point is `vidtv_pes_write_into()`. Internal helpers compute optional/header lengths, write PES header stuffing, encode PTS/DTS (`vidtv_pes_write_pts_dts()`), write PES headers (`vidtv_pes_write_h()`), write PCR bits, write TS adaptation stuffing, and write TS headers. Constants define private stream ID for S302M, PES header stuffing limit, and TS stuffing limit.

Control flow: `vidtv_pes_write_into()` aligns the starting offset if needed, then loops while access-unit bytes remain. The first TS packet reserves space for the PES header and optional PES stuffing; the first packet also reserves PCR adaptation bytes. For the final packet it computes stuffing to maintain 188-byte TS alignment and caps stuffing to the allowed maximum by reducing payload if necessary. Each iteration writes a TS header/adaptation field, writes the PES header once, copies payload, advances source pointer, and decreases remaining bytes.

State and persistence: no persistent state except the caller-owned continuity counter updated through `vidtv_ts_inc_cc()`. `last_pcr` is local and currently only updated when PCR is written.

Dependencies and integration points: uses vidtv common bounded memory helpers, TS header definitions/helpers, encoder IDs, and kernel endian/math helpers. Called by `vidtv_mux_packetize_access_units()` for each access unit.

Risks: pointer arithmetic on `void *` is a GNU C extension accepted in kernel builds. If bounded writes return 0, the loop may still continue based on logical payload sizes, so output can be shorter than expected without hard failure. PES length is always set to optional length plus AU length and does not use the PES_MAX_LEN zero-length convention mentioned in the header. PCR is written only on the first TS packet for an AU. The alignment recovery path pads with fill bytes outside a normal TS packet header, so it is a last-resort warning path.

Test signals: TS packet analyzer checks for 188-byte alignment, payload-unit-start indicator on the first packet, continuity increments, valid PTS fields, S302M private stream ID, last-packet stuffing behavior, large AU spanning many TS packets, and small-buffer overflow tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_pes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_pes.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_pes.h

Purpose: PES packetization structure definitions and API for vidtv.

Important APIs/types/functions: defines PES constants, packed structs for optional PTS and PTS/DTS fields, optional PES header flags, PES base header, `struct pes_header_write_args`, `struct pes_ts_header_write_args`, `struct pes_write_args`, and prototype `vidtv_pes_write_into()`.

Control flow: header only; it describes the inputs used by `vidtv_pes.c` to write PES headers and split payload into TS packets.

State and persistence: packetization state is caller supplied. The continuity counter pointer lets the writer persist TS continuity across calls for a PID.

Dependencies and integration points: includes Linux types and `vidtv_common.h`; used by mux and PES implementation.

Risks: callers must provide valid buffer size/offset, access-unit length, stream ID/PID, continuity counter, and timestamp flags. Incorrect values can produce syntactically invalid TS even if memory writes remain bounded.

Test signals: compile coverage, PES/TS conformance checks for generated headers, and mux-level service playback/scan tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_pes.h -->
