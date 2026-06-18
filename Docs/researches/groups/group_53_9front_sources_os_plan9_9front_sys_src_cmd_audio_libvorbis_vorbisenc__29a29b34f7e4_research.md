# Group Research: group_53_9front_sources_os_plan9_9front_sys_src_cmd_audio_libvorbis_vorbisenc__29a29b34f7e4

Scope: `Docs/research_subset_a.md`, specifically the listed 9front audio/libvorbis encoder, vorbisfile, window, and mixfs sources. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/vorbisenc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/vorbisenc.c

High-level libvorbis encoder setup implementation. It selects encoder setup templates, materializes codec setup structs, configures psychoacoustic parameters, floors, residues, mappings, block sizes, bitrate management, and the public `vorbis_encode_*` control/init entry points.

Important contents:
- Defines local setup data structures: `static_bookblock`, `vorbis_residue_template`, `vorbis_mapping_template`, `ve_setup_data_template`, and small psychoacoustic adjustment blocks.
- Includes all encoder mode setup headers: `setup_44.h`, `setup_44u.h`, `setup_44p51.h`, `setup_32.h`, `setup_8.h`, `setup_11.h`, `setup_16.h`, `setup_22.h`, and `setup_X.h`.
- `setup_list[]` orders stereo, 5.1, uncoupled, low-rate, and generic setup templates for template selection by channel count, sample rate, quality, or bitrate.
- `vorbis_encode_floor_setup()` copies floor1 templates, offsets book numbers into the codec setup book table, and installs floor params.
- `vorbis_encode_global_psych_setup()` and `vorbis_encode_global_stereo()` interpolate global pre/post echo thresholds, stereo coupling point limits, and sliding lowpass limits.
- `vorbis_encode_psyset_setup()`, `vorbis_encode_tonemask_setup()`, `vorbis_encode_compand_setup()`, `vorbis_encode_peak_setup()`, `vorbis_encode_noisebias_setup()`, and `vorbis_encode_ath_setup()` populate per-block psychoacoustic parameters from tuning tables.
- `vorbis_encode_residue_setup()` copies residue templates, deduplicates/reuses codebooks, chooses managed/unmanaged books, computes residue end points from lowpass/stereo/LFE limits, and handles residue type 2 bundled-channel sizing.
- `vorbis_encode_map_n_res_setup()` builds one or two mode/map entries depending on whether short and long block sizes differ.
- `get_setup_template()` searches `setup_list[]` for a channel/rate-compatible setup whose quality or bitrate request falls in the template mapping range.
- Public setup/init functions are `vorbis_encode_setup_vbr()`, `vorbis_encode_init_vbr()`, `vorbis_encode_setup_managed()`, `vorbis_encode_init()`, `vorbis_encode_setup_init()`, and `vorbis_encode_ctl()`.

Control-flow summary:
- VBR or managed setup records the request, finds a setup template, initializes high-level defaults, then leaves detailed setup pending.
- `vorbis_encode_setup_init()` freezes the high-level setup, clamps nonsensical ATH/amplitude values, sets block sizes, installs floors, psych parameters, residues/maps, nominal bitrate fields, and bitrate manager state.
- `vorbis_encode_ctl()` can adjust rate management, lowpass, impulse block tuning, and coupling until setup is frozen via `hi->set_in_stone`.

Integration points:
- Depends on `vorbis/codec.h`, `vorbis/vorbisenc.h`, `codec_internal.h`, `os.h`, and `misc.h`.
- Consumes the static setup tables under `modes/` and generated codebooks under `books/`.
- Produces internal `codec_setup_info` state consumed by the rest of libvorbis analysis/encoding.

Risk and review signals:
- Many arrays are indexed by interpolated `base_setting`; correctness depends on template mapping counts matching all tuning arrays.
- `book_dup_or_new()` deduplicates only by pointer identity, so generated/static book pointer stability matters.
- `vorbis_encode_residue_setup()` assumes residue templates use at most 12 partitions and four stages, matching the local `static_bookblock` shape.
- Control calls that mutate setup after `set_in_stone` correctly return `OV_EINVAL`; callers must sequence ctl calls before `vorbis_encode_setup_init()`.
- Residue type 2 end calculation scans installed mappings to infer channel count; mapping/residue setup order is therefore important.

Filesystem relevance:
- No filesystem implementation. This is vendored audio codec encoder configuration code used by 9front audio commands.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/vorbisenc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/vorbisfile.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/vorbisfile.c

Libvorbisfile convenience layer for opening, probing, seeking, decoding, and reading Ogg/Vorbis streams through stdio or caller-supplied callbacks. It supports seekable files, non-seekable streams, chained logical bitstreams, raw/PCM/time seeking, halfrate decode, integer/float PCM reads, and crosslap seeking.

Important contents:
- Defines page input constants `CHUNKSIZE` and `READSIZE`.
- `_get_data()` reads from callback datasource into `ogg_sync_state`.
- `_seek_helper()` seeks callback datasource and resets sync state while tracking absolute stream offset.
- `_get_next_page()`, `_get_prev_page()`, and `_get_prev_page_serial()` implement forward and backward Ogg page search, including serial-number-aware selection.
- `_fetch_headers()` scans BOS pages, identifies Vorbis headers, rejects duplicate serial numbers in initial header sets, and loads the three Vorbis headers.
- `_initial_pcmoffset()` decodes packet block sizes until a granule position is available to determine the first PCM offset for a link.
- `_bisect_forward_serialno()` recursively discovers chained logical streams in a seekable physical bitstream, allocates per-link metadata, and stores offsets, serials, comments, info, and PCM lengths.
- `_make_decode_ready()`, `_decode_clear()`, and `_fetch_and_process_packet()` manage the live decoder state as reading crosses pages, packets, holes, EOF, multiplexed pages, or logical stream boundaries.
- `_ov_open1()` performs partial open/probe and first-link header parsing; `_ov_open2()` completes seekable or streaming setup.
- Public open/probe APIs include `ov_open_callbacks()`, `ov_open()`, `ov_fopen()`, `ov_test_callbacks()`, `ov_test()`, and `ov_test_open()`.
- Public info APIs include `ov_clear()`, `ov_streams()`, `ov_seekable()`, `ov_bitrate()`, `ov_bitrate_instant()`, `ov_serialnumber()`, `ov_raw_total()`, `ov_pcm_total()`, `ov_time_total()`, `ov_raw_tell()`, `ov_pcm_tell()`, `ov_time_tell()`, `ov_info()`, and `ov_comment()`.
- Public seek APIs include `ov_raw_seek()`, `ov_pcm_seek_page()`, `ov_pcm_seek()`, `ov_time_seek()`, `ov_time_seek_page()`, and `_lap` variants.
- Public read APIs include `ov_read_filter()`, `ov_read()`, and `ov_read_float()`.
- Crosslap support is implemented by `_ov_splice()`, `_ov_initset()`, `_ov_initprime()`, `_ov_getlap()`, `ov_crosslap()`, `_ov_64_seek_lap()`, and `_ov_d_seek_lap()`.

Control-flow summary:
- Opening initializes sync and stream state, optionally seeds initial bytes, tests seekability, parses headers, and either completes streaming setup or recursively maps all chains for random access.
- Reading first ensures decoded PCM exists; if not, it fetches/processes packets, initializes decoder state on demand, handles boundaries, then packs float PCM into requested integer format or returns float channel buffers.
- Seeking maps raw, PCM, or time positions to Ogg page/packet positions. PCM seek uses page-granularity seek first, then discards/tracks packets/samples until exact sample alignment is reached.
- Lap seeking captures overlap from the current decode state, performs the requested seek, primes the new position, and splices the old lap into the new lap buffer using Vorbis windows.

Integration points:
- Depends on `vorbis/codec.h`, `vorbis/vorbisfile.h`, `os.h`, `misc.h`, libogg sync/page/stream APIs, and libvorbis synthesis APIs.
- Uses callback-based I/O, with stdio wrappers for `fread`, `fseek`, `fclose`, and `ftell`.
- Calls external `vorbis_window()` for crosslap windowing.

Risk and review signals:
- Backward page search and chained-stream bisection are sensitive to malformed, truncated, multiplexed, or changing streams.
- Seekability requires both seek and tell callbacks; missing tell after a seek-capable open yields `OV_EINVAL`.
- `ov_read_filter()` validates channel count 1..255 and word size, but relies on caller-provided output buffer length being meaningful.
- Integer PCM packing has separate host-endian, requested-endian, signed, unsigned, 8-bit, and 16-bit paths.
- Several malloc paths in crosslap/lap seeking assume allocation success; this is inherited libvorbisfile code style.
- Non-seekable streams expose only current-link information and cannot report totals or seek.

Filesystem relevance:
- Not a filesystem implementation. It performs file/stream I/O through callbacks and stdio, but its domain is Ogg/Vorbis media parsing and decoding.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/vorbisfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/window.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/window.c

Vorbis window coefficient table and window application implementation. The bulk of the file is static precomputed window data for legal Vorbis block sizes.

Important contents:
- Includes `os.h`, `misc.h`, and `window.h`.
- Defines static half-window coefficient arrays:
  - `vwin64[32]`
  - `vwin128[64]`
  - `vwin256[128]`
  - `vwin512[256]`
  - `vwin1024[512]`
  - `vwin2048[1024]`
  - `vwin4096[2048]`
  - `vwin8192[4096]`
- Defines `vwin[8]`, an index table mapping window number to the corresponding coefficient array.
- `_vorbis_window_get(int n)` returns `vwin[n]`.
- `_vorbis_apply_window(float *d, int *winno, long *blocksizes, int lW, int W, int nW)` zeros samples outside overlap regions and applies the appropriate left and right overlap windows.

Control-flow summary:
- `_vorbis_apply_window()` normalizes previous/next window flags when the current block is short.
- It selects left and right window tables using `winno[lW]` and `winno[nW]`.
- It computes block sizes and overlap bounds:
  - left overlap begins at `n/4 - ln/4`
  - left overlap ends at `leftbegin + ln/2`
  - right overlap begins at `n/2 + n/4 - rn/4`
  - right overlap ends at `rightbegin + rn/2`
- It zeros leading samples, multiplies left overlap by ascending left window coefficients, multiplies right overlap by descending right window coefficients, and zeros trailing samples.

Integration points:
- Used by libvorbis synthesis/analysis block processing for MDCT lapping.
- Declared in `window.h`.
- Related to `vorbisfile.c` crosslap logic, which uses public/internal Vorbis window access for splicing decoded PCM.

Risk and review signals:
- `_vorbis_window_get()` does no bounds checking; callers must pass valid window indexes 0..7.
- `_vorbis_apply_window()` assumes `blocksizes`, `winno`, and `d` describe a legal Vorbis block/window configuration.
- Static table edits would directly affect codec reconstruction accuracy.
- The coefficient tables are data-heavy but behaviorally simple.

Filesystem relevance:
- No filesystem logic. This is codec DSP support data and windowing code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/window.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/window.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/window.h

Small private header for libvorbis window helpers.

Important contents:
- Include guard `_V_WINDOW_`.
- Declares `extern const float *_vorbis_window_get(int n);`.
- Declares `extern void _vorbis_apply_window(float *d,int *winno,long *blocksizes,int lW,int W,int nW);`.

Integration points:
- Included by `window.c`.
- Used by other libvorbis internals needing access to precomputed window coefficients or direct window application.

Risk and review signals:
- No implementation in this file.
- Function contracts are implicit; callers must know legal window indexes, block sizes, and Vorbis lapping semantics from codec internals.

Filesystem relevance:
- No filesystem logic. This is a private audio codec header.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/window.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mixfs/mixfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mixfs/mixfs.c

Plan 9 user-space 9P audio mixer filesystem. It presents `audio` and `volume` files, mixes multiple client writes into a single physical audio output stream, exposes mixed playback for reads, and binds the service over `/dev/audio` and `/dev/volume`.

Important contents:
- Uses Plan 9 libraries: `<u.h>`, `<libc.h>`, `<tos.h>`, `<fcall.h>`, `<thread.h>`, `<9p.h>`, and `<pcm.h>`.
- Constants define mixer buffer sizes and output format assumptions: `NBUF`, `NDELAY`, `NQUANTA`, stereo `NCHAN`, and `ABUF`.
- `Stream` tracks per-open audio state: `used`, open `mode`, `flush`, `run`, read/write positions, `QLock`, and `Rendez`.
- Global ring buffers:
  - `mixbuf[NBUF][NCHAN]` accumulates mixed client writes.
  - `lbbuf[NBUF][NCHAN]` stores last buffered/clipped output samples for read clients.
  - `mixrp` is the shared mixer read/play cursor.
- Device state includes `devaudio`, `audiofd`, `volfd`, `devlock`, volume values, PCM format state, null-device mode, and output delay.
- `s16()` reads signed little-endian 16-bit PCM samples.
- `clip16()` clamps mixed integer samples to signed 16-bit output.
- `closeaudiodev()` closes the physical output fd under `devlock`.
- `updfmt()` reads the underlying volume control to discover `fmtout` or `speed`, updating `fmt`.
- `reopendevs()` validates and opens an audio device path, discovers `/dev/audio*` when no explicit path is usable, opens the associated volume control, handles `/dev/null`, and updates output format.
- 9P handlers:
  - `fsopen()` allocates a free `Stream` for opens of `audio`.
  - `fsflush()` marks active stream requests as flushed and wakes sleepers.
  - `fsclunk()` releases per-fid stream ownership.
  - `fsread()` serves volume status or reads mixed audio from `lbbuf`.
  - `fswrite()` handles volume/control commands or writes PCM samples into `mixbuf`.
  - `fsstat()` reports pending buffered bytes for an active audio stream.
  - `fsstart()` initializes streams and starts `audioproc`.
  - `fsend()` exits all threads.
- `audioproc()` is the mixer/output loop. It wakes waiting streams, determines available samples, opens/reopens the physical device, mixes/clips/scales samples into output buffers, advances `mixrp`, converts PCM format if needed, and writes to `audiofd`.
- `threadmain()` parses `-D`, `-s`, and `-m`, installs PCM format printing, opens/closes the target device once, builds the 9P tree, posts/mounts the service, binds it into `/dev`, and exits the thread after setup.

Control-flow summary:
- Clients open `/dev/audio`; each fid gets a `Stream`.
- Writers block when their stream gets too far ahead of `mixrp`; their signed 16-bit stereo samples are added into `mixbuf`.
- `audioproc()` periodically consumes `mixbuf` at `mixrp`, applies mixer volume, stores last output in `lbbuf`, clears consumed mix slots, advances `mixrp`, converts to hardware format if needed, and writes to the selected audio device.
- Readers follow `mixrp` through `lbbuf` to observe recent mixed output and block until new mixed samples are available.
- `/dev/volume` supports local `dev`, `mix`, and `delay` commands, passes other messages to the real volume fd when present, and synthesizes status including device, mix volume, default output format, and speed.

Integration points:
- Provides a 9P service through `Srv fs` and `threadpostmountsrv()`.
- Binds the mounted `audio` and `volume` files over `/dev/audio` and `/dev/volume`.
- Uses Plan 9 audio devices such as `/dev/audio*`, `#u/audio*`, `#A/audio*`, or `/dev/null`.
- Uses `pcm` helpers `Pcmdesc`, `mkpcmdesc`, `allocpcmconv`, `pcmratio`, `pcmconv`, `freepcmconv`, and `pcmdescfmt`.

Risk and review signals:
- Device path validation is intentionally narrow, but still allows specific kernel device namespaces and `/dev/null`.
- Audio writes assume incoming data is signed 16-bit stereo little-endian matching `pcmdescdef`.
- `fsclunk()` writes `s->used = 0` without taking the stream lock, while other paths use `qlock(s)`.
- `audioproc()` reads `audiofd` outside `devlock` in several places; `closeaudiodev()` protects close/reassignment, but concurrent visibility is simple Plan 9 style rather than fully serialized.
- `fswrite()` sets `r->ofcall.count` to the input byte count before sample alignment; partial frame bytes are effectively ignored by the mixer loop.
- Null-device timing uses cycle counter/nanosecond fallback to simulate playback progress.
- Volume scaling uses exponential mapping from 0..100 to 0..65536 for about 60 dB range.

Filesystem relevance:
- This is directly filesystem-relevant. It is a user-space synthetic 9P filesystem that virtualizes `/dev/audio` and `/dev/volume`, multiplexing multiple clients onto one audio output device.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mixfs/mixfs.c -->