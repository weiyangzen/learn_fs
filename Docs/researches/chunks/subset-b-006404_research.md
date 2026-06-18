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
