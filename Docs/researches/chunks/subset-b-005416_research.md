# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-tables.c lines 1-8065

## Scope

This chunk covers the opening 8065 lines of `ipu3-tables.c`. It includes the file header, the `ipu3-tables.h` include, the local `X` macro definition, and the first large exported constant table:

- `imgu_css_bds_configs[IMGU_BDS_CONFIG_LEN]`, from the start of the initializer through line 8065.

The chunk is not a complete translation unit view. It ends inside the table entry for scale factor `32 / (32 + 86) = 0.271186`, specifically partway through that entry's horizontal odd phase array. Complete BDS entries visible in this chunk are scale indices 0 through 85; index 86 and the remaining tables in `ipu3-tables.c` continue after this chunk and must be merged with subsequent chunk research.

## Purpose

This code provides precomputed Bayer Down Scaling (BDS) hardware/programming tables for the Intel IPU3 staging media driver. The table maps a discrete inverse scale factor to:

- horizontal and vertical phase coefficient arrays,
- horizontal and vertical sample pattern bit arrays,
- the sample pattern length programmed into the BDS control registers,
- horizontal and vertical downscale enable flags.

The scale comments show the indexing model: table entry `n` represents scale factor `32 / (32 + n)`. With `IMGU_BDS_GRANULARITY` and `IMGU_BDS_MIN_SF_INV` both equal to 32 in `ipu3-tables.h`, runtime code computes an inverse scale value from effective input height and BDS output height, subtracts 32, and indexes this table. Entry 0 is the identity case (`32 / 32 = 1`) and disables both downscale directions. Entries 1 through 85 in this chunk enable both horizontal and vertical downscaling and carry filter/pattern data for progressively stronger reduction down to `32 / 117 = 0.273504`. The partial entry 86 starts the next reduction step, `32 / 118 = 0.271186`.

## Important APIs, Types, and Data

`imgu_css_bds_configs` is the only exported object that begins in this chunk. Its type is:

- `const struct imgu_css_bds_config imgu_css_bds_configs[IMGU_BDS_CONFIG_LEN]`

`struct imgu_css_bds_config` is declared in `ipu3-tables.h` and contains:

- `struct imgu_abi_bds_phase_arr hor_phase_arr`
- `struct imgu_abi_bds_phase_arr ver_phase_arr`
- `struct imgu_abi_bds_ptrn_arr ptrn_arr`
- `u16 sample_patrn_length`
- `u8 hor_ds_en`
- `u8 ver_ds_en`

The phase arrays use ABI structures from `ipu3-abi.h`. A `struct imgu_abi_bds_phase_arr` has `even` and `odd` arrays, each with `IMGU_ABI_BDS_PHASE_COEFFS_ARRAY_SIZE` entries. That size is 32. Each `struct imgu_abi_bds_phase_entry` has seven signed 8-bit coefficient/control fields (`coeff_min2`, `coeff_min1`, `coeff_0`, `nf`, `coeff_pls1`, `coeff_pls2`, `coeff_pls3`) and a reserved byte. The initializer rows in this chunk are seven-value rows; the omitted reserved byte is zero-initialized by C.

The pattern array type, `struct imgu_abi_bds_ptrn_arr`, has eight 32-bit elements (`IMGU_ABI_BDS_SAMPLE_PATTERN_ARRAY_SIZE`). Many entries initialize fewer than eight words; the rest are zero-initialized. Longer scale periods use more pattern words, for example entries with sample pattern lengths above 200 use up to eight visible 32-bit values.

`X` is defined as `0` with the comment "Don't care value". It is not used in the visible lines 1-8065. It may exist to make later generated tables more readable or to preserve compatibility with generated table sources.

## Table Shape and Visible Content

The visible table entries follow a repeated structure:

1. A comment gives the scale factor as `32 / (32 + n)`.
2. `.hor_phase_arr` provides even and odd phase rows.
3. `.ver_phase_arr` usually mirrors the same rows as `.hor_phase_arr`.
4. `.ptrn_arr` provides BDS sample pattern words.
5. `.sample_patrn_length` gives the active pattern length.
6. `.hor_ds_en` and `.ver_ds_en` enable or disable downscaling.

The identity entry at scale index 0 is compact:

- one all-pass-looking phase row for horizontal even/odd and vertical even/odd,
- `ptrn_arr = { { 0x3 } }`,
- `sample_patrn_length = 2`,
- `hor_ds_en = 0`,
- `ver_ds_en = 0`.

Entries 1 through 85 are downscale entries:

- both enable flags are `1`,
- phase tables contain fixed generated coefficients for the target scale ratio,
- horizontal and vertical phase arrays are identical within each entry in this chunk,
- sample pattern lengths vary with the period of the scale pattern.

The sampled entry starts show the pattern of complete coverage:

- index 1 at line 22: `32 / 33 = 0.969697`, sample pattern length 66,
- index 16 at line 1502: `32 / 48 = 0.666667`, sample pattern length 94,
- index 32 at line 2998: `32 / 64 = 0.5`, sample pattern length 126,
- index 64 at line 6001: `32 / 96 = 0.333333`, sample pattern length 190,
- index 85 at line 7903: `32 / 117 = 0.273504`, sample pattern length 234.

Line 8040 starts index 86, `32 / 118 = 0.271186`. Lines 8041-8057 include its horizontal even phase rows. Lines 8058-8065 include only the first eight horizontal odd phase rows, so the chunk does not contain the rest of that table entry's phase arrays, pattern words, sample length, or enable flags.

## Control Flow

There is no executable control flow in this chunk. The C compiler places the exported `const` table in read-only data, and runtime control flow appears in users of this data.

The primary integration path is `imgu_css_cfg_acc()` in `ipu3-css-params.c`:

1. The driver computes `bds_ds` from the effective input height and BDS output height:
   `effective_height * IMGU_BDS_GRANULARITY / bds_height`.
2. It rejects values below `IMGU_BDS_MIN_SF_INV` or above the table length.
3. It selects `cfg_bds = &imgu_css_bds_configs[bds_ds - IMGU_BDS_MIN_SF_INV]`.
4. It copies `sample_patrn_length`, `hor_ds_en`, `ver_ds_en`, `ptrn_arr`, `hor_phase_arr`, and `ver_phase_arr` into the firmware ABI accumulator parameter block.
5. It sets BDS clipping bounds from `IMGU_BDS_MIN_CLIP_VAL` and `IMGU_BDS_MAX_CLIP_VAL`, uses current frame dimensions for control fields, fills per-stripe BDS data, and sets `acc->bds.enabled` from the enable flags.

The table therefore behaves as a static lookup layer between negotiated stream geometry and packed firmware-visible BDS configuration. The table rows themselves do not branch, allocate, validate, or mutate state.

## State and Persistence Behavior

The chunk defines immutable process/kernel image state:

- `imgu_css_bds_configs` is global `const` data exported through `ipu3-tables.h`.
- No heap memory, locks, reference counts, file state, device state, or persistent storage are modified here.
- All stateful effects happen when runtime configuration code copies a selected table entry into `struct imgu_abi_acc_param`, which is later submitted through the IPU3 CSS/firmware parameter path.

Because the table is fixed at build time, changing any values is a driver behavior change for every runtime stream configuration that maps to the affected scale index. There is no runtime calibration or fallback logic in this chunk.

## Dependencies and Integration Points

Direct dependencies:

- `ipu3-tables.h` supplies `IMGU_BDS_CONFIG_LEN`, `IMGU_BDS_GRANULARITY`, `IMGU_BDS_MIN_SF_INV`, and `struct imgu_css_bds_config`.
- `ipu3-tables.h` includes `ipu3-abi.h`, which supplies the packed BDS ABI structures used by the table.
- Linux integer typedefs such as `u8`, `u16`, `s8`, and `u32` are pulled in through the kernel header chain used by the IPU3 driver.

Primary consumers:

- `ipu3-css-params.c` uses `imgu_css_bds_configs` while building accelerator parameters in `imgu_css_cfg_acc()`.
- The packed `struct imgu_abi_bds_config` ultimately represents firmware-visible state, so the exact field widths and array sizes in `ipu3-abi.h` define what each table value means to hardware/firmware.

Geometry integration:

- The index is based on output BDS height, not width, in the visible `imgu_css_cfg_acc()` path.
- The selected row is copied to both horizontal and vertical BDS configuration.
- Stripe configuration is computed separately, but depends on the same stream rectangles and the BDS output size.

## Risks and Edge Cases

- The chunk boundary is mid-entry. A merger must not treat lines 1-8065 as a syntactically complete `imgu_css_bds_configs` initializer; entry 86 and the closing table syntax continue in a later chunk.
- The table relies on exact correspondence between `IMGU_BDS_CONFIG_LEN` and the number of initialized entries. The complete file has 97 BDS entries for indices 0 through 96; this chunk only contains complete entries 0 through 85 plus a partial 86.
- `imgu_css_cfg_acc()` indexes by `bds_ds - IMGU_BDS_MIN_SF_INV`. If geometry calculation changes from truncating integer division to rounding, the selected coefficient table can change for borderline dimensions.
- Entry 0 disables BDS. Any accidental enable flag change in the identity entry would cause the firmware path to treat a no-scale case as active BDS.
- Entries 1 through 85 have both horizontal and vertical enable flags set. If a future use case needs asymmetric horizontal-only or vertical-only BDS, this table's combined row model is not sufficient by itself.
- Phase rows are dense generated constants with no local invariants checked in C. Coefficient typos, sign errors, or row ordering mistakes will compile cleanly but can degrade image quality or violate firmware expectations.
- The ABI field widths constrain values. `sample_patrn_length` is copied into a 9-bit bitfield, and phase coefficients are signed 8-bit fields. Current visible values fit these ranges, but generated updates should validate the full table mechanically.
- Several array initializers rely on implicit zero-fill for unused phase entries and pattern words. This is valid C, but mechanical rewrites that expand, reorder, or transform initializers must preserve zero-fill semantics.
- Horizontal and vertical phase arrays are identical in this visible chunk. If a generator or patch changes only one direction, reviewers should confirm that asymmetry is intentional.
- The local `X` macro is unused in the chunk. If later chunks use it for "don't care" table cells, replacing it or removing it without checking the whole file can alter readability or compile behavior.

## Test and Validation Signals

- Build validation should compile the IPU3 staging driver after any table or ABI changes. A missing brace, wrong scalar type, or array-size mismatch in this generated-style initializer should fail at compile time.
- Add or run a table-shape check that counts `IMGU_BDS_CONFIG_LEN` entries and confirms the scale comments cover indices 0 through 96 in order in the full file.
- Validate that every complete BDS entry has `sample_patrn_length` within the 9-bit ABI limit and pattern word usage within `IMGU_ABI_BDS_SAMPLE_PATTERN_ARRAY_SIZE`.
- Validate that each visible phase coefficient fits `s8`, and that every `nf` value is within the expected hardware range used by the generated coefficient rows.
- Runtime tests should exercise BDS output heights that select representative entries: identity index 0, moderate downscale around indices 16 and 32, stronger downscale around indices 64 and 85, and boundary cases near the handoff to later chunks.
- Stream configuration tests should confirm `imgu_css_cfg_acc()` rejects out-of-range `bds_ds` values and selects the expected table index for valid effective/BDS height pairs.
- Image-quality or golden-frame tests should compare output for known Bayer inputs at several BDS ratios. These are the only practical signals for coefficient transposition, sign, or pattern mistakes that still compile.
- Stripe tests should include one-stripe and two-stripe modes, since `imgu_css_cfg_acc()` copies the selected BDS row before filling per-stripe data and the same scale geometry affects stripe width/offset calculations.
- Firmware parameter dump tests can verify that selected rows are copied intact into `acc->bds.hor.*` and `acc->bds.ver.*`, including enable flags, pattern arrays, and phase arrays.
