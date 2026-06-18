# Group Research: group_1527_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_jpeg_rdppm_c_sources_os_bab21b316781

This group covers a Plan 9 vendored Ghostscript/IJG/libpng slice under `sources/os/plan9/plan9/sys/src/cmd/gs`. The files are not filesystem implementation code; they are image-format adapters for IJG command-line tools, JPEG transform support, Ghostscript utility shell/Perl/AWK wrappers, and a small libpng 1.2.8 support/sample subset.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/rdppm.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/rdppm.c

IJG `cjpeg` source adapter for PPM/PGM input, compiled only under `PPM_SUPPORTED`.

Key behavior:

- Parses PBMPLUS-style PGM/PPM headers for text P2/P3 and raw P5/P6 formats, with comment skipping via `pbm_getc()`.
- Rejects PBM and malformed headers, then fills `j_compress_ptr` input geometry, component count, color space, and precision.
- Provides row readers for text gray/RGB, raw byte gray/RGB with rescaling, direct raw-byte rows when `maxval == MAXJSAMPLE`, and nonstandard 2-byte-per-sample raw formats.
- Allocates a one-row physical I/O buffer for raw formats and a libjpeg sample row unless raw bytes can be read directly into the compressor buffer.
- Builds a `rescale` lookup table when input `maxval` differs from the JPEG sample range.

The data path is entirely stdio-to-libjpeg: `jinit_read_ppm()` creates the `cjpeg_source_struct`, `start_input_ppm()` selects the row-reader, and each `get_*_row()` returns one decompressor input row. It has no Plan 9 filesystem-specific logic beyond ordinary `FILE *` reads.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/rdppm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/rdrle.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/rdrle.c

IJG `cjpeg` source adapter for Utah Raster Toolkit RLE files, compiled only under `RLE_SUPPORTED`.

Main structures and modes:

- `rle_source_struct` wraps `cjpeg_source_struct`, an `rle_hdr`, a virtual sample array, a row counter, temporary `rle_pixel **` rows, and an `rle_kind`.
- Supported visual classes are grayscale, mapped grayscale, pseudocolor, truecolor with colormap, and direct color; alpha is explicitly ignored.
- The code requires 8-bit `JSAMPLE` because it assumes `JSAMPLE` and `rle_pixel` have compatible representations.

Flow:

- `start_input_rle()` calls `rle_get_setup()`, normalizes the RLE x origin, determines color interpretation from `ncolors`/`ncmap`, fills libjpeg image metadata, allocates conversion rows, and requests a virtual array.
- `load_image()` is the first `get_pixel_rows` implementation. It reads the whole RLE stream bottom-up into the virtual array, converts mapped variants through the RLE colormap when needed, clears the alpha channel request, then switches future calls to `get_rle_row()` or `get_pseudocolor_row()`.
- `get_rle_row()` returns rows from the virtual array in JPEG top-down order by decrementing the stored row index.
- `get_pseudocolor_row()` maps one-channel pseudocolor indexes into RGB using three 256-entry colormap planes.

This module depends on the external Utah RLE library and libjpeg virtual arrays to bridge RLE’s lower-left origin to JPEG’s top-left scan order.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/rdrle.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/rdswitch.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/rdswitch.c

Helper parser for advanced `cjpeg` command-line switches.

Handled switch families:

- `-qtables file`: `read_quant_tables()` reads one or more 64-entry decimal quantization tables from comment-capable text and installs them with `jpeg_add_quant_table()`.
- `-scans file`: under `C_MULTISCAN_FILES_SUPPORTED`, `read_scan_script()` parses up to 100 scan definitions, including optional progressive JPEG parameters `Ss Se Ah Al`, then stores a `jpeg_scan_info` array in `cinfo`.
- `-qslots N[,N,...]`: `set_quant_slots()` assigns per-component quantization table selectors, replicating the last supplied value.
- `-sample HxV[,HxV,...]`: `set_sample_factors()` assigns per-component horizontal/vertical sampling factors, defaulting the rest to `1x1`.

Internal parsing uses `text_getc()` to skip `#` comments and `read_text_integer()` / `read_scan_integer()` to read decimal numbers plus punctuation. Errors are reported to `stderr` and returned as `FALSE` rather than through libjpeg fatal exits. The file mutates compressor setup state but performs no image I/O itself.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/rdswitch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/rdtarga.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/rdtarga.c

IJG `cjpeg` source adapter for Targa/TGA input, compiled only under `TARGA_SUPPORTED`.

Supported input forms:

- Uncompressed or RLE-coded colormapped images with 8-bit indexes and 24-bit BGR colormaps.
- Uncompressed or RLE-coded truecolor images with 16-bit 5-5-5, 24-bit BGR, or 32-bit BGRA pixels.
- Uncompressed or RLE-coded 8-bit grayscale images.
- Non-interlaced top-down files directly, and bottom-up files via a full-image virtual array.

Key functions:

- `read_byte()`, `read_colormap()`, `read_non_rle_pixel()`, and `read_rle_pixel()` provide byte and pixel-level TGA input.
- `get_8bit_gray_row()`, `get_8bit_row()`, `get_16bit_row()`, and `get_24bit_row()` expand TGA pixels into libjpeg grayscale or RGB rows. The 16-bit path uses `c5to8bits[]` to round 5-bit color channels to 8-bit samples.
- `preload_image()` reads bottom-up images into `whole_image`, then switches to `get_memory_row()` to return rows in JPEG order.
- `start_input_tga()` validates the 18-byte header, chooses the pixel reader and row expander, allocates either a one-row buffer or virtual array, skips the image ID, reads the colormap, and fills compressor metadata.

The code deliberately rejects interlaced TGA and unsupported colormap forms. It is format-conversion glue around libjpeg’s `cjpeg_source_struct`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/rdtarga.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/transupp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/transupp.c

Support library for `jpegtran`-style lossless JPEG transformations and optional marker copying. It is outside the core JPEG codec but uses `JPEG_INTERNALS` for coefficient-array helpers.

Transform implementation:

- `do_flip_h()` mirrors DCT blocks in place and negates odd-column coefficients.
- `do_flip_v()` writes to destination coefficient arrays and negates odd-row coefficients.
- `do_transpose()` transposes DCT coefficient blocks and swaps image axes.
- `do_rot_90()`, `do_rot_270()`, `do_rot_180()`, and `do_transverse()` implement compound rotations/transverse transpose directly over coefficient arrays, preserving untransformable edge blocks unless trimming is requested.

Public transform API:

- `jtransform_request_workspace()` decides how many components are processed, handles force-grayscale component reduction, and requests virtual coefficient arrays when a transform cannot be done in place.
- `jtransform_adjust_parameters()` applies force-grayscale color-space changes, transposes dimensions/sampling/quantization tables for axis-swapping transforms, trims partial iMCU edges when requested, and returns the coefficient array set that should be written.
- `jtransform_execute_transformation()` dispatches to the selected coefficient transform after `jpeg_write_coefficients()` has initialized destination component dimensions.

Marker-copy support:

- `jcopy_markers_setup()` requests saving COM markers or all APPn markers before header read.
- `jcopy_markers_execute()` writes saved markers to the output, skipping duplicate JFIF APP0 and Adobe APP14 markers already emitted by the encoder.

This file is sensitive to JPEG iMCU geometry, padding, sampling factors, and quantization-table orientation. Its logic is image-transform-specific, not filesystem-related.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/transupp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/transupp.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/transupp.h

External interface for `transupp.c`.

Defines:

- `TRANSFORMS_SUPPORTED`, defaulting transform support on.
- Short external-name aliases for constrained linkers.
- `JXFORM_CODE`: none, horizontal/vertical flip, transpose, transverse, and 90/180/270 degree rotations.
- `jpeg_transform_info`: caller options `transform`, `trim`, `force_grayscale`, plus internal `num_components` and `workspace_coef_arrays`.
- Transform lifecycle functions: `jtransform_request_workspace()`, `jtransform_adjust_parameters()`, and `jtransform_execute_transformation()`.
- `JCOPY_OPTION`: copy no optional markers, comments only, or all optional markers, with `JCOPYOPT_DEFAULT` set to comments.
- Marker-copy functions: `jcopy_markers_setup()` and `jcopy_markers_execute()`.

The header documents the iMCU edge-padding problem and why `trim` exists. Correct callers must invoke the functions at specific points in the libjpeg read/write coefficient pipeline.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/transupp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/wrbmp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/wrbmp.c

IJG `djpeg` destination adapter for uncompressed BMP output, compiled only under `BMP_SUPPORTED`.

Responsibilities:

- Supports Microsoft Windows 3.x BMP and OS/2 1.x BMP headers.
- Emits either 24-bit BGR rows or 8-bit indexed/grayscale rows with colormaps.
- Requires 8-bit `JSAMPLE`; 12-bit JPEG output is intentionally unsupported.
- Uses a full-image virtual array because BMP stores rows bottom-up while JPEG decompression supplies rows top-down.

Key functions:

- `put_pixel_rows()` converts RGB to BGR and appends row padding.
- `put_gray_rows()` stores grayscale or palette-index rows with padding.
- `write_bmp_header()` and `write_os2_header()` generate file/info headers and choose colormap sizes.
- `write_colormap()` emits BGR0 Windows map entries or BGR OS/2 entries, synthesizing a grayscale ramp when needed.
- `finish_output_bmp()` writes the header and then flushes the virtual image from bottom to top.
- `jinit_write_bmp()` validates output color space, calculates padded row width, allocates the virtual array and row buffer, and installs callbacks.

The module is a format writer behind `djpeg`; all persistent storage interaction is ordinary stdio output.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/wrbmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/wrgif.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/wrgif.c

IJG `djpeg` destination adapter for GIF output, compiled only under `GIF_SUPPORTED`.

Important design point:

- The file intentionally writes “uncompressed GIF” data to avoid LZW patent concerns in the original era. It emits each pixel as a code and periodically emits clear codes before the code width would grow.

Key functions:

- `flush_packet()`, `CHAR_OUT`, and `output()` pack variable-width GIF codes into GIF data sub-blocks.
- `compress_init()`, `compress_pixel()`, and `compress_term()` implement the pseudo-compressor state machine.
- `emit_header()` writes a GIF87a header, logical screen descriptor, global color table, image descriptor, initial code size, and starts pseudo-compression.
- `start_output_gif()` emits the header using the decompressor colormap or a synthesized 256-entry grayscale map.
- `put_pixel_rows()` writes one row of palette indexes.
- `finish_output_gif()` terminates the pseudo-compressed stream, writes the GIF block terminator and trailer, and checks write errors.
- `jinit_write_gif()` validates grayscale/RGB output, forces quantization for color or >8-bit input, caps desired colors at 256, verifies single-component output, and allocates the row buffer.

This is a command-line image-output adapter and does not interact with filesystem internals beyond writing the output stream.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/wrgif.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/wrjpgcom.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/wrjpgcom.c

Standalone IJG utility that inserts a textual COM marker into a JPEG stream.

Core marker logic:

- Defines minimal JPEG marker constants for SOI, EOI, SOS, SOFn variants, and COM.
- `first_marker()` validates the initial SOI bytes.
- `next_marker()` scans marker boundaries before compressed scan data, swallowing fill `0xFF` bytes and warning about discarded non-marker garbage.
- `copy_variable()` copies a variable-length marker payload, while `skip_variable()` discards one.
- `scan_JPEG_header()` copies markers up to the first SOFn or EOI, optionally removing existing COM markers.

Command-line behavior:

- Supports `-replace`, `-comment "text"`, and `-cfile name`, with abbreviated case-insensitive switch matching in `keymatch()`.
- Reads comment text from `-comment`, a file, or standard input, bounded by `MAX_COM_LENGTH`.
- Handles Unix one-file stdout style or `TWO_FILE_COMMANDLINE` platforms with explicit input/output names.
- Inserts the new COM marker just before the first SOFn marker so it follows JFIF/JFXX headers, then copies the remainder of the source file unchanged.

This utility is a small binary stream rewriter. It does not decode JPEG entropy data and does not depend on libjpeg compression/decompression objects.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/wrjpgcom.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/wrppm.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/wrppm.c

IJG `djpeg` destination adapter for raw PPM/PGM output, compiled only under `PPM_SUPPORTED`.

Key behavior:

- Emits raw P5 PGM for grayscale and raw P6 PPM for RGB.
- Supports standard 8-bit byte samples and optionally nonstandard 2-byte-per-sample output for wider `JSAMPLE` builds unless `PPM_NORAWWORD` downscaling is selected.
- Uses direct `JFWRITE()` from the decompressor row buffer in the common case where `JSAMPLE` is byte-sized and no quantized colormap demapping is needed.
- Uses `copy_pixel_rows()` for sample-size translation, `put_demapped_rgb()` for quantized RGB indexes, and `put_demapped_gray()` for quantized grayscale indexes.

`jinit_write_ppm()` calculates output dimensions, allocates a physical I/O buffer, decides whether the decompressor can write directly into it, and installs the appropriate row callback. `finish_output_ppm()` only flushes and checks the stream.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/wrppm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/wrrle.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/wrrle.c

IJG `djpeg` destination adapter for Utah Raster Toolkit RLE output, compiled only under `RLE_SUPPORTED`.

Main behavior:

- Requires 8-bit `JSAMPLE`, matching the RLE library’s `rle_pixel` assumption.
- Validates RLE 16-bit signed dimension limits and restricts output to grayscale or RGB with one or three channels.
- Because RLE stores rows bottom-up, stores decompressor rows in a virtual array and emits them in reverse order during `finish_output_rle()`.
- Converts libjpeg colormaps to RLE `rle_map` format by left-shifting 8-bit samples and stores a `color_map_length` comment when quantized output is used.

Key functions:

- `start_output_rle()` validates image constraints, converts any colormap, initializes the first virtual row buffer, and installs `rle_put_pixel_rows()`.
- `rle_put_pixel_rows()` advances the output buffer to the next virtual row.
- `finish_output_rle()` builds an `rle_hdr`, writes setup/colormap, emits one-channel rows directly or splits interleaved RGB rows into RLE planes, then writes EOF.
- `jinit_write_rle()` allocates the RLE plane work rows and full-image virtual array.

This file is an RLE library bridge for `djpeg`, not Plan 9 storage code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/wrrle.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/wrtarga.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/wrtarga.c

IJG `djpeg` destination adapter for Targa/TGA output, compiled only under `TARGA_SUPPORTED`.

Supported outputs:

- Uncompressed top-down 8-bit grayscale.
- Uncompressed top-down 24-bit RGB stored as BGR bytes.
- 8-bit colormapped RGB with a 24-bit BGR palette when decompressor quantization is active.
- Quantized grayscale is demapped to grayscale samples because Targa has no mapped grayscale form in this writer.

Key functions:

- `write_header()` builds the 18-byte TGA header, selecting image type 1, 2, or 3 and marking the image top-down/non-interlaced.
- `put_pixel_rows()` converts RGB rows to BGR output.
- `put_gray_rows()` writes grayscale or palette-index rows directly.
- `put_demapped_gray()` maps quantized grayscale indexes back through the single-channel colormap.
- `start_output_tga()` writes the header, emits a BGR colormap when needed, and installs the final row writer.
- `jinit_write_targa()` calculates dimensions and allocates an I/O row buffer plus decompressor row buffer.

The writer assumes 8-bit samples and uses ordinary stdio output.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/wrtarga.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/afmdiff.awk -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/afmdiff.awk

AWK utility for comparing two Adobe Font Metric files.

Behavior:

- Records the first two `FontName` values encountered, corresponding to the two input AFM files.
- For AFM character metric lines beginning `C `, tracks character names, declared `WX` widths, and bounding-box width/height derived from BBox fields.
- Reports character repertoire differences in both directions.
- Reports numeric differences for `WX`, bounding-box width, and bounding-box height.
- Sorts each report column through `sort -f | pr -c3 -w80 -l1 -t`.

The script is purely metrics-analysis tooling for Ghostscript font data. It has no repository-build or filesystem-layer role.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/afmdiff.awk -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/bdftops -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/bdftops

Tiny shell wrapper around Ghostscript’s `bdftops.ps`.

It sets `GS_EXECUTABLE=gs` and then executes:

- `gs -q -dBATCH -dNODISPLAY -- bdftops.ps "$@"`

Purpose: run the PostScript helper that converts BDF font data to PostScript form. The executable name is intended to be patched during installation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/bdftops -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/dumphint -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/dumphint

Shell wrapper for formatting linearized PDF hint data.

Behavior:

- Initializes `GS_EXECUTABLE=gs`.
- Accumulates leading `-*` options into `OPTIONS`, defaulting to `-dSAFER -dDELAYSAFER`.
- Requires exactly one `input.pdf`.
- Executes Ghostscript in quiet no-display mode over `dumphint.ps`.

This is command-line glue for a Ghostscript PostScript utility.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/dumphint -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/dvipdf -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/dvipdf

Shell wrapper converting DVI to PDF through `dvips` and Ghostscript.

Behavior:

- Collects leading options for Ghostscript.
- Accepts `input.dvi` and optional `output.pdf`; otherwise derives the output name from the input basename.
- Pipes `dvips -q -f "$infile"` into `gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile="$outfile" ... -c .setpdfwrite -`.
- Passes options twice because `-I` only takes effect before other options.

This script is a document-conversion wrapper only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/dvipdf -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/eps2eps -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/eps2eps

Shell wrapper for “distilling” Encapsulated PostScript to EPS through Ghostscript.

Behavior:

- Defaults large device dimensions with `-dDEVICEWIDTH=250000 -dDEVICEHEIGHT=250000`.
- Appends leading command-line switches to `OPTIONS`.
- Requires exactly `input.eps output.eps`.
- Executes `gs -q -sDEVICE=epswrite -sOutputFile=... -dNOPAUSE -dBATCH -dSAFER`.

It is a thin CLI adapter around Ghostscript’s EPS writer device.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/eps2eps -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/fixmswrd.pl -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/fixmswrd.pl

Perl filter that patches Microsoft Word printer-driver PostScript so older Ghostview can view pages independently.

Problem addressed:

- Word-generated DSC may open a procset dictionary outside page sections and close it in the trailer.
- Page viewers that isolate pages miss that dictionary context.

Behavior:

- Accepts `[-v] [file [output-file]]`, otherwise reads stdin and writes stdout.
- Reads and preserves header comments, adding `%LOCALGhostviewPatched` before `%%EndComments` unless already present.
- Detects procset/dictionary names from `%%BeginResource: procset ...` or older `%%BeginProcSet: ...`.
- Removes the original global `dict begin` line and trailer `end` line.
- Inserts `dict begin` after each `%%Page:` and `end` after each `showpage`.
- If the marker is already present, passes input through unchanged.

This is PostScript structure repair tooling; it does not touch Ghostscript internals.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/fixmswrd.pl -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/font2c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/font2c

Tiny shell wrapper around Ghostscript’s `font2c.ps`.

It sets `GS_EXECUTABLE=gs` and runs:

- `gs -q -dNODISPLAY -dWRITESYSTEMDICT -- font2c.ps "$@"`

Purpose: execute the PostScript helper that converts font data to C-source form.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/font2c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/gsbj -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/gsbj

Shell convenience wrapper for printing through Ghostscript’s Canon BJ-10e device.

It runs `gs` quietly with:

- `-sDEVICE=bj10e`
- `-r180`
- `-dNOPAUSE`
- `-sPROGNAME=$0`
- `gslp.ps --heading-center "$(date)" "$@"`

This is a printer preset wrapper.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/gsbj -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/gsdj -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/gsdj

Shell convenience wrapper for printing through Ghostscript’s DeskJet device.

It runs `gs` quietly with:

- `-sDEVICE=deskjet`
- `-r300`
- `-dNOPAUSE`
- `-sPROGNAME=$0`
- `gslp.ps --heading-center "$(date)" "$@"`

This is a printer preset wrapper.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/gsdj -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/gsdj500 -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/gsdj500

Shell convenience wrapper for printing through Ghostscript’s DeskJet 500 device.

It runs `gs` quietly with:

- `-sDEVICE=djet500`
- `-r300`
- `-dNOPAUSE`
- `-sPROGNAME=$0`
- `gslp.ps --heading-center "$(date)" "$@"`

This is a printer preset wrapper.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/gsdj500 -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/gslj -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/gslj

Shell convenience wrapper for printing through Ghostscript’s LaserJet device.

It runs `gs` quietly with:

- `-sDEVICE=laserjet`
- `-r300`
- `-dNOPAUSE`
- `-sPROGNAME=$0`
- `gslp.ps --heading-center "$(date)" "$@"`

This is a printer preset wrapper.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/gslj -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/gslp -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/gslp

Shell convenience wrapper for printing through Ghostscript’s Epson device.

It runs `gs` quietly with:

- `-sDEVICE=epson`
- `-r180`
- `-dNOPAUSE`
- `-sPROGNAME=$0`
- `gslp.ps --heading-center "$(date)" "$@"`

This is a printer preset wrapper.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/gslp -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/gsnd -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/gsnd

Minimal no-display Ghostscript wrapper.

It sets `GS_EXECUTABLE=gs` and executes:

- `gs -dNODISPLAY "$@"`

Purpose: run Ghostscript as a non-display PostScript interpreter with caller-supplied arguments.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/gsnd -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/lprsetup.sh -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/lprsetup.sh

BSD print-filter setup utility for Ghostscript.

Behavior:

- Defines printer devices, filter names, printer port/type, Ghostscript library/filter directories, spool directory, and helper names.
- Requires the Ghostscript library directory to be writable.
- Creates a filter directory, `direct` and `indirect` symlink aliases, symlinks each lpr filter name to `unix-lpr.sh`, and creates device symlinks.
- Generates a `printcap.insert` file in the current directory with example queue entries for each configured Ghostscript device.
- Handles `.dq` device suffixes as dual-queue setups with raw output queues.
- Emits a sorted reminder of spool directories/log/accounting files the administrator must create.

This is installation/admin scaffolding for Unix BSD `lpr`; it does not configure Plan 9 printing or filesystem internals.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/lprsetup.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/pdf2dsc -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/pdf2dsc

Shell wrapper that generates a DSC index for a PDF file.

Behavior:

- Accepts `pdffile [dscfile]`; otherwise derives `.dsc` by replacing the input extension.
- Runs Ghostscript no-display and safe with `pdf2dsc.ps`, passing `-sPDFname` and `-sDSCname`, then `-c quit`.

This is a Ghostscript utility launcher for PDF page-index metadata.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/pdf2dsc -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/pdf2ps -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/pdf2ps

Shell wrapper converting PDF to PostScript.

Behavior:

- Accumulates leading options.
- Accepts `input.pdf [output.ps]`, deriving the output name when omitted.
- Runs Ghostscript with `-sDEVICE=pswrite`, `-dNOPAUSE`, `-dBATCH`, `-dSAFER`, and an initial `save pop` to reduce font flushing between pages.
- Passes options both before and after fixed switches so include-path options can take effect early.

This is document conversion command glue.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/pdf2ps -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/pdfopt -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/pdfopt

Shell wrapper for optimizing a PDF through Ghostscript’s `pdfopt.ps`.

Behavior:

- Defaults options to `-dSAFER -dDELAYSAFER`.
- Appends leading command-line switches.
- Requires `input.pdf output.pdf`.
- Executes Ghostscript quietly in no-display mode with `pdfopt.ps`.

This is a utility wrapper, not a library module.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/pdfopt -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/pf2afm -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/pf2afm

Shell wrapper that makes an AFM file from PFB/PFA and optionally PFM font files.

It runs:

- `gs -q -dNODISPLAY -dSAFER -dDELAYSAFER -- pf2afm.ps "$@"`

The PostScript helper owns the actual font metric extraction. This file only selects the Ghostscript invocation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/pf2afm -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/pfbtopfa -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/pfbtopfa

Shell wrapper converting binary Type 1 `.pfb` fonts to ASCII `.pfa`.

Behavior:

- Accepts `input.pfb [output.pfa]`; derives the output basename when omitted.
- Rejects other argument counts with usage text.
- Runs Ghostscript in no-display mode over `pfbtopfa.ps` with input and output paths.

The script is font conversion glue.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/pfbtopfa -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/pphs -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/pphs

Shell wrapper for printing the Primary Hint Stream from a linearized PDF.

It sets `GS_EXECUTABLE=gs` and executes:

- `gs -q -dNODISPLAY -- pphs.ps "$@"`

Output goes to stdout. The actual parsing is in `pphs.ps`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/pphs -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/printafm -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/printafm

Tiny shell wrapper for printing metrics from an AFM font.

It directly executes:

- `gs -q -dNODISPLAY -- printafm.ps "$@"`

Unlike nearby wrappers, it hardcodes `gs` rather than using `GS_EXECUTABLE`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/printafm -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2ascii -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2ascii

Shell wrapper for extracting ASCII text from PostScript.

Behavior:

- Uses Ghostscript with `-q -dNODISPLAY -dSAFER -dDELAYBIND -dWRITESYSTEMDICT -dSIMPLE`.
- Accepts zero, one, or two arguments:
  - no arguments: stdin to stdout,
  - one input file: text to stdout,
  - input plus output: redirects text to the output file.
- Runs `ps2ascii.ps` and terminates with `-c quit`.
- Installs a trap to remove `_temp_.err` and `_temp_.out`, though this wrapper itself does not create them directly.

This is text-extraction command glue.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2ascii -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2epsi -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2epsi

Shell wrapper that produces EPSI from PostScript.

Behavior:

- Accepts `file.ps [file.epsi]`; derives `.epsi` from common PostScript/EPS suffixes when omitted.
- Creates a temporary metadata file in `/tmp/ps2epsi$$`.
- Uses `ls -l` plus AWK and the input’s DSC comments to synthesize PostScript variables for title, creator, creation date, and user.
- Runs Ghostscript at 72 dpi with the `bit` device and `ps2epsi.ps` to generate preview metadata, redirecting Ghostscript output to stderr.
- Rewrites the final EPSI by emitting a prolog/trailer wrapper around the original input with old preview and selected DSC boilerplate stripped by `sed`.

It is document-conversion shell glue with temporary-file handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2epsi -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2pdf -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2pdf

Compatibility wrapper for PostScript-to-PDF conversion.

Behavior:

- Documents that the default currently targets PDF 1.4 but may change.
- Executes `ps2pdf14 "$@"`.

The actual Ghostscript invocation is delegated through `ps2pdf14` to `ps2pdfwr`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2pdf -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2pdf12 -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2pdf12

Compatibility wrapper for PostScript-to-PDF 1.2.

It executes:

- `ps2pdfwr -dCompatibilityLevel=1.2 "$@"`

This selects Acrobat 3-era PDF compatibility while delegating all conversion behavior to `ps2pdfwr`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2pdf12 -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2pdf13 -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2pdf13

Compatibility wrapper for PostScript-to-PDF 1.3.

It executes:

- `ps2pdfwr -dCompatibilityLevel=1.3 "$@"`

This selects Acrobat 4-era PDF compatibility while delegating all conversion behavior to `ps2pdfwr`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2pdf13 -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2pdf14 -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2pdf14

Compatibility wrapper for PostScript-to-PDF 1.4.

It executes:

- `ps2pdfwr -dCompatibilityLevel=1.4 "$@"`

This selects Acrobat 5-era PDF compatibility while delegating all conversion behavior to `ps2pdfwr`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2pdf14 -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2pdfwr -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2pdfwr

Core shell wrapper for PostScript/EPS-to-PDF conversion without setting a compatibility level itself.

Behavior:

- Defaults options to `-dSAFER` and appends leading switches.
- Accepts `(input.[e]ps|-) [output.pdf|-]`.
- Derives the output name from `.eps`, `.ps`, or the full basename when omitted; preserves `-` for stdin/stdout-style usage.
- Runs Ghostscript with `-q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile=...`, repeats options, calls `.setpdfwrite`, and reads the input with `-f`.

PDF-version wrappers `ps2pdf12`, `ps2pdf13`, and `ps2pdf14` call this script with `-dCompatibilityLevel`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2pdfwr -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2ps -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2ps

Shell wrapper for distilling PostScript to PostScript through Ghostscript’s older `pswrite` device.

Behavior:

- Defaults to `-dSAFER`.
- Appends leading switches.
- Requires `input.ps output.ps`.
- Runs `gs -q -sDEVICE=pswrite -sOutputFile=... -dNOPAUSE -dBATCH`.

This is command glue for PostScript normalization.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2ps -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2ps2 -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2ps2

Shell wrapper for distilling PostScript through Ghostscript’s newer `ps2write` device.

Behavior mirrors `ps2ps` except:

- It uses `-sDEVICE=ps2write`.
- It identifies as revision 1.1 in the source header.

The script requires `input.ps output.ps` and passes optional leading Ghostscript switches.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2ps2 -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/pv.sh -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/pv.sh

Shell helper for previewing one page of a DVI file in Ghostscript.

Behavior:

- Requires `page_number file_name[.dvi]`.
- Sets `GS_EXECUTABLE=gs`, `TEMPDIR=.`, and installs a trap to remove `$TEMPDIR/$FILE.$$.pv`.
- Runs `dvips -p $PAGE -n 1 $FILE ... -o $FILE.$$.pv`.
- Opens the generated one-page PostScript file with Ghostscript.

The script is an interactive document-preview convenience wrapper.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/pv.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/unix-lpr.sh -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/unix-lpr.sh

Unix BSD `lpr` filter script for Ghostscript-rendered printer queues.

Key behavior:

- Sets search paths for Ghostscript, PBMPLUS, PostScript filters, and X11 libraries.
- Redirects stdout to stderr for logging while preserving file descriptor 3 for raw printer output.
- Parses lpr filter arguments for user, host, and accounting file.
- Infers filter name, device name, and direct/indirect queue type from `$0` path layout created by `lprsetup.sh`.
- Parses optional device suffixes for colors and bits-per-pixel.
- Logs job metadata using the spool lock/control file.
- Chooses output strategy:
  - `direct`: pipe rendered bytes to fd 3,
  - `indirect`: pipe rendered bytes to `lpr -P${device}.raw`.
- Filters input through format-specific preprocessors based on filter name (`gsif`, `gsnf`, `gstf`, `gsgf`, `gsvf`, `gsdf`).
- Appends PostScript accounting code that records page count, host, and user.
- Runs Ghostscript with `-sDEVICE`, `-dBitsPerPixel`, optional color count, and `-sOutputFile=|...`.

This is legacy Unix print-spool integration. It is operational shell code but outside Plan 9 filesystem research scope.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/unix-lpr.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/wftopfa -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/wftopfa

Tiny shell wrapper around Ghostscript’s `wftopfa.ps`.

It sets `GS_EXECUTABLE=gs` and runs:

- `gs -q -dNODISPLAY -- wftopfa.ps "$@"`

Purpose: execute the associated PostScript font-conversion helper.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/lib/wftopfa -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/configure -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/configure

Stub shell script for the vendored libpng 1.2.8 tree.

It prints a message explaining:

- This distribution has no real `configure` script.
- Users should copy an appropriate makefile from the `scripts` directory and read `INSTALL`.
- A separate `libpng-1.2.8-config.tar.gz` configure-based distribution is available from libpng distribution sites.

No configuration is performed; the script only informs the user.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/configure -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/example.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/example.c

Non-compiling libpng instructional example, disabled by top-level `#if 0`.

Purpose:

- Demonstrates how applications can read and write PNG files with libpng.
- Explicitly says missing application-specific pieces must be supplied and points to `pngtest.c` for a minimal working program.

Covered read patterns:

- `check_if_png()` opens a file, reads four signature bytes, and checks them with `png_sig_cmp()`.
- Two `read_png()` prototypes show filename-owned and already-open-file flows.
- Demonstrates `png_create_read_struct()`, `png_create_info_struct()`, `setjmp` error handling, standard I/O via `png_init_io()` or custom read callbacks, `png_set_sig_bytes()`, `png_read_info()`, `png_get_IHDR()`, and high-level `png_read_png()`.
- Shows optional transforms: strip 16-bit, strip alpha, packing, palette-to-RGB, grayscale expansion, tRNS-to-alpha, background compositing, gamma correction, dithering, monochrome inversion, sBIT shifting, BGR ordering, alpha swapping, endian swapping, filler bytes, and interlace handling.
- Demonstrates whole-image and row-by-row reads, followed by `png_read_end()` and `png_destroy_read_struct()`.

Progressive read examples:

- `initialize_png_reader()` creates read/info structs, sets setjmp handling, and installs progressive callbacks.
- `process_data()` feeds byte chunks into `png_process_data()`.
- `info_callback()`, `row_callback()`, and `end_callback()` show where to prepare transforms, combine rows with `png_progressive_combine_row()`, and mark completion.

Write pattern:

- `write_png()` demonstrates `png_create_write_struct()`, `png_create_info_struct()`, `png_init_io()` or custom write callbacks, high-level `png_write_png()`, lower-level `png_set_IHDR()`, palette setup, sBIT/gAMA/text metadata, transform setup, interlace handling, `png_write_image()` or `png_write_rows()`, `png_write_end()`, explicit freeing of caller-allocated palette/auxiliary data, and `png_destroy_write_struct()`.

This file is documentation-as-code and is intentionally excluded from compilation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/example.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/png.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/png.c

General-purpose libpng 1.2.8 core utility file.

Version and global data:

- Defines `PNG_INTERNAL` and includes `png.h`.
- Uses a typedef guard to force a compile-time mismatch if an older `png.h` is found.
- Under `PNG_USE_GLOBAL_ARRAYS`, defines the libpng version string, PNG signature bytes, chunk-name constants, and Adam7 interlace pass tables/masks.

Signature, zlib, and CRC helpers:

- `png_set_sig_bytes()` records how many PNG signature bytes the caller already consumed.
- `png_sig_cmp()` compares a caller-supplied byte range against the PNG signature.
- `png_check_sig()` is the obsolete boolean signature wrapper.
- `png_zalloc()` and `png_zfree()` provide zlib allocation/free hooks backed by libpng memory functions, with overflow checking.
- `png_reset_crc()` and `png_calculate_crc()` manage chunk CRC state while respecting configured CRC ignore/use flags.

`png_info` lifecycle:

- `png_create_info_struct()` allocates and initializes a public info struct.
- `png_destroy_info_struct()` destroys a single info struct.
- `png_info_init()` and `png_info_init_3()` zero/reinitialize info storage and handle older ABI size expectations.
- `png_data_freer()` sets ownership policy bits when `PNG_FREE_ME_SUPPORTED` is enabled.
- `png_free_data()` frees selected owned fields: text, transparency, sCAL, pCAL, iCCP, suggested palettes, unknown chunks, histogram, palette, and row pointers.
- `png_info_destroy()` frees all info-owned data, unknown chunk lists, and reinitializes the struct.

Other API helpers:

- `png_get_io_ptr()` returns the user I/O pointer.
- `png_init_io()` stores a `FILE *` as the default I/O pointer when stdio is available.
- `png_convert_to_rfc1123()` formats PNG time data as an RFC 1123-style UTC string.
- `png_get_copyright()`, `png_get_libpng_ver()`, `png_get_header_ver()`, `png_get_header_version()`, and `png_access_version_number()` expose version/copyright strings and numeric version.
- `png_handle_as_unknown()` queries caller-configured unknown-chunk handling.
- `png_reset_zstream()` calls zlib `inflateReset()`.
- `png_init_mmx_flags()` initializes assembler/MMX capability flags when compiled with assembler support; `png_mmx_support()` returns `-1` in builds without runtime MMX detection.
- `png_convert_size()` safely narrows `size_t` to `png_size_t` when `PNG_SIZE_T` is configured.

This is library support plumbing for libpng memory ownership, metadata cleanup, signatures, CRC, versioning, I/O pointer storage, and optional CPU feature flags.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/png.c -->