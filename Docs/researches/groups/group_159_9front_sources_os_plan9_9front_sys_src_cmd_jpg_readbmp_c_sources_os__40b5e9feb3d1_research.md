# Group Research: group_159_9front_sources_os_plan9_9front_sys_src_cmd_jpg_readbmp_c_sources_os__40b5e9feb3d1

Scope checked against `Docs/research_subset_a.md`: `sources/os/plan9/9front` is included in subset A. I read every listed source file completely and summarized each file below for source-tree-aligned splitting.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/readbmp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/readbmp.c

BMP decoder for the Plan 9 image tools. It reads MS BMP and limited OS/2 1.x BMP headers, handles little-endian header fields, optional color tables/bitfields, and returns `Rawimage**` through `Breadbmp`/`readbmp`.

It supports 1, 4, 8, 16, 24, and 32 bpp input, including RLE4/RLE8 and bottom-up or top-down orientation. Indexed formats expand through a CLUT; true-color formats are split into three `CRGB` channels.

Errors are a mix of `sysfatal`, `werrstr`, and `nil` returns. Image dimensions and allocation sizes are trusted after header parsing, so this is format-decoding utility code rather than hardened untrusted-input infrastructure.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/readbmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/readgif.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/readgif.c

GIF87a/GIF89a decoder returning an array of `Rawimage*`. `readgif` accepts `justone`, initializes a `Header` state object, and uses `setjmp`/`longjmp` cleanup paths for parse and allocation failures.

The parser reads global/local color maps, image descriptors, graphic-control extensions, comments/application extensions, NETSCAPE loop counts, LZW image data, and GIF interlacing. Decoded frames carry GIF metadata fields such as delay, transparency index, flags, and loop count.

The LZW decoder keeps reading through malformed overflow cases to preserve stream synchronization. `colorspace` is unused; decoded frames are indexed `CRGB1` with a copied color map.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/readgif.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/readjpg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/readjpg.c

JPEG decoder for baseline and progressive Huffman JPEG. Public entry points are `Breadjpg` and `readjpg`, returning one `Rawimage` in a null-terminated array, with output in `CRGB`, `CYCbCr`, or `CY` depending on input and requested color space.

It parses markers and segments including SOI/EOI, APPn, DQT, DHT, SOF, SOF2, SOS, DRI, and COM. It builds Huffman fast lookup tables, reads quantization tables, decodes baseline MCUs, supports restart intervals, and handles progressive DC/AC scans with refinement before final IDCT.

Color output paths cover grayscale, direct 1x1 sampling, and general resampling. Error handling preserves partial images when possible and uses `longjmp` for fatal decode errors.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/readjpg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/readpng.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/readpng.c

PNG reader backed by Plan 9 `flate` zlib inflation and CRC checking. It verifies the PNG signature, reads chunks through `getchunk`, requires IHDR, accepts PLTE while streaming, and decompresses IDAT data through callback-based inflate.

It supports PNG color types 0, 2, 3, 4, and 6 with bit depths allowed by the format checks, converts indexed pixels through the palette, handles alpha into `CYA16`/`CRGBA32`, and supports Adam7 interlacing. Scanline filters include None, Sub, Up, Average, and Paeth.

The decoder emits one-channel packed true-color style `Rawimage` buffers (`CY`, `CRGB24`, `CYA16`, `CRGBA32`). Many parse failures call `sysfatal`, so callers do not receive recoverable errors for malformed PNGs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/readpng.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/readppm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/readppm.c

Netpbm reader for PBM/PGM/PPM variants. `readpixmap` wraps a `Biobuf`, recognizes `P` magic, and delegates to `readppm`.

The `Pix` table covers P1/P4 bitmap, P2/P5 greymap, and P3/P6 pixmap forms. Text forms skip `#` comments and parse decimal fields; raw bitmap uses bit-level reads. Pixel samples are scaled to 0-255 and stored as `CY` or planar `CRGB`.

The file maintains static bit-buffer state for PBM raw reads and flushes it per row. On failures it frees allocated channels and reports a generic format/read/memory error through `errstr`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/readppm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/readtga.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/readtga.c

TGA decoder for uncompressed and RLE color-mapped, RGB, and grayscale images. It parses the 18-byte TGA header, optional ID field, color-map origin/length, and converts color maps from BGR/BGRA or 15/16-bit packed form.

Pixel readers cover color-map indices, luma, luma RLE, RGB(A), and RGB(A) RLE for 15/16/24/32 bpp. Output channel descriptors include `CY`, `CRGB1`, `CRGBV`, `CRGB`, and `CRGBA`.

After decoding it applies horizontal reflection and vertical flip based on descriptor origin bits. It ignores alpha for most tool-level display paths, matching the file comment that TGA alpha is largely ignored.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/readtga.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/readtif.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/readtif.c

TIFF reader implementing endian-aware IFD parsing, strip loading, decompression, and conversion to Plan 9 `Rawimage`. Public entry points are `Breadtif` and `readtif`, accepting only `CRGB24` as requested color space.

Supported image classes include bilevel/gray, RGB, and palette TIFF with depths 1, 4, 8, and 24. Supported compression includes none, CCITT Huffman/T4/T6 fax, LZW with horizontal predictor, and PackBits. It requires orientation 1, planar configuration 1, valid strip offsets/counts, and compatible samples/photometric fields.

The file contains full fax white/black/mode code tables, 1D/2D fax decoders, LZW table expansion, predictor reversal, PackBits expansion, and palette/gray/RGB decode paths. It uses `werrstr` for validation failures and `sysfatal` for some low-level read/allocation failures.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/readtif.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/readv210.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/readv210.c

Decoder for single-frame QuickTime `v210` 10-bit YUV video stills. It infers dimensions and per-line chunk size by comparing file size against `/lib/video.specs`.

`BreadV210` unpacks 32-bit little-endian groups into 10-bit Cb/Y/Cr/Y samples, stores an intermediate multiplexed frame, then converts YCbCr to planar `CRGB` bytes. It selects conversion constants for PAL-like 625-line versus 525/HD cases.

Only `CYCbCr` input mode is accepted by the API despite returning RGB channels. Missing video specs or unknown file sizes produce recoverable `werrstr`/`nil` failures.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/readv210.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/readyuv.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/readyuv.c

Reader for Abekas A66-style raw YUV images. Like `readv210.c`, it relies on `/lib/video.specs` and file length to infer pixels, lines, and whether the source stores 8-bit or 10-bit samples.

It reads the high 8 bits of every multiplexed YUV sample first, then optionally reads packed low 2-bit planes for 10-bit input. Samples are converted from YCbCr pairs to planar 8-bit RGB channels using fixed-point coefficients.

The public API is `Breadyuv`/`readyuv`; it accepts `CYCbCr` as the requested color space and returns a `Rawimage` marked `CRGB`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/readyuv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/rgbrgbv.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/rgbrgbv.c

Table generator for RGB to Plan 9 RGBV palette mapping. It computes nearest Plan 9 colormap entries using squared RGB distance against `cmap2rgb`.

`main` prints two C initializers: `rgbmap[256]`, mapping palette indices to RGB triples, and `closestrgb[16*16*16]`, mapping 4-bit-per-channel RGB cubes to nearest palette indices.

This is a build/helper utility rather than runtime image conversion code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/rgbrgbv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/rgbycc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/rgbycc.c

Table generator for YCbCr/RGBV conversion support. It computes Plan 9 colormap entries nearest to YCbCr-derived RGB colors and prints generated C tables.

The output includes `ycbcrmap[256]`, converting palette entries to YCbCr-like packed values, and `closestycbcr[16*16*16]`, a coarse nearest-palette lookup table. The code uses floating-point YCbCr formulas and edge guards for high-end Y/Cb/Cr values.

This file feeds generated lookup headers used by runtime remapping code such as `torgbv.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/rgbycc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/tga.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/tga.c

Interactive TGA viewer/converter command. It reads TGA via `readtga`, optionally displays it in a draw window, and can emit Plan 9 raw image formats.

Command flags select display suppression, Floyd-Steinberg diffusion, grayscale/RGBV/true-color output, compressed raw output through `writerawimage`, or uncompressed Plan 9 image output. The display path centers the image and waits for keyboard input before continuing.

Conversion routes through `torgbv` for `CMAP8` output or `totruecolor` for gray/RGB/RGBA output.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/tga.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/tif.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/tif.c

Interactive TIFF viewer/converter command. It opens files or stdin, decodes through `Breadtif(&b, CRGB24)`, displays through libdraw unless suppressed, and can write Plan 9 raw-image output.

Flags mirror the other image tools: compressed output, uncompressed `-9`, grayscale, true-color, RGBV, and error-diffusion control. Output conversion either keeps decoded `CY`/`CRGB24` when true-color output is selected or remaps with `torgbv`.

Memory cleanup frees converted images only when distinct from decoded images, then frees decoded channels and the array.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/tif.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/togif.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/togif.c

Command-line converter from Plan 9 image input to GIF. It reads `Memimage` data from stdin or files, converts to one-channel palette form with `memonechan`, and writes through `memstartgif`, `memwritegif`, and `memendgif`.

Options support loop count, comment, per-frame delay in milliseconds, transparency index, and `-E` streaming multiple images from stdin until EOF. For multiple file arguments, inline `-d` arguments can change subsequent frame delay.

The command manages animation defaults: no loop for a single image, infinite loop for multiple files unless explicitly overridden.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/togif.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/toico.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/toico.c

ICO writer command that reads one or more Plan 9 images and emits a Windows `.ico` file. It builds the ICO file header, per-icon descriptors, BMP-like icon headers, color maps, XOR pixel masks, and AND transparency masks.

Images are converted to 8-bit grayscale or colormap images when needed. `mkxorand` counts used colors, creates a Plan 9-to-ICO palette map, chooses 1/2/4/8 bpp based on color count, aligns rows to 32-bit boundaries, and writes bottom-up masks.

Transparency is inferred from palette value `0xff` in the AND mask path.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/toico.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/tojpg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/tojpg.c

Command-line JPEG converter. It reads a Plan 9 image from stdin or one file, converts to multi-channel `Memimage` form with `memmultichan`, and writes JPEG using `memwritejpg`.

Options include `-c` comment, `-k` grayscale output, and `-s` alternate/scaled quantization path passed to the JPEG writer. Output is written to stdout through a `Biobuf`.

The command itself is thin; format-specific encoding lives in `writejpg.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/tojpg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/topng.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/topng.c

Command-line PNG converter. It reads a Plan 9 image as `Memimage`, accepts optional comment and gamma metadata, then writes PNG through `memwritepng`.

The `ImageInfo` flags indicate which optional PNG chunks to emit. The `-t` option is accepted but ignored in this file.

All image encoding details are delegated to `writepng.c`; this file mainly handles argument parsing, input opening, and output setup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/topng.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/toppm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/toppm.c

Command-line Netpbm converter. It reads a Plan 9 image, converts to a multi-channel memory image where needed, and writes PBM/PGM/PPM through `memwriteppm`.

Options support a single-line comment and raw output mode (`P4/P5/P6`) versus text output (`P1/P2/P3`). For file input it synthesizes a default conversion comment if none is provided.

It rejects comments containing newlines to preserve valid Netpbm comment formatting.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/toppm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/torgbv.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/torgbv.c

Rawimage remapper to Plan 9 RGBV (`CRGBV`) indexed color. It handles indexed RGB maps, RGB/Y/CbCr planar images, packed RGB/RGBA images, and grayscale/gray-alpha inputs.

The converter uses generated `rgbv.h` and `ycbcr.h` lookup tables, optional modified Floyd-Steinberg error diffusion, and clamp/error arrays per scanline. Output is a one-channel `Rawimage` sharing the source rectangle and containing palette indices.

Failures are reported through `_remaperror`, setting `errstr` and returning `nil`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/torgbv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/totif.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/totif.c

Command-line TIFF converter. It reads a Plan 9 image, optionally converts its channel descriptor, and writes TIFF via `memwritetif`.

Options select output channel (`GREY1`, `GREY4`, `GREY8`, `CMAP8`, `BGR24`) and compression (`none`, Huffman, T4, T4 2D, T6, LZW, LZW predictor, PackBits). Fax compression forces bilevel output.

`memtochan` performs channel conversion with `memimagedraw`; unsupported or unsuitable input channels are converted before writing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/totif.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/totruecolor.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/totruecolor.c

Rawimage converter from the project’s decoded formats to true-color or grayscale packed formats. Target descriptors are `CY`, `CRGB24`, and `CRGBA32`.

It handles grayscale, indexed `CRGB1`/`CRGBV`, planar `CRGB`/`CRGBA`, and planar `CYCbCr`. Indexed colors are expanded from color maps; YCbCr is converted with fixed-point coefficients; RGBA output premultiplies alpha.

This is a central bridge between format decoders that produce planar or indexed `Rawimage` data and display/writer code expecting packed Plan 9 channels.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/totruecolor.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/v210.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/v210.c

Interactive viewer/converter command for raw `v210` video-frame files. It parallels `yuv.c` but calls `readV210(fd, CYCbCr)`.

Flags select display suppression, compressed raw output, Plan 9 uncompressed output, grayscale, RGBV, true-color, and diffusion behavior. Display code centers the converted image in a libdraw window and exits on `q`, delete, or EOF.

The conversion path uses `torgbv` for palette output and `totruecolor` for grayscale/RGB output.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/v210.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/writegif.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/writegif.c

GIF89a writer for libdraw `Image` and `Memimage` inputs. Public functions include `startgif`, `memstartgif`, `writegif`, `memwritegif`, `endgif`, and `memendgif`.

It writes logical screen descriptors, global color tables for Plan 9 palette/gray depths, optional NETSCAPE loop extensions, comments, graphic-control blocks for delay/transparency, image descriptors, and LZW-compressed image data.

Supported channels are `GREY1`, `GREY2`, `GREY4`, `GREY8`, and `CMAP8`. The LZW encoder manages GIF sub-block output and dictionary resets at 12-bit code size.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/writegif.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/writejpg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/writejpg.c

Baseline JPEG writer for Plan 9 images. It emits JFIF, optional comments, quantization tables, Huffman tables, SOF0, SOS, entropy-coded data, and EOI.

Input support covers gray depths and `RGB24`; grayscale channels force single-component JPEG. Encoding converts pixels to YCbCr, applies an integer FDCT, quantizes with built-in luminance/chrominance tables, builds canonical Huffman encode tables, and writes entropy-coded DC/AC coefficients with byte stuffing.

Public entry points are `writejpg` and `memwritejpg`. The `sflag` path changes quantization/zigzag handling, while `kflag` requests grayscale output.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/writejpg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/writepng.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/writepng.c

PNG writer for `Memimage`. It writes PNG signature, IHDR, tIME, optional gAMA, optional tEXt comment, compressed IDAT chunks, and IEND.

`memRGBA` converts source images to BGR24 or ABGR32 arranged so the byte stream becomes PNG RGB/RGBA order. Alpha channels are converted from Plan 9 premultiplied representation back to non-premultiplied PNG samples during zlib input streaming.

The writer uses filter type None only, no interlace, 8 bits per channel, and zlib compression level 6.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/writepng.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/writeppm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/writeppm.c

Netpbm writer for Plan 9 `Image`/`Memimage`. It supports PBM, PGM, and PPM output in raw or text mode through `writeppm` and `memwriteppm`.

Channel support includes `GREY1`, `GREY2`, `GREY4`, `GREY8`, and `RGB24`. It emits the correct magic (`P1`-`P6`), optional comment, dimensions, max sample where required, and scaled or raw pixel data.

Packed gray pixels are extracted with bit masks; RGB24 output swaps Plan 9 byte order into PPM RGB order.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/writeppm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/writerawimage.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/writerawimage.c

Writer for Plan 9 compressed image format from `Rawimage`. It emits a `compressed` header with channel descriptor and rectangle, then compresses scanline blocks.

Supported `Rawimage` descriptors include `CY`, `CYA16`, `CRGBV`, `CRGBVA16`, `CRGB24`, and `CRGBA32`, mapped to draw channel descriptors such as `GREY8`, `CMAP8`, `RGB24`, and `RGBA32`.

The compressor uses Plan 9 image compression constants (`NMATCH`, `NRUN`, `NDUMP`, `NMEM`) and a hash-chain sliding window, flushing blocks when the encoded buffer fills.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/writerawimage.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/writetif.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/writetif.c

TIFF writer for libdraw `Image` and `Memimage`. It writes big-endian TIFF, builds IFD fields, strip offsets/counts, optional descriptions, resolution rationals, palettes, and compressed or uncompressed image data.

Supported output channels include gray, colormap, and BGR24. Compression support includes none, CCITT Huffman/T4/T6 fax, LZW with optional horizontal predictor, and PackBits. Fax paths force photometric white-zero bilevel output.

The file contains fax run-code tables and 1D/2D encoders, LZW hash encoder, PackBits row encoder, strip planning, palette creation from `cmap2rgb`, and field serialization. Public entry points are `writetif` and `memwritetif`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/writetif.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/yuv.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/yuv.c

Interactive viewer/converter command for Abekas-style YUV files. It calls `readyuv(fd, CYCbCr)` and then displays or writes converted output.

Its flag set and control flow match `tga.c`/`v210.c`: choose compressed or Plan 9 raw output, grayscale/RGBV/true-color conversion, suppress display, and toggle error diffusion. Display uses libdraw window setup and keyboard wait.

Decoded images are converted through `torgbv` or `totruecolor`, then freed with the source `Rawimage` array.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/jpg/yuv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ka/a.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ka/a.h

Shared header for the 9front `ka` assembler. It includes Plan 9 runtime headers, `k.out.h`, and C compiler compatibility definitions, then declares assembler-wide structures and globals.

Core structures are `Sym` for symbols/macros, `Io` for input stack buffers, `Gen` for parsed operands/addresses, and `Hist` for source history. Macros define buffer sizes, hash sizes, EOF/IGN sentinels, `GETC`, and assembler constants.

The header declares lexer/parser, macro preprocessor, include handling, history, symbol lookup, output encoding, and assembly driver functions used across the assembler implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ka/a.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ka/a.y -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ka/a.y

Yacc grammar for the `ka` assembler frontend. It defines token value types, precedence for assembler expressions, instruction grammar, address grammar, and semantic actions that emit assembled instructions via `outcode`.

The instruction rules cover SPARC-like integer loads/stores, floating-point and coprocessor moves, arithmetic/logical/shift forms, branches, calls/jump-and-link, traps, state-register moves, flush, floating/coprocessor operations, `TEXT`, `DATA`, `RETURN`, `NOP`, and `END`.

Operand nonterminals build `Gen` records for registers, special registers, coprocessor/floating registers, immediates, string/float constants, branches, offsets, stack/static names, and register-relative addressing. Expression rules support constants, variables, unary operations, arithmetic, shifts, and bitwise operators.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ka/a.y -->