# Group Research: group_58_9front_sources_os_plan9_9front_sys_src_cmd_audio_mp3enc_util_c_source_4b1760153ec1

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/util.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/util.c

LAME utility implementation for encoder housekeeping, psychoacoustic helpers, sample-rate/bitrate mapping, resampling, diagnostics, CPU feature probing, and simple statistics.

Key responsibilities:
- Frees `lame_internal_flags` owned buffers in `freegfc()`, including resampler/filter state, bitstream buffer, VBR seek table, and ATH data.
- Implements several ATH formulas and dispatches through `ATHformula()` based on `gfp->ATHtype`.
- Converts frequencies to Bark scale and critical-band width.
- Computes frame bit budgets in `getframebits()` and maps legal bitrate/sample-rate values through `FindNearestBitrate()`, `BitrateIndex()`, `SmpFrqIndex()`, and `map2MP3Frequency()`.
- Reorders short-block spectral coefficients in `freorder()`.
- Provides FIR Blackman-window resampling in `fill_buffer()` and `fill_buffer_resample()` when `KLEMM_44` is not enabled.
- Routes debug/message/error output through caller callbacks or `stderr`.
- Provides optional NASM-backed CPU feature probes and updates bitrate/stereo-mode histograms.
- Implements in-place quickselect-like `select_kth_int()` and platform-specific floating-point exception setup.

Dependencies:
- Uses LAME internal structures from `util.h`, MPEG tables such as `bitrate_table`, and math/libc routines.
- Resampling depends on persistent buffers in `lame_internal_flags`.

Research notes:
- `select_kth_int()` intentionally reorders its input array.
- Resampling lazily allocates filter tables and historical input buffers; `freegfc()` owns cleanup.
- CPU feature probes return false unless built with NASM support.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/util.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/util.h

Central LAME internal utility header defining common constants, bitstream state, psychoacoustic state, VBR seek tracking, resampler state, and the large private encoder state structure.

Key contents:
- Defines fallback math constants, boolean constants, buffer sizing, min/max macros, and bitstream constants.
- Defines `Bit_stream_struc`, `nsPsy_t`, `VBR_seek_info_t`, `ATH_t`, `coding_t`, and `resample_t`.
- Defines `lame_internal_flags`, the main internal encoder context used across bitstream, quantization, psychoacoustic, MDCT, reservoir, ID3, VBR, ATH, CPU feature, and analyzer code.
- Declares utility functions implemented in `util.c`: cleanup, bitrate/sample-rate mapping, ATH/frequency helpers, frame-bit calculation, sample buffer filling, CPU probes, stats, message printing, and quickselect.

Dependencies:
- Includes `machine.h`, `encoder.h`, `lame.h`, `lame-analysis.h`, `id3tag.h`, and `l3side.h`.

Research notes:
- The header exposes many implementation details globally rather than hiding them behind an opaque type.
- `lame_internal_flags` carries both persistent encoder configuration and per-frame scratch/history state.
- Several fields and comments show this is an older vendored LAME codebase with optional compile-time variants.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/util.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/vbrquantize.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/vbrquantize.c

LAME variable-bitrate quantization path for MPEG Layer III frames.

Key responsibilities:
- Computes scalefactor-band quantization noise with optional IEEE754 conversion shortcuts.
- Searches scalefactor values that keep quantization error below psychoacoustic masking thresholds.
- Computes MPEG-1 and LSF long/short block scalefactors, including `scalefac_scale`, `preflag`, and short-block subblock gain.
- Builds scaled `xr34` arrays for long and short blocks using selected scalefactors.
- Quantizes granules, counts Huffman bits, optionally applies best-Huffman division, and returns encoding status.
- Implements two VBR noise-shaping strategies: the older iterative path and `VBR_noise_shaping2()` with fallback to CBR-like binary step-size search.
- Top-level `VBR_quantize()` calculates masking thresholds, silence detection, min/max bit budgets, reservoir constraints, quality adjustment, final bitrate index selection, scalefactor storage optimization, and sign restoration.

Dependencies:
- Uses `util.h`, `l3side.h`, `quantize.h`, `reservoir.h`, `quantize_pvt.h`, and analyzer structures.
- Relies on tables/macros such as `pow43`, `adj43`, `pretab`, `POW20`, `IPOW20`, `IXMAX_VAL`, `LARGE_BITS`, and MPEG scalefactor-band constants.

Research notes:
- This file is algorithmically dense and stateful; most operations mutate `gfc->l3_side` granule/channel metadata.
- The top-level VBR loop lowers quality and bit limits until total frame bits fit the reservoir-permitted frame budget.
- Several branches preserve historical LAME tuning experiments and compile-time optimization paths.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/vbrquantize.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/version.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/version.c

LAME version-string and numerical-version implementation.

Key responsibilities:
- Stringifies version macros from `version.h`.
- Builds full and short LAME version strings, including alpha/beta/date and compile-time feature markers where applicable.
- Provides GPSYCHO and mp3x version strings.
- Returns the LAME project URL.
- Fills `lame_version_t` with LAME and psychoacoustic model version numbers plus compile-time feature text.

Dependencies:
- Includes public `lame.h` and local `version.h`.

Research notes:
- Full alpha/beta version strings may include compile date/time, while short versions avoid date/time for output validation stability.
- Compile-time feature suffixes come from `MMX_choose_table`, `KLEMM`, and `RH`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/version.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/version.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/version.h

LAME version macro header and version API declarations.

Key contents:
- Defines LAME URL and version components: LAME 3.88 beta 1, PSY 0.85, and mp3x 0.82.
- Declares full/short LAME version, psychoacoustic version, mp3x version, URL, and numerical version functions.

Dependencies:
- Requires `lame_version_t` from `lame.h`.

Research notes:
- This is static version metadata used by `version.c` and callers embedding/reporting the encoder version.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/version.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/vorbis_interface.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/vorbis_interface.c

Optional LAME bridge to libvorbis for Ogg Vorbis decoding and encoding, compiled only under `HAVE_VORBIS`.

Key responsibilities:
- Initializes Ogg/Vorbis decode state from an input file, validates the first Vorbis header, reads comment/codebook headers, and exposes stream metadata through `mp3data_struct`.
- Decodes Vorbis packets to signed 16-bit PCM arrays in chunks.
- Initializes Vorbis encoding mode based on LAME compression ratio and channel/sample-rate settings.
- Emits Vorbis headers, encodes LAME frame-sized PCM buffers, flushes pages into caller-provided output buffers, and finishes/cleans the stream.
- Adds a basic Vorbis comment identifying the LAME libvorbis interface.

Dependencies:
- Uses libogg/libvorbis headers and older mode presets from `modes/modes.h`.
- Uses LAME diagnostics through `ERRORF`/`MSGF`.

Research notes:
- Decode and encode state is stored in file-scope globals, so this interface is not reentrant.
- Output buffer overflow returns negative error codes.
- Some ID3-to-Vorbis comment mapping code is disabled by a compile-time guard.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/vorbis_interface.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/oggdec/oggdec.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/oggdec/oggdec.c

Plan 9-adapted Ogg Vorbis decoder command that writes raw audio through `audio/pcmconv`.

Key responsibilities:
- Reads Ogg pages from stdin, validates Vorbis headers, prints comments/stream metadata, and decodes chained streams.
- Converts libvorbis planar float PCM into interleaved float samples.
- Starts or restarts `/bin/audio/pcmconv` whenever sample rate or channel count changes.
- Supports `-s SECONDS` seeking using Ogg granule time and coarse `fseek` adjustment.
- Handles chained bitstreams by resetting stream/decoder state on a new BOS page.

Dependencies:
- Uses libogg/libvorbis, POSIX stdio/fork/pipe APIs, and Plan 9 compatibility headers.
- Depends on `/bin/audio/pcmconv` for conversion to default Plan 9 audio output format.

Research notes:
- The converter subprocess receives float PCM with format string like `f32r44100c2`.
- Seek behavior is heuristic and only applies to seekable stdin.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/oggdec/oggdec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/oggenc/oggenc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/oggenc/oggenc.c

Simple libvorbis encoder example command.

Key responsibilities:
- Reads hardcoded stereo 16-bit 44.1 kHz raw PCM from stdin.
- Initializes Vorbis VBR encoding at quality `0.5`.
- Emits Vorbis identification/comment/codebook headers with page flushing.
- Converts little-endian interleaved signed PCM into float analysis buffers.
- Runs Vorbis analysis/bitrate packet flushing and writes Ogg pages to stdout.
- Cleans all Ogg/Vorbis state on exit.

Dependencies:
- Uses `vorbis/vorbisenc.h`, libogg/libvorbis APIs, stdio, and time-based stream serial selection.

Research notes:
- Format is fixed; there are no command-line options for rate, channels, or quality.
- It is close to the upstream Xiph encoder example with minimal Plan 9 integration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/oggenc/oggenc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/pcmconv/pcmconv.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/pcmconv/pcmconv.c

Generic PCM format conversion command.

Key responsibilities:
- Parses input/output PCM descriptors with `-i fmt` and `-o fmt`; defaults both from `pcmdescdef`.
- Accepts optional byte length limit through `-l length`.
- Allocates a conversion context with `allocpcmconv()`.
- Computes output buffer sizing via `pcmratio()`.
- Streams stdin through `pcmconv()` and writes converted audio to stdout.

Dependencies:
- Uses Plan 9 `pcm.h` conversion API.

Research notes:
- The loop stops when `pcmconv()` returns zero, which may follow EOF or converter drain behavior.
- Length limiting is byte-based on input reads.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/pcmconv/pcmconv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/readtags/readtags.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/readtags/readtags.c

Audio metadata inspection command with optional embedded image extraction/display.

Key responsibilities:
- Uses libtags `tagsget()` with custom read/seek callbacks over stdin or file paths.
- Prints known tags such as artist, album, title, date, track, replaygain, genre, composer, comment, albumartist, and image metadata.
- Prints duration, sample rate, channel count, and bitrate when available.
- With `-i`, extracts the first embedded JPEG/PNG image, optionally runs its special tag reader, and pipes it into `jpg -9t` or `png -9t`.

Dependencies:
- Uses Plan 9 `tags.h`, subprocess creation through `rfork`, and image decoder commands.

Research notes:
- Unknown tags print their original key.
- `-i` exits with an error if no image is found.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/readtags/readtags.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/scream/screamdec.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/scream/screamdec.c

Decoder for Scream network audio packets.

Key responsibilities:
- Reads packets containing a 5-byte Scream header plus PCM payload from stdin.
- Decodes sample rate, bit depth, and channel count into a Plan 9 PCM format string.
- Starts `/bin/audio/pcmconv` only when the stream format differs from default `s16c2r44100`.
- Restarts the converter when packet format changes.
- Writes payload audio to either stdout or the converter pipe.

Dependencies:
- Uses `/bin/audio/pcmconv` for non-default PCM conversion.

Research notes:
- Uses a short alarm around reads, making it suited to live network streams.
- Packet header comparison drives converter restart.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/scream/screamdec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/scream/screamenc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/scream/screamenc.c

Encoder for wrapping raw PCM into Scream packet framing.

Key responsibilities:
- Uses fixed defaults: 44.1 kHz, stereo, 16-bit PCM, and 5 ms packet delay.
- Builds the 5-byte Scream header from rate multiplier, bits per sample, and channel count.
- Reads frame-sized chunks from stdin and writes header plus payload to stdout.

Research notes:
- There are no command-line options; globals are compile-time defaults.
- Intended to be paired with `/dev/audio` and the `screamsend` wrapper.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/scream/screamenc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/scream/screamrecv -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/scream/screamrecv

Rc wrapper for receiving Scream multicast audio.

Key behavior:
- Accepts optional IPv4 interface addresses.
- Defaults interfaces by reading IPv4 unicast entries from `/net/ipselftab`.
- Runs `aux/listen1` on UDP multicast `239.255.77.77!4010` with multicast add options.
- Pipes received data through `audio/screamdec` to `/dev/audio`.

Dependencies:
- Uses Plan 9 `rc`, `aux/listen1`, multicast network control, and `audio/screamdec`.

Research notes:
- Non-address arguments trigger usage.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/scream/screamrecv -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/scream/screamsend -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/scream/screamsend

Rc wrapper for sending local audio as Scream multicast.

Key behavior:
- Accepts optional IPv4 interface addresses.
- Defaults interfaces from `/net/ipselftab`.
- Dials UDP multicast `239.255.77.77!4010` with multicast add options.
- Sends `/dev/audio` through `audio/screamenc`.

Dependencies:
- Uses Plan 9 `rc`, `aux/dial`, multicast network control, and `audio/screamenc`.

Research notes:
- Non-address arguments trigger usage.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/scream/screamsend -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/sundec/sundec.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/sundec/sundec.c

Sun/NeXT `.snd`/AU audio header decoder that delegates payload conversion to `pcmconv`.

Key responsibilities:
- Reads big-endian AU magic, data offset, length, encoding, sample rate, and channel count.
- Maps supported AU encoding codes to Plan 9 PCM descriptor fragments.
- Skips annotation/header padding before audio data.
- Executes `/bin/audio/pcmconv -i fmt`, optionally with `-l len` when data length is known.

Dependencies:
- Uses `/bin/audio/pcmconv` for actual sample conversion.

Research notes:
- Supports u-law, A-law, signed integer PCM widths, and float encodings listed in `fmttab`.
- Unknown or malformed encodings terminate with `sysfatal`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/sundec/sundec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/wavdec/wavdec.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/wavdec/wavdec.c

WAV/RIFF decoder front-end that parses headers and delegates sample conversion to `pcmconv`.

Key responsibilities:
- Validates `RIFF`/`WAVE` headers.
- Iterates chunks until `fmt ` and `data` are found, skipping unknown chunks.
- Parses PCM format, channels, rate, frame size, and bit depth.
- Maps WAV format codes for PCM, IEEE float, A-law, and u-law into Plan 9 PCM descriptors.
- Supports `-s SECONDS` by seeking within data based on rate and frame size.
- Executes `/bin/audio/pcmconv -i fmt -l data_len`.

Dependencies:
- Uses `/bin/audio/pcmconv`.

Research notes:
- Seeking is done by byte offset on stdin and only works on seekable inputs.
- The expression used to align seek offset depends on `wav.framesz`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/wavdec/wavdec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/zuke/icy.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/zuke/icy.c

HTTP ICY/Shoutcast stream helper for zuke.

Key responsibilities:
- Opens an HTTP stream with `Icy-MetaData: 1`.
- Follows up to 10 `Location:` redirects.
- Reads ICY response headers, populating title/artist metadata for playlist generation or sending initial title updates.
- Parses `icy-metaint` and strips metadata blocks from the audio stream.
- Writes audio bytes to an output fd while sending `StreamTitle` updates over a channel.
- Runs the stream puller in a separate proc and closes the title channel on EOF/error.

Dependencies:
- Uses Plan 9 networking (`dial`, `netmkaddr`), `Biobuf`, threads/channels, and zuke `Meta`.

Research notes:
- Only plain HTTP URLs are handled; the code rewrites host/port into Plan 9 network addresses.
- Metadata parsing specifically looks for `StreamTitle='...';`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/zuke/icy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/zuke/icy.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/zuke/icy.h

Declaration header for zuke ICY stream support.

Key contents:
- Declares `icyget(Meta *m, int outfd, Channel **newtitle)`.

Role:
- Allows `mkplist.c` and `zuke.c` to share ICY metadata/stream setup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/zuke/icy.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/zuke/mkplist.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/zuke/mkplist.c

Playlist generator for zuke.

Key responsibilities:
- Recursively scans file/directory arguments, with bounded recursion and path normalization.
- Uses libtags to read metadata, duration, replaygain, embedded image info, and file format.
- Handles HTTP/HTTPS arguments as stream entries, using `icyget()` to retrieve ICY title/artist metadata.
- Optionally invokes `audio/moddec -r 0` to determine module-file duration.
- Uses worker procs to scan tags in parallel and a metadata thread to collect and sort tracks.
- Sorts tracks by path/artist/composer/date/album/track unless `-s` simple path sort is requested.
- Emits zuke playlist records via `printmeta()`.

Dependencies:
- Uses `tags.h`, Plan 9 thread channels, `plist.h`, and `icy.h`.

Research notes:
- Format names are mapped from libtags enum values to decoder names such as `mp3`, `ogg`, `flac`, `m4a`, `opus`, `wav`, or `mod`.
- Missing tags/durations are reported to stderr but do not necessarily exclude a track.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/zuke/mkplist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/zuke/plist.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/zuke/plist.c

Zuke playlist metadata serializer.

Key responsibilities:
- Writes `Meta` fields as one-letter tagged lines to a `Biobuf`.
- Emits path and file format first.
- Emits all artists, optional album/title/composer/date/track, duration, replaygain values, and embedded image metadata.
- Terminates each record with a blank line.

Dependencies:
- Uses field tags and `Meta` from `plist.h`.

Research notes:
- The serializer is intentionally simple and pairs with `zuke.c` playlist parsing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/zuke/plist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/zuke/plist.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/zuke/plist.h

Shared zuke playlist format and metadata header.

Key contents:
- Documents the intended playlist record layout.
- Defines one-letter field tags for album, artist, basename, composer, date, duration, format, image, title, track, path, and replaygain.
- Defines `Maxartist`.
- Defines `Meta`, including artist array, album/title/path/basename/image/file format, replaygain, duration, and embedded-image fields.
- Declares `printmeta()`.

Research notes:
- Comments mention a counted record format, while current `printmeta()` writes blank-line-delimited records.
- `Meta` fields are mostly borrowed pointers when parsed by `zuke.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/zuke/plist.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/zuke/zuke.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/zuke/zuke.c

Graphical Plan 9 audio playlist player for zuke playlists.

Key responsibilities:
- Parses playlists from stdin into in-memory `Meta` records backed by one raw buffer.
- Draws playlist rows, columns, scrollbar, seek bar, volume, replaygain/shuffle/repeat status, current track highlighting, and cover art.
- Manages `/dev/audio` output, `/dev/volume` changes, and audio open/close locking.
- Starts decoder subprocesses like `/bin/audio/mp3dec`, `/bin/audio/oggdec`, etc., or `/bin/play` for generic/URL playback.
- Handles ICY HTTP streams through `icyget()` and live title updates.
- Supports preloading the next player, replaygain track/album modes, repeat-one, shuffle, keyboard/mouse navigation, seeking, searching, and plumb messages.
- Loads embedded or sidecar cover art through `audio/readtags -i`, `jpg`, `png`, and `resample`.
- Emits current-track notifications to stdout when stdout is not `/dev/cons`.

Dependencies:
- Uses Plan 9 draw/mouse/keyboard/plumb/thread libraries, `plist.h`, `icy.h`, audio decoder commands, image decoders, `/dev/audio`, and `/dev/volume`.

Research notes:
- Playback is subprocess-based; zuke itself reads decoded PCM from pipes and writes to `/dev/audio`.
- Shuffle builds a deterministic-looking permutation using an LCG over a power-of-two mask.
- The UI redraw path caches a backing image and coalesces redraw requests through a channel.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/zuke/zuke.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/acmed.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/acmed.c

ACME v2 client for obtaining TLS certificates on Plan 9.

Key responsibilities:
- Discovers ACME directory endpoints from the provider URL, defaulting to Let's Encrypt production.
- Encodes base64url values and JSON strings for JWS requests.
- Signs RS256 JWS payloads through factotum using an RSA account key.
- Creates/uses an ACME account and submits new certificate orders from CSR subject names.
- Handles HTTP-01, DNS-01, or external command challenge fulfillment.
- Polls authorization and order status until valid, submits CSR, fetches certificate PEM, and writes it to stdout.
- Loads JWK public account key JSON, computes the ACME JWK thumbprint, and supports IDN conversion.

Dependencies:
- Uses Plan 9 `webfs` under `/mnt/web`, `factotum` `/mnt/factotum/rpc`, JSON library, libsec X.509/RSA helpers, and authsrv interfaces.

Research notes:
- Challenge command mode executes a user-supplied command with challenge type, domain, token, and authorization string.
- DNS challenge mode writes an ndb-style challenge file and refreshes `/net/dns`.
- Request signing depends on a matching factotum key spec.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/acmed.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/as.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/as.c

Run a command as another user on a CPU server using Plan 9 uid capabilities.

Key responsibilities:
- Parses `-d` namespace debug and `-n namespace`.
- Creates a private environment/name space.
- Generates a kernel uid-change capability through `/dev/caphash` and consumes it through `/dev/capuse`.
- Mounts factotum for the new user.
- Builds the target user's namespace and execs the requested command or interactive rc.

Dependencies:
- Uses auth namespace setup from `authcmdlib.h`/auth library and Plan 9 capability devices.

Research notes:
- Intended for hostowner use.
- Relative commands are retried under `/bin`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/as.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/asaudit.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/asaudit.c

Authentication setup audit tool.

Key responsibilities:
- Reads hostowner and reports mismatch with current user.
- Opens ndb and checks that nvram `authdom` maps to an auth server.
- Reads nvram safe and validates authid/authdom expectations.
- Starts `auth/keyfs -r`, reads the keyfs AES key, and compares it with nvram.
- Checks factotum for an enabled `dp9ik` key matching nvram authdom/authid.
- Exercises factotum dp9ik server authentication using nvram or keyfs key material.

Dependencies:
- Uses nvram, keyfs, factotum rpc, dp9ik/PAK helpers, ndb, and authsrv ticket structures.

Research notes:
- Reports `GOOD`/`BAD` diagnostic lines rather than enforcing one exit-code-only result.
- It can fall back to testing keyfs when factotum does not match nvram.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/asaudit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/asn12rsa.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/asn12rsa.c

ASN.1 RSA key converter to Plan 9 factotum key syntax.

Key responsibilities:
- Reads ASN.1 DER data from a file or stdin.
- Attempts to parse an RSA private key first, then an RSA public key.
- Prints a factotum `key proto=rsa ...` line with optional tag fields.
- Emits private components with `!` prefixes for secret attributes.

Dependencies:
- Uses libsec ASN.1/RSA parsing and multiprecision formatting.

Research notes:
- Entire input is slurped into memory before parsing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/asn12rsa.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/asn1dump.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/asn1dump.c

ASN.1/X.509 dump utility.

Key responsibilities:
- Reads ASN.1 DER input from a file or stdin.
- Installs formatting hooks for multiprecision integers and hex/base encodings.
- Calls `asn1dump()` and `X509dump()` on the full input buffer.

Dependencies:
- Uses libsec ASN.1/X.509 dump routines.

Research notes:
- This is a diagnostic utility; it does not validate command-specific object types.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/asn1dump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/authcmdlib.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/authcmdlib.h

Shared declarations for Plan 9 auth command support library.

Key contents:
- Sets library pragma for `./lib.$O.a`.
- Defines key database paths, auth log name, max challenge/path constants, account bio structures, filesystem descriptors, and Plan 9/Securenet selector constants.
- Declares helper functions for password/key management, key lookup, challenge checks, account bio read/write, logging, and file I/O.
- Declares `%K` formatting for DES keys.

Role:
- Shared contract for auth commands such as `authsrv`, `changeuser`, and bio conversion tools.

Research notes:
- The header exposes legacy DES/Securenet and newer AES/auth key helpers side by side.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/authcmdlib.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/authsrv.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/authsrv.c

Plan 9 authentication server protocol handler.

Key responsibilities:
- Reads `Ticketreq` messages and dispatches to Plan 9 ticket, challenge-response, password change, APOP/CRAM, CHAP, MSCHAP/MSCHAPv2, NTLM, VNC, and PAK handlers.
- Performs PAK key exchange and supports ticket-form mode that disables DES fallback.
- Looks up user/host/auth keys and secrets from auth databases, masking lookup failures with generated keys where needed.
- Issues client/server tickets and authenticators.
- Validates host `speaksfor` authorization via ndb.
- Implements password change protocol with old/new password validation and optional secret update.
- Implements Microsoft LM/NTLM/NTLMv2/MSCHAP hash and response checks.
- Maintains keyseed-backed deterministic fake DES keys for failed lookup masking.
- Logs success/failure through auth syslog.

Dependencies:
- Uses authsrv structures, libsec crypto, ndb, regexp/libc, and shared helpers from `authcmdlib.h`.

Research notes:
- Connection lifetime is capped by a 10-minute alarm.
- Some protocols exit after one successful exchange; others retry a bounded number of times.
- Security-sensitive comparisons use `tsmemcmp`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/authsrv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/box.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/box.c

Namespace/device sandbox wrapper for running commands in a skeletal filesystem view.

Key responsibilities:
- Parses bind options for read/replace/create paths, device exposure flags, debug, and shell mode.
- Starts `skelfs` and mounts skeleton file and directory servers at `/mnt/f` and `/mnt/d`.
- Resolves relative paths against the current directory.
- Constructs a new root under `/mnt/d/newroot.<pid>` by binding skeleton directories/files for required path components.
- Binds requested paths into the new root, replaces `/`, restricts devices through `/dev/drivers`, and execs the target command.

Dependencies:
- Uses Plan 9 namespace operations, `skelfs`, `/dev/drivers`, and auth/libc APIs.

Research notes:
- `-s` shell mode binds `/srv`, `/env`, `/rc`, and `/bin` and runs `/bin/rc`.
- Debug mode prints generated bind and device commands.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/box.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/challenge.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/challenge.c

Interactive factotum challenge-response tester.

Key responsibilities:
- Opens `/mnt/factotum/rpc`.
- Creates an auth challenge from the supplied parameter string.
- Prints the challenge, reads optional user and response from stdin, and submits the response.
- Prints authenticated client/server user ids from returned `AuthInfo`.

Dependencies:
- Uses Plan 9 auth challenge APIs and factotum rpc.

Research notes:
- The allocated `AuthRpc` is opened but not directly used after `auth_challenge()`, relying on auth library behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/challenge.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/changeuser.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/changeuser.c

Interactive user account/key installer for Plan 9 and Securenet authentication databases.

Key responsibilities:
- Selects Plan 9 (`-p`) and/or Securenet (`-n`) account updates; defaults to Plan 9.
- Validates username length.
- Prompts whether to assign new Plan 9 password and optional Inferno/POP secret.
- Preserves existing expiration time and writes key/secret updates.
- Queries and writes account bio records.
- For Securenet, generates a random DES key, writes it, prints the key and checksum for verification.
- Logs account installation through auth syslog.

Dependencies:
- Uses helpers from `authcmdlib.h`, including key database access, password prompting, account bio I/O, and DES key formatting.

Research notes:
- `install()` creates user directories when absent and writes expiration if present.
- The command intentionally calls `private()` before modifying auth state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/changeuser.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/convbio.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/convbio.c

Account bio format converter.

Key responsibilities:
- Reads legacy whitespace/angle-bracket account bio lines from stdin.
- Parses user, name, department, and up to `Nemail` email addresses.
- Writes normalized pipe-delimited records containing user, post id, name, department, and emails.
- Clears/reuses `Acctbio` storage for each input record.

Dependencies:
- Uses `Acctbio` and constants from `authcmdlib.h`.

Research notes:
- If no email is present, output defaults the first email field to the username.
- The parser returns one account per successful `ordbio()` call.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/convbio.c -->