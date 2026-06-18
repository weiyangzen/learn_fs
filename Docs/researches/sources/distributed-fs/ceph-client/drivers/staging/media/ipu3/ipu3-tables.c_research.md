# Research: sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-tables.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-005416`: lines 1-8065, `Docs/researches/chunks/subset-b-005416_research.md`
- `subset-b-005417`: lines 8066-9609, `Docs/researches/chunks/subset-b-005417_research.md`

## Chunk Research

### subset-b-005416: lines 1-8065

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

### subset-b-005417: lines 8066-9609

# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-tables.c lines 8066-9609

## Scope

This chunk covers the final part of Intel IPU3 CSS static table definitions in `ipu3-tables.c`. The range starts inside the Bayer Down Scaler (`imgu_css_bds_configs`) entry for scale factor `32 / (32 + 86)` and continues through the final BDS entries for scale factors `32 / (32 + 87)` through `32 / (32 + 96)`. It then defines the exported default tables used by the IPU3 CSS parameter builder:

- Output-system scaler FIR kernels: `imgu_css_downscale_4taps` and `imgu_css_downscale_2taps`.
- Geometric Distortion Correction LUT: `imgu_css_gdc_lut`.
- XNR3 vector-memory defaults: `imgu_css_xnr3_vmem_defaults`.
- Accelerator-cluster defaults for BNR, demosaic, CCM, gamma, CSC, CDS, shading, IEFD, YDS, CHNR, Y edge enhancement/noise reduction, TCC LUTs, ANR, AWB filter response, AE, AE CCM, AF, and AWB.

The chunk contains constant data only. There are no functions, dynamic allocations, locks, or direct control-flow statements in this source range.

## Purpose

`ipu3-tables.c` is the static tuning and hardware-default table file for the IPU3 image-processing pipeline. The data in this chunk gives the driver known-good initial values for fixed-function ISP blocks when userspace has not provided a corresponding `ipu3_uapi_*` parameter section and no previous parameter set is available.

The BDS entries provide precomputed phase arrays and sample patterns for the strongest predefined Bayer downscale ratios in the table. With `IMGU_BDS_GRANULARITY` set to 32 and `IMGU_BDS_CONFIG_LEN` set to 97, `imgu_css_bds_configs[n]` represents scale factor `32 / (32 + n)`. This chunk therefore covers BDS indexes 86 through 96, equivalent to inverse scale values 118 through 128 and output scale factors about 0.271 down to 0.25. These entries are selected later from the effective input height and requested BDS output height.

The remaining constants are defaults for OSYS scaling, geometric correction, XNR/ANR denoise behavior, color correction and conversion, gamma, chroma and luma denoise, statistics grids, and 3A setup. They let the driver synthesize a complete ACC parameter block even when userspace only supplies a subset of tuning controls.

## Important APIs, Types, and Data

The declarations are exported through `ipu3-tables.h`, which defines the local table shapes and constants:

- `struct imgu_css_bds_config` contains horizontal and vertical BDS phase arrays, a shared BDS pattern array, sample-pattern length, and horizontal/vertical downscale-enable bits.
- `IMGU_BDS_GRANULARITY`, `IMGU_BDS_MIN_SF_INV`, and `IMGU_BDS_CONFIG_LEN` define the BDS scale-index contract.
- `IMGU_SCALER_DOWNSCALE_4TAPS_LEN`, `IMGU_SCALER_DOWNSCALE_2TAPS_LEN`, and `IMGU_SCALER_FP` define the OSYS scaler kernel sizes and fixed-point scale where `BIT(31)` represents 1.0.
- `struct imgu_css_xnr3_vmem_defaults` holds 16-entry `x`, `a`, `b`, and `c` default curves for XNR3 vector memory.
- `IMGU_GDC_LUT_UNIT` and `IMGU_GDC_LUT_LEN` describe the 4 by 256 GDC LUT layout.

The BDS section uses `struct imgu_abi_bds_phase_arr` and `struct imgu_abi_bds_ptrn_arr` from `ipu3-abi.h`. Each BDS config has mirrored horizontal and vertical phase arrays with `.even` and `.odd` subarrays plus `.ptrn_arr`, `.sample_patrn_length`, `.hor_ds_en`, and `.ver_ds_en`.

The ACC defaults use UAPI and ABI structures from `include/uapi/intel-ipu3.h` and `ipu3-abi.h`, including:

- `struct ipu3_uapi_bnr_static_config` for Bayer noise reduction static settings.
- `struct ipu3_uapi_dm_config`, `ipu3_uapi_ccm_mat_config`, `ipu3_uapi_gamma_corr_lut`, `ipu3_uapi_csc_mat_config`, and `ipu3_uapi_cds_params` for demosaic and color pipeline defaults.
- `struct ipu3_uapi_shd_config_static` for lens shading grid and black-level defaults.
- `struct ipu3_uapi_yuvp1_iefd_config`, `ipu3_uapi_yuvp1_yds_config`, `ipu3_uapi_yuvp1_chnr_config`, and `ipu3_uapi_yuvp1_y_ee_nr_config` for YUVP1 enhancement, downscale, chroma denoise, and edge/noise behavior.
- `struct ipu3_uapi_yuvp2_tcc_gain_pcwl_lut_static_config` and `ipu3_uapi_yuvp2_tcc_r_sqr_lut_static_config` for total color correction LUT defaults.
- `struct imgu_abi_anr_config` for advanced noise reduction transform and stitch defaults.
- `struct ipu3_uapi_awb_fr_config_s`, `ipu3_uapi_ae_grid_config`, `ipu3_uapi_ae_ccm`, `ipu3_uapi_af_config_s`, and `ipu3_uapi_awb_config_s` for statistics and 3A defaults.

The macro `X` is defined earlier in the file as `0` and marks hardware fields documented as don't-care or reserved in many initializer rows.

## Control Flow and Use Sites

This chunk has no local control flow, but the constants are consumed by `ipu3-css-params.c` and `ipu3-css.c`.

OSYS scaler setup calls `imgu_css_scaler_setup_lut()` with `imgu_css_downscale_4taps` for luma and `imgu_css_downscale_2taps` for chroma. The scaler calculation retries with a small phase-step correction until the generated output dimensions meet the target and height-alignment constraints. These arrays therefore feed runtime coefficient generation rather than being copied verbatim as a whole hardware block.

ACC parameter construction follows a repeated user/old/default pattern. For each ACC section, `ipu3-css-params.c` first checks the `use->acc_*` flag to accept userspace values, otherwise preserves the old value if an old parameter block exists, otherwise copies the default from this file. Examples include `imgu_css_bnr_defaults`, `imgu_css_dm_defaults`, `imgu_css_ccm_defaults`, `imgu_css_gamma_lut`, `imgu_css_csc_defaults`, `imgu_css_cds_defaults`, `imgu_css_shd_defaults`, `imgu_css_iefd_defaults`, `imgu_css_yds_defaults`, `imgu_css_chnr_defaults`, `imgu_css_y_ee_nr_defaults`, the TCC LUTs, `imgu_css_anr_defaults`, `imgu_css_awb_fr_defaults`, `imgu_css_ae_grid_defaults`, `imgu_css_ae_ccm_defaults`, `imgu_css_af_defaults`, and `imgu_css_awb_defaults`.

The BDS config is selected with:

```c
bds_ds = effective_height * IMGU_BDS_GRANULARITY / bds_height;
cfg_bds = &imgu_css_bds_configs[bds_ds - IMGU_BDS_MIN_SF_INV];
```

The selected table entry is copied into horizontal and vertical BDS ABI fields, including sample pattern length, enable bits, pattern arrays, and phase arrays. The code then computes per-stripe BDS data and marks `acc->bds.enabled` from `hor_ds_en || ver_ds_en`.

The GDC LUT is programmed directly in `ipu3-css.c` during CSS initialization. The driver iterates over 256 entries, masks each of the four signed tables with `IMGU_GDC_LUT_MASK`, packs table pairs into two 32-bit writes, and writes them under `IMGU_REG_GDC_LUT_BASE`.

XNR3 VMEM setup in `ipu3-css-params.c` copies the 16-entry XNR defaults into the larger vector-memory parameter layout using modulo indexing. TNR3 VMEM is nearby but generated separately with sigma defaults.

## State and Persistence Behavior

The data in this chunk is immutable compiled-in driver state. It has static storage duration and is exported as `const`, so it is shared across devices and streams and should not be modified at runtime.

Persistent hardware or per-frame state is created only when consumers copy these defaults into parameter buffers or registers:

- ACC defaults become part of the per-pipe CSS parameter buffer sent to firmware/hardware. Later parameter submissions may preserve previous values through the `acc_old` path rather than copying these defaults again.
- BDS table data becomes per-frame/per-pipe BDS ABI state selected from current effective and BDS rectangle dimensions.
- GDC LUT values are written into hardware registers during CSS initialization and remain hardware state until reset or reprogramming.
- XNR3 VMEM defaults become vector-memory parameter data when the XNR3 VMEM section is built.

Several consumers add runtime-derived fields after copying defaults. BNR gets `column_size` from TNR frame width, demosaic gets `frame_width`, shading derives grid slice and operation data, ANR gets enable bits and frame dimensions and clamps `xreset`/`yreset`, AWB/AF/AE grids derive end coordinates and stripe-specific grids, and TCC defaults are combined with generated identity MACC and inverse-Y tables.

## Dependencies and Integration Points

This chunk depends on `ipu3-tables.h`, `ipu3-abi.h`, and the packed IPU3 UAPI structures in `include/uapi/intel-ipu3.h`. Correctness depends on those structures matching the firmware ABI and hardware register packing. Many fields are bitfields or fixed-width packed structures, so positional initializers must stay aligned with the exact UAPI layout.

Important integration points are:

- `ipu3-css-params.c`, which builds CSS/ACC parameter memory and selects between userspace, old, and default values.
- `ipu3-css.c`, which writes the GDC LUT into hardware registers.
- The V4L2 userspace parameter ABI, especially `struct ipu3_uapi_acc_param` and `struct ipu3_uapi_flags`, whose `acc_*`, `tnr3_*`, and `xnr3_*` flags determine whether defaults are used.
- IPU3 firmware/ABI structures under `ipu3-abi.h`, particularly BDS phase/pattern arrays and ANR structures.
- Pipeline rectangle calculation, stripe splitting, and statistics-grid helpers in `ipu3-css-params.c`, which adapt static defaults to frame geometry.

## Risks

- The BDS section begins mid-entry in this chunk. A complete review of the `32 / (32 + 86)` entry requires the preceding chunk; this chunk covers its tail and all later entries through index 96.
- BDS table indexing is geometry-derived. Any mismatch between `IMGU_BDS_CONFIG_LEN`, the number of initializers, and `bds_ds - IMGU_BDS_MIN_SF_INV` can produce invalid scale selection or `-EINVAL`.
- The BDS phase and pattern tables are dense hand/generated numeric data. Single-value drift can cause image-quality issues, aliasing, incorrect sample selection, or hardware-programming failures that are hard to diagnose from normal control-flow tests.
- The scaler kernels use signed fixed-point constants generated from floating-point expressions. Changes to `IMGU_SCALER_FP`, array length, tap count assumptions, or compiler conversion behavior would affect luma/chroma scaler coefficients.
- The GDC LUT is packed into hardware registers after masking signed 16-bit values. Incorrect LUT dimensions, sign handling, or mask width can distort geometric correction globally.
- Positional initializers for packed UAPI structures are fragile. Adding, removing, or reordering fields in `intel-ipu3.h` without converting these defaults to named initializers can silently assign values to the wrong hardware fields.
- Defaults are only a baseline. Runtime code must still fill frame-dependent fields such as BNR column size, DM frame width, SHD operations, ANR dimensions, and AE/AWB/AF stripe grids. Testing only the constants is not enough.
- Statistics grid defaults set fixed 16 by 16 regions and enable bits. Bad stripe splitting or grid end calculation around these defaults can disable the wrong stripe or produce invalid statistic memory layout.

## Test and Validation Signals

Useful validation signals for this chunk include:

- Build coverage for `drivers/staging/media/ipu3`, including `ipu3-tables.c`, `ipu3-css-params.c`, and `ipu3-css.c`, to catch structure-size and symbol mismatches.
- Static checks that `ARRAY_SIZE(imgu_css_bds_configs) == IMGU_BDS_CONFIG_LEN`, `ARRAY_SIZE(imgu_css_downscale_4taps) == IMGU_SCALER_DOWNSCALE_4TAPS_LEN`, `ARRAY_SIZE(imgu_css_downscale_2taps) == IMGU_SCALER_DOWNSCALE_2TAPS_LEN`, and the GDC LUT dimensions match `IMGU_GDC_LUT_UNIT` by `IMGU_GDC_LUT_LEN`.
- Pipeline tests that request BDS ratios near 0.271 and 0.25 so indexes 86 through 96 are selected and copied into ACC BDS fields.
- Image-quality or conformance tests for OSYS luma/chroma downscaling, especially dimensions that exercise the scaler phase-step correction loop.
- Hardware initialization tests that read back or observe GDC LUT programming and verify no CSS initialization error is reported.
- Parameter-submission tests for the user/old/default paths: submit no ACC parameters to force these defaults, submit partial `use->acc_*` flags to verify old/default preservation, and submit explicit userspace values to verify defaults are bypassed.
- 3A statistics tests for AWB filter response, AE, AF, and AWB grids across one-stripe and two-stripe layouts, checking grid enable bits, end coordinates, and height-per-slice derivation.
- Runtime image tests with gamma, CCM/CSC, BNR, ANR, CHNR, Y edge enhancement/noise reduction, and TCC defaults enabled to catch visible regressions from table corruption.
