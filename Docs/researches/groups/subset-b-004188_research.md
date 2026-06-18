# Research: subset-b-004188

Grouped research for Linux media test-driver files under `sources/distributed-fs/ceph-client/drivers/media/test-drivers`. Each file section is delimited for reconciliation into its source-tree-aligned per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_psi.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_psi.c

## Purpose
`vidtv_psi.c` implements the virtual DVB driver's MPEG Program Specific Information and DVB Service Information table model. It builds PAT, PMT, SDT, NIT, and EIT structures in memory, maintains section lengths and version numbers, serializes descriptor loops, computes CRC32 values, and packetizes table bytes into MPEG-TS packets using the helpers from `vidtv_ts.c`. The code deliberately treats each logical table as a single section for vidtv, which keeps the simulator simpler while still exercising user-space DVB PSI parsing.

## Important APIs, Types, and Functions
The public constructors and destructors include `vidtv_psi_pat_table_init()`, `vidtv_psi_pmt_table_init()`, `vidtv_psi_sdt_table_init()`, `vidtv_psi_nit_table_init()`, `vidtv_psi_eit_table_init()`, the matching destroy helpers, and constructors for PAT programs, PMT streams, SDT services, EIT events, and descriptors. Writer entry points are `vidtv_psi_pat_write_into()`, `vidtv_psi_pmt_write_into()`, `vidtv_psi_sdt_write_into()`, `vidtv_psi_nit_write_into()`, and `vidtv_psi_eit_write_into()`. Descriptor handling centers on `vidtv_psi_desc_clone()`, `vidtv_psi_desc_destroy()`, `vidtv_psi_desc_assign()`, `vidtv_pmt_desc_assign()`, `vidtv_sdt_desc_assign()`, and `vidtv_psi_desc_write_into()`.

Internal helpers manage bitfields: `vidtv_psi_get_sec_len()`, `vidtv_psi_set_sec_len()`, `vidtv_psi_set_desc_loop_len()`, `vidtv_psi_update_version_num()`, `vidtv_psi_get_pat_program_pid()`, and `vidtv_psi_pmt_stream_get_elem_pid()`. `vidtv_psi_ts_psi_write_into()` is the serialization core: it writes TS headers, pointer fields, payload fragments, padding, and continuity counter updates while optionally folding the bytes into a running big-endian CRC.

## Control Flow
The typical flow is construct, assign children or descriptors, recompute section length, then write. Constructors initialize table IDs, MPEG reserved bits, current/next flags, section IDs, default versions, and descriptor-loop bitfields. Assignment helpers transfer ownership of linked lists into their table, recompute length, enforce maximum section limits, and bump the version. Writer functions start with `INITIAL_CRC`, write the common PSI header through `vidtv_psi_table_header_write_into()`, walk table-specific linked lists, write nested descriptors, then append the CRC with `table_section_crc32_write_into()`. The packetizer inserts a new TS header at every 188-byte boundary, uses a pointer field for new PSI sections, and pads the final CRC packet with `TS_FILL_BYTE`.

## State and Persistence
All table state is in heap-allocated linked structures owned by the caller until assigned to a table. There is no persistence beyond module memory and no global mutable table cache in this file. Version numbers are stored in table headers and increment on assignments; continuity counters are passed by pointer from callers and updated during serialization. EIT events embed a wall-clock-derived Modified Julian Date start time at event creation, so the emitted schedule depends on current kernel time. Destroy paths recursively free descriptor loops and child linked lists.

## Dependencies and Integration Points
The file depends on kernel allocation/string/time/CRC helpers, endian helpers, `vidtv_common.h` safe buffer copy/fill wrappers, `vidtv_psi.h` layout definitions, and `vidtv_ts.h` TS constants and continuity helpers. Upstream vidtv muxing code uses these APIs to create DVB service metadata and interleave PSI tables with audio/video elementary streams. PID constants are standardized for PAT, SDT, NIT, and EIT, while PMT PID lookup is derived from PAT entries.

## Risks and Edge Cases
The implementation has many ownership-transfer APIs; callers must not reuse or double-free assigned descriptor or program chains. Section length checks are limited: some assignment loops null out new input after one pass, so oversize rejection effectively drops newly assigned content rather than returning an error. `vidtv_psi_desc_clone()` can leak already cloned descriptors if a later clone fails. Packetization warns but forcibly pads when asked to start a PSI section at a non-TS-aligned offset. Descriptor lengths are stored in `u8`, so overly long strings can truncate protocol length fields even though allocations use `u32` string lengths. EIT events have a fixed nearly-one-day duration and no rollover logic.

## Test Signals
Useful validation includes MPEG-TS analyzers confirming PAT/PMT/SDT/NIT/EIT CRCs, section lengths, descriptor loop lengths, PIDs, and continuity counters; DVB user-space scans discovering the expected services; fault injection for allocation failures in descriptor/table constructors; and buffer-boundary tests around 184-byte payload breaks. Regression tests should exercise descriptor cloning/destruction and oversize descriptor loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_psi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_psi.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_psi.h

## Purpose
`vidtv_psi.h` is the public contract for vidtv's PSI/SI model. It declares the packed wire-oriented structures for descriptors and DVB/MPEG tables, the write-argument structs used by the serializer, PID and section-length constants, descriptor and stream type enums, and all constructor, assignment, writer, query, and destroy APIs implemented in `vidtv_psi.c`.

## Important APIs, Types, and Functions
Important data types include `struct vidtv_psi_table_header`, `struct vidtv_psi_table_pat`, `struct vidtv_psi_table_pmt`, `struct vidtv_psi_table_sdt`, `struct vidtv_psi_table_nit`, `struct vidtv_psi_table_eit`, and linked child structures for PAT programs, PMT streams, SDT services, NIT transports, and EIT events. Descriptor structures specialize the generic `struct vidtv_psi_desc` for service, registration, network-name, service-list, and short-event descriptors. The header also declares writer argument structures such as `vidtv_psi_pat_write_args`, `vidtv_psi_pmt_write_args`, `vidtv_psi_sdt_write_args`, `vidtv_psi_nit_write_args`, and `vidtv_psi_eit_write_args`.

Public routines expose a consistent lifecycle: `*_init()` allocates and initializes, `*_assign()` transfers ownership into a parent and refreshes metadata, `*_write_into()` serializes into a TS buffer, and `*_destroy()` frees linked ownership trees. Query helpers retrieve PIDs from packed bitfields and map PAT programs to PMT sections.

## Control Flow
The header encodes how callers assemble PSI: create a table, create linked children, assign children or descriptors, and write the table into a caller-owned buffer with caller-owned continuity counters. The common `psi_write_args`, `desc_write_args`, `header_write_args`, and `crc32_write_args` types make internal writer stages share buffer, PID, offset, CRC, and continuity-counter state.

## State and Persistence
The structures are packed and contain big-endian protocol fields plus C-only `next` pointers and descriptor pointers. The file itself has no storage, but it defines ownership semantics in comments: assignment transfers ownership to the parent table and destroy helpers free the whole chain. State is transient kernel memory; persistence is represented only by serialized bytes emitted to TS buffers.

## Dependencies and Integration Points
The header depends on `linux/types.h` for fixed-width and endian-qualified types. It integrates with vidtv encoder/muxer code that needs MPEG-TS service metadata and with `vidtv_ts.h` via shared constants such as PIDs and packetization arguments. The field layouts mirror ISO/IEC 13818-1 and ETSI EN 300 468, so the structs are part of the simulator's ABI with external DVB analysis tools through emitted bytes, not a user-space C ABI.

## Risks and Edge Cases
The packed structs mix wire fields and kernel pointers; only selected prefixes are serialized, so future changes must keep writer size calculations synchronized with struct layout. Several bitfields use C bitfield syntax for protocol flags, which is sensitive to compiler layout assumptions and endian handling. Descriptor `length` is `u8`, so APIs taking strings or additional info must avoid data that exceeds the descriptor field capacity. Comments document ownership transfer, but the compiler cannot enforce it.

## Test Signals
Tests should include build coverage for all declarations, static analysis for packed-struct size assumptions, and runtime emission checks that table bytes match the standards. ABI-sensitive changes should be validated with TS analyzers and by comparing serialized section sizes against `MAX_SECTION_LEN` or `EIT_MAX_SECTION_LEN`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_psi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_s302m.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_s302m.c

## Purpose
`vidtv_s302m.c` implements a virtual SMPTE 302M/AES3 audio encoder for vidtv. It produces 16-bit AES3 subframes in an MPEG private stream, either from a caller-provided sample buffer or from a built-in sine-wave melody generator. The encoder can run independently or synchronize audio access units to a video encoder's access-unit list and PTS values.

## Important APIs, Types, and Functions
The exported lifecycle is `vidtv_s302m_encoder_init()` and `vidtv_s302m_encoder_destroy()`, returning and freeing a generic `struct vidtv_encoder`. Internally, `vidtv_s302m_encode()` is installed as the encoder callback and `vidtv_s302m_clear()` resets buffered output and access units. Access-unit helpers include `vidtv_s302m_access_unit_init()`, `vidtv_s302m_access_unit_destroy()`, `vidtv_s302m_alloc_au()`, `vidtv_s302m_compute_sample_count_from_video()`, and `vidtv_s302m_compute_pts_from_video()`. Sample and frame generation happens through `vidtv_s302m_get_sample()`, `vidtv_s302m_write_h()`, `vidtv_s302m_write_frame()`, and `vidtv_s302m_write_frames()`.

## Control Flow
Encoding starts by destroying the previous access-unit list and allocating a new one. If a sync video encoder exists, one audio access unit is created for each video access unit, sample counts are derived from sample duration ratios, and PTS values are copied from video. Without sync, a single access unit is emitted using ffmpeg-derived default frame count, PTS increment, and offset. For each access unit, the encoder writes a 302M elementary-stream header, generates or reads samples, writes 5-byte AES3 frames with ffmpeg's bit-reversal table, advances offsets and counters, and records each access unit's byte size and buffer offset.

## State and Persistence
Persistent runtime state lives in `struct vidtv_s302m_ctx` and the containing `struct vidtv_encoder`: frame index within a 192-frame block, access-unit count, melody note duration/offset, source buffer offset, sample count, encoder buffer, and access-unit linked list. All state is in memory and reset by clear/destroy; no data persists across module unload. The source-buffer exhaustion callback is invoked before wrapping to offset zero.

## Dependencies and Integration Points
The file depends on kernel fixed-point sine math, allocation, vmalloc, jiffies-related utilities, endian helpers, and vidtv's generic encoder interface. It emits `PES_PRIVATE_STREAM_1`, sets `S302M` as the encoder ID, and uses `VIDTV_S302M_FORMAT_IDENTIFIER` from the header for PMT registration descriptors elsewhere. It integrates with video encoders via `args.sync` and with muxing code through the generic encoder's access-unit metadata.

## Risks and Edge Cases
The encoder assumes 16-bit samples and reads `u16` directly from `src_buf`, so callers must provide properly sized and aligned sample data. `vidtv_s302m_get_sample()` handles `src_buf_offset > src_buf_sz` as a bug and wraps, but a malformed size can still produce abrupt audio loops. Buffer writes rely on `vidtv_memcpy()` bounds behavior; output larger than `VIDTV_S302M_BUF_SZ` would truncate or warn through helpers rather than return a direct error. Sync sample-count computation uses rounded integer durations, so long runs can drift relative to video.

## Test Signals
Validation should include generated stream decoding with ffmpeg or DVB tools, PTS alignment with video access units, source-buffer wrap callback behavior, and clear/destroy leak checks. Boundary tests should stress maximum access-unit counts, no-sync mode, null source tone generation, and small destination buffer behavior through the common safe-copy wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_s302m.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_s302m.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_s302m.h

## Purpose
`vidtv_s302m.h` declares the public interface and core wire layouts for vidtv's SMPTE 302M audio encoder. It lets vidtv service setup code instantiate an audio encoder, attach it to an encoder chain, and destroy it through a type-specific wrapper.

## Important APIs, Types, and Functions
The key public type is `struct vidtv_s302m_encoder_init_args`, which carries the encoder name, optional source buffer and size, elementary-stream PID, optional video sync encoder, source-exhaustion callback, and optional chain head. `struct vidtv_s302m_ctx` is the private context used by the implementation. `struct vidtv_smpte_s302m_es` models the 302M elementary-stream header bitfield, and `struct vidtv_s302m_frame_16` holds one 5-byte encoded 16-bit AES3 frame. `vidtv_s302m_encoder_init()` returns a populated `struct vidtv_encoder`; `vidtv_s302m_encoder_destroy()` frees it.

## Control Flow
Callers pass initialization arguments to `vidtv_s302m_encoder_init()`, which allocates the generic encoder and private context, configures callbacks, stream IDs, sample rate, source buffer settings, and optional chain linkage. Later muxing code calls the generic encoder's `encode` and `clear` callbacks.

## State and Persistence
The header-defined state is per encoder instance. It tracks current AES3 frame position, total access units, melody tone state, and back-pointer to the generic encoder. All state is volatile kernel memory owned by the encoder lifecycle.

## Dependencies and Integration Points
The header includes `linux/types.h` and `vidtv_encoder.h`, binding the S302M implementation to vidtv's generic encoder abstraction and musical note enum. `VIDTV_S302M_BUF_SZ` constrains the output buffer, and `VIDTV_S302M_FORMAT_IDENTIFIER` is used for MPEG registration signaling.

## Risks and Edge Cases
Because the header exposes the private context layout, unrelated code could couple to implementation details. The initialization args do not encode ownership for `src_buf`; the implementation borrows that pointer. The source-buffer callback is optional and must tolerate repeated wrap notifications.

## Test Signals
Compile coverage should verify integration with generic encoder callers. Runtime tests should instantiate with and without `sync`, with and without `src_buf`, and confirm the configured ES PID and private stream ID are reflected in downstream PMT/PES output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_s302m.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_ts.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_ts.c

## Purpose
`vidtv_ts.c` provides low-level MPEG transport-stream packet helpers for vidtv. It increments 4-bit continuity counters, emits null packets for padding, and emits PCR-only packets with an adaptation field.

## Important APIs, Types, and Functions
Public functions are `vidtv_ts_inc_cc()`, `vidtv_ts_null_write_into()`, and `vidtv_ts_pcr_write_into()`. Internal `vidtv_ts_write_pcr_bits()` converts a 27 MHz PCR counter into the 6-byte PCR base/extension encoding copied from ffmpeg-style logic. The functions use `struct vidtv_mpeg_ts`, `struct vidtv_mpeg_ts_adaption`, `struct null_packet_write_args`, and `struct pcr_write_args` declared in `vidtv_ts.h`.

## Control Flow
Null packet writing builds a TS header with PID `0x1fff`, payload-only mode, and the caller's continuity counter, copies it into the destination, increments the counter, then fills the remainder of the 188-byte packet with `0xff`. PCR writing builds a TS header for the caller's PID with adaptation-field-only mode, writes an adaptation field length of 183 with PCR flag set, writes the six PCR bytes, and pads the rest of the packet. PCR packets intentionally do not increment the continuity counter, following the cited MPEG rule for adaptation-only packets.

## State and Persistence
No module-level state is stored. The only mutable state is the caller-owned continuity-counter byte. Destination data is written into caller-owned buffers via vidtv safe copy/fill helpers.

## Dependencies and Integration Points
The file depends on `linux/math64.h`, printk ratelimiting, `vidtv_common.h`, and `vidtv_ts.h`. PSI serialization and the transport muxer use these routines to pad streams and insert timing references.

## Risks and Edge Cases
All writers assume the caller supplied a valid buffer, offset, size, and continuity pointer. Short buffers rely on `vidtv_memcpy()`/`vidtv_memset()` behavior to avoid overflow, but the functions still return the number of bytes attempted or copied by helpers and only warn if the final packet size is not exactly 188 bytes. PCR encoding uses integer division by 300 and expects a PCR value in 27 MHz ticks.

## Test Signals
Tests should assert null packets are exactly 188 bytes, have sync byte `0x47`, PID `0x1fff`, valid stuffing, and continuity wrap from 15 to 0. PCR tests should decode the written adaptation field and compare PCR base/extension against known input counter values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_ts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_ts.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_ts.h

## Purpose
`vidtv_ts.h` defines vidtv's MPEG-TS packet constants, packed header structures, write-argument types, and prototypes for null packet and PCR packet helpers.

## Important APIs, Types, and Functions
Constants include `TS_SYNC_BYTE`, `TS_PACKET_LEN`, `TS_PAYLOAD_LEN`, `TS_NULL_PACKET_PID`, `TS_CC_MAX_VAL`, `TS_LAST_VALID_PID`, and `TS_FILL_BYTE`. `struct vidtv_mpeg_ts` models the 4-byte TS header with sync byte, PID bitfield, scrambling/adaptation/payload flags, and continuity counter. `struct vidtv_mpeg_ts_adaption` models the adaptation-field prefix. Public APIs are `vidtv_ts_inc_cc()`, `vidtv_ts_null_write_into()`, and `vidtv_ts_pcr_write_into()`.

## Control Flow
Callers construct `null_packet_write_args` or `pcr_write_args` with destination buffer metadata and a continuity-counter pointer, then call the corresponding writer. The functions serialize one full TS packet at the supplied offset.

## State and Persistence
The header defines no storage. Continuity state is external and passed by pointer. The packed structures are transient serialization helpers.

## Dependencies and Integration Points
It includes `linux/types.h` and is consumed by PSI, muxing, and other vidtv TS-generation code. `TS_LAST_VALID_PID` is also used by PSI logic to return an invalid sentinel when a PMT PID is not found.

## Risks and Edge Cases
The C bitfield layout in the packed TS header is implementation-sensitive; the code compensates for PID endianness with explicit big-endian fields but still relies on local bitfield packing for flags. Callers must keep offsets TS-packet aligned when required by higher-level packetizers.

## Test Signals
Compile-time structure-size checks and runtime packet decoding should verify header layout, continuity counter wrap, null PID, adaptation-field flags, and payload-length assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_ts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_tuner.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_tuner.c

## Purpose
`vidtv_tuner.c` implements a virtual DVB tuner as an I2C driver. It simulates tuner lifecycle, frequency lock, bandwidth, intermediate frequency, and RF strength based on configured valid frequencies and DVB frontend properties.

## Important APIs, Types, and Functions
The file registers `vidtv_tuner_i2c_driver` with ID `"dvb_vidtv_tuner"`. `struct vidtv_tuner_dev` combines the `dvb_frontend`, simulated hardware state, and copied `vidtv_tuner_config`. `struct vidtv_tuner_hardware_state` records asleep/lock status, IF frequency, tuned frequency, and bandwidth. `vidtv_tuner_ops` implements DVB tuner callbacks: `init`, `sleep`, `suspend`, `resume`, `set_params`, `set_config`, `get_bandwidth`, `get_frequency`, `get_if_frequency`, `get_status`, and `get_rf_strength`.

## Control Flow
Probe receives platform data with a `dvb_frontend`, allocates tuner state, stores it as I2C client data, copies the tuner ops into `fe->ops.tuner_ops`, copies config, and stores the client in `fe->tuner_priv`. Tuning validates frontend frequency and bandwidth against tuner limits, stores requested values, marks lock, sleeps for the mock tune delay, then calls `vidtv_tuner_check_frequency_shift()` to confirm the requested frequency matches one of the configured valid arrays within `max_frequency_shift_hz`. Signal strength first checks shift/lock, selects a C/N table for DVB-T/T2, DVB-S, DVB-S2, or DVB-C Annex A, and returns a good or degraded millidB value based on modulation and FEC.

## State and Persistence
State is per I2C client and in-memory only. Sleep/suspend/resume toggle `hw_state.asleep`; tuning updates lock, frequency, and bandwidth; init sets IF frequency to a hardcoded 5000. The configuration can be replaced through `set_config()`.

## Dependencies and Integration Points
The implementation depends on I2C core, DVB frontend APIs, configured `dtv_frontend_properties`, and valid-frequency arrays supplied by the vidtv bridge. It plugs into the demod/bridge frontend by replacing tuner ops at probe time.

## Risks and Edge Cases
`vidtv_tuner_check_frequency_shift()` uses `abs(c->frequency - valid_freqs[i])` on unsigned values, which can be fragile if frequencies differ across the signed range. The `max_frequency_shift_hz` field is `u8`, likely too small for realistic Hz tolerances. Unsupported delivery systems return `-EINVAL` and clear or avoid lock. C/N fallback interpolation depends on `shift` being a 0-100 percentage and can produce misleading values if the shift calculation changes.

## Test Signals
Tests should tune each delivery system to exact and shifted valid frequencies, verify lock status and RF strength, exercise invalid bandwidth/frequency paths, and check probe/remove lifetime. DVB scan utilities should discover services only on configured valid frequencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_tuner.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_tuner.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_tuner.h

## Purpose
`vidtv_tuner.h` defines the bridge-provided configuration for the virtual DVB tuner.

## Important APIs, Types, and Functions
The main type is `struct vidtv_tuner_config`. It contains a `struct dvb_frontend *fe`, mock power-up and tune delays, arrays of valid DVB-T, DVB-C, and DVB-S frequencies with `NUM_VALID_TUNER_FREQS` slots each, and `max_frequency_shift_hz`, the tolerated frequency offset for partial signal quality.

## Control Flow
The vidtv bridge fills this structure and passes it as I2C client platform data. `vidtv_tuner_i2c_probe()` copies it into private state and uses `fe` to install tuner callbacks.

## State and Persistence
The header defines configuration, not storage. At runtime the implementation copies the config per tuner instance and can replace it through the DVB tuner `set_config` callback.

## Dependencies and Integration Points
It includes `linux/types.h` and `media/dvb_frontend.h`, tying the tuner to DVB frontend registration. The valid frequency arrays are consumed according to `dtv_frontend_properties.delivery_system`.

## Risks and Edge Cases
`max_frequency_shift_hz` is declared as `u8`, which limits tolerance to 255 Hz despite the name implying Hz-scale tuning offsets. Array termination relies on zero entries; a full array with no zero terminator is valid because iteration is bounded, but zeros cannot represent valid frequency 0.

## Test Signals
Configuration tests should verify bridge-provided valid frequencies are honored for all supported systems and that `set_config` updates runtime behavior without requiring reprobe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_tuner.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vim2m.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vim2m.c

## Purpose
`vim2m.c` is a virtual V4L2 memory-to-memory test device. It exercises the mem2mem and videobuf2 frameworks by accepting OUTPUT buffers, transforming pixels into CAPTURE buffers, and completing jobs through delayed work that simulates hardware interrupt latency.

## Important APIs, Types, and Functions
The driver registers a platform device/driver named `"vim2m"` and a `video_device` with V4L2 M2M capabilities. Device state is `struct vim2m_dev`; per-open-instance state is `struct vim2m_ctx`; per-queue format state is `struct vim2m_q_data`; supported formats are in `formats[]`. Core processing functions are `device_process()`, `copy_line()`, and `copy_two_pixels()`, supporting RGB565/RGB565X/RGB24/BGR24 input and RGB/YUYV/Bayer capture output. Mem2mem callbacks are `device_run()`, `job_ready()`, `job_abort()`, and delayed-work `device_work()`. V4L2 ioctl handlers cover format enumeration, try/set/get format, frame sizes, streaming, buffer operations, request controls, and events.

## Control Flow
Module init registers the platform device and driver. Probe allocates the device, registers a V4L2 device, initializes `v4l2_m2m_dev`, sets up a media device and media-controller entity, registers `/dev/video0` or another free node, and registers the media device. On open, a `vim2m_ctx` is allocated, controls are created, default source and destination formats are initialized, and a mem2mem context creates vb2 queues. Users queue source and destination buffers; `job_ready()` waits until `translen` buffers are available on both sides. `device_run()` applies request controls, processes the next buffer pair immediately, completes request controls, and schedules delayed work. `device_work()` removes buffers, marks them done, and either finishes the M2M job or recursively starts the next pair in the transaction.

## State and Persistence
Global module parameters control debug level, default transaction time, and single-planar versus multiplanar operation. Per-device state tracks instance count, locks, V4L2/media objects, and the mem2mem scheduler. Per-context state tracks controls, pending transaction length/time, abort flag, H/V flip mode, colorimetry, source/destination format data, sequence counters, vb2 mutex, and delayed work. All state is volatile and released on close/remove/module unload.

## Dependencies and Integration Points
The driver uses V4L2 core, media controller, `v4l2-mem2mem`, videobuf2 vmalloc memory ops, V4L2 controls/events/requests, and platform-driver registration. It is intended for user-space V4L2 compliance tools and applications testing mem2mem scheduling, format negotiation, requests, scaling, flipping, and conversion without hardware.

## Risks and Edge Cases
Processing assumes a single memory plane in `device_process()` by accessing plane 0 even in multiplanar mode; current formats are effectively single-plane, but future multi-plane formats would need deeper handling. Format conversion processes pixels in pairs (`width >> 1`), so width alignment is critical, especially for Bayer output. `copy_line()` reverse mode assumes even widths. `stop_streaming()` cancels delayed work and returns all queued buffers as errors, but controls must be completed for every path. `job_abort()` only sets a flag, so completion waits for the delayed work path. Memory limit enforcement can reduce requested buffer counts down to zero if formats grow.

## Test Signals
Useful tests include `v4l2-compliance` in both single-planar and multiplanar modes, format enumeration and try/set/get checks, HFLIP/VFLIP controls, transaction length/time controls, request API behavior, streaming stop during delayed work, Bayer alignment, scaling between different resolutions, and conversion correctness using known pixel patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vim2m.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/Kconfig

## Purpose
`vimc/Kconfig` exposes the Virtual Media Controller driver as `CONFIG_VIDEO_VIMC`.

## Important APIs, Types, and Functions
The option is a tristate named "Virtual Media Controller Driver (VIMC)". It depends on `VIDEO_DEV` and selects `FONT_SUPPORT`, `FONT_8x16`, `MEDIA_CONTROLLER`, `VIDEO_V4L2_SUBDEV_API`, `VIDEOBUF2_VMALLOC`, `VIDEOBUF2_DMA_CONTIG`, and `VIDEO_V4L2_TPG`.

## Control Flow
When enabled as built-in or module, the Makefile builds `vimc.o`, whose init path registers a virtual platform device and platform driver. The selected dependencies ensure the media graph, subdev active-state APIs, font-backed OSD, vb2 allocators, and test pattern generator are available.

## State and Persistence
Kconfig state persists in the kernel build configuration only. It does not create runtime state by itself.

## Dependencies and Integration Points
The dependency and select list matches the implementation: VIMC needs video device core, media controller topology, V4L2 subdev nodes, vmalloc or DMA-contig capture queues, and TPG/font support for sensor frames.

## Risks and Edge Cases
Because it selects features, enabling VIMC can pull in media-controller and buffer allocator code that test kernels might not otherwise include. The help text notes the topology is hard coded, so enabling it is primarily for testing and development.

## Test Signals
Build tests should verify `CONFIG_VIDEO_VIMC=m` and `=y`. Runtime smoke tests should confirm the module loads, creates a media device and video nodes, and exposes the expected hard-coded topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/Makefile

## Purpose
`vimc/Makefile` defines the object composition for the VIMC kernel module.

## Important APIs, Types, and Functions
`vimc-y` aggregates `vimc-core.o`, `vimc-common.o`, `vimc-streamer.o`, `vimc-capture.o`, `vimc-debayer.o`, `vimc-scaler.o`, `vimc-sensor.o`, and `vimc-lens.o`. `obj-$(CONFIG_VIDEO_VIMC) += vimc.o` connects the aggregate to the Kconfig option.

## Control Flow
When `CONFIG_VIDEO_VIMC` is enabled, kbuild links the listed objects into one `vimc` module or built-in object. `vimc-core.o` owns module init/exit; the remaining objects supply entity type callbacks and shared helpers referenced by the core topology.

## State and Persistence
The file has no runtime state. Build state is derived from Kconfig.

## Dependencies and Integration Points
The object list must stay synchronized with declarations in `vimc-common.h` and entity references in `vimc-core.c`. Removing one entity object without changing topology would leave unresolved symbols such as `vimc_sensor_type`.

## Risks and Edge Cases
Adding a new entity type requires updating this file, the topology config, and common declarations together. Object ordering is generally not semantically important after linking, but missing objects break module linkage.

## Test Signals
Build VIMC as module and built-in to catch missing object references. `modinfo` and load tests should show one `vimc` module containing all entity implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-capture.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-capture.c

## Purpose
`vimc-capture.c` implements VIMC capture video nodes. A capture entity is the sink at the end of a VIMC media pipeline; it owns a vb2 queue, accepts user buffers, starts/stops a `vimc_stream`, and copies processed frames into queued capture buffers.

## Important APIs, Types, and Functions
`struct vimc_capture_device` embeds `vimc_ent_device`, `video_device`, `v4l2_pix_format`, `vb2_queue`, queued-buffer list, locks, sequence counter, stream, and sink pad. `struct vimc_capture_buffer` wraps `vb2_v4l2_buffer`. The entity is exported as `vimc_capture_type` with add/unregister/release callbacks. Key callbacks include format ioctls, `vimc_capture_start_streaming()`, `vimc_capture_stop_streaming()`, queue setup/prepare/queue, and `vimc_capture_process_frame()`.

## Control Flow
`vimc_capture_add()` allocates and initializes a video node, sink media pad, mutex/spinlock, vb2 queue, default format, `vimc_ent_device` callbacks, and V4L2 ioctl/fops before registering the video device. When users start streaming, vb2 calls `vimc_capture_start_streaming()`, which starts the media pipeline and then calls `vimc_streamer_s_stream()` to build and run the upstream processing thread. The streamer eventually calls `vimc_capture_process_frame()`, which pops one queued buffer, timestamps and sequences it, copies the incoming frame into plane 0, sets payload, and marks it done.

## State and Persistence
Per-node runtime state includes current format, queue contents, sequence counter, and stream thread handle through `struct vimc_stream`. State is in memory and resets on stream start/stop or device removal. Buffers are returned queued on start failure and error on stop.

## Dependencies and Integration Points
The file depends on V4L2 ioctl helpers, videobuf2 core, vmalloc and DMA-contig memops, VIMC common helpers, and the VIMC streamer. Link validation uses `vimc_vdev_link_validate()`. The global `vimc_allocator` selects vmalloc versus DMA-contig memory operations and USERPTR availability.

## Risks and Edge Cases
If no capture buffer is queued, `process_frame()` returns `ERR_PTR(-EAGAIN)`, causing the streamer to stop processing that frame without delivering data. Format changes are blocked while vb2 is busy. The frame copy assumes the incoming frame matches `format.sizeimage`; upstream link validation and format propagation are responsible for that. The code uses a spinlock as a hardware-driver reference even though the virtual thread context can sleep.

## Test Signals
Use media-ctl to validate links, `v4l2-compliance` for capture ioctls and vb2 behavior, streaming tests with too few buffers, streamoff cleanup checks, and format negotiation tests across RGB/Bayer formats and both allocator modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-capture.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-common.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-common.c

## Purpose
`vimc-common.c` provides shared pixel-format mapping, source detection, link validation, and subdevice registration helpers for all VIMC entities.

## Important APIs, Types, and Functions
The central static table `vimc_pix_map_list[]` maps media-bus codes to V4L2 fourcc formats, bytes per pixel, and Bayer/non-Bayer classification. Exported lookup helpers are `vimc_pix_map_by_index()`, `vimc_mbus_code_by_index()`, `vimc_pix_map_by_code()`, and `vimc_pix_map_by_pixelformat()`. `vimc_is_source()` detects entities with no sink pads. `vimc_vdev_link_validate()` compares source and sink formats. `vimc_ent_sd_register()` initializes and registers a V4L2 subdevice entity with pads, ops, optional active-state initialization, and devnode exposure.

## Control Flow
Link validation retrieves a source and sink `v4l2_pix_format` either through subdev `get_fmt` or a video-device `vdev_get_format` callback, logs both formats, enforces matching width, height, pixelformat, compatible field order, and compatible colorimetry. Subdevice registration fills `vimc_ent_device`, initializes the subdev, assigns entity function and ops, sets flags for devnode/events, initializes pads, finalizes active state if supported, and registers with the parent V4L2 device.

## State and Persistence
The format map is static read-only state. The helper functions do not own long-lived resources except during successful subdevice registration. `vimc_ent_sd_register()` transfers initialized media entity/subdev state to V4L2 core and cleans it up on failure.

## Dependencies and Integration Points
The file depends on media entity helpers, V4L2 subdev and video-device APIs, V4L2 controls, and `vimc-common.h`. All entity implementations depend on these helpers for consistent format negotiation and registration.

## Risks and Edge Cases
`vimc_get_pix_format()` assumes `vimc_pix_map_by_code()` succeeds after subdev `get_fmt`; a missing map would lead to a null dereference. Link validation intentionally skips detailed colorimetry comparison if either side uses default colorspace. The format table ordering matters because the scaler's enumeration expects non-Bayer formats first.

## Test Signals
Tests should enumerate all bus codes and pixel formats, validate links with matching and mismatching dimensions/pixelformats/colorimetry, and run subdevice registration failure injection to verify cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-common.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-common.h

## Purpose
`vimc-common.h` is the shared interface for the VIMC virtual media graph. It defines common constants, controls, entity abstractions, pixel-format maps, device structures, sensor state, and helper prototypes.

## Important APIs, Types, and Functions
Important definitions include frame size limits, fixed timing constants, custom controls `VIMC_CID_TEST_PATTERN`, `VIMC_CID_MEAN_WIN_SIZE`, and `VIMC_CID_OSD_TEXT_MODE`, allocator enum, source/sink pad macros, and `vimc_colorimetry_clamp()`. Core types are `struct vimc_pix_map`, `struct vimc_ent_device`, `struct vimc_device`, `struct vimc_ent_type`, `struct vimc_ent_config`, and `struct vimc_sensor_device`. It declares all entity type exports and common helpers for format lookup, subdev registration, source detection, and link validation.

## Control Flow
`vimc-core.c` consumes `vimc_ent_config` and `vimc_ent_type` callbacks to instantiate topology entities. Each entity embeds or references `vimc_ent_device` so the streamer can call `process_frame()` uniformly and link validation can query video-node formats through `vdev_get_format()`.

## State and Persistence
Most structures describe per-device or per-entity runtime state. `vimc_sensor_device` includes test-pattern generator state, controls, media pad, frame buffer, and virtual hardware timing/OSD configuration. `vimc_allocator` is a module parameter declared externally and used by capture queue setup.

## Dependencies and Integration Points
The header includes platform device, slab, media-device, V4L2 device, TPG, and V4L2 controls headers. It forms the internal ABI between all VIMC object files; changes here can impact core topology, streamer, capture, sensor, debayer, scaler, and lens.

## Risks and Edge Cases
The `VIMC_IS_SRC(pad)` and `VIMC_IS_SINK(pad)` macros assume pad 0 is sink and nonzero is source, which matches current two-pad entities but is not a general media-entity rule. `vimc_colorimetry_clamp()` uses upper-bound checks tied to current V4L2 enum ranges. Exposing `vimc_sensor_device` here allows streamer code to inspect sensor hardware timing, but also couples streamer to sensor internals.

## Test Signals
Build tests catch internal ABI drift. Runtime tests should exercise custom controls, allocator selection, frame size limits, colorimetry clamping, and pipeline traversal across all entity types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-core.c

## Purpose
`vimc-core.c` owns VIMC module/platform registration and hard-coded media topology construction. It creates sensors, debayers, raw capture nodes, an RGB/YUV input, scaler, RGB/YUV capture node, and lens ancillary entities, links them, registers V4L2/media devices, and tears everything down.

## Important APIs, Types, and Functions
Module parameter `vimc_allocator` selects vmalloc or DMA-contig capture allocation. Topology is described by `ent_config[]`, `data_links[]`, `ancillary_links[]`, and `pipe_cfg`. Lifecycle helpers include `vimc_add_subdevs()`, `vimc_create_links()`, `vimc_unregister_subdevs()`, `vimc_release_subdevs()`, `vimc_register_devices()`, `vimc_probe()`, `vimc_remove()`, `vimc_init()`, and `vimc_exit()`.

## Control Flow
Module init registers a virtual platform device then a matching platform driver. Probe finds the VGA8x16 font for OSD text, configures the TPG font, optionally coerces DMA mask for DMA-contig mode, allocates `vimc_device`, initializes media and V4L2 devices, allocates the entity array, calls each entity type's `add()` callback, creates data and ancillary links, registers the media device, and exposes subdev nodes. Remove unregisters entity nodes, media device, and V4L2 device; final cleanup occurs through the V4L2 device release callback.

## State and Persistence
Runtime state is held in one `struct vimc_device` associated with the platform device. It owns the media device, V4L2 device, pipe config pointer, and array of entity device pointers. State exists only while the module/platform driver is loaded.

## Dependencies and Integration Points
The core depends on platform bus, DMA mask helpers, font support, media controller, TPG font setup, V4L2 device registration, and all `vimc_*_type` entity exports. User-space sees the resulting topology through media controller and V4L2 nodes.

## Risks and Edge Cases
The topology indexes in data and ancillary links must match `ent_config[]`; incorrect indices create wrong links or out-of-bounds access. Probe fails if the font is unavailable. Error paths must avoid double release because subdevice release is split between explicit failure cleanup and the V4L2 device release callback after successful registration. The TODO RGB/YUV input currently reuses the sensor implementation.

## Test Signals
Load/unload tests should verify all entities and links appear and disappear cleanly. `media-ctl -p` should show the expected topology. Tests should cover both allocator modes, link toggling between debayers/input and scaler, and failure injection around entity registration/link creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-debayer.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-debayer.c

## Purpose
`vimc-debayer.c` implements a VIMC subdevice that converts Bayer-pattern sink frames to RGB-like source frames. It is a virtual pixel conversion stage used between sensors and the scaler/capture pipeline.

## Important APIs, Types, and Functions
`struct vimc_debayer_device` embeds entity/subdev/control/pad state, a source frame buffer, conversion callback, and virtual hardware configuration. Static maps describe Bayer code color ordering and supported RGB source bus codes. Key callbacks are `vimc_debayer_init_state()`, `vimc_debayer_enum_mbus_code()`, `vimc_debayer_set_fmt()`, `vimc_debayer_s_stream()`, `vimc_debayer_process_frame()`, and `vimc_debayer_s_ctrl()`. The entity export is `vimc_debayer_type`.

## Control Flow
Active state initializes sink pad to SRGGB8 and source pad to RGB888. Format setting is allowed only on the sink when not streaming; the source follows dimensions/colorimetry with RGB output code. Stream-on snapshots active formats into `hw`, determines sink bytes per pixel, source code, Bayer map, dimensions, and allocates a source frame. For each incoming frame, `vimc_debayer_process_frame()` iterates over every pixel, computes RGB values by averaging same-color samples in the configured odd-sized mean window, and writes RGB/BGR bytes to the source frame.

## State and Persistence
State is per subdevice. Active V4L2 subdev state stores negotiated formats. `hw` is a stream-time snapshot plus mean-window control value. `src_frame` exists only while streaming and is freed on stream-off. There is no persistent storage.

## Dependencies and Integration Points
The file depends on V4L2 subdev active-state APIs, controls/events, vmalloc, media-bus formats, and common VIMC pixel maps. It integrates with the streamer through `ved.process_frame` and with user space through V4L2 subdev format and control ioctls.

## Risks and Edge Cases
The per-pixel mean-window algorithm is intentionally simple but expensive, especially at large resolutions and window sizes. `vimc_debayer_process_rgb_frame()` handles RGB24 and BGR24 pixelformats; other valid source bus codes mapped to RGB24 are okay through `vimc_pix_map_by_code()`, but unsupported fourcc cases silently write nothing. `set_fmt()` blocks active changes when `src_frame` exists, so stream state must be correct. The control handler stores mean-window changes directly into `hw`, including while streaming.

## Test Signals
Tests should enumerate sink Bayer and source RGB codes, verify source format propagation, change mean-window control, stream known Bayer patterns through the pipeline, and validate stream-on/off buffer allocation cleanup. Performance tests at maximum resolution can expose excessive CPU use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-debayer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-lens.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-lens.c

## Purpose
`vimc-lens.c` implements a minimal virtual lens subdevice for VIMC ancillary links. It exposes a focus control but does not process frames.

## Important APIs, Types, and Functions
`struct vimc_lens_device` embeds `vimc_ent_device`, `v4l2_subdev`, `v4l2_ctrl_handler`, and the last `focus_absolute` value. `vimc_lens_add()` allocates the device, creates `V4L2_CID_FOCUS_ABSOLUTE`, registers a `MEDIA_ENT_F_LENS` subdev with no pads, and returns the entity wrapper. `vimc_lens_s_ctrl()` stores focus values. `vimc_lens_release()` frees controls, subdev state, entity state, and memory. The export is `vimc_lens_type`.

## Control Flow
The core topology creates two lens entities and attaches them as ancillary links to sensors. User-space control writes call `vimc_lens_s_ctrl()`, which updates in-memory focus state. There is no stream callback and no media data path.

## State and Persistence
The only simulated hardware state is `focus_absolute`, per lens instance and volatile. It resets on device release.

## Dependencies and Integration Points
The file uses V4L2 controls/events/subdev APIs and VIMC common registration. It integrates with media-controller ancillary links from `vimc-core.c`, allowing user space to see a sensor-lens relationship.

## Risks and Edge Cases
The focus value has no effect on generated sensor frames, so it is suitable for topology/control testing rather than optical simulation. There are no pads, so any code assuming every entity has a pad must handle lens entities carefully.

## Test Signals
Tests should verify lens subdevices appear in media topology, ancillary links point to sensors, focus control range is 0 to 1023, and control events/log status work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-lens.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-scaler.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-scaler.c

## Purpose
`vimc-scaler.c` implements a two-pad VIMC scaler subdevice. It accepts non-Bayer frames, supports sink cropping and source scaling, and produces a resized frame for downstream capture.

## Important APIs, Types, and Functions
`struct vimc_scaler_device` embeds entity/subdev/pads, a stream-time source frame, and virtual hardware snapshots of sink/source formats, crop rectangle, and bytes per pixel. Key callbacks are `vimc_scaler_init_state()`, `vimc_scaler_enum_mbus_code()`, `vimc_scaler_set_fmt()`, `vimc_scaler_get_selection()`, `vimc_scaler_set_selection()`, `vimc_scaler_s_stream()`, and `vimc_scaler_process_frame()`. The entity export is `vimc_scaler_type`.

## Control Flow
Default active state sets both pads to 640x480 RGB888 and crop to the full sink. The scaler enumerates only non-Bayer bus codes. Sink format changes update code/colorimetry, clamp dimensions, reset crop, and propagate to source; source format changes can adjust dimensions but inherit code/colorimetry. Crop selection is allowed only on the sink and is clamped inside sink bounds with minimum size. Stream-on snapshots formats and crop, computes frame size, and allocates `src_frame`. Frame processing uses nearest-neighbor mapping from each output pixel to a cropped input pixel and copies one pixel of `bpp` bytes.

## State and Persistence
Negotiated formats and crop live in V4L2 subdev state. The `hw` snapshot and `src_frame` exist while streaming. State is freed on stream-off and release.

## Dependencies and Integration Points
The scaler depends on media-bus formats, V4L2 rectangle helpers, subdev active-state APIs, vmalloc, and common pixel-map helpers. It sits between debayer/input and RGB/YUV capture in the hard-coded topology.

## Risks and Edge Cases
The scaler rejects Bayer formats, so links from raw Bayer sources must pass through debayer or raw capture instead. Active format/crop changes are blocked while `src_frame` exists. The scaling algorithm is simple nearest-neighbor and does not handle multi-plane formats. It assumes `vimc_pix_map_by_code(format->code)` succeeds for active formats.

## Test Signals
Tests should enumerate only non-Bayer codes, verify crop bounds/minimums, confirm source propagation from sink, stream scaling up/down with known patterns, and validate link failures when formats do not match downstream capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-scaler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-sensor.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-sensor.c

## Purpose
`vimc-sensor.c` implements VIMC source subdevices backed by the V4L2 test pattern generator. Sensors generate frames, overlay optional text, expose image and timing controls, and provide frame cadence information used by the streamer thread.

## Important APIs, Types, and Functions
The implementation uses `struct vimc_sensor_device` from `vimc-common.h`. Key callbacks are `vimc_sensor_init_state()`, bus-code/frame-size enumeration, `vimc_sensor_set_fmt()`, `vimc_sensor_s_stream()`, `vimc_sensor_process_frame()`, and `vimc_sensor_s_ctrl()`. Timing helpers include `vimc_calc_vblank()` and `vimc_sensor_update_frame_timing()`. Controls include test pattern, OSD mode, H/V flip, brightness, contrast, hue, saturation, read-only pixel rate, read-only hblank, and adjustable vblank.

## Control Flow
Subdev state initializes to 640x480 RGB888. Format setting clamps size, validates bus code, clamps colorimetry, blocks active changes while streaming, updates hardware size, recalculates default vblank based on resolution target FPS, and updates timing controls. Stream-on configures the TPG for active format, computes frame size, updates frame timing, allocates a frame buffer, and records stream start time. `process_frame()` fills the frame with TPG output and optionally overlays color order, control values, sensor size, and elapsed-time counters.

## State and Persistence
Runtime state includes active subdev format, TPG data, control handler values, allocated frame, and `hw` fields for size, OSD mode, stream timestamp, and `fps_jiffies`. It is volatile and reset on stream-off/release. `fps_jiffies` is read by `vimc-streamer.c` to schedule frames.

## Dependencies and Integration Points
The sensor depends on V4L2 subdev/control/event APIs, media-bus formats, vmalloc, V4L2 TPG, and common VIMC helpers. It is the source for raw capture, debayer, scaler through the RGB/YUV input placeholder, and ancillary lens links.

## Risks and Edge Cases
TPG allocation is sized to maximum width and must remain consistent with negotiated formats. Stream-off frees `frame` without checking whether it is already null, which is safe for `vfree()`. Timing is simulated through jiffies, so precision is coarse. The RGB/YUV input entity reuses sensor behavior, which may blur semantic distinctions in topology tests.

## Test Signals
Tests should stream all supported formats, exercise TPG controls, OSD modes, timing controls and resolution changes, verify frame cadence changes around the 30 FPS threshold, and ensure active format changes are rejected during streaming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-sensor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-streamer.c -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-streamer.c

## Purpose
`vimc-streamer.c` runs the active VIMC media pipeline. It walks upstream from a capture node, enables subdevices, creates an ordered pipeline list, and starts a kernel thread that repeatedly pulls a frame from the source and pushes it through each entity to the capture sink.

## Important APIs, Types, and Functions
The exported API is `vimc_streamer_s_stream(struct vimc_stream *stream, struct vimc_ent_device *ved, int enable)`. Internal helpers include `vimc_get_source_entity()`, `vimc_streamer_pipeline_init()`, `vimc_streamer_pipeline_terminate()`, `vimc_streamer_get_sensor()`, and `vimc_streamer_thread()`. `struct vimc_stream` is declared in `vimc-streamer.h`.

## Control Flow
On enable, `vimc_streamer_s_stream()` returns if a thread already exists, otherwise initializes the pipeline. Pipeline initialization starts with the capture entity, stores each `vimc_ent_device`, enables subdev streaming where applicable, follows the first linked sink pad upstream, and stops when it reaches an entity with no upstream source, which must be source-only. It then starts `vimc-streamer thread`. The thread loops until stopped, reads FPS jiffies from the first sensor in the pipeline or defaults to 30 FPS, then iterates from source to sink calling each entity's `process_frame()` with the previous frame pointer. On disable, it stops the thread and terminates the pipeline in reverse order.

## State and Persistence
The stream object stores the media pipeline, up to 16 entity pointers, pipeline size, and kthread pointer. This state exists only while capture streaming is active and is cleared during termination.

## Dependencies and Integration Points
The streamer depends on media graph helpers, V4L2 subdev streaming state, kernel freezer/kthread APIs, and VIMC entity callbacks. Capture nodes call it from vb2 start/stop streaming; sensor/debayer/scaler/capture implementations provide the frame-processing callbacks it invokes.

## Risks and Edge Cases
Only the first sink pad is followed, so more complex fan-in topologies are not represented. Pipeline length is capped at 16. If any `process_frame()` returns null or error, remaining downstream entities are skipped for that frame. The streamer reads sensor internals to get frame cadence, coupling it to `struct vimc_sensor_device`.

## Test Signals
Tests should start and stop streaming repeatedly, validate pipeline order for each enabled link path, test immediate streamoff after streamon, confirm subdev `s_stream` calls balance on failures, and exercise no-buffer capture behavior where processing returns `-EAGAIN`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-streamer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-streamer.h -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-streamer.h

## Purpose
`vimc-streamer.h` declares the streaming engine state and the start/stop API used by VIMC capture nodes.

## Important APIs, Types, and Functions
`VIMC_STREAMER_PIPELINE_MAX_SIZE` limits a runtime pipeline to 16 entities. `struct vimc_stream` contains a `media_pipeline`, ordered `ved_pipeline` array, `pipe_size`, and `task_struct *kthread`. `vimc_streamer_s_stream()` starts or stops streaming for a capture-anchored pipeline.

## Control Flow
Capture entities embed `struct vimc_stream` and pass it plus their `vimc_ent_device` to `vimc_streamer_s_stream()` from vb2 start/stop callbacks. The implementation fills the array and manages the thread.

## State and Persistence
The struct is per capture stream and transient. It does not persist beyond active streaming and is reset by the implementation on stop.

## Dependencies and Integration Points
The header includes media-device APIs and `vimc-common.h`. It is consumed by `vimc-capture.c` and implemented by `vimc-streamer.c`.

## Risks and Edge Cases
The fixed-size array means topology expansion must also revisit the max size. Callers must pass a valid capture-side entity and must not concurrently start/stop the same stream without the capture/vb2 locks.

## Test Signals
Compile tests catch API drift. Runtime tests should verify no stale `kthread` pointer remains after stop and that pipeline sizes fit the hard-coded topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-streamer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/Kconfig

## Purpose
`visl/Kconfig` exposes the Virtual Stateless Decoder Driver and its optional debugfs support.

## Important APIs, Types, and Functions
`CONFIG_VIDEO_VISL` is a tristate depending on `VIDEO_DEV` and selecting `FONT_SUPPORT`, `FONT_8x16`, `VIDEOBUF2_VMALLOC`, `V4L2_MEM2MEM_DEV`, `MEDIA_CONTROLLER`, and `VIDEO_V4L2_TPG`. `CONFIG_VISL_DEBUGFS` is a bool depending on `VIDEO_VISL` and `DEBUG_FS`, enabling debugfs bitstream dumps.

## Control Flow
When `VIDEO_VISL` is enabled, kbuild builds the VISL module from objects in the Makefile. If `VISL_DEBUGFS=y`, the debugfs object is added.

## State and Persistence
This file stores build configuration only. Runtime decoder and debugfs state are in the VISL source files outside this work item.

## Dependencies and Integration Points
VISL integrates with V4L2 mem2mem, media controller, vb2 vmalloc, TPG, and font support. It is used for stateless codec uAPI development and can run user-space decode loops without hardware.

## Risks and Edge Cases
Enabling debugfs can expose bitstream buffers for diagnostics and should be limited to debug/development kernels. The core driver selects several media facilities, which can enlarge minimal test kernels.

## Test Signals
Build with `VIDEO_VISL=m/y` and with `VISL_DEBUGFS=y/n`. Runtime tests should confirm module load, media/video node creation, mem2mem operation, and debugfs entries only when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/Makefile

## Purpose
`visl/Makefile` defines the object composition for the VISL virtual stateless decoder module.

## Important APIs, Types, and Functions
`visl-y` includes `visl-core.o`, `visl-video.o`, `visl-dec.o`, and `visl-trace-points.o`. When `CONFIG_VISL_DEBUGFS=y`, it adds `visl-debugfs.o`. `obj-$(CONFIG_VIDEO_VISL) += visl.o` connects the aggregate to Kconfig.

## Control Flow
Kbuild links the listed objects into `visl.o` when `VIDEO_VISL` is enabled, conditionally including debugfs support. Runtime module entry points are provided by the VISL core object.

## State and Persistence
The file has no runtime state. It controls build-time inclusion only.

## Dependencies and Integration Points
The object list must match VISL implementation symbol dependencies. Trace points are always included; debugfs is conditional on Kconfig.

## Risks and Edge Cases
Adding codec support or diagnostics requires updating this Makefile with new objects. A mismatch between `CONFIG_VISL_DEBUGFS` and debugfs code references would cause link failures.

## Test Signals
Build matrix coverage for debugfs enabled and disabled should catch missing objects. Module load tests should confirm tracepoints are present and debugfs support appears only under the configured option.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/Makefile -->
