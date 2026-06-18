# Group Research: Plan 9 IP utilities and image conversion tools

Scope checked against `Docs/research_subset_a.md`: `sources/os/plan9/plan9` is included. Files in this group are user-space Plan 9 commands, mostly network utilities and image format readers/writers; they are not filesystem implementations, but they exercise Plan 9 file, namespace, `/net`, `/dev/screen`, and image I/O APIs.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/tftpd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/tftpd.c

## Purpose
Implements a Plan 9 TFTP server. It serves RRQ/WRQ requests over UDP from a configured network mount point, defaults to service `69`, and defaults its root to `/lib/tftpd`.

## Main Behavior
The daemon parses `-d`, `-h`, `-r`, `-s`, and `-x`, becomes user `none`, builds a namespace, changes to the serving directory, announces `udp!*!service`, forks per connection, and handles one TFTP request per accepted data fd.

It supports RFC-style TFTP opcodes for read, write, data, ack, error, and option acknowledge. Reads use `sendfile`; writes use `recvfile`.

## Option Handling
Supports `timeout`, `blksize`, and `tsize` options. `options()` validates values, emits OACK packets, computes `tsize` from `dirstat`, and contains a network MTU workaround reducing large block sizes to `Bandtblksz`, except for a Cavium U-Boot block size.

## Path and Boot Handling
`-r` restricts paths by rejecting `#`, `../`, embedded `/../`, and absolute paths outside the serving root. `mapname()` expands one `%I`, `%C`, or `%E` using the remote IP and `/net/arp`. `sunkernel()` detects Sun-style hex IP boot requests and maps them through NDB `bootf`.

## Error and Retry Model
Read transfers wait for ACKs with alarms and retransmit up to `timeout` attempts. It tolerates Intel PXE EOF ACK quirks and block wraparound. Errors are sent with `nak()` and logged with `syslog`.

## Dependencies
Uses Plan 9 auth, Bio, IP, NDB, namespace, `/net`, and UDP conversation files. Filesystem relevance is serving and creating files inside a constrained namespace.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/tftpd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/traceroute.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/traceroute.c

## Purpose
Implements `traceroute` using Plan 9 network conversation files. It probes successive TTL values and reports hop address, low/average/high round-trip time in microseconds, and optional reverse DNS names.

## Main Behavior
Parses dial strings into netdir/protocol/remote components. Defaults to `/net`, protocol `tcp`, and remote service `32767` when no service is present. `csquery()` asks `/net/cs` to resolve the dial string, falling back to direct numeric dialing when no connection server is available.

## Probe Types
`call()` opens the protocol clone, opens the data file, sets TTL through the control file, and dispatches to protocol-specific probes:
- TCP/IL: writes a `connect` request and relies on connection errors.
- UDP: connects to an unlikely port and sends data until timeout or network error.
- ICMP: sends ICMPv4 echo requests and validates echo replies with a magic sequence and payload.

## Output
For each TTL, runs multiple tries, aggregates timing, prints hop info, and can print histograms with `-h`. `-n` suppresses reverse DNS. `-a` sets tries, `-t` starting TTL, and `-x` net mount point.

## Dependencies
Uses `/net`, `/net/cs`, DNS through `dnsquery`, Plan 9 alarms/notes, and `icmp.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/traceroute.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/udpecho.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/udpecho.c

## Purpose
Simple UDP echo service.

## Behavior
Accepts `-x netmtpt`, announces `udp!*!echo`, enables `headers` mode on the control file, opens the announced conversation’s `data` file, then loops reading packets and writing the same bytes back.

## Dependencies
Uses Plan 9 `/net` UDP announce/open/read/write flow and `setnetmtpt`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/udpecho.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/wol.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/wol.c

## Purpose
Sends Wake-on-LAN magic packets.

## Behavior
Builds a packet containing six `0xff` bytes, sixteen copies of the parsed Ethernet address, and an optional six-byte password. Defaults to dialing `udp!255.255.255.255!0`, or uses `-a dialstr`. `-c` supplies the password and `-v` prints packet details.

## Dependencies
Uses `parseether`, `dial`, Plan 9 IP formatting, and writes the packed structure directly to the UDP connection.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ip/wol.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/join.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/join.c

## Purpose
Plan 9 implementation of the Unix `join` command for joining two sorted files on selected fields.

## Main Behavior
Parses `-1`, `-2`, `-j`, `-a`, `-e`, `-t`, and `-o`. It opens two files or stdin, requires at least one randomly seekable input, and uses `Bseek` to revisit duplicate-key ranges.

## Data Model
Input lines are read through Bio into fixed `Rune` buffers, split into up to `NFLD` fields, and compared with `runestrcmp`. Default separators are space and tab; with `-t`, a single explicit separator is used.

## Output
Default output prints the join field followed by non-join fields from file 1 and file 2. `-o` controls explicit field output, including field `0` for the join key. Missing fields can use the `-e` replacement.

## Risks and Limits
Lines are bounded by `Bsize`; truncated lines set `discard` and cause a final fatal error. The algorithm assumes sorted inputs and seekability for duplicate group replay.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/join.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/bmp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/bmp.c

## Purpose
Command-line BMP viewer/converter front end.

## Behavior
Reads BMP images via `readbmp(fd, CRGB)`, converts to display or output format using `torgbv` or `totruecolor`, optionally displays via libdraw/event, and can emit Plan 9 raw image headers/data or compressed rawimage format.

## Options
Supports common image tool flags: `-c` compressed output, `-9` uncompressed Plan 9 output, `-d` no display, `-e` disable error diffusion, `-k` grey, `-v` RGBV/CMAP8, `-t` true color, and `-3` three-color output.

## Dependencies
Uses `imagefile.h`, `readbmp`, `writerawimage`, libdraw, and event keyboard handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/bmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/bmp.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/bmp.h

## Purpose
Shared BMP structures and constants.

## Contents
Defines BMP compression constants (`BMP_RGB`, `BMP_RLE8`, `BMP_RLE4`, `BMP_BITFIELDS`), `Rgb`, `Filehdr`, and `Infohdr`.

## Usage
Included by the BMP reader to represent little-endian BMP file and info headers after parsing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/bmp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/close.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/close.c

## Purpose
Utility generator for YCbCr-to-RGBV lookup data.

## Behavior
Computes the closest Plan 9 colormap index for YCbCr values by converting to RGB and minimizing squared RGB distance across all 256 Plan 9 colormap entries. It buckets the 24-bit Y/Cb/Cr cube into `32^3` cells and records which colormap indices occur in each cell.

## Notes
This is a table-generation/support program, not a normal image conversion command. It is CPU-heavy by design, iterating all 256^3 YCbCr triples.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/close.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/gif.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/gif.c

## Purpose
GIF viewer/converter front end with animation and transparency support.

## Behavior
Reads one or more GIF frames using `readgif`, converts each frame to CMAP8, grey, RGB24, or alpha-bearing output, displays animation using frame delays and loop count, and writes only the first frame for raw/Plan 9 output.

## GIF-Specific Handling
Creates masks for transparent-index GIF frames. When writing output for transparent GIFs, `addalpha()` expands CMAP/Grey/RGB data to include alpha, and `blackout()` zeros transparent pixels.

## Options
Uses the common `-39cdektv` image flags. Display mode supports frame looping and exits on `q`, delete, or EOF control character.

## Dependencies
Uses `readgif`, `torgbv`, `totruecolor`, `writerawimage`, libdraw, and event handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/gif.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/ico.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/ico.c

## Purpose
Interactive Microsoft ICO file viewer/extractor.

## Main Behavior
Parses ICO headers and icon directory entries, loads supported icon images, displays them in a Plan 9 window, and lets button-3 menu actions write the selected image or mask as Plan 9 image files.

## Format Handling
Supports ICO type 1 with 1, 2, 4, and 8 bit indexed BMP-like payloads. It reads little-endian fields, translates BMP color maps to Plan 9 colormap indices, decodes XOR image bits, decodes/inverts AND mask bits, and composes an image over a white background.

## UI
Displays each decoded icon with borders, updates status text on hover, and uses a sight cursor for selecting icons to save.

## Limits
Does not support true-color ICO entries or multiple planes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/ico.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/imagefile.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/imagefile.h

## Purpose
Shared interface for the Plan 9 image conversion suite.

## Key Types
Defines `Rawimage`, which carries rectangle, optional colormap, channel count, up to four channel buffers, channel descriptor, channel length, and format-specific GIF fields.

## Channel Descriptors
Defines internal descriptors such as `CRGB`, `CYCbCr`, `CY`, `CRGB1`, `CRGBV`, `CRGB24`, `CRGBA32`, `CYA16`, and `CRGBVA16`.

## API Surface
Declares readers for JPEG/PNG/GIF/PPM, conversion helpers `torgbv` and `totruecolor`, raw writer, GIF/PPM/PNG writers, and single/multi-channel conversion helpers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/imagefile.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/jpegdump.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/jpegdump.c

## Purpose
Standalone JPEG marker dumper/parser by Tom Szymanski.

## Behavior
Reads a JPEG file with stdio, walks marker segments, and prints SOI, EOI, APP, COM, DQT, DHT, SOF, SOS, restart, and entropy sequence information. `-t` prints quantization and Huffman table contents.

## Implementation
Uses byte readers `get1`/`get2`, segment-specific parsers, and scans entropy-coded data by counting bytes and stuffed `0xff00` markers until the next marker.

## Dependencies
Uses ISO C headers rather than Plan 9 libc interfaces. It is diagnostic tooling, not part of the runtime decoder.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/jpegdump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/jpg.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/jpg.c

## Purpose
JPEG viewer/converter front end.

## Behavior
Reads JPEGs through `Breadjpg`, optionally repeatedly for movie-like streams, converts decoded `Rawimage` data to display/output format, and can display, dump compressed rawimage, or write uncompressed Plan 9 image data.

## Options
Supports common conversion flags plus JPEG-specific `-J` decode-only, `-r` output RGB rather than YCbCr, `-y` keep YCbCr for debugging, `-f` merge two fields per image, and `-F` movie mode with field merge.

## Field Merge
`vidmerge()` interleaves scanlines from paired decoded images, doubling the output height and freeing source channel buffers.

## Dependencies
Uses `Breadjpg`, `torgbv`, `totruecolor`, `writerawimage`, Bio, libdraw, and event handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/jpg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/multichan.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/multichan.c

## Purpose
Converts Plan 9 `Image` or `Memimage` values to a simple multi-channel format suitable for PPM writing.

## Behavior
If the image is already GREY1/2/4/8 or RGB24, returns it unchanged. Otherwise allocates an RGB24 image and draws the source into it.

## APIs
Exports `multichan(Image*)` and `memmultichan(Memimage*)`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/multichan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/onechan.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/onechan.c

## Purpose
Converts arbitrary Plan 9 images to one byte per pixel, usually CMAP8/RGBV, for GIF writing.

## Behavior
Leaves GREY1/2/4, CMAP8, and GREY8 unchanged. For easy RGB formats, unloads pixels directly; for other formats, first draws to RGB24. It repacks RGB16/RGB24/RGBA32/ARGB32 into a temporary `Rawimage`, passes it through `torgbv`, and loads the resulting CMAP8 bytes into a new image.

## APIs
Exports `onechan(Image*)` and `memonechan(Memimage*)`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/onechan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/png.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/png.c

## Purpose
PNG viewer/converter front end.

## Behavior
Reads PNG via `Breadpng`, converts indexed/truecolor/alpha outputs to the requested display or file channel, optionally displays over a black backing image for alpha composition, and writes Plan 9 raw or compressed rawimage output.

## Options
Supports `-D` decoder debug plus common image flags `-39cdekrtv`.

## Format Handling
Unlike other front ends, it preserves already packed PNG output descriptors such as `CY`, `CYA16`, `CRGB24`, and `CRGBA32` when writing truecolor output.

## Dependencies
Uses `Breadpng`, `torgbv`, `writerawimage`, Bio, libdraw, and event handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/png.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/ppm.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/ppm.c

## Purpose
PBM/PGM/PPM viewer/converter front end.

## Behavior
Reads Netpbm images through `readpixmap`, converts with `torgbv` or `totruecolor`, optionally displays, and emits Plan 9 uncompressed or compressed rawimage data.

## Options
Uses the common image flags `-39cdektv`.

## Dependencies
Uses `readpixmap`, conversion helpers, `writerawimage`, libdraw, Bio, and event handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/ppm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/readbmp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/readbmp.c

## Purpose
BMP decoder returning `Rawimage` data.

## Format Support
Handles Windows and OS/2 BMP headers, indexed 1/4/8-bit images, 16/24/32-bit truecolor, RLE4, RLE8, top-down and bottom-up images, and 16/32-bit bitfield masks.

## Implementation
Reads little-endian fields through `r16`/`r32`, reads palettes or bit masks, seeks to pixel data, decodes into an intermediate `Rgb` array, then splits into three `Rawimage` channels with descriptor `CRGB`.

## Error Handling
Some malformed inputs call `sysfatal`; allocation cleanup paths return nil. Only `CRGB` output is accepted.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/readbmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/readgif.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/readgif.c

## Purpose
GIF decoder returning an array of `Rawimage` frames.

## Format Support
Recognizes GIF87a/GIF89a, global and local color maps, Graphic Control Extension, comments/application/plain-text extension skipping, Netscape loop-count extension, image descriptors, LZW image data, and interlacing.

## Implementation
Uses a `Header` state with `setjmp`/`longjmp` error unwinding. `decode()` implements GIF LZW with clear/EOD codes, dynamic table entries, KwKwK handling, sub-block reading, and optional clipping of invalid palette indices.

## Output
Each frame is `CRGB1` indexed data with colormap, rectangle, GIF flags, delay, transparent index, and loop count.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/readgif.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/readjpg.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/readjpg.c

## Purpose
JPEG decoder returning `Rawimage` data in either YCbCr or RGB channel form.

## Format Support
Handles SOI/EOI, APP/COM, DQT, DHT, SOF0 baseline Huffman, SOF2 progressive Huffman, SOS, DRI restart intervals, one- and three-component images, quantization, Huffman entropy decoding, IDCT, chroma subsampling, and color conversion.

## Implementation
`Header` stores bitstream state, frame components, quantization tables, Huffman tables, MCU block buffers, progressive coefficient storage, and output image state. Baseline scans decode MCU blocks directly, dequantize, IDCT, and map into channels. Progressive scans accumulate DC/AC coefficients across scans, then run IDCT at EOI.

## Color Handling
Can preserve YCbCr or convert to RGB using fixed-point coefficients. `colormap1`, `colormapall1`, and `colormap` handle grey, simple 1x1 sampling, and general subsampling.

## Error Handling
Uses `setjmp`/`longjmp` cleanup, marker recovery for entropy peek-ahead, restart validation, and explicit errors for unsupported DNL/arithmetic/hierarchical modes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/readjpg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/readpng.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/readpng.c

## Purpose
PNG decoder returning one `Rawimage`.

## Format Support
Validates PNG signature and CRCs, parses IHDR, PLTE, IDAT, IEND, skips ancillary chunks, supports deflate/zlib compression, PNG filters None/Sub/Up/Avg/Paeth, non-interlaced and Adam7 interlaced images, and color types 0, 2, 3, 4, and 6.

## Implementation
`zread()` feeds IDAT bytes to `inflatezlib`; `zwrite()` rebuilds scanlines, applies filters, expands bit depths to 8-bit values, maps palettes, and writes CY/CRGB24/CYA16/CRGBA32 packed channel data.

## Limits
Only compression method 0 and filter method 0 are accepted. Unsupported mandatory chunks or invalid CRCs are fatal.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/readpng.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/readppm.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/readppm.c

## Purpose
Netpbm PBM/PGM/PPM decoder.

## Format Support
Reads P1/P4 bitmap, P2/P5 greymap, and P3/P6 pixmap formats. Handles comments beginning with `#`, decimal integer parsing, ASCII and raw samples, bitmap bit packing, max-value scaling, and PBM inversion.

## Output
Returns a one-element `Rawimage` array. Greyscale formats produce `CY`; pixmap formats produce three-channel `CRGB`.

## Dependencies
Uses Bio and `imagefile.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/readppm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/readtga.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/readtga.c

## Purpose
TGA decoder for image viewer front ends.

## Format Support
Reads 18-byte TGA headers, optional color maps, uncompressed RGB, uncompressed greyscale, RLE RGB, and RLE greyscale. Supports 16/24/32-bit RGB input and ignores alpha channels.

## Implementation
Decodes BGR(A) input into separate R/G/B channel buffers or luma into one channel. Applies vertical flip for lower-left origin and horizontal reflection when x origin indicates right-origin storage.

## Limits
Color-mapped and more exotic compressed TGA types are rejected.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/readtga.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/readv210.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/readv210.c

## Purpose
Decoder for single uncompressed QuickTime v210 YUV images.

## Behavior
Infers pixel count, line count, and chunk size from file length using `/lib/video.specs`. Reads packed 10-bit v210 words into 10-bit Y/Cb/Cr samples, then converts 4:2:2 pairs to RGB byte channels.

## Color Conversion
Uses fixed-point coefficients, choosing one coefficient set for 625-line/PAL-like 601 and another for 525-line/HD-style data.

## Output
Returns a three-channel `Rawimage`, descriptor `CRGB`, with dimensions from video specs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/readv210.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/readyuv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/readyuv.c

## Purpose
Decoder for Abekas A66-style raw YUV image files.

## Behavior
Infers dimensions and 8/10-bit storage from `/lib/video.specs` and file size. Reads base 8-bit interleaved 4:2:2 samples and, for 10-bit files, reads separate low-bit packing to reconstruct 10-bit samples.

## Color Conversion
Converts Cb/Y/Cr/Y pairs to RGB using fixed-point 601/HD coefficients and clips to 8-bit output.

## Output
Returns one three-channel `Rawimage`, descriptor `CRGB`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/readyuv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/rgbrgbv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/rgbrgbv.c

## Purpose
Generator for RGBV lookup tables.

## Behavior
Computes `rgbmap[256]`, the RGB value of each Plan 9 colormap index, and `closestrgb[16*16*16]`, the closest colormap index for each 4-bit-per-channel RGB cube cell.

## Notes
The file comments that `closest()` is now installed as `rgb2cmap` in libdraw. Output is C source table text intended for inclusion in `rgbv.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/rgbrgbv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/rgbv.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/rgbv.h

## Purpose
Generated lookup table header for Plan 9 RGBV/CMAP8 conversion.

## Contents
Defines `rgbmap[256]`, mapping each Plan 9 colormap index to packed RGB, and `closestrgb[4096]`, mapping 4-bit RGB cube cells to closest colormap indices.

## Usage
Consumed by `torgbv.c` for fast truecolor-to-CMAP8 conversion and error diffusion.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/rgbv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/rgbycc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/rgbycc.c

## Purpose
Generator for YCbCr lookup tables.

## Behavior
Computes `ycbcrmap[256]`, mapping Plan 9 colormap entries into Y/Cb/Cr, and `closestycbcr[4096]`, mapping 4-bit YCbCr cube cells to closest colormap indices.

## Notes
Uses 601-style floating-point conversion constants and edge-case constraints for high luma/chroma values. Output is C source table text for a generated header.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/rgbycc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/tga.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/tga.c

## Purpose
TGA viewer/converter front end.

## Behavior
Reads TGA through `readtga`, converts to requested CMAP8/GREY8/RGB24 output, optionally displays through libdraw, and can write Plan 9 uncompressed or compressed rawimage output.

## Options
Uses common image flags `-39cdektv`.

## Dependencies
Uses `readtga`, `torgbv`, `totruecolor`, `writerawimage`, libdraw, and event handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/tga.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/togif.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/togif.c

## Purpose
Converts Plan 9 image files to GIF.

## Behavior
Reads one or more Plan 9 images as `Memimage`, converts to one-channel CMAP/Grey using `memonechan`, starts a GIF stream, writes frames, and ends the GIF. Supports stdin for a single image.

## Options
`-l` loop count, `-c` comment, `-d` frame delay in milliseconds, and `-t` transparent color index. Multiple input files default to infinite looping; single images default to no loop.

## Dependencies
Uses `memstartgif`, `memwritegif`, `memendgif`, and Plan 9 memdraw image readers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/togif.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/toico.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/toico.c

## Purpose
Converts Plan 9 images to a Microsoft ICO file.

## Behavior
Reads each input image, converts non-indexed images to 8-bit grey or CMAP8, computes used colors, minimizes output bit depth to 1/2/4/8 bits, and writes ICO file header, icon directory entries, BMP-like icon headers, color maps, XOR masks, and AND masks.

## Notes
Rows are padded to 32-bit boundaries and stored bottom-up. Transparent mask generation treats pixel value `0xff` as transparent in the AND mask logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/toico.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/topng.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/topng.c

## Purpose
Converts a Plan 9 image to PNG.

## Behavior
Reads a Plan 9 image from stdin or one file, initializes memdraw, and writes PNG through `memwritepng`.

## Options
`-c` adds a text comment, `-g` adds gamma metadata, and `-t` is accepted but has no effect.

## Note
`ImageInfo II` is stack allocated and not visibly zeroed before option parsing, so callers rely on fields being set only when options are used; this is a potential initialization bug.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/topng.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/toppm.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/toppm.c

## Purpose
Converts a Plan 9 image to ASCII Netpbm PPM/PGM/PBM output.

## Behavior
Reads stdin or one file as `Memimage`, converts unsupported channel layouts to GREY/RGB through `memmultichan`, then writes with `memwriteppm`.

## Options
`-c` supplies a comment; comments containing newlines are rejected. Without a comment for file input, it emits a “Converted by Plan 9 from …” comment.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/toppm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/torgbv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/torgbv.c

## Purpose
Converts `Rawimage` inputs to Plan 9 RGBV/CMAP8 one-byte-per-pixel output.

## Supported Inputs
Handles indexed `CRGB1`, YCbCr, planar RGB, packed RGB24/RGBA32, grey, and grey+alpha. It validates channel counts and color map sizes.

## Conversion
Uses `rgbv.h` and YCbCr lookup tables for nearest-colormap selection. Optional modified Floyd-Steinberg error diffusion spreads per-channel error across rows using 3/16, 3/16, and 7/16-style terms.

## Output
Returns a new `Rawimage` with descriptor `CRGBV` and one channel of CMAP8-compatible bytes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/torgbv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/totruecolor.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/totruecolor.c

## Purpose
Converts `Rawimage` data to packed truecolor or greyscale output.

## Supported Outputs
Only `CY` and `CRGB24` are accepted.

## Conversion
Handles existing greyscale, indexed-color maps, planar RGB, packed RGB24/RGBA32, YCbCr, and grey-alpha style input. RGB output is in Plan 9 loadimage order; greyscale uses weighted luma conversion where needed. YCbCr-to-RGB uses fixed-point coefficients.

## Output
Returns a new one-channel `Rawimage` with packed bytes and requested descriptor.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/totruecolor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/v210.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/v210.c

## Purpose
Viewer/converter front end for v210 raw video frames.

## Behavior
Reads frames with `readV210(fd, CYCbCr)`, converts to display or output channel format using the standard image conversion helpers, optionally displays, and writes Plan 9 raw or compressed image output.

## Options
Uses common image flags `-39cdektv`.

## Dependencies
Depends on `readv210.c`, `/lib/video.specs` indirectly, libdraw, and `writerawimage`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/v210.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/writegif.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/writegif.c

## Purpose
GIF writer for `Image` and `Memimage`.

## API Surface
Exports `startgif`, `writegif`, `endgif`, and memimage variants.

## Format Handling
Writes GIF89a header, logical screen descriptor, global color table for GREY1/2/4/8 or CMAP8, optional Netscape loop extension, optional comment extension, optional Graphic Control Extension with delay/transparency, image descriptor, LZW image data, and trailer.

## Compression
Implements GIF LZW encoding with clear code, EOD code, dynamic dictionary, 12-bit limit, hash lookup, and sub-block output capped at 255 bytes.

## Limits
Only grey and CMAP8-style channels are accepted; callers convert richer images first.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/writegif.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/writepng.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/writepng.c

## Purpose
PNG writer for `Memimage`.

## Behavior
Converts input to BGR24 or ABGR32 memory layout so bytes can be written as PNG RGB/RGBA order, writes signature, IHDR, tIME, optional gAMA, optional tEXt comment, deflated IDAT chunks, and IEND.

## Compression
Uses `deflatezlib` with filter type 0 for every scanline. `zread()` injects filter bytes and streams pixels. For alpha, it converts Plan 9 premultiplied alpha back to non-premultiplied RGB before encoding.

## Dependencies
Uses `flate`, CRC helpers, Bio, and memdraw.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/writepng.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/writeppm.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/writeppm.c

## Purpose
ASCII Netpbm writer for `Image` and `Memimage`.

## API Surface
Exports `writeppm` and `memwriteppm`.

## Format Handling
Writes P1 for GREY1, P2 for GREY2/GREY4/GREY8, and P3 for RGB24. Optional comments are emitted after the magic. Pixel data is unloaded from draw/memdraw images and printed with line wrapping around 70 columns.

## Limits
Does not write raw P4/P5/P6; unsupported channel types return errors.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/writeppm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/writerawimage.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/writerawimage.c

## Purpose
Writes `Rawimage` data in Plan 9 compressed image format.

## Behavior
Maps internal `Rawimage` descriptors to Plan 9 channel descriptors, writes a `compressed` header with channel string and rectangle, and compresses scanline bands using the Plan 9 image compression scheme.

## Compression
Uses hash chains over previous byte sequences, dump blocks for literals, run blocks for repeated matches, and block-size limits from draw’s compression helpers. It emits per-band headers containing ending y coordinate and compressed byte count.

## Supported Inputs
Supports `CY`, `CYA16`, `CRGBV`, `CRGBVA16`, `CRGB24`, and `CRGBA32`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/jpg/writerawimage.c -->