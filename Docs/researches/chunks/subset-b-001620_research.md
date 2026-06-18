# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 24909-27383

## Purpose

This chunk is part of the generated AMD DCN 2.0 register shift/mask header. It contains preprocessor constants only; there are no C functions, structs, storage objects, branches, or executable algorithms in this source slice. Each hardware register field is exposed as a bit-position macro ending in `__SHIFT` and a positioned bit mask ending in `_MASK`.

The covered hardware area is the MPC MPCC output gamma block (`MPCC_OGAM`) for DCN 2.0. `MPCC` is the multi-plane compositor component, and this chunk describes the programmable output/blend gamma LUT registers attached to MPCC instances:

- The chunk starts in the tail of `MPCC_OGAM0`, covering `MPCC_OGAM_RAMB_REGION_30_31` and `MPCC_OGAM_RAMB_REGION_32_33`.
- It then defines complete `dce_dc_mpc_mpcc_ogam1_dispdec` through `dce_dc_mpc_mpcc_ogam5_dispdec` address blocks.
- It begins `dce_dc_mpc_mpcc_ogam6_dispdec` and continues through `MPCC_OGAM6_MPCC_OGAM_RAMB_REGION_18_19` within the requested line range.

Although the repository path is under a `ceph-client` source mirror, this source chunk is AMD GPU display register metadata. It does not implement Ceph filesystem behavior, distributed storage state, network protocol handling, or filesystem persistence.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The public interface is the macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: low bit number for a field.
- `<REGISTER>__<FIELD>_MASK`: already-positioned mask for the same field.

The chunk contains 2,091 `#define` entries: 1,047 shift constants and 1,044 mask constants. The small count mismatch is because the selected range begins and ends in the middle of repeated register groups, so some paired definitions are outside the chunk.

Important register families are:

- `MPCC_OGAMn_MPCC_OGAM_MODE`: output gamma mode selection. Local DCN20 code writes this field with `0` for bypass and `1` or `2` for RAM A/RAM B selection.
- `MPCC_OGAMn_MPCC_OGAM_LUT_INDEX`: 9-bit LUT index field (`0x000001FF`) used to set the host programming cursor before writing LUT data.
- `MPCC_OGAMn_MPCC_OGAM_LUT_DATA`: 19-bit LUT data field (`0x0007FFFF`) used for red/green/blue and delta entries in the PWL LUT stream.
- `MPCC_OGAMn_MPCC_OGAM_LUT_RAM_CONTROL`: host programming control with `MPCC_OGAM_LUT_WRITE_EN_MASK`, `MPCC_OGAM_LUT_RAM_SEL`, and `MPCC_OGAM_CONFIG_STATUS`. The write-enable mask occupies bits 0..2, RAM select is bit 3, and config status occupies bits 4..5.
- `MPCC_OGAMn_MPCC_OGAM_RAMA_*` and `MPCC_OGAMn_MPCC_OGAM_RAMB_*`: duplicate RAM-bank register sets for double-buffered LUT programming.
- `*_START_CNTL_[BGR]`: per-channel exponential-region start value and start segment. Start is 18 bits (`0x0003FFFF`), and start segment is 7 bits at bit 20 (`0x07F00000`).
- `*_SLOPE_CNTL_[BGR]`: per-channel 18-bit linear slope.
- `*_END_CNTL1_[BGR]`: per-channel 16-bit region end value.
- `*_END_CNTL2_[BGR]`: per-channel 16-bit end slope and 16-bit end base packed in one register.
- `*_REGION_<even>_<odd>`: packed descriptors for PWL regions 0 through 33. Each register carries two region descriptors: a 9-bit LUT offset and a 3-bit segment-count code for each region, at shifts `0`, `0xc`, `0x10`, and `0x1c`.

The full repeated instances in this chunk are `MPCC_OGAM1` through `MPCC_OGAM5`. For each of those instances, both RAM A and RAM B have per-channel start/slope/end registers and 17 packed region registers (`REGION_0_1` through `REGION_32_33`), covering 34 regions. `MPCC_OGAM6` is partial in this chunk, and `MPCC_OGAM0` is only represented by the tail of RAM B.

## Control Flow

This header chunk has no runtime control flow. Runtime behavior is created by Display Core code that combines these generated masks and shifts with matching register addresses from `dcn_2_0_0_offset.h`.

The local DCN20 MPC integration follows this pattern:

1. `display/dc/resource/dcn20/dcn20_resource.c` includes `dcn/dcn_2_0_0_offset.h` and `dcn/dcn_2_0_0_sh_mask.h` while constructing DCN 2.0 resources.
2. `display/dc/mpc/dcn20/dcn20_mpc.h` uses `SRII(MPCC_OGAM_*, MPCC_OGAM, inst)` to build per-instance register-address arrays and `SF(MPCC_OGAM0_*, field, mask_sh)` to populate the shared shift/mask tables.
3. `display/dc/mpc/dcn20/dcn20_mpc.c` maps the generated fields into `struct xfer_func_reg` in `mpc2_ogam_get_reg_field()`.
4. `mpc2_set_output_gamma()` chooses the next LUT bank, powers the OGAM LUT memory, configures the host RAM select, programs RAM A or RAM B region registers, streams LUT entries through `MPCC_OGAM_LUT_DATA`, and finally writes `MPCC_OGAM_MODE` to make the selected bank active.
5. `mpc2_read_mpcc_state()` reads `MPCC_OGAM_CONFIG_STATUS` through `MPCC_OGAM_LUT_RAM_CONTROL` into the MPCC state snapshot.

The implied hardware sequencing is important even though this file only contains constants:

- The driver alternates RAM A and RAM B so a new output gamma curve can be programmed without overwriting the currently active bank.
- `MPCC_OGAM_LUT_RAM_CONTROL` selects the host-visible RAM and enables per-channel writes.
- `MPCC_OGAM_LUT_INDEX` resets the LUT write cursor before the PWL data stream.
- Region start/slope/end registers describe the PWL segmentation, while `MPCC_OGAM_LUT_DATA` carries the actual RGB and delta entries.
- `MPCC_OGAM_MODE` switches the hardware between bypass, RAM A, and RAM B after programming is complete.

## State And Persistence Behavior

The header itself stores no state and persists nothing. The state represented by these macros lives in GPU display registers and in caller-maintained Display Core objects.

Hardware state represented in this chunk includes:

- Active MPCC output gamma mode for each covered MPCC instance.
- Host programming cursor state through `MPCC_OGAM_LUT_INDEX`.
- Host-write control, selected RAM bank, write-enable channel mask, and hardware config-status readback through `MPCC_OGAM_LUT_RAM_CONTROL`.
- RAM A and RAM B PWL metadata: per-channel region starts, start segments, linear slopes, region ends, end slopes, end bases, region LUT offsets, and segment-count codes.
- RAM A and RAM B LUT entry contents written through `MPCC_OGAM_LUT_DATA`.

Persistence is hardware-scoped:

- Programmed RAM A/RAM B LUT contents and PWL region metadata persist until overwritten, reset, or lost through display block power/reset.
- `MPCC_OGAM_MODE` persists as the active bypass/RAM-bank selection until changed by the driver or reset.
- `MPCC_OGAM_CONFIG_STATUS` is readback/status state, not durable software state.
- The source file gives bit layout only. It does not encode reset values, legal enum meanings beyond field widths, access type, bank latch timing, or power-domain behavior.

Display Core mirrors part of this state in higher-level structures. For example, `dc.h` has MPCC OGAM snapshot fields for mode, selected bank, and PWL disable state, while `dcn20_mpc.c` reads the hardware config status into `struct mpcc_state`.

## Dependencies And Integration Points

This chunk depends on the generated DCN 2.0 register contract. The constants are meaningful only with sibling generated headers and Display Core register helpers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h` provides matching `MPCC_OGAMn_*` register addresses and base-index metadata.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/navi10_enum.h` provides related enum values for `MPCC_OGAM_LUT_RAM_SEL` and `MPCC_OGAM_MODE`.
- `display/dc/mpc/dcn20/dcn20_mpc.h` binds these generated field names into MPC register, mask, and shift tables.
- `display/dc/mpc/dcn20/dcn20_mpc.c` is the primary local runtime consumer for DCN20 output gamma programming.
- `display/dc/resource/dcn20/dcn20_resource.c` declares DCN2 color capabilities, including programmable output gamma RAM support and the absence of OGAM ROM curves on DCN2.
- `display/dc/hwss/dcn20/dcn20_hwseq.c` coordinates higher-level color programming and notes that OGAM is programmed only for the top pipe.
- `display/dc/core/dc.c` captures or synthesizes MPCC OGAM state for active pipes in broader display state snapshots.

Other files include `dcn_2_0_0_sh_mask.h` for DCN20 interrupt, GPIO, DMUB, clock-manager, and GMC code, but the OGAM fields in this chunk are specifically consumed by the MPC/display color-management path.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. These are raw preprocessor constants; a wrong shift, wrong mask, stale generated value, or mismatch against the offset header can compile successfully while programming the wrong display bits.

Important risk areas in this chunk are:

- Instance repetition. `MPCC_OGAM1` through `MPCC_OGAM6` repeat nearly identical fields. A register-address prefix or MPCC index mismatch can program the wrong compositor pipe with no type-system protection.
- Chunk boundaries. The slice starts after most of `MPCC_OGAM0` and ends before the rest of `MPCC_OGAM6`, so final per-file analysis must merge neighboring chunks before describing all MPCC OGAM instances.
- Bank switching. Runtime code depends on correctly selecting inactive RAM A or RAM B, programming it fully, and then changing `MPCC_OGAM_MODE`. Selecting the active bank or switching early can expose partially programmed gamma curves.
- LUT cursor and write-mask handling. `MPCC_OGAM_LUT_INDEX`, `MPCC_OGAM_LUT_WRITE_EN_MASK`, and `MPCC_OGAM_LUT_DATA` form a write stream. Wrong index reset, channel mask, or data width can scramble red/green/blue entries or deltas.
- PWL region consistency. Region start, segment count, LUT offset, slope, end, end slope, and end base fields must match the transfer-function generator's expectations. Bad values can produce banding, clipping, color shifts, or visibly discontinuous gamma ramps.
- Field width truncation. LUT offsets are 9 bits, LUT data is 19 bits, starts/slopes are 18 bits, ends and bases are 16 bits, and region segment counts are 3 bits. Callers must clamp/encode values before register writes.
- Status interpretation. `MPCC_OGAM_CONFIG_STATUS` is read from the same control register used for write enable and RAM selection. Generic read-modify-write sequences must avoid disturbing write-enable or selected-bank fields while polling status.
- Power sequencing. DCN20 code powers OGAM LUT memory via `MPCC_MEM_PWR_CTRL` before programming. Programming while the block is powered down or before status is stable can lose writes or make polling unreliable.
- Hardware workaround interaction. `dcn20_mpc.c` has a DEDCN20-305 workaround around `MPCC_OGAM_MODE`; mode transitions can depend on OTG/update-lock conditions outside this header.

## Test Signals

Useful validation signals for code that consumes this chunk include:

- Build coverage for DCN20 display code that includes `dcn_2_0_0_sh_mask.h` and instantiates `dcn20_mpc` resources.
- Static generated-header checks that every field has aligned shift/mask values, masks are positioned consistently, and repeated `MPCC_OGAM1-6` families match the authoritative register database.
- Diff checks against `dcn_2_0_0_offset.h` to ensure each `MPCC_OGAMn_*` field family has the expected matching register address.
- Unit or emulation coverage for `mpc2_set_output_gamma()` exercising bypass, RAM A programming, RAM B programming, bank alternation, and NULL transfer-function paths.
- Tests or hardware validation that `MPCC_OGAM_CONFIG_STATUS` reports bypass, RAM A, and RAM B consistently after mode changes.
- Color-management tests with identity, sRGB-like, PQ/HLG-like, and custom PWL curves to catch broken region descriptors, LUT offsets, segment counts, slopes, or data widths.
- Visual validation for banding, clipping, channel swaps, and discontinuities after output gamma changes on active pipes.
- Multi-pipe and multi-plane tests verifying OGAM is programmed on the intended top pipe/MPCC instance and does not affect unrelated pipes.
- Suspend/resume, display reset, and runtime power-management tests that confirm OGAM LUT contents are restored or safely reprogrammed after power loss.
- Regression coverage for DEDCN20-305 workaround paths and update-lock sequencing around `MPCC_OGAM_MODE` changes.

## Cross-Chunk Notes

This chunk is a middle slice of the `MPCC_OGAM` register area. The full per-file report should merge adjacent chunks to cover the beginning of `MPCC_OGAM0`, the remaining `MPCC_OGAM6` definitions after line 27383, and any subsequent MPCC OGAM or MPC color-register families.
