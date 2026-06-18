# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4.c

## Purpose

This file implements the GFX 9.4 RAS hardware operations for Arcturus-like GC 9.4.1 devices. It enumerates EDC counter registers, maps register bitfields to human-readable GFX sub-block names, queries and resets SRAM and UTC error counters, and reports fatal EA error status before reset.

## Important APIs, types, and functions

- `gfx_v9_4_edc_counter_regs[]`: table of GC EDC counter registers with per-register shader-engine count and instance count.
- `gfx_v9_4_ras_fields[]`: maps each EDC register to SEC and DED masks/shifts and diagnostic names for CPC, CPF, GDS, SPI, SQ, SQC, TA, TCA, TCC, TCI, TCP, TD, EA, GCEA, and RLC memories.
- `gfx_v9_4_select_se_sh()`: local GRBM index helper for selecting SE/SH/instance before indexed register reads.
- `gfx_v9_4_query_utc_edc_status()`: walks UTC/VML2/UTCL2/ATC indexed ECC counters and accumulates corrected and uncorrected counts into `struct ras_err_data`.
- `gfx_v9_4_query_ras_error_count()`: main `.query_ras_error_count` implementation. It scans SRAM EDC counters under `adev->grbm_idx_mutex`, restores broadcast selection, then queries UTC counters.
- `gfx_v9_4_reset_ras_error_count()`: clears counters mostly by reading them, plus writes UTC/ATC index and control registers to reset indexed counter state.
- `gfx_v9_4_query_ras_error_status()`: reads `mmGCEA_ERR_STATUS` across EA instances and logs SDP read/write response or parity errors.
- `gfx_v9_4_ras_ops` and `gfx_v9_4_ras`: exported RAS ops attached by `gfx_v9_0.c` for matching ASICs.

## Control flow

RAS query entry first checks `amdgpu_ras_is_supported(adev, AMDGPU_RAS_BLOCK__GFX)`. Count query zeroes caller-visible counts, iterates every table row, selects each SE and instance, reads the register, and if non-zero decodes every matching field entry. After accumulating SRAM counters it restores GRBM broadcast selection and calls the UTC indexed-counter query. Reset follows the same table scan but reads counters for clear-on-read behavior, then walks every UTC indexed instance to clear those counters as well. Error-status query is separate and only reports EA fatal-status bits.

## State and persistence behavior

This code reads and clears persistent hardware error counters. Querying SRAM counters in `gfx_v9_4_query_ras_error_count()` appears read-only, while reset explicitly consumes counters through read side effects. UTC reset writes ECC index and control registers, walks indexed memories, then restores index registers to `255`. The file mutates global hardware index state and therefore protects GRBM selection with `adev->grbm_idx_mutex`.

## Dependencies and integration points

The file depends on GC 9.4.1 register offset and mask headers, SOC15 register access macros, `amdgpu_ras` infrastructure, `struct ras_err_data`, and AMDGPU device logging. `gfx_v9_0.c` chooses `gfx_v9_4_ras` for relevant devices, so these callbacks run through the generic AMDGPU RAS block interface rather than direct external calls.

## Risks

The counter tables encode topology assumptions such as eight SQ/SQC shader engines, 16 TCC instances, and 72 TCI instances. A wrong count can miss counters or select invalid instances. Several UTC setup lines write `mmATC_L2_CACHE_2M_DSM_CNTL` while preparing 4K state, which should be reviewed against hardware docs because it may be intentional aliasing or a copy/paste hazard. Since query and reset paths clear some indexed counters, diagnostics can be lost if called unexpectedly.

## Test signals

Good signals are RAS injection tests that produce expected CE/UE totals, dmesg lines naming the correct GFX sub-block and instance, no lockdep warnings around GRBM index access, reset tests showing counters return to zero, and fatal EA error paths logging status before GPU reset.
