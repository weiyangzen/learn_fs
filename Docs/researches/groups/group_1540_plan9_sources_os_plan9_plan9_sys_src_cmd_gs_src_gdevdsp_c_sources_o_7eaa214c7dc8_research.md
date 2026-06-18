# Group Research: group_1540_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gdevdsp_c_sources_o_7eaa214c7dc8

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/plan9`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdsp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdsp.c

Implements Ghostscript’s callback-based `display` device for embedding GS in applications. It wraps a memory device, renders into a caller-visible bitmap, and calls host callbacks for open, presize, size, update, sync, page, preclose, close, memory allocation, and separation metadata.

Key behavior:
- Supports many packed display formats via `DisplayFormat`: native 1/4/8/16-bit, gray, RGB/BGR, CMYK, and DeviceN separations.
- Parses `DisplayHandle` as string on 64-bit systems and legacy long on 32-bit systems.
- Allows resize while open, but rejects changing handle/format after open.
- Allocates backing bitmap either through callback `display_memalloc/display_memfree` or Ghostscript non-GC memory.
- Uses `gdev_mem_device_for_bits`, `gs_make_mem_device`, and forwards draw ops to the memory device.
- DeviceN separation support maps spot components and equivalent CMYK values through `display_separation`.

Risks / notes:
- Host callback ABI is trusted after structure validation; incorrect callback behavior can break rendering.
- Pointer encoded in `DisplayHandle` is inherently unsafe if exposed to untrusted PostScript.
- Row-size arithmetic uses `int`; very large dimensions could overflow in old environments.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdsp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdsp.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdsp.h

Public ABI header for the Ghostscript display callback device.

Key contents:
- Documents API order: `gsapi_new_instance`, `gsapi_set_display_callback`, `gsapi_init_with_args`.
- Defines display format bitfields for color model, alpha/unused component layout, bit depth, endian/channel order, first row direction, 555/565 packing, and row alignment.
- Defines `display_callback` version 2, adding `display_separation`.
- Keeps `display_callback_v1_s` for backward compatibility.

Risks / notes:
- ABI depends on exact structure size/version checks in `gdevdsp.c`.
- `DisplayHandle` carries caller pointer-like data as a string/number.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdsp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdsp2.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdsp2.h

Internal display device structure header.

Key contents:
- Declares `gx_device_display`.
- Defines common fields: backing memory device, callback pointer, handle, format, bitmap pointer/size, resolution flag, DeviceN params, equivalent CMYK colors.
- Defines GC descriptor macro `public_st_device_display()` used by `gdevdsp.c`.

Risks / notes:
- Layout couples tightly to Ghostscript device and GC relocation machinery.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdsp2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevegaa.asm -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevegaa.asm

16-bit x86 assembly helpers for PC EGA/VGA framebuffer operations.

Key contents:
- `_vesa_call_set_page` calls VESA page-switch procedure.
- Defines `rop_params` layout shared with C framebuffer code.
- Implements `_memsetcol`, `_memsetrect`, `_memrwcol`, `_memrwcol2` for column/rectangle fill and shifted bitmap copy using far pointers.
- Preserves registers expected by Turbo C large memory model.

Risks / notes:
- Architecture- and compiler-model-specific DOS code.
- C and assembly must keep `rop_params` layout exactly aligned.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevegaa.asm -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevemap.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevemap.c

Static encoding map tables between PostScript StandardEncoding and ISO Latin-1.

Key contents:
- `gs_map_std_to_iso[256]`
- `gs_map_iso_to_std[256]`

Risks / notes:
- Data-only table file; zero entries indicate unmapped code points.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevemap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevepsc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevepsc.c

Color Epson dot-matrix printer driver, primarily for LQ-2550-style color output.

Key behavior:
- Defines `epsonc` printer device.
- Maps RGB to 8 Epson ribbon colors, with violet mapped to blue on reverse conversion.
- Converts scanline bands into Epson graphics commands.
- Handles 9-pin/24-pin modes, double-density passes, vertical skipping, tabbing, and color passes.
- Transposes 8x8 raster blocks into printer pin order.

Risks / notes:
- Compile-time `X_DPI`/`Y_DPI` combinations are not fully validated.
- Complex color-pass logic mutates the color buffer while extracting per-color mono passes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevepsc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevepsn.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevepsn.c

Monochrome Epson/IBM dot-matrix printer family driver.

Key behavior:
- Defines `epson`, `eps9mid`, `eps9high`, and `ibmpro`.
- Shared `eps_print_page` handles printer initialization, scanline copying, vertical skipping, 8x8 transposition, horizontal tab compression, and double-density even/odd passes.
- Special 9-pin modes interleave or merge vertical lines for higher apparent resolution.
- IBM ProPrinter path uses different initialization and archaic behavior.

Risks / notes:
- Assumes specific legal DPI combinations but mostly trusts configured values.
- Many printer quirks are compile-time macros.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevepsn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevescp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevescp.c

Epson ESC/P2 raster printer driver for `st800` and `ap3250`.

Key behavior:
- Supports 180/360 DPI combinations.
- Initializes ESC/P2 graphics mode, sets line spacing, handles A4 page commands when compiled.
- Clips to margins on byte boundaries.
- Skips vertical blank bands.
- Compresses each scanline using ESC/P2 run-length coding and emits raster graphics commands.

Risks / notes:
- Resolution validation occurs at print time.
- Compression writes into a fixed work buffer sized to one band; logic assumes worst-case output fits.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevescp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevevga.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevevga.c

DOS BIOS support routines for IBM PC EGA/VGA display drivers.

Key behavior:
- Real rendering is in `gdevpcfb.c`.
- Provides no-op signal setup.
- Saves current BIOS video/text state via interrupt `0x10`.
- Sets/restores display mode, text page, font, cursor mode, text attributes, and border color.

Risks / notes:
- DOS BIOS-only code, not portable.
- Falls back to mode 3 defaults if current mode is not text mode 3.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevevga.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevfax.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevfax.c

Fax output devices using Ghostscript CCITT Fax encoding streams.

Key behavior:
- Defines `faxg3`, `faxg32d`, and `faxg4`.
- Adds `AdjustWidth` parameter.
- Initializes `stream_CFE_state` with `BlackIs1`, page columns/rows, and optional legal fax width adjustment.
- Shared `gdev_fax_print_strip` streams scanlines through a CCITT encoder and writes compressed output.
- G3 1-D, G3 2-D, and G4 differ by `K`, EOL, and block settings.

Risks / notes:
- Special-cases output filename `nul`.
- Width may differ from device width after fax adjustment, so buffer sizing accounts for both.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevfax.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevfax.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevfax.h

Fax device declarations and defaults.

Key contents:
- Default fax resolution: 204x196 DPI.
- Defines `gx_device_fax` extension with `AdjustWidth`.
- Defines `FAX_DEVICE_BODY`.
- Declares fax open/get/put params and shared fax print helpers.

Risks / notes:
- Intended to be shared by fax-like devices, including TIFF strip use.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevfax.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevherc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevherc.c

Direct Hercules Graphics Card framebuffer display driver for DOS-era PC hardware.

Key behavior:
- Defines `herc` display at 720x350 mono.
- Programs Hercules CRTC/registers directly and clears video memory at `0xb0000000L`.
- Implements fill rectangle, mono copy, and color copy using far framebuffer pointers and Hercules interleaved memory layout.
- Saves/restores previous BIOS video mode.

Risks / notes:
- Highly hardware-specific and non-portable.
- Direct port I/O and far pointers assume 16-bit x86 DOS memory model.
- Several loops use inclusive bounds after clipping; behavior depends on historical helper macros.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevherc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevhit.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevhit.c

Minimal hit-detection device for insideness testing.

Key behavior:
- Exports `gs_hit_detected = gs_error_hit_detected`.
- Defines `gs_hit_device`.
- `hit_fill_rectangle` returns `gs_error_hit_detected` for any positive-area fill.

Risks / notes:
- Intentionally non-rendering; the “hit” is signaled through error control flow.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevhit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevhl7x.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevhl7x.c

Brother HL-720/HL-730 GDI/HBP printer driver.

Key behavior:
- Defines `hl7x0` printer device.
- Sets margins based on PCL paper size helper despite not being a PCL printer.
- Sends PJL/HBP initialization and Brother command streams.
- Builds command buffers with blank-line runs, horizontal offsets, line delta/repeat command encoding, and page form-feed.
- Compression between lines is disabled unless `USE_POSSIBLY_FLAWED_COMPRESSION` is defined, due documented streaking artifacts.

Risks / notes:
- External command format is custom and fragile.
- Historical comments document real printer compatibility problems.
- Temporary buffer free call appears inconsistent with allocation size naming, worth checking if maintaining.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevhl7x.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevifno.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevifno.c

Plan 9 / Inferno bitmap output device.

Key behavior:
- Defines `inferno` printer device.
- Tracks requested colors to infer output `ldepth`.
- Converts RGB scanlines to Inferno/Plan 9 colormap formats, including John Hobby dithering table initialization.
- Writes `compressed` Inferno image format with a sliding-window compressor adapted from Plan 9/Brazil drawing tools.
- Supports 1/2/4/8-bit-per-pixel-style depths via `ldepth`, though `ldepth == 1` path is fatal.

Risks / notes:
- Uses both Ghostscript memory and libc `malloc/free`.
- Some parameter get/put code is present but disabled in the active proc table.
- Contains debug `printf` remnants in inactive paths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevifno.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevijs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevijs.c

Ghostscript IJS client device for driving external IJS printer servers such as hpijs.

Key behavior:
- Defines `ijs` printer device and `gx_device_ijs`.
- Starts an external server from `IjsServer`, opens an IJS job, passes output by filename or duplicated file descriptor.
- Negotiates generic params, duplex/tumble, paper size, printable area, top-left margins, resolution, color model, bits per sample.
- Has special compatibility paths for old hpijs 1.0 IJS version 0.29.
- Sends raster rows to IJS in `gsijs_output_page`, with hpijs white-row workaround.
- Parameter handling enforces `LockSafetyParams` for changing `IjsServer`.

Risks / notes:
- File itself warns that command-line selectable server executable is a security risk; `-dSAFER` is expected.
- `gsijs_read_string` writes `str[new_value.size+1] = '\0'`, which looks off by one for exact copied length.
- External process lifetime and error handling are central to reliability.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevijs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevimgn.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevimgn.c

Imagen ImPRESS printer driver.

Key behavior:
- Defines `imagen` printer device.
- Opens a multi-page ImPRESS document and closes with ImPRESS EOF, optionally byte-stream EOF.
- Supports 75/150/300 DPI through ImPRESS magnification.
- Converts raster pages into 32x32-bit ImPRESS swatches.
- Skips blank swatches and emits bitmap commands only for nonblank swatch runs.
- Optional byte-stream quoting handles quote/EOF/control characters.

Risks / notes:
- Uses environment variable `IMPRESSHEADER` to alter document header.
- Hardware assumptions are Canon CX/ImageStation oriented.
- Swatch copy optimization depends on `BIGTYPE` alignment and size assumptions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevimgn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevjpeg.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevjpeg.c

JPEG output driver built on Ghostscript’s DCT/JPEG stream wrappers and IJG library.

Key behavior:
- Defines `jpeg` RGB, `jpeggray`, and `jpegcmyk` devices.
- Exposes `JPEGQ` and `QFactor`; `JPEGQ` takes precedence.
- CMYK path stores inverted CMYK values for compatibility with Photoshop-style CMYK JPEG expectations.
- `jpeg_print_page` creates JPEG compression state, sets image size/color space/density, applies quality, streams each scanline into a DCTEncode filter, and flushes to output file.

Risks / notes:
- No alpha/deviceN support; only 8-bit gray, 24-bit RGB, and 32-bit CMYK.
- Quality parameter validation is simple and delegated to JPEG setup routines.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevjpeg.c -->