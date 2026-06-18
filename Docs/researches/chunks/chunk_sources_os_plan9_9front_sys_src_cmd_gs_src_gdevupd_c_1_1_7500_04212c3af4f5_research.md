# Chunk Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevupd.c lines 1-7500

## Scope

This chunk covers nearly all of Ghostscript's old `uniprint` printer driver implementation in 9front's imported `cmd/gs` tree. The source tree `sources/os/plan9/9front` is included by `Docs/research_subset_a.md`; this file is not filesystem code, but it is in the scoped Plan 9 source tree. Lines 1-7500 define the device prototype, parameter tables, private driver state, device lifecycle, Ghostscript parameter import/export, color mapping, Floyd-Steinberg rendering, output-buffer setup, Sun raster/ESC/P/ESC/P2/nozzle-map/PCL/Canon writers, run-length compression, and forward plus reverse pixel-reader dispatch setup. The chunk ends just before the reverse pixel-reader function bodies continue at line 7501.

## APIs and Entry Points

- The exported driver object is `gs_uniprint_device`, a `upd_device` built with `prn_device_body()` and the private procedure table `upd_procs`.
- Ghostscript device callbacks implemented here are `upd_open()`, `upd_close()`, `upd_print_page()`, `upd_get_params()`, `upd_put_params()`, color encode/decode callbacks, and CMYK mapping callbacks.
- Rendering functions selected by `upRendering` are `upd_fscomp()`, `upd_fscmyk()`, and `upd_fscmy_k()`.
- Output writers selected by `upOutputFormat` are Sun raster, ESC/P, ESC/P2 Y-weave, ESC/P2 X/Y-weave, Epson nozzle-map, HP RTL/PCL, and Canon extended mode.
- Pixel-reader entry setup is `upd_pxlfwd()` and `upd_pxlrev()`, which install specialized `upd_pxlget*` callbacks for packed depths 1/2/4/8/16/24/32 bits. Reverse reader bodies continue in the next chunk.

## Control Flow and State

`upd_put_params()` reads the `up*` parameter namespace, accepts null as reset-to-empty, copies arrays/strings into driver-owned memory, derives missing `upColorInfo`, component bit widths/shifts, ramps, and margins, then calls `gdev_prn_put_params()`. Changed parameters or geometry force close/reopen so `upd_open()` recomputes map/render/writer state.

`upd_open()` enforces margins, calls `gdev_prn_open()`, initializes color mapping, computes printable raster dimensions, allocates the raw Ghostscript scan buffer, opens rendering, opens the writer, and records device geometry. `upd_print_page()` writes job/page command sequences, pulls scanlines with `get_bits`, renders into circular component buffers, writes buffered passes, handles optional signal abort, and writes page/job termination sequences. `upd_close()` writes any deferred close sequence and frees map/render/writer/parameter state.

The central `upd_s` owns parameter copies, color maps, raw scan buffer, pixel-reader state, render/writer function pointers, scan buffers, FS error buffers, output buffer, readiness flags, geometry, pass counters, printer positions, and component-selection state.

## Mapping, Rendering, Writers

`upd_open_map()` validates selected color model, component bit layout, and monotonic transfer curves, allocates interpolation tables, fills `upd->cmap[]`, and installs Ghostscript mapping procedures. Mapping modes include grayscale, RGB, RGBW, CMYK/KCMY, generated-black CMYK, and RGB-to-CMYK with undercolor removal.

Rendering converts packed Ghostscript indices to one-bit component scanlines. `upd_open_fscomp()` allocates component FS state and error buffers, computes threshold/scale/spotsize, optionally randomizes initial error, and installs `upd_fscomp()`. Specialized CMYK renderers either assume 32-bit KCMY byte layout or enforce CMY/K-separated output. Renderers support direction toggling, whitespace skipping, Y-flip, pass limits, and optional K reduction.

`upd_open_writer()` normalizes weave/pass/pin parameters, creates defaults, validates command arrays, computes circular scan-buffer sizes, and dispatches format setup. Writers cover Sun raster headers/data, ESC/P pin columns, ESC/P2 RLE rows, X-weaved ESC/P2 repacking, Stylus Color 300 nozzle maps, HP RTL/PCL/PJL command rewriting, Canon extended-mode rows, and shared PackBits-like `upd_rle()` compression.

## Dependencies

This chunk depends on Ghostscript printer-device APIs (`gdevprn.h`), parameter APIs (`gsparam.h`), Ghostscript memory allocation, device procedure tables, color/index conventions, C stdlib/limits/ctype helpers, optional POSIX signals, `FILE *` I/O, architecture endian/word-size macros, and macros such as `countof`, `set_dev_proc`, `dev_proc`, margin helpers, and `gx_device_raster()`.

## Risks and Edge Cases

- Manual output-buffer sizing feeds many `memcpy`, `sprintf`, `fprintf`, `fwrite`, and RLE paths; estimate mistakes can overflow buffers.
- `upd_put_params()` overloads `error` as both negative error code and positive change bitset.
- User-controlled geometry/pass/pin values are multiplied in signed intermediates.
- `upd_pxlrev()` can underflow `width-1` if invalid configuration yields zero width.
- `upd_truncate()` relies on transfer-table neighbor access during binary search.
- Debug-only `upd_1color_rgb()` references `prgb[0]` though the parameter is `cv`.
- `UPD_M_FSBUF` initialization uses `UPD_VALPTR_MAX < icomp`, so it never initializes the arrays as intended.
- `upd_close_writer()` references `words[0]` in `updscan_t`, but this chunk defines only `bytes`, suggesting a stale or broken local source variant.
- Optional signal abort uses one static `sigupd`, so concurrent print jobs are not signal-safe.

## Cross-Chunk References

- Lines 7501-7642 continue reverse pixel-reader bodies (`upd_pxlget1r*`, `2r*`, `4r*`, `8r`, `16r`, `24r`, `32r`). Renderers in this chunk depend on those callbacks after `upd_pxlrev()`.
- The final per-file report must merge this chunk with the tail to cover complete pixel-reader behavior.
- External Ghostscript `.upp` configuration files provide the `up*` parameters consumed here; this chunk defines the driver-side contract.