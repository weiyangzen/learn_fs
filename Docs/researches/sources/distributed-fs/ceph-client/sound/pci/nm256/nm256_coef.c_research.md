# Research: sources/distributed-fs/ceph-client/sound/pci/nm256/nm256_coef.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006403`: lines 1-3914, `Docs/researches/chunks/subset-b-006403_research.md`
- `subset-b-006404`: lines 3915-4608, `Docs/researches/chunks/subset-b-006404_research.md`

## Chunk Research

### subset-b-006403: lines 1-3914

# sources/distributed-fs/ceph-client/sound/pci/nm256/nm256_coef.c lines 1-3914

## Scope

This chunk covers the beginning and bulk of `nm256_coef.c`, from the GPL-2.0 SPDX tag through line 3914. The covered range defines `NM_TOTAL_COEFF_COUNT` and begins the static `coefficients` initializer. It does not reach the closing brace of `coefficients`, and it does not reach the later `coefficient_sizes[8 * 2]` table at the end of the file.

Although the repository path is under a Ceph client source tree, this file is Linux ALSA PCI audio driver data for NeoMagic NM256 hardware. It has no CephFS or distributed-filesystem logic.

## Purpose

The chunk provides compiled-in coefficient bytes used by the NM256 ALSA driver when programming the hardware sample-rate filter tables for playback and capture. The file is included directly by `nm256.c`, so the `static const char coefficients[]` object becomes part of the `snd-nm256` module translation unit rather than a separately linked object.

`NM_TOTAL_COEFF_COUNT` is defined as `0x3158`, and the byte array is declared as `NM_TOTAL_COEFF_COUNT * 4`, or 50,528 bytes. Lines 1-3914 contain 43,010 byte initializers, so this chunk covers most, but not all, of the static coefficient payload. The values are byte literals that encode little-endian signed-looking numeric coefficient streams, with many repeated and mirror-like sequences typical of FIR/filter coefficient tables. The driver treats them as opaque bytes; no code in this chunk decodes or validates their mathematical meaning.

## Important APIs, Types, And Symbols

- `NM_TOTAL_COEFF_COUNT`: Compile-time coefficient count constant. `nm256.c` uses `NM_TOTAL_COEFF_COUNT * 4` to reserve video-RAM buffer space and to copy the full coefficient cache when `use_cache` is enabled.
- `coefficients`: `static const char coefficients[NM_TOTAL_COEFF_COUNT * 4]`. This is the main hardware coefficient blob. This chunk starts the initializer and continues through line 3914 without closing it.
- `coefficient_sizes`: Not present in this chunk, but important for interpretation. Later lines define 16 `u16` sizes for eight playback and eight capture coefficient segments; `nm256.c` uses those sizes to find offsets inside `coefficients`.

There are no functions, structs, enums, exported symbols, callbacks, or macros beyond the total-size define in this chunk.

## Control Flow

This range has no executable control flow. Its behavior is entirely through static data consumed by functions in `nm256.c`:

- `snd_nm256_get_start_offset()` sums prior `coefficient_sizes[]` entries to compute a byte offset into `coefficients`.
- `snd_nm256_load_one_coefficient()` copies one segment from `coefficients + offset` into a per-stream coefficient buffer, then writes start/end buffer addresses to NM256 control registers.
- `snd_nm256_load_coefficient()` chooses playback entries 0-7 or capture entries 8-15, refuses to load while the selected engine is enabled, and either copies one segment or uses a cached full table.
- `snd_nm256_set_format()` calls `snd_nm256_load_coefficient()` when ALSA configures playback or capture format/rate.

With `use_cache` disabled, a rate change copies only the selected coefficient segment into the stream-specific buffer. With `use_cache` enabled, the first coefficient load copies the whole `coefficients` array into `chip->all_coeff_buf`, then later loads program register pointers into that cached table.

## State And Persistence Behavior

The `coefficients` array is immutable kernel module data. It is not persisted to disk, changed at runtime, or generated dynamically. Runtime state lives in `struct nm256` in `nm256.c`, especially:

- `chip->use_cache`, deciding full-table cache versus per-load segment copy.
- `chip->coeffs_current`, marking whether the full coefficient cache has already been copied.
- `chip->all_coeff_buf`, the NM256 memory offset used for cached full-table storage.
- `chip->coeff_buf[SNDRV_PCM_STREAM_PLAYBACK]` and `chip->coeff_buf[SNDRV_PCM_STREAM_CAPTURE]`, per-stream temporary coefficient buffers when caching is disabled.

Power management invalidates coefficient cache state. `nm256_suspend()` sets `chip->coeffs_current = 0`, and resume reinitializes stream formats through `snd_nm256_set_format()`, which reloads the coefficient data as needed. Device creation also initializes `coeffs_current` to zero after assigning the coefficient buffer layout.

## Dependencies And Integration Points

`nm256_coef.c` is included by `sources/distributed-fs/ceph-client/sound/pci/nm256/nm256.c` near the top of the driver, before the coefficient loader functions. This inclusion gives `nm256.c` direct visibility into `NM_TOTAL_COEFF_COUNT`, `coefficients`, and the later `coefficient_sizes` table.

The table integrates with:

- ALSA PCM format setup through `snd_nm256_set_format()`.
- NM256 PCI memory mapping, where `snd_nm256_create()` reserves either the full `NM_TOTAL_COEFF_COUNT * 4` bytes or the maximum playback/record coefficient scratch buffers.
- MMIO-style buffer writes through `snd_nm256_write_buffer()`, which uses `memcpy_toio()` into the device buffer mapping.
- Hardware control-register programming through `snd_nm256_writel()` writes of coefficient start/end pointers.
- Module parameter `use_cache`, which changes whether this data is copied wholesale once or segment-by-segment.

The file depends on the including C file for kernel integer typedefs used later (`u16`) and for all function consumers. This chunk by itself is not a complete compilable translation unit in the module build.

## Risks And Edge Cases

- The table is an opaque hardware payload. Small byte changes can alter audio filter behavior without producing compiler errors.
- The declaration size must remain consistent with the actual initializer and with the sum of `coefficient_sizes[]`. The full file's size table sums to 50,528 bytes, matching `NM_TOTAL_COEFF_COUNT * 4`; this chunk alone is incomplete at 43,010 byte literals.
- Segment offsets are derived by summing `u16` sizes. Reordering or resizing later `coefficient_sizes[]` entries would retarget loader offsets into this byte stream.
- `coefficients` is declared as `char`, not `u8`. The current code copies bytes without arithmetic, so signedness should not affect behavior, but future code that inspects values numerically could introduce signed-char portability bugs.
- In cached mode, the driver reserves and copies the full 50,528-byte table into device memory. Buffer layout calculations in `snd_nm256_create()` rely on this constant when placing playback, capture, and coefficient areas below `buffer_end`.
- In non-cached mode, correctness depends on `NM_MAX_PLAYBACK_COEF_SIZE` and `NM_MAX_RECORD_COEF_SIZE` being large enough for the largest playback/capture `coefficient_sizes[]` entries.
- The chunk ends mid-initializer. Merge/reconciliation must combine this report with later chunks before drawing final conclusions about table termination, size metadata, and complete initializer coverage.

## Test Signals

Useful static/build signals:

- Build `snd-nm256` with `CONFIG_SND_NM256` enabled and warnings elevated; the initializer should fit exactly in `coefficients[NM_TOTAL_COEFF_COUNT * 4]`.
- Check that the full-file sum of `coefficient_sizes[]` is 50,528 bytes, matching `NM_TOTAL_COEFF_COUNT * 4`.
- Check that the largest playback and capture segment sizes fit the non-cache scratch allocation constants.
- Confirm the array remains `static const`, keeping the coefficient payload read-only and translation-unit-local after inclusion.

Useful runtime signals:

- Playback and capture should work at all eight supported rates: 8000, 11025, 16000, 22050, 24000, 32000, 44100, and 48000 Hz.
- Exercise both `use_cache=0` and `use_cache=1`; the former should copy selected segments and the latter should copy the full coefficient table once after init or resume.
- Repeated rate changes should not log "Engine was enabled while loading coefficients!" during normal ALSA prepare/setup sequencing.
- Suspend/resume should restore audio after `coeffs_current` is invalidated and the relevant coefficient segment or cache is reloaded.
- With `CONFIG_SND_DEBUG`, invalid coefficient buffer offsets would be reported by `snd_nm256_write_buffer()`; no such errors should appear during normal PCM open/prepare cycles.

### subset-b-006404: lines 3915-4608

# sources/distributed-fs/ceph-client/sound/pci/nm256/nm256_coef.c lines 3915-4608

## Scope

This chunk covers the final 694 lines of `nm256_coef.c`. It is the tail of the static `coefficients` byte array and the complete `coefficient_sizes[8 * 2]` table. The file is not a standalone translation unit in normal use; `nm256.c` includes it directly so these `static const` objects are compiled into the NeoMagic NM256 ALSA PCI driver.

## Purpose

The data in this chunk supplies hardware coefficient payloads for the NM256 audio engine. The driver uses these payloads when configuring playback and capture for one of the eight supported sample-rate slots. The byte values are opaque DSP/filter/mixer coefficient data, apparently vendor-derived, and the source contains no generation logic or semantic labels for individual coefficients.

The chunk closes the `coefficients[NM_TOTAL_COEFF_COUNT * 4]` initializer and then defines the segment-size table that maps logical playback/capture rate indices to contiguous slices inside that byte blob.

## Important APIs, Types, and Data

- `coefficients`: a `static const char` byte array declared earlier in the file as `NM_TOTAL_COEFF_COUNT * 4` bytes. This chunk contributes the final bytes of the table and terminates the initializer.
- `coefficient_sizes`: a `static const u16` array with 16 entries. Entries 0-7 are playback sizes, entries 8-15 are capture sizes.
- `NM_TOTAL_COEFF_COUNT`: defined at the top of the file as `0x3158`; the total coefficient byte size is therefore `0xc560`.
- Size table values:
  - Playback: `0x00c0`, `0x5000`, `0x0060`, `0x2800`, `0x0040`, `0x0060`, `0x1400`, `0x0000`.
  - Capture: `0x0020`, `0x1260`, `0x0020`, `0x1260`, `0x0000`, `0x0040`, `0x1260`, `0x0000`.

The sum of all `coefficient_sizes` entries is `0xc560`, matching `NM_TOTAL_COEFF_COUNT * 4`. That invariant is central because `nm256.c` derives slice starts by summing all prior sizes instead of storing explicit offsets.

## Control Flow and Integration

This chunk has no executable control flow by itself. Its data is consumed through the coefficient handlers in `nm256.c`:

- `snd_nm256_get_start_offset(which)` sums `coefficient_sizes[0..which-1]` to compute a byte offset into `coefficients`.
- `snd_nm256_load_one_coefficient()` copies one selected segment from `coefficients + offset` into a hardware-visible coefficient buffer and writes start/end addresses to the NM256 coefficient registers.
- `snd_nm256_load_coefficient()` masks the requested rate slot to `0..7`, adds 8 for capture streams, and either loads one segment or, when coefficient caching is enabled, copies the full `coefficients` blob into the reserved buffer once and later points the engine at the relevant subrange.
- Device setup accounts for this data in buffer reservation: cached mode reserves `NM_TOTAL_COEFF_COUNT * 4`; uncached mode reserves only the maximum playback and record coefficient sizes.

The zero-size entries are meaningful table slots for unsupported or no-op rate/configuration positions. Callers can still compute offsets through them, but loading such an entry would produce a zero-length range unless higher-level sample-rate constraints avoid it.

## State and Persistence Behavior

The arrays are compile-time constants with no runtime mutation or persistence. Runtime state lives in the including driver:

- `chip->coeffs_current` tracks whether the full coefficient cache has already been copied to I/O memory.
- `chip->all_coeff_buf` stores the base address for the cached full table.
- `chip->coeff_buf[stream]` stores per-stream coefficient buffer locations for uncached loading.

Because this chunk is pure data, persistence risk is about preserving byte-for-byte table contents and size alignment across builds, not about local state transitions.

## Dependencies

- Depends on kernel integer typedef `u16` being visible from the including `nm256.c` context.
- Depends on `nm256.c` including this file before coefficient handlers need `coefficients`, `coefficient_sizes`, and `NM_TOTAL_COEFF_COUNT`.
- Depends on ALSA PCM stream numbering conventions used by the including code: playback selects entries 0-7, capture selects entries 8-15.
- Depends on the hardware register protocol in `nm256.c`, especially `NM_COEFF_START_OFFSET`, playback/capture register offsets, and the playback-only end-address decrement.

## Risks and Edge Cases

- The table is opaque binary data represented as C numeric initializers. A single changed byte can produce audible artifacts, failed playback/capture at a rate, or hardware misconfiguration with little source-level evidence.
- `coefficient_sizes` is the only segment map. Any mismatch between these sizes and the actual blob layout shifts all later offsets and corrupts subsequent coefficient loads.
- The summed size must remain exactly `NM_TOTAL_COEFF_COUNT * 4`; otherwise cached full-table copying and segment offset computation diverge from the declared array contract.
- The type of `coefficients` is `char`, but the values are byte literals. Consumers pass it to `memcpy_toio`, so signedness should not affect copying, but careless transformations to textual or numeric processing could misinterpret values above `0x7f`.
- Debug bounds checking in `snd_nm256_write_buffer()` validates only the starting offset against the mapped buffer, not `offset + size`; size-table corruption could therefore escape that guard.
- Zero-size slots should be treated intentionally. Replacing them with generated or inferred values could change behavior for unsupported sample-rate entries.

## Test Signals

Useful validation signals for this chunk are structural and integration-oriented:

- Build the NM256 driver and ensure `nm256.c` still compiles with the included data table.
- Assert or manually verify that `sum(coefficient_sizes) == NM_TOTAL_COEFF_COUNT * 4`.
- Check that all coefficient loads for supported sample-rate indices compute offsets within the array and that `offset + size` never exceeds `NM_TOTAL_COEFF_COUNT * 4`.
- Exercise playback and capture at the supported ALSA rates `8000`, `11025`, `16000`, `22050`, `24000`, `32000`, `44100`, and `48000` on NM256 hardware or an equivalent test environment.
- In cached mode, confirm the first coefficient load copies the complete `0xc560` bytes and later loads only update coefficient register start/end addresses.
