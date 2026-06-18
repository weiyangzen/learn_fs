# subset-b-004131 Research

This grouped report covers the requested media platform Kconfig, Makefile, Allegro DVT encoder, Allegro mailbox/NAL helpers, and Amlogic C3 ISP capture files. Each section is bounded by source-path markers for deterministic reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/Kconfig

## Purpose

This top-level media platform Kconfig file gates the whole `drivers/media/platform` subtree. It defines broad user-visible switches for platform media drivers, V4L platform devices, SDR platform devices, DVB platform devices, and V4L2 memory-to-memory drivers, then sources per-vendor platform Kconfig files in alphabetic order.

## Important APIs, Types, And Symbols

- `MEDIA_PLATFORM_DRIVERS` is a `menuconfig` defaulting to `y`; every later symbol in this file is guarded by `if MEDIA_PLATFORM_DRIVERS`.
- `V4L_PLATFORM_DRIVERS`, `SDR_PLATFORM_DRIVERS`, `DVB_PLATFORM_DRIVERS`, and `V4L_MEM2MEM_DRIVERS` are umbrella booleans used by child drivers.
- `VIDEO_MEM2MEM_DEINTERLACE` and `VIDEO_MUX` are ancillary non-SoC-specific platform drivers selected directly from this file.
- `source "drivers/media/platform/<vendor>/Kconfig"` lines integrate Allegro DVT, Amlogic, and many other SoC/vendor subtrees.

## Control Flow

Kconfig evaluation enters the menu when `MEDIA_PLATFORM_DRIVERS` is enabled. Users or defconfigs can enable the category booleans, and later sourced child files use those category symbols as dependencies. The file has no runtime control flow; it controls compile-time visibility and dependency resolution.

## State And Persistence

The persistent state is the kernel configuration generated from these symbols. Choices are stored in `.config` and affect which objects are built. There is no runtime state.

## Dependencies And Integration Points

This file integrates with the broader media subsystem through symbols such as `VIDEO_DEV`, `MEDIA_SDR_SUPPORT`, and `MEDIA_DIGITAL_TV_SUPPORT`. It integrates vendor subtrees by sourcing child Kconfig files, including the Allegro DVT encoder and Amlogic C3 ISP tree researched in this item.

## Risks

Dependency mistakes here can hide large classes of drivers or expose drivers without required core media support. Ordering is intentionally alphabetic; merge conflicts or misplaced source lines can make maintenance harder. Broad defaults such as `MEDIA_PLATFORM_DRIVERS=y` affect build coverage across architectures.

## Test Signals

Useful validation includes `make menuconfig` visibility checks, `make olddefconfig` on representative configs, allmodconfig build coverage, and verifying that enabling `VIDEO_ALLEGRO_DVT` or `VIDEO_C3_ISP` is only possible when their dependencies are satisfied.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/Makefile

## Purpose

This Makefile descends into platform media driver subdirectories and builds two ancillary platform driver objects. It mirrors the Kconfig vendor list so that each child directory can decide its own object inclusion from Kconfig symbols.

## Important APIs, Types, And Symbols

- `obj-y += allegro-dvt/`, `obj-y += amlogic/`, and similar lines always visit child directories during media platform builds.
- `obj-$(CONFIG_VIDEO_MEM2MEM_DEINTERLACE) += m2m-deinterlace.o` builds the generic deinterlace driver when selected.
- `obj-$(CONFIG_VIDEO_MUX) += video-mux.o` builds the ancillary video multiplexer when selected.

## Control Flow

Kbuild evaluates this Makefile when the media platform subtree is entered. Directory traversal happens unconditionally through `obj-y` entries; the child Makefiles contain the final `CONFIG_*` gates for their driver objects.

## State And Persistence

There is no runtime state. Build output state is the set of compiled objects and modules produced from the current `.config`.

## Dependencies And Integration Points

This file is coupled to `drivers/media/platform/Kconfig` by directory naming and ordering. It also integrates with Kbuild's recursive object traversal rules and with child directories such as `allegro-dvt/` and `amlogic/`.

## Risks

Adding a Kconfig source without a matching Makefile directory entry, or the reverse, can create confusing config/build mismatches. Alphabetic ordering comments are maintenance constraints but not enforced by Kbuild.

## Test Signals

Run `make drivers/media/platform/` or allmodconfig builds after directory changes. Confirm that selected child modules, for example `allegro.o` and `c3-isp.o`, are reached by the traversal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/Kconfig

## Purpose

This Kconfig file exposes the Allegro DVT Video IP Core encoder driver as `VIDEO_ALLEGRO_DVT`. The help text identifies the hardware as an Allegro DVT encoder IP used in Xilinx ZynqMP EV family devices, called VCU in Xilinx documentation.

## Important APIs, Types, And Symbols

- `VIDEO_ALLEGRO_DVT` is a tristate driver symbol.
- It depends on `V4L_MEM2MEM_DRIVERS`, `VIDEO_DEV`, and either `ARCH_ZYNQMP` or `COMPILE_TEST`.
- It selects `V4L2_MEM2MEM_DEV`, `VIDEOBUF2_DMA_CONTIG`, and `REGMAP_MMIO`.
- The module name is documented as `allegro`.

## Control Flow

The symbol is visible only when the top media platform and memory-to-memory dependencies are enabled. If selected as built-in or module, the corresponding Makefile builds `allegro.o`.

## State And Persistence

The only persistent state is the `.config` value for `VIDEO_ALLEGRO_DVT`. At runtime, driver state is implemented in `allegro-core.c`, not here.

## Dependencies And Integration Points

The selected dependencies match the implementation: the driver registers a V4L2 mem2mem video node, uses contiguous DMA buffers through vb2, and maps MCU/SRAM register spaces through regmap MMIO.

## Risks

The dependency on `ARCH_ZYNQMP || COMPILE_TEST` prevents accidental visibility on unrelated platforms, but compile-test builds still need headers for the media and regmap APIs. Missing selected dependencies would cause link or compile failures in the driver body.

## Test Signals

Check Kconfig visibility on ZynqMP defconfigs and allmodconfig. A successful module build should produce `allegro.ko` when the symbol is set to `m`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/Makefile

## Purpose

This Makefile builds the Allegro DVT encoder module from the core driver, mailbox protocol helpers, and H.264/HEVC RBSP/NAL helper files.

## Important APIs, Types, And Symbols

- `allegro-objs := allegro-core.o allegro-mail.o` defines the main module object list.
- Additional objects are `nal-rbsp.o`, `nal-h264.o`, and `nal-hevc.o`.
- `obj-$(CONFIG_VIDEO_ALLEGRO_DVT) += allegro.o` ties the aggregate object to the Kconfig symbol.

## Control Flow

Kbuild aggregates all listed objects into one `allegro` module or built-in object when `VIDEO_ALLEGRO_DVT` is enabled. There is no runtime logic in the Makefile.

## State And Persistence

Build artifacts are the only state. Runtime state lives in the compiled C files.

## Dependencies And Integration Points

The object list mirrors internal dependencies: `allegro-core.c` calls `allegro-mail.c` for firmware message serialization and uses `nal-rbsp.c`, `nal-h264.c`, and `nal-hevc.c` to synthesize codec parameter-set NAL units.

## Risks

If an object is omitted, link failures or missing exported helper symbols will occur. Because helper APIs are local to the module but some functions are exported, changes should keep symbol visibility and module composition consistent.

## Test Signals

Build `CONFIG_VIDEO_ALLEGRO_DVT=m` and inspect that `allegro.ko` includes all helper objects. Linker errors around `nal_*` or `allegro_*mail*` symbols point directly to this Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/allegro-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/allegro-core.c

## Purpose

`allegro-core.c` is the main V4L2 mem2mem encoder driver for Allegro DVT AL5E/VCU hardware. It probes a platform device, loads MCU and codec firmware, initializes mailbox communication, exposes a `/dev/video*` mem2mem encoder, accepts raw NV12 output buffers, returns H.264 or HEVC elementary streams, and injects generated VPS/SPS/PPS/filler NAL units around firmware-produced frame payloads.

## Important APIs, Types, And Functions

- Device/channel state: `struct allegro_dev` owns V4L2 device/video device state, regmaps, clocks, firmware buffers, mailboxes, runtime init state, and the channel list. `struct allegro_channel` owns one open file context, V4L2 controls, negotiated formats, MCU channel ids, internal buffer lists, vb2 shadow lists, and completion/error state.
- Firmware compatibility: `struct fw_info` and `supported_firmware[]` identify known firmware pairs by firmware file size and set mailbox offsets, message version, and suballocator size.
- Address conversion helpers: `to_mcu_addr()`, `to_mcu_size()`, and `to_codec_addr()` translate CPU DMA addresses to MCU/codec address spaces and warn if an address is outside expected windows.
- Mailbox helpers: `allegro_mbox_init()`, `allegro_mbox_write()`, `allegro_mbox_read()`, `allegro_mbox_send()`, and `allegro_mbox_notify()` implement ring-buffer transfer through SRAM-backed mailbox registers.
- MCU message senders: `allegro_mcu_send_init()`, `allegro_mcu_send_create_channel()`, `allegro_mcu_send_destroy_channel()`, `allegro_mcu_send_put_stream_buffer()`, and `allegro_mcu_send_encode_frame()`.
- Channel creation/destruction: `fill_create_channel_param()`, `allegro_create_channel()`, `allegro_destroy_channel()`, `allegro_handle_create_channel()`, and buffer allocation helpers create firmware channels and push firmware-requested internal buffers.
- Bitstream header generation: `allegro_h264_write_sps()`, `allegro_h264_write_pps()`, `allegro_hevc_write_vps()`, `allegro_hevc_write_sps()`, and `allegro_hevc_write_pps()` fill NAL helper structs from V4L2 state.
- Frame completion: `allegro_channel_finish_frame()` validates firmware partition offsets, copies metadata, writes non-VCL NAL units into reserved capture-buffer space, marks source and destination buffers done, and emits EOS/keyframe flags.
- V4L2/vb2 entry points: `allegro_open()`, `allegro_release()`, format ioctls, stream parameter ioctls, `allegro_queue_setup()`, `allegro_buf_prepare()`, `allegro_buf_queue()`, `allegro_start_streaming()`, `allegro_stop_streaming()`, and `allegro_device_run()`.
- Platform/power flow: `allegro_probe()`, `allegro_remove()`, `allegro_fw_callback()`, `allegro_mcu_hw_init()`, `allegro_mcu_hw_deinit()`, `allegro_runtime_resume()`, and `allegro_runtime_suspend()`.

## Control Flow

Probe allocates `allegro_dev`, maps named `regs` and `sram` resources through regmap, looks up Xilinx VCU settings, gets core and MCU clocks, registers an IRQ thread, registers a V4L2 device, and starts asynchronous firmware loading. The firmware callback requests both `al5e_b.fw` and `al5e.fw`, matches their sizes against `supported_firmware[]`, enables runtime PM, resets the MCU, copies MCU firmware into SRAM, copies codec firmware into coherent DMA memory, initializes mailboxes, waits for firmware `INIT`, sends suballocator configuration, initializes the V4L2 mem2mem core, and registers the video node.

On open, the driver creates an `allegro_channel`, initializes controls for H.264, HEVC, bitrate, QP, GOP size, and the Allegro encoder-buffer control, creates source and destination vb2 queues via `v4l2_m2m_ctx_init()`, and links the channel into the device list. Capture stream-on triggers `allegro_create_channel()`: controls are grabbed, a unique user id is allocated, the create-channel blob is encoded and DMA-addressed, and the driver waits up to 5 seconds for firmware response. The response sets `mcu_channel_id`, decodes firmware-adjusted config, allocates intermediate and reference buffers, and sends those buffers back to firmware.

For each mem2mem job, `allegro_device_run()` removes one destination and one source buffer, sends the destination as a stream buffer, sends the source as an encode-frame request, records pointer handles in shadow lists, and finishes the mem2mem job immediately; actual completion is asynchronous through the IRQ thread. `allegro_irq_thread()` drains status mailbox messages and dispatches them. Encode-frame responses call `allegro_channel_finish_frame()`, which maps handles back to vb2 buffers, checks firmware error code and partition table bounds, writes parameter-set/filler NAL units into the pre-reserved offset area, sets payload/data-offset/keyframe metadata, and completes buffers.

Stop streaming tears down shadow lists and queued buffers; capture stop also destroys the firmware channel. Removal unregisters the video device, releases mem2mem state, deinitializes MCU hardware, frees codec firmware DMA memory, disables runtime PM, and unregisters V4L2 state.

## State And Persistence

Persistent runtime state is in memory and hardware registers. Device-level state includes firmware compatibility, suballocator/coherent firmware buffers, mailbox ring positions in SRAM, runtime PM clock state, and registered channels. Channel-level state includes negotiated raw and encoded formats, codec choice, frame rate, V4L2 control values, MCU channel id, firmware-requested internal buffers, source and stream shadow lists, frame sequences, and last error. The driver stores no data across module unload or reboot.

Mailbox state persists in the device SRAM head/tail words while the device is initialized. Firmware files are requested from the kernel firmware loader but not modified. V4L2 controls become immutable for a channel while the MCU channel exists via `v4l2_ctrl_grab()`.

## Dependencies And Integration Points

The driver depends on V4L2 core, V4L2 controls/events/ioctls, V4L2 mem2mem, videobuf2 DMA-contig, regmap MMIO, runtime PM, firmware loading, platform resources, IRQs, clocks, and Xilinx VCU syscon settings. It integrates with `allegro-mail.h/.c` for mailbox protocol serialization and `nal-h264`/`nal-hevc` helpers for generated parameter-set/filler NALs. Device tree integration is through compatible string `allegro,al5e-1.1`, named memory resources `regs` and `sram`, clocks `core_clk` and `mcu_clk`, and one IRQ.

## Risks

The firmware match uses firmware file sizes as ids, which is simple but fragile if firmware binaries change size without an intended protocol change. Mailbox wrap handling assumes message headers do not wrap and requires size alignment; corruption in SRAM head/tail values can lead to `-EIO`. `v4l2_cpb_size_to_mcu()` divides by bitrate in kbps, so zero bitrate or inconsistent control ranges would be dangerous. Parameter-set generation assumes enough reserved bytes before the firmware partition offset; frame completion fails if firmware chooses a too-small offset. Shadow-list handles are raw kernel pointers cast to `u64`, safe only inside this driver instance and protected by `shadow_list_lock`. Runtime PM depends on a valid `xlnx,vcu-settings` regmap; missing settings can block resume.

## Test Signals

Compile-test with `CONFIG_VIDEO_ALLEGRO_DVT=m` and allmodconfig catches API and link problems. Runtime validation should cover firmware loading success/failure, probe resource failures, stream-on timeout/error paths, H.264 and HEVC encoding, EOS commands, buffer underrun/stop-streaming cleanup, VBR/CBR and QP control clamping, generated SPS/PPS/VPS parsing with standard decoders, IRQ/mailbox drain behavior, and runtime suspend/resume. V4L2 compliance tools and mem2mem encode smoke tests with malformed buffer sizes are high-value signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/allegro-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/allegro-mail.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/allegro-mail.c

## Purpose

`allegro-mail.c` translates between the driver's typed C mailbox message structs and the 32-bit word protocol used by Allegro firmware. It hides firmware-version differences, packs bitfields for requests, unpacks firmware responses, and supplies message type names for logging.

## Important APIs, Types, And Functions

- `msg_type_name()` maps `enum mcu_msg_type` values to human-readable names and formats unknown values.
- `allegro_encode_mail()` is the main request serializer. It dispatches to per-message encoders and writes a combined type/body-length header word.
- `allegro_decode_mail()` is the main response parser. It reads the type from the mailbox header and fills `union mcu_msg_response` members.
- `allegro_encode_config_blob()` serializes `struct create_channel_param` into the firmware create-channel configuration blob, with branches for `MCU_MSG_VERSION_2018_2` and `MCU_MSG_VERSION_2019_2`.
- `allegro_decode_config_blob()` extracts reference-index values that changed location between firmware versions.
- Internal encoders handle init, create/destroy channel, push internal buffers, put stream buffer, and encode-frame requests.
- Internal decoders handle init, create-channel, destroy-channel, and encode-frame responses.

## Control Flow

Request flow starts with a typed message whose first field is `struct mcu_msg_header`. `allegro_encode_mail()` dispatches on `header.type`, writes the body into `dst[1...]`, and writes the firmware header to `dst[0]` with the high 16 bits as type and low 16 bits as byte length. For create-channel requests, older firmware embeds the whole config blob in the message, while 2019.2+ firmware receives a DMA-visible blob address.

Response flow starts with `allegro_decode_mail()`, which extracts the response type from `src[0]`, advances past the header, and dispatches to a decoder. The encode-frame response parser reconstructs 64-bit handles, extracts packed fields such as skip/reference flags, tile dimensions, QP, slice type, and IDR flags, and optionally consumes 2019.2 reserved words.

## State And Persistence

The file does not keep persistent state. All state is passed in message structs and word buffers. The only static mutable object is the fallback buffer in `msg_type_name()` for formatting unknown message ids; concurrent callers can overwrite that string.

## Dependencies And Integration Points

It depends on Linux bitfield helpers, errno, string helpers, V4L2 pixel format constants, and the protocol definitions in `allegro-mail.h`. It is called by `allegro-core.c` before writing command mailboxes and after reading status mailboxes. Firmware-version conditionals must remain aligned with `supported_firmware[]` in the core driver.

## Risks

Protocol layout mistakes are high impact because firmware will misinterpret requests or the driver will mis-handle returned buffers. Some bit packing uses signed values through `FIELD_PREP`, so range and sign-extension assumptions matter. The config blob has many partly documented or unknown fields, making regression risk high when changing encoder parameters. `msg_type_name()`'s static buffer is not thread-safe for unknown types, though logging impact is minor.

## Test Signals

Good tests include round-trip encode/decode fixtures for known firmware versions, byte-for-byte comparison against known working firmware messages, compile coverage for both protocol versions, and runtime traces confirming create-channel responses allocate the expected internal/reference buffer counts. Encode-frame response tests should validate 64-bit handle reconstruction and partition/tile fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/allegro-mail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/allegro-mail.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/allegro-mail.h

## Purpose

`allegro-mail.h` defines the C representation of the Allegro firmware mailbox protocol. It provides message type/version enums, request and response structs, create-channel parameter layout, encode options, response unions, and serializer/parser prototypes.

## Important APIs, Types, And Symbols

- `enum mcu_msg_type` defines protocol commands such as `INIT`, `CREATE_CHANNEL`, `DESTROY_CHANNEL`, `ENCODE_FRAME`, `PUT_STREAM_BUFFER`, and internal buffer push commands.
- `enum mcu_msg_version` distinguishes `MCU_MSG_VERSION_2018_2` and `MCU_MSG_VERSION_2019_2`.
- `struct create_channel_param` is the large channel configuration contract covering format, codec profile/level/tier, reference counts, loop filters, motion estimation ranges, rate control, GOP settings, LDA factors, and merge candidates.
- Request structs include `mcu_msg_init_request`, `mcu_msg_create_channel`, `mcu_msg_destroy_channel`, `mcu_msg_push_buffers_internal`, `mcu_msg_put_stream_buffer`, and `mcu_msg_encode_frame`.
- Response structs include `mcu_msg_init_response`, `mcu_msg_create_channel_response`, `mcu_msg_destroy_channel_response`, and `mcu_msg_encode_frame_response`.
- `union mcu_msg_response` lets the core allocate one response object and dispatch based on `header.type`.
- Option bits include `AL_OPT_FORCE_LOAD`, `AL_OPT_USE_L2`, `AL_OPT_UPDATE_PARAMS`, and related encode/request flags.

## Control Flow

This header has no executable flow, but it defines the structures consumed by the flow in `allegro-core.c` and serialized by `allegro-mail.c`. The flexible array member in `mcu_msg_push_buffers_internal` lets the core create variable-length internal buffer lists for the firmware.

## State And Persistence

The structs represent transient mailbox messages and channel creation state. They are not persisted outside memory or firmware mailboxes. Handles in stream/frame messages persist only long enough for a firmware response to identify the matching vb2 buffers.

## Dependencies And Integration Points

The header depends on kernel integer types and `BIT()` from `<linux/kernel.h>`. It integrates tightly with the core driver's `fill_create_channel_param()` and mailbox send/receive code. The response fields are also consumed by NAL generation, especially HEVC tile layout in `mcu_msg_encode_frame_response`.

## Risks

This is an ABI-like contract with firmware; field reordering or type-size changes can silently break hardware communication. The counted flexible array relies on correct `struct_size()` allocation by callers. Several fields are reserved or unknown, so readers should avoid assuming they are free for reuse.

## Test Signals

Build warnings around flexible arrays or struct types are useful early signals. Runtime tests should verify create-channel and encode-frame responses are decoded with expected ids, buffer counts, error codes, and tile metadata for each supported firmware version.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/allegro-mail.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/nal-h264.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/nal-h264.c

## Purpose

`nal-h264.c` converts between H.264 NAL units in raw byte sequence payload form and the C structs defined in `nal-h264.h`. In this driver, the encoder side uses it to generate SPS, PPS, and filler NAL units that the Allegro firmware does not fully provide.

## Important APIs, Types, And Functions

- Public exported APIs: `nal_h264_write_sps()`, `nal_h264_read_sps()`, `nal_h264_write_pps()`, `nal_h264_read_pps()`, `nal_h264_write_filler()`, and `nal_h264_read_filler()`.
- Syntax walkers: `nal_h264_rbsp_sps()`, `nal_h264_rbsp_pps()`, `nal_h264_rbsp_vui_parameters()`, and `nal_h264_rbsp_hrd_parameters()` use generic `rbsp_*` operations for both read and write paths.
- Start-code helpers write and validate the four-byte Annex B prefix `00 00 00 01`.
- Filler helpers fill available bytes with `0xff` payload followed by RBSP trailing bits.

## Control Flow

Each public writer initializes an `rbsp` with write ops, writes the start-code prefix and NAL header bits, walks the relevant syntax struct, appends trailing bits, and returns the rounded byte count. Readers perform the inverse: initialize read ops, validate the prefix and selected header fields, walk the same syntax function to populate the struct, consume trailing bits, and return the consumed byte count.

## State And Persistence

All state is local to the passed `struct rbsp` and target/source buffers. The module exports helper functions but stores no persistent state.

## Dependencies And Integration Points

The file depends on `nal-h264.h` for syntax structs and conversion declarations and on `nal-rbsp.h` for bitstream operations. `allegro-core.c` calls the write APIs when preparing IDR/I-frame output buffers. The read APIs are general-purpose helpers that can validate generated payloads or support other drivers.

## Risks

Supported H.264 syntax is intentionally partial. Scaling matrices and some advanced PPS/SPS branches set `rbsp->error = -EINVAL`. `nal_h264_read_sps()` requires `nal_ref_idc == 0` for SPS even though many H.264 streams use nonzero reference IDC for parameter sets; this may make the parser stricter than external streams. Array bounds depend on syntax counts such as `cpb_cnt_minus1` and slice group counts staying within fixed struct array sizes. Filler writing assumes the provided size leaves enough space for prefix, header, payload, and trailing marker.

## Test Signals

High-value tests are encode/decode round trips for baseline SPS/PPS values generated by `allegro-core.c`, fuzzing/truncated input tests for `-EINVAL`, decoder acceptance of generated Annex B parameter sets, and explicit tests for small filler buffers and unsupported syntax branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/nal-h264.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/nal-h264.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/nal-h264.h

## Purpose

`nal-h264.h` declares C structs for H.264 SPS, PPS, VUI, and HRD syntax and provides inline mapping helpers from V4L2 codec/color controls to H.264 bitstream numeric values.

## Important APIs, Types, And Symbols

- `struct nal_h264_hrd_parameters`, `struct nal_h264_vui_parameters`, `struct nal_h264_sps`, and `struct nal_h264_pps` model H.264 syntax elements.
- Inline mapping helpers include `nal_h264_profile()`, `nal_h264_level()`, `nal_h264_full_range()`, `nal_h264_color_primaries()`, `nal_h264_transfer_characteristics()`, and `nal_h264_matrix_coeffs()`.
- Public function declarations cover SPS/PPS/filler read and write helpers plus print prototypes.

## Control Flow

The inline helpers use switch statements to convert V4L2 enum values into H.264 profile ids, level ids, color primaries, transfer characteristics, matrix coefficients, and full-range flags. The structs are consumed by `nal-h264.c` syntax walkers.

## State And Persistence

The header defines data layouts and pure conversions only. No state is stored globally or persistently.

## Dependencies And Integration Points

It depends on V4L2 control and pixel format enums. `allegro-core.c` fills these structs from current channel controls and colorimetry, then passes them to `nal_h264_write_*()`. The helpers also rely on V4L2 default color mapping macros for default transfer/ycbcr settings.

## Risks

The structs contain fixed-size arrays for HRD and slice-group data; parser code must constrain syntax counts before indexing. Some mappings default to generic values rather than returning errors, which improves tolerance but can hide unsupported color metadata. The declared `nal_h264_print_sps()` and `nal_h264_print_pps()` prototypes are not implemented in the researched object list, so callers outside this module must not rely on them unless another translation unit supplies them.

## Test Signals

Unit tests should check V4L2-to-H.264 mappings for common colorimetry and all supported profiles/levels. Build/link tests should catch accidental use of undeclared or unimplemented print helpers. Bitstream tests should verify generated SPS/PPS values match channel settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/nal-h264.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/nal-hevc.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/nal-hevc.c

## Purpose

`nal-hevc.c` converts HEVC/H.265 VPS, SPS, PPS, and filler NAL units between C structs and RBSP/Annex B byte streams. The Allegro encoder driver uses the writer side to synthesize VPS/SPS/PPS/filler data before firmware-produced HEVC frame payloads.

## Important APIs, Types, And Functions

- Public exported APIs: `nal_hevc_write_vps()`, `nal_hevc_read_vps()`, `nal_hevc_write_sps()`, `nal_hevc_read_sps()`, `nal_hevc_write_pps()`, `nal_hevc_read_pps()`, `nal_hevc_write_filler()`, and `nal_hevc_read_filler()`.
- Internal syntax walkers include `nal_hevc_rbsp_profile_tier_level()`, `nal_hevc_rbsp_vps()`, `nal_hevc_rbsp_hrd_parameters()`, `nal_hevc_rbsp_vui_parameters()`, `nal_hevc_rbsp_sps()`, and `nal_hevc_rbsp_pps()`.
- NAL unit types handled are VPS 32, SPS 33, PPS 34, and filler data 38.
- Start-code and filler helpers parallel the H.264 implementation but write the two-byte HEVC NAL header fields.

## Control Flow

Writers initialize `struct rbsp` with write ops, write the Annex B start-code prefix, write HEVC NAL header bits, walk the relevant syntax tree, add trailing bits, check `rbsp.error`, and return byte length. Readers validate the start prefix and important header fields, walk the same syntax functions with read ops, and return consumed byte length. Unsupported syntax branches, such as timing info, scaling lists, short-term reference picture sets, long-term reference pictures, and extension flags, call `rbsp_unsupported()`.

## State And Persistence

State is local to the `rbsp` cursor and the input/output struct. The file exports helper symbols but stores no global runtime state.

## Dependencies And Integration Points

It depends on `nal-hevc.h` for syntax structs and mapping helpers and on `nal-rbsp.h` for bit/Exp-Golomb operations. `allegro-core.c` fills HEVC VPS/SPS/PPS structs based on channel controls, firmware tile metadata, loop-filter options, HRD values, and colorimetry before calling these writers.

## Risks

The HEVC syntax support is deliberately limited to the simple subset generated by the Allegro driver. Several fixed arrays are small, notably PPS tile arrays in the header, while firmware responses can describe more rows/columns; the core driver writes tile data based on firmware counts, so bounds need scrutiny if hardware tile counts change. In `nal_hevc_rbsp_hrd_parameters()`, the branch for `nal_hrd_parameters_present_flag` writes `vcl_hrd` rather than `nal_hrd`, which is suspicious and should be checked if NAL HRD is enabled. Reader validation is partial for PPS, where header fields are read but not checked against PPS type before parsing.

## Test Signals

Round-trip tests for VPS/SPS/PPS generated from Allegro channel defaults, external decoder acceptance tests, fuzz/truncation tests for readers, and tile-layout regression tests are important. HEVC tests should explicitly cover IDR output that includes VPS/SPS/PPS and non-IDR output where filler/data offsets differ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/nal-hevc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/nal-hevc.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/nal-hevc.h

## Purpose

`nal-hevc.h` defines C representations of HEVC VPS, SPS, PPS, VUI, HRD, and profile-tier-level syntax and supplies inline helpers to map V4L2 HEVC controls and colorimetry to HEVC bitstream values.

## Important APIs, Types, And Symbols

- Main structs are `nal_hevc_profile_tier_level`, `nal_hevc_vps`, `nal_hevc_hrd_parameters`, `nal_hevc_vui_parameters`, `nal_hevc_sps`, and `nal_hevc_pps`.
- `N_HRD_PARAMS` is set to 1, limiting represented HRD CPB entries.
- Inline mapping helpers include `nal_hevc_profile()`, `nal_hevc_tier()`, `nal_hevc_level()`, `nal_hevc_full_range()`, `nal_hevc_color_primaries()`, `nal_hevc_transfer_characteristics()`, and `nal_hevc_matrix_coeffs()`.
- Public prototypes expose VPS/SPS/PPS/filler read and write helpers.

## Control Flow

Inline helper flow is simple switch-based mapping from V4L2 enums into HEVC syntax values. Larger control flow is in `nal-hevc.c`, which traverses these structs to emit or parse RBSP.

## State And Persistence

The header declares transient struct layouts and pure conversion functions. It has no persistent state.

## Dependencies And Integration Points

It depends on kernel integer/error helpers and V4L2 control/color enums. It is used directly by `allegro-core.c` when building HEVC VPS/SPS/PPS metadata and by `nal-hevc.c` for serialization.

## Risks

Some arrays model only small subsets of the HEVC syntax, for example one HRD parameter set and one explicit tile width/height entry in PPS, even though the firmware response can carry more tile dimensions. Helper defaults return generic values for unsupported color metadata, which can reduce precision. Future support for Main 10 or advanced profiles must audit both struct fields and writer branches for unsupported syntax.

## Test Signals

Compile coverage across current V4L2 HEVC enum values, unit tests for profile/tier/level mapping, generated stream validation with HEVC decoders, and boundary tests around tile counts and HRD parameters are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/nal-hevc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/nal-rbsp.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/nal-rbsp.c

## Purpose

`nal-rbsp.c` provides the shared bit-level RBSP reader/writer used by both H.264 and HEVC NAL helpers. It manages bit positions, emulation-prevention byte insertion/removal, unsigned and signed Exp-Golomb coding, and RBSP trailing bits.

## Important APIs, Types, And Functions

- `rbsp_init()` initializes a cursor over a byte buffer with either `read` or `write` operations.
- Public wrappers `rbsp_bit()`, `rbsp_bits()`, `rbsp_uev()`, and `rbsp_sev()` dispatch to the current ops table and stop once `rbsp->error` is set.
- `rbsp_trailing_bits()` writes or reads the stop bit and alignment zero bits through the same wrapper API.
- Internal functions implement bit reads/writes, multi-bit reads/writes, unsigned Exp-Golomb, signed Exp-Golomb, and emulation-prevention handling.
- Global ops tables `write` and `read` provide the operation strategy used by syntax walkers.

## Control Flow

Writers call syntax walkers that repeatedly call the public wrappers. `rbsp_write_bit()` inserts an emulation-prevention pattern when the zero counter reaches the trigger threshold, writes one bit at the current byte/bit offset, advances `pos`, and updates the zero counter. Readers mirror this by discarding the emulation-prevention pattern when needed, reading a bit, advancing, and updating counters. Exp-Golomb helpers are built on top of those bit primitives. If any operation fails, `rbsp->error` is set and later wrapper calls become no-ops.

## State And Persistence

All active state is in `struct rbsp`: target data pointer, byte size, bit position, consecutive-zero count, ops pointer, and error code. There is no external persistence. The `read` and `write` ops tables are global shared constants in practice, though not declared `const`.

## Dependencies And Integration Points

The file depends on kernel math/log2 helpers and `nal-rbsp.h`. It is consumed by `nal-h264.c` and `nal-hevc.c`, which provide the actual codec syntax. Its behavior directly affects every generated SPS/PPS/VPS/filler NAL emitted by the Allegro driver.

## Risks

The emulation-prevention implementation is subtle: it tracks consecutive zero bits rather than simply scanning bytes, so off-by-one errors could corrupt generated streams. `rbsp_write_uev()` uses `ilog2(*value + 1)`, so callers must avoid overflow at `UINT_MAX`. Signed Exp-Golomb conversion must handle negative values safely. The global ops objects are writable, so accidental mutation would affect all users.

## Test Signals

Unit tests should cover bit-level reads/writes across byte boundaries, unsigned and signed Exp-Golomb round trips, buffer-too-small errors, trailing-bit alignment, and known byte sequences requiring emulation-prevention insertion/removal. Codec-level SPS/PPS/VPS round trips exercise this layer indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/nal-rbsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/nal-rbsp.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/nal-rbsp.h

## Purpose

`nal-rbsp.h` declares the shared RBSP cursor, operation table, and public bit/Exp-Golomb helper API used by codec-specific NAL parsers/generators.

## Important APIs, Types, And Symbols

- `struct nal_rbsp_ops` abstracts bit, fixed-width, unsigned Exp-Golomb, and signed Exp-Golomb operations.
- `struct rbsp` stores the data pointer, buffer size, current bit position, consecutive-zero count, ops table, and error state.
- External ops tables `write` and `read` select generator or parser behavior.
- Public functions include `rbsp_init()`, `rbsp_unsupported()`, `rbsp_bit()`, `rbsp_bits()`, `rbsp_uev()`, `rbsp_sev()`, and `rbsp_trailing_bits()`.

## Control Flow

Codec syntax walkers receive a `struct rbsp *` and call the public helpers in specification order. The selected ops table determines whether those calls read from a source buffer or write to a destination buffer, allowing one syntax walker to serve both directions.

## State And Persistence

State is caller-owned in the `struct rbsp` instance. The header does not allocate or persist data.

## Dependencies And Integration Points

This header depends on kernel integer types. It is included by H.264 and HEVC NAL helper C files and underpins Allegro parameter-set generation.

## Risks

Because `write` and `read` are exported as mutable global objects, code could accidentally modify operation callbacks. `rbsp_bits()` accepts an `int *` while the ops callback uses `unsigned int *`, which works with current callers but is type-fragile. Callers must check `rbsp.error` after syntax traversal.

## Test Signals

Compile tests catch callback signature drift. Functional tests should exercise the same codec syntax walker with both `read` and `write` ops to ensure the abstraction remains symmetric.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/nal-rbsp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/Kconfig

## Purpose

This Kconfig file is the Amlogic media platform submenu. It groups Amlogic-specific media drivers and sources the C3 and Meson GE2D child Kconfig files.

## Important APIs, Types, And Symbols

- The file emits a `comment "Amlogic media platform drivers"`.
- It sources `drivers/media/platform/amlogic/c3/Kconfig`.
- It sources `drivers/media/platform/amlogic/meson-ge2d/Kconfig`.

## Control Flow

There is no runtime flow. Kconfig includes this file from the top-level platform Kconfig and then recursively loads child driver configuration.

## State And Persistence

The file contributes to persistent kernel `.config` choices through its children. It owns no runtime state.

## Dependencies And Integration Points

It integrates the Amlogic subtree into the media platform menu and must remain paired with the sibling Makefile that descends into `c3/` and `meson-ge2d/`.

## Risks

Missing or incorrect `source` lines can hide entire Amlogic driver families. The comment does not gate anything, so each child must provide its own dependencies.

## Test Signals

Kconfig menu visibility checks and allmodconfig builds should show both C3 and Meson GE2D options under Amlogic media platform drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/Makefile

## Purpose

This Makefile descends into Amlogic media platform subdirectories.

## Important APIs, Types, And Symbols

- `obj-y += c3/` enters the Amlogic C3 media driver subtree.
- `obj-y += meson-ge2d/` enters the Meson GE2D subtree.

## Control Flow

Kbuild traverses both child directories when the Amlogic media platform directory is reached. The child Makefiles contain the actual Kconfig object gates.

## State And Persistence

There is no runtime state. Build artifacts are determined by child Makefiles and `.config`.

## Dependencies And Integration Points

The file pairs with `amlogic/Kconfig` and delegates C3 ISP, C3 MIPI, and GE2D build selection to child directories.

## Risks

A child Kconfig source without a matching `obj-y` traversal entry would make a visible config option fail to build its objects. Conversely, extra traversal is normally harmless but can expose stale Makefiles.

## Test Signals

Builds with `CONFIG_VIDEO_C3_ISP=m` should enter `amlogic/c3/isp/` and produce `c3-isp.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/Kconfig

## Purpose

This C3 Kconfig file sources the media blocks for the Amlogic C3 SoC family: ISP, MIPI adapter, and MIPI CSI-2 receiver.

## Important APIs, Types, And Symbols

- Sources `drivers/media/platform/amlogic/c3/isp/Kconfig`.
- Sources `drivers/media/platform/amlogic/c3/mipi-adapter/Kconfig`.
- Sources `drivers/media/platform/amlogic/c3/mipi-csi2/Kconfig`.

## Control Flow

Kconfig recursively evaluates the three child files when the Amlogic C3 subtree is loaded. Runtime behavior is entirely in the selected child drivers.

## State And Persistence

Only child Kconfig selections persist in `.config`.

## Dependencies And Integration Points

This file aligns with `amlogic/c3/Makefile`, which descends into the same three child directories. The C3 ISP capture code researched here depends on the ISP child symbol.

## Risks

Wrong child paths or missing source lines can break visibility for a pipeline component, which is especially important because ISP capture requires upstream C3 media entities to form a working pipeline.

## Test Signals

Run `make menuconfig` and confirm ISP, MIPI adapter, and CSI-2 entries are visible under Amlogic C3 when their dependencies are met.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/Makefile

## Purpose

This Makefile descends into the three Amlogic C3 media component directories.

## Important APIs, Types, And Symbols

- `obj-y += isp/`
- `obj-y += mipi-adapter/`
- `obj-y += mipi-csi2/`

## Control Flow

Kbuild traverses each child directory and lets each child Makefile apply `CONFIG_*` gates to actual objects.

## State And Persistence

No runtime state exists here. Build state is produced by child objects.

## Dependencies And Integration Points

The traversal mirrors `amlogic/c3/Kconfig`, keeping the ISP, MIPI adapter, and CSI-2 components build-reachable.

## Risks

Pipeline components can become impossible to build if Kconfig and Makefile child lists diverge. Since the entries are unconditional traversal, stale child directories can surface build issues in broad configs.

## Test Signals

Allmodconfig and targeted `CONFIG_VIDEO_C3_ISP` builds should traverse `isp/` successfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/Kconfig

## Purpose

This Kconfig file exposes the Amlogic C3 Image Signal Processor driver as `VIDEO_C3_ISP`. The driver provides a V4L2/media-controller ISP pipeline for processing raw images and writing results to memory.

## Important APIs, Types, And Symbols

- `VIDEO_C3_ISP` is a tristate symbol.
- Dependencies are `ARCH_MESON || COMPILE_TEST`, `VIDEO_DEV`, and `OF`.
- It selects `MEDIA_CONTROLLER`, `V4L2_FWNODE`, `VIDEO_V4L2_SUBDEV_API`, `VIDEOBUF2_DMA_CONTIG`, `VIDEOBUF2_VMALLOC`, and `V4L2_ISP`.

## Control Flow

When dependencies are satisfied, users can build the C3 ISP as a module or built-in. The sibling Makefile aggregates multiple C3 ISP objects into `c3-isp.o`.

## State And Persistence

The `.config` setting is the only state here. Runtime state is in the C3 ISP C files and shared header.

## Dependencies And Integration Points

The selected symbols match the implementation: media graph entities, V4L2 subdevs, fwnode parsing, DMA-contig capture buffers, vmalloc metadata/parameter buffers, and the V4L2 ISP API are all used by the driver family.

## Risks

If dependencies are incomplete, compile or link failures will appear in broad build testing. The help text says "outputing", a spelling issue only. The symbol depends on OF, so non-device-tree use is intentionally excluded.

## Test Signals

Compile with `CONFIG_VIDEO_C3_ISP=m` under `ARCH_MESON` and `COMPILE_TEST`. Runtime signals include media-controller entity registration and successful ISP capture video node creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/Makefile

## Purpose

This Makefile builds the Amlogic C3 ISP driver aggregate object from device, params, stats, capture, core, and resizer implementation files.

## Important APIs, Types, And Symbols

- `c3-isp-objs` includes `c3-isp-dev.o`, `c3-isp-params.o`, `c3-isp-stats.o`, `c3-isp-capture.o`, `c3-isp-core.o`, and `c3-isp-resizer.o`.
- `obj-$(CONFIG_VIDEO_C3_ISP) += c3-isp.o` gates the aggregate driver object.

## Control Flow

Kbuild links all component objects into one `c3-isp` module or built-in object when `VIDEO_C3_ISP` is enabled.

## State And Persistence

There is no runtime state in this file. It determines build composition only.

## Dependencies And Integration Points

The object list corresponds to the shared data structures and prototypes in `c3-isp-common.h`: device probing, core subdev, resizers, capture nodes, stats node, and params node are all separate implementation units linked together.

## Risks

Omitting one component causes unresolved symbols for the registration, ISR, or pre-configuration functions declared in the common header. Adding a new shared entry point requires updating this object list if it lives in a new source file.

## Test Signals

Targeted module builds should produce `c3-isp.ko` without unresolved symbols. Link errors involving `c3_isp_captures_*`, `c3_isp_stats_*`, `c3_isp_params_*`, `c3_isp_core_*`, or `c3_isp_resizers_*` implicate this Makefile or matching source files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/c3-isp-capture.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/c3-isp-capture.c

## Purpose

`c3-isp-capture.c` implements the capture video nodes for the Amlogic C3 ISP driver. It exposes three memory capture devices, validates their media links against upstream resizer output, programs WRMIFX3 write-memory-interface registers, manages vb2 DMA-contig capture buffers, and completes frames from the ISP interrupt path.

## Important APIs, Types, And Functions

- `cap_formats[]` maps supported media bus codes and V4L2 pixel formats to WRMIFX3 hardware format bits, plane layout, input bit depth, UV swap, and chroma subsampling. Supported outputs include GREY, NV12M, NV21M, NV16M, NV61M, and several 12-bit Bayer formats stored as 16-bit raw.
- Register helpers: `C3_ISP_WRMIFX3_REG()`, `c3_isp_cap_wrmifx3_buff()`, `c3_isp_cap_wrmifx3_format()`, `c3_isp_cap_start()`, and `c3_isp_cap_stop()` program buffer addresses, format/window/stride fields, and top-level path enables.
- Buffer helpers: `c3_isp_cap_dummy_buff_create()`, `c3_isp_cap_dummy_buff_destroy()`, `c3_isp_cap_cfg_buff()`, `c3_isp_cap_done()`, and `c3_isp_cap_return_buffers()`.
- V4L2 ioctl handlers: querycap, enum format, get/set/try multiplanar format, enum frame sizes, event subscribe/unsubscribe, and standard vb2 ioctls.
- Media graph validation: `c3_isp_cap_link_validate()` compares upstream subdev active format against capture dimensions and expected mbus code.
- vb2 operations: queue setup, buffer init, buffer prepare, queue, start streaming, and stop streaming.
- Registration APIs: `c3_isp_captures_register()`, `c3_isp_captures_unregister()`, and `c3_isp_captures_isr()`.

## Control Flow

Registration iterates over `C3_ISP_CAP_DEV_0..2`, initializes default 1920x1080 NV12M format, binds each capture device to the matching resizer, initializes locks and pending lists, and registers a `video_device` with a sink media pad and a DMA-contig vb2 queue.

Format setting calls `c3_cap_try_fmt()`, which clamps dimensions to 160x120 through 2888x2240, selects a supported format, sets fixed field/colorimetry defaults, determines memory-plane count from `v4l2_format_info()`, aligns bytesperline to 16 bytes, and computes per-plane `sizeimage`. Link validation later ensures the capture format matches the upstream subdev source format and media bus code.

Streaming starts by starting the media pipeline, allocating a dummy DMA buffer for frame drops/no-buffer cases, runtime-resuming the ISP device, programming the current buffer and format into WRMIFX3, enabling the WRMIF path, and enabling streams on the matching resizer source pad. Streaming stops in reverse: disable WRMIF path, return current/pending buffers with error, disable upstream streams, runtime-put the device, destroy the dummy buffer, and stop the media pipeline.

Queued vb2 buffers are appended to `cap->pending` under `buff_lock`. At frame completion, `c3_isp_captures_isr()` calls `c3_isp_cap_done()` for all three capture devices. The active buffer gets sequence/timestamp/field metadata and is completed with `VB2_BUF_STATE_DONE`; the next pending buffer is selected and programmed, or the dummy buffer is used if no pending buffer exists.

## State And Persistence

Each `struct c3_isp_capture` stores its id, vb2 queue, video node, media pad, mutex, parent ISP pointer, associated resizer, dummy buffer, current active buffer, spinlock-protected pending list, and active pixel format. State is volatile driver runtime state. The dummy buffer is DMA memory allocated only while streaming. Frame sequence comes from the parent `isp->frm_sequence`.

## Dependencies And Integration Points

The file depends on V4L2 controls/events/ioctls/media-controller helpers, vb2 DMA-contig, runtime PM, common C3 ISP state from `c3-isp-common.h`, and register bit definitions from `c3-isp-regs.h`. It integrates with resizer subdevices via `v4l2_subdev_enable_streams()`/`disable_streams()` and with the top-level device ISR through `c3_isp_captures_isr()`.

## Risks

`c3_isp_cap_dummy_buff_destroy()` frees unconditionally and assumes a successful prior allocation; error paths currently call it only after create success, but future changes should preserve that invariant. The dummy buffer uses the maximum of Y and UV plane sizes and maps both hardware channels to the same DMA address when no buffer is active; this is intentional for dropping output but must be large enough for both channels. The capture ISR completes all three captures on every call, so top-level IRQ filtering must ensure this corresponds to frame completion. `c3_isp_cap_s_fmt_mplane()` does not reject format changes while buffers are busy, so callers may need external serialization or vb2 busy checks if format changes during streaming are possible. Link validation relies on upstream active format being available.

## Test Signals

Run media-ctl graph validation, `v4l2-compliance` on all three capture nodes, streaming tests for each supported pixel format, no-buffer streaming tests to exercise dummy buffers, DMABUF and MMAP capture tests, runtime PM start/stop tests, frame sequence/timestamp checks, and negative tests for mismatched upstream mbus code or dimensions. Register programming can be checked with hardware traces or debug instrumentation around WRMIFX3 address/format writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/c3-isp-capture.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/c3-isp-common.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/c3-isp-common.h

## Purpose

`c3-isp-common.h` defines the shared data model and cross-file function contracts for the Amlogic C3 ISP driver. It centralizes limits, pad indexes, resizer/capture ids, pixel-plane ids, buffer wrappers, media entity structs, the top-level device struct, register access prototypes, registration prototypes, and ISR/pre-configuration hooks.

## Important APIs, Types, And Symbols

- Driver limits: `C3_ISP_DRIVER_NAME`, `C3_ISP_CLOCK_NUM_MAX`, default/min/max width and height, and `C3_ISP_DMA_SIZE_ALIGN_BYTES`.
- Graph enums: `c3_isp_core_pads`, `c3_isp_resizer_ids`, `c3_isp_resizer_pads`, `c3_isp_cap_devs`, and `c3_isp_planes`.
- Format/buffer structs: `c3_isp_cap_format_info`, `c3_isp_cap_buffer`, `c3_isp_stats_buffer`, `c3_isp_params_buffer`, and `c3_isp_dummy_buffer`.
- Entity/device structs: `c3_isp_core`, `c3_isp_resizer`, `c3_isp_stats`, `c3_isp_params`, `c3_isp_capture`, `c3_isp_info`, and `c3_isp_device`.
- Shared function prototypes: register read/write/update helpers, core/resizer/capture/stats/params register/unregister functions, ISR handlers, and stats/params pre-configuration hooks.

## Control Flow

The header has no executable control flow. It defines how the component implementation files cooperate: the top-level device code owns `struct c3_isp_device`, initializes hardware/base clocks/media devices, calls component registration functions, and dispatches ISR work into core, capture, stats, and params handlers. Capture, stats, params, core, and resizer implementation files manipulate their portion of the shared device struct.

## State And Persistence

Runtime state is organized under `struct c3_isp_device`: device pointer, register base, clocks, V4L2 async notifier, V4L2 and media devices, media pipeline, core subdev, three resizers, stats node, params node, three capture nodes, frame sequence, and version information. Per-node structs store vb2 queues, video devices, pads, locks, active buffers, and pending lists. None of this persists beyond driver lifetime.

## Dependencies And Integration Points

The header depends on Linux clocks and media/V4L2/vb2 headers. It is included by all C3 ISP component files and acts as the internal ABI between the aggregate module objects listed in the Makefile. The capture file uses the capture enums, format info, buffer structs, parent device, resizer pointers, and register access prototypes from this header.

## Risks

Because this header defines shared structs across multiple implementation files, field layout changes have broad impact. Locking comments are part of the contract: `mutex lock` protects queue/video-device state while spinlocks protect active/pending buffers. Format and dimension constants must stay consistent with hardware and all format-setting paths. Function prototypes must remain matched with the objects linked into `c3-isp.o`.

## Test Signals

Build tests are strong signals for cross-file contract drift. Runtime tests should validate media entity registration, async notifier binding, all component unregister paths, ISR dispatch, concurrent buffer queue/complete locking, and width/height boundary handling across capture and resizer components.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/c3-isp-common.h -->
