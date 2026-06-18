# Chunk Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevupd.c lines 1-7500

## Scope

This chunk covers the Ghostscript `uniprint` printer driver from file start through the forward pixel readers and reverse-reader dispatcher. The final reverse pixel reader implementations continue after this chunk at lines 7501-7642.

## High-Level Role

`gdevupd.c` implements Ghostscript's `uniprint` device, a configurable raster printer driver driven by PostScript-visible parameters. It maps Ghostscript color values to packed device pixels, dithers scanlines into per-component 1-bit output planes, and writes those planes in several printer command formats: Sun raster, ESC/P, ESC/P2, HP RTL/PCL, Canon extended mode, and Epson nozzle-map mode.

The exported device object is `gs_uniprint_device`, built on `gx_device_common`, `gx_prn_device_common`, and a custom `upd` extension pointer. The device procedure table installs custom open, close, print-page, get-params, put-params, and color mapping behavior.

## Public / Device-Facing APIs

- `upd_print_page(gx_device_printer *pdev, FILE *out)`: main page renderer/writer. It requires `B_OK4GO` (`B_MAP | B_BUF | B_RENDER | B_FORMAT`) and writes job/page open/close/abort command strings around the scan conversion loop.
- `upd_open(gx_device *pdev)`: calls `gdev_prn_open`, applies `upMargins`, opens color mapping, allocates the Ghostscript scanline buffer, opens rendering, and opens the writer.
- `upd_close(gx_device *pdev)`: emits pending close command if a job is open, frees writer/render/map/parameter memory, then calls `gdev_prn_close`.
- `upd_get_params(...)`: exports `upVersion` plus all named choices, flags, ints, int arrays, strings, string arrays, and float arrays.
- `upd_put_params(...)`: imports the same parameter families, copies/mutates them off to the side, adjusts `color_info`, margins, and geometry, closes the device on meaningful changes, installs new `upd` state, and refreshes color procedures.
- Color map procedures selected by `upd_procs_map`: grayscale, RGB, RGBW, CMYK/KCMY, generated black, and RGB-to-CMYK variants.

## Parameter Model and State

The central state is `struct upd_s`. It owns parameter arrays, four `updcmap_t` color maps, input raster buffers, rendering buffers, output scan buffers, output buffer, dimensions, pass counters, printer positions, and flags.

Configuration is exposed as PostScript/Ghostscript parameters:

- Choices: `upColorModel`, `upRendering`, `upOutputFormat`.
- Flags: FS direction/white/zero options, page command adjustment flags, absolute positioning, initialized-state flags, abort/error/open flags, Y flip, and K reduction.
- Ints: output size/components, scan buffers, X/Y step and offset, pin/pass/weave geometry, nozzle-map row/repeat parameters.
- Int arrays: `upColorInfo`, component bits/shifts/order, weave feed/start/pin tables, nozzle row mask and scan offsets.
- Strings: model, begin/end job/page, abort, X/Y movement, step, and linefeed commands.
- String arrays: component-select and component-write commands.
- Float arrays: transfer curves for W/R/G/B/K/C/M/Y plus margins and color map.

Memory management is macro-based (`UPD_MM_*`) around `gs_malloc`/`gs_free`, because parameters are copied into mutable driver-owned storage.

## Control Flow

Open/setup flow:

1. `upd_put_params` reads requested parameters, computes defaults for `upColorInfo`, `upComponentBits`, and `upComponentShift`, updates Ghostscript `color_info`, and closes the device if live state must be rebuilt.
2. `upd_open` applies private margins, calls superclass open, invokes `upd_open_map`, allocates `gsbuf`, invokes `upd_open_render`, invokes `upd_open_writer`, and records opened geometry.
3. `upd_open_map` validates mapper choice, bit widths/shifts, monotonic transfer curves, allocates color code tables, fills inverse mapping tables, sets `ncomp`, and installs device color procedures.
4. `upd_open_render` selects one rendering algorithm and initializes `valbuf` / `valptr`.
5. `upd_open_writer` normalizes pass/weave defaults, validates arrays and command strings, computes ring buffer sizes, asks the format-specific open routine for output needs, and allocates `outbuf` plus per-component scan buffers.

Print flow: `upd_print_page` emits job/page commands, fills the scan ring with `get_bits` plus `upd->render`, writes while enough scanlines are buffered via `upd->writer`, handles abort/page-end/close commands, flushes, and returns interrupt/I/O/success status.

## Color Mapping

`upd_truncate` maps a full `gx_color_value` into a component code using a monotonic transfer table and component mask/shift. `upd_expand` reverses packed component bits into a `gx_color_value`.

The color models are `MAP_GRAY`, `MAP_RGB`, `MAP_RGBW`, `MAP_CMYK`, `MAP_CMYKGEN`, `MAP_RGBOV`, and `MAP_RGBNOV`. Several mappers avoid returning `gx_no_color_index` by flipping the low bit if truncation produces the sentinel value.

## Rendering and Writers

Rendering converts packed Ghostscript pixels into component bitplanes in `scnbuf` using Floyd-Steinberg variants:

- `upd_fscomp`: general component-wise renderer with direction toggling, Y flip, whitespace trimming, and optional K reduction.
- `upd_fscmyk`: optimized byte-aligned 32-bit KCMY rendering.
- `upd_fscmy_k`: CMY/K rendering that prefers black when possible.

Writers support `FMT_RAS`, `FMT_EPSON`, `FMT_ESCP2Y`, `FMT_ESCP2XY`, `FMT_ESCNMY`, `FMT_RTL`, and `FMT_CANON`. `upd_rle` implements PackBits-like RLE and zero-row emission.

## Pixel Readers

This chunk includes declarations for all pixel readers, full forward readers, the dummy reader, and `upd_pxlrev`:

- `upd_pxlfwd` selects forward readers for 1/2/4/8/16/24/32-bit depths.
- Forward readers update `upd->pxlget` for sub-byte depths and advance `pxlptr` at byte boundaries.
- `upd_pxlrev` computes the last-pixel start pointer and selects a reverse reader.
- Reverse reader implementations start at line 7501, outside this chunk.

## Dependencies

Visible dependencies include Ghostscript device/printer APIs (`gdev_prn_*`, `gx_device_*`, `set_dev_proc`, `dev_proc`), parameter APIs (`param_read_*`, `param_write_*`), color constants (`gx_color_value`, `gx_no_color_index`), memory/error APIs (`gs_malloc`, `gs_free`, `gs_error_*`), and standard C I/O/string/signal functions.

## Risks and Edge Cases

- `upd_put_params` uses `error` as both negative error code and positive changed-parameter bitfield.
- Several writer paths manually size and fill raw output buffers.
- Component bit overlap in `upd_open_map` is warning-only under `UPD_M_WARNING`.
- `upd_truncate` relies on carefully shaped monotonic code tables and pointer indexing around `p[-1]`.
- `upd_print_page` ignores writer return values and relies on progress, abort state, and `ferror`.
- Signal handling uses one static `sigupd`, so concurrent devices would not be safe.
- `upd_close_writer` references `words[0]` on `updscan_t`, but this chunk’s struct has no `words` field.
- `upd_1color_rgb` debug logging references `prgb[0]` although the parameter is named `cv`.
- `upd_open_fscomp` debug initialization loop condition appears inverted and never runs.
- Nozzle-map output manually mutates `y` and contains comments expressing uncertainty, so off-by-one risk is higher.
- Reverse pixel reader behavior is only partially visible in this chunk.

## Cross-Chunk References

Lines 7501-7642 continue the reverse pixel readers selected by `upd_pxlrev`: `upd_pxlget1r*`, `upd_pxlget2r*`, `upd_pxlget4r*`, `upd_pxlget8r`, `upd_pxlget16r`, `upd_pxlget24r`, and `upd_pxlget32r`.