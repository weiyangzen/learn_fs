# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_sh_mask.h lines 1-2364

## Purpose

This chunk is the opening portion of the generated AMDGPU MMHUB 1.7 register field mask header. It provides preprocessor constants for MMHUB DAGB decoder register fields: every field is represented by a `<REGISTER>__<FIELD>__SHIFT` macro and a matching `<REGISTER>__<FIELD>_MASK` macro. The companion `mmhub_1_7_offset.h` file provides the register addresses; this file provides the bit layout needed to build, decode, and read-modify-write 32-bit register values.

The range covers the license/header guard, all of `addressBlock: mmhub_dagb_dagbdec0`, and the start of `addressBlock: mmhub_dagb_dagbdec1` through `DAGB1_RD_VC1_CNTL`. The definitions are hardware contract data for the MMHUB memory path, not executable driver logic.

## Major Register Families Covered

- `DAGB0_RDCLI0` through `DAGB0_RDCLI15`: per-read-client routing and throttling fields. Each client has `VIRT_CHAN`, `CHECK_TLB_CREDIT`, `URG_HIGH`, `URG_LOW`, `MAX_BW_ENABLE`, `MAX_BW`, `MIN_BW_ENABLE`, `MIN_BW`, `OSD_LIMITER_ENABLE`, and `MAX_OSD` fields.
- `DAGB0_RD_CNTL`, `DAGB0_RD_GMI_CNTL`, and `DAGB0_RD_ADDR_DAGB`: global read-side controls for clock/window sizing, IO level overrides, virtual-channel sharing, GMI credits/level/burst/timer fields, and address DAGB enable/jump/self-init/identity mode.
- `DAGB0_RD_OUTPUT_DAGB_*`, `DAGB0_RD_ADDR_DAGB_*`, and `DAGB0_RD_VC0_CNTL` through `DAGB0_RD_VC7_CNTL`: read output and address arbitration controls. These define per-VC max burst/lazy timer nibbles, per-client burst/timer tables for clients 0-15, and per-VC storage/EA credits plus max/min bandwidth and outstanding-request limits.
- `DAGB0_RD_CNTL_MISC`, `DAGB0_RD_TLB_CREDIT`, `DAGB0_RD_RDRET_CREDIT_CNTL`, and `DAGB0_RD_RDRET_CREDIT_CNTL2`: read-side pool credit, IO/EA credit, UTCL2 client ID, return FIFO credit, per-TLB credit, and read-return credit controls.
- `DAGB0_RDCLI_*_PENDING`: read-client status bitmaps for `ASK`, `GO`, `GBLSEND`, `TLB`, `OARB`, and `OSD` pending states.
- `DAGB0_WRCLI0` through `DAGB0_WRCLI15`: write-client mirrors of the read-client routing and throttling fields with the same virtual-channel, TLB-credit, urgency, bandwidth, and OSD-limit layout.
- `DAGB0_WR_CNTL`, `DAGB0_WR_GMI_CNTL`, `DAGB0_WR_ADDR_DAGB`, `DAGB0_WR_DATA_DAGB`, and related max-burst/lazy-timer tables: write-side global controls for address and data DAGB arbitration, per-client burst/timer limits, and per-VC write credits.
- `DAGB0_WR_CNTL_MISC`, `DAGB0_WR_TLB_CREDIT`, `DAGB0_WR_DATA_CREDIT`, `DAGB0_WR_MISC_CREDIT`, `DAGB0_WR_OSD_CREDIT_CNTL*`, and `DAGB0_WR_ATOMIC_FIFO_CREDIT_CNTL1`: write-side pool, TLB, data burst, OSD, deadlock-VC, and atomic FIFO credit fields.
- `DAGB0_WRCLI_GPU_SNOOP_OVERRIDE`, `DAGB0_WRCLI_GPU_SNOOP_OVERRIDE_VALUE`, and `DAGB0_WRCLI_*_PENDING`: write-client snoop override bitmaps and pending-state bitmaps for write request progress, including data-bus ask/go pending states.
- `DAGB0_DAGB_DLY`, `DAGB0_CNTL_MISC`, and `DAGB0_CNTL_MISC2`: top-level DAGB delay, EA virtual-channel remap, bandwidth initialization/gap timing, urgent boost/halt, clock-gating disable, busy-signal disable, swap control, HDP client ID, and read-return deadlock FIFO credit fields.
- `DAGB0_FATAL_ERROR_*`: fatal-error filter, clear, and status capture fields. Status fields expose validity, client ID, low/high address bits, tag, VFID/VF, address space, IO, size, FED, operation, TMZ, snoop, invalid, NACK, read-only, memory log, and EOP state.
- `DAGB0_FIFO_EMPTY`, `DAGB0_FIFO_FULL`, `DAGB0_WR_CREDITS_FULL`, and `DAGB0_RD_CREDITS_FULL`: broad status bitmaps for FIFO and credit saturation.
- `DAGB0_PERFCOUNTER_*`: low/high counter results, compare value, three performance counter configuration registers, and result-control fields for selection, triggers, enable, clear, and stop-on-saturate behavior.
- `DAGB0_L1TLB_REG_RW` and `DAGB0_RESERVE1` through `DAGB0_RESERVE4`: L1 TLB register read/write and exception/parity/check controls plus reserved full-width registers.
- `DAGB1_RDCLI0` through `DAGB1_RDCLI15`, `DAGB1_RD_CNTL`, `DAGB1_RD_GMI_CNTL`, `DAGB1_RD_ADDR_DAGB`, read output/address DAGB burst/timer tables, and `DAGB1_RD_VC0_CNTL` through the start of `DAGB1_RD_VC1_CNTL`: the beginning of the second DAGB decoder instance, using the same read-side field layout as `DAGB0`.

## Important APIs, Types, and Functions

This header defines no C functions, structs, enums, or variables. Its API surface is the macro namespace:

- `*_MASK` constants isolate bit fields in 32-bit MMHUB registers.
- `*__SHIFT` constants define the bit position for packing caller-provided field values or unpacking hardware register reads.
- `DAGB0_*` and `DAGB1_*` prefixes identify separate DAGB decoder instances; callers must pair them with the matching `regDAGB0_*` or `regDAGB1_*` offsets from `mmhub_1_7_offset.h`.

Typical AMDGPU use is through register helpers such as `RREG32`, `WREG32`, or field helper macros that combine an offset macro, the `*_MASK`, and the `*__SHIFT`. Because these are untyped preprocessor definitions, the compiler cannot prevent mixing a mask from the wrong MMHUB generation or DAGB instance.

## Control Flow

There is no runtime control flow in this file. Including the header only exposes constants under `_mmhub_1_7_SH_MASK_HEADER`. Runtime behavior is created in downstream driver code that uses these constants to program hardware registers.

The implied register manipulation flow is:

1. Select an MMHUB 1.7 register offset, usually from `mmhub_1_7_offset.h`.
2. Read the current register value when preserving unrelated fields.
3. Clear a field with the corresponding `*_MASK`.
4. Shift the new value by `*__SHIFT`, mask it, and OR it into the register value.
5. Write the result back to the MMHUB register.

Status decoding reverses that flow: read the register, mask the field, shift it down, then interpret the value as a bitmap, client ID, address fragment, credit count, pending flag, or performance/debug state.

## State and Persistence Behavior

The header has no mutable state and persists no data. The constants describe MMHUB hardware state that exists in GPU registers while the device is powered and initialized.

Many fields configure long-lived routing and arbitration state: virtual-channel assignment, urgency thresholds, bandwidth windows, min/max bandwidth enforcement, outstanding-request limits, storage/EA/TLB credits, per-client burst sizes, lazy timers, GMI controls, virtual-channel remapping, and clock-gating behavior. Other fields expose transient state such as pending client requests, FIFO empty/full state, credit fullness, performance counters, and fatal-error captures. Clear/control fields such as `DAGB0_FATAL_ERROR_CLEAR__CLEAR`, performance counter `CLEAR`, and result-control `CLEAR_ALL` represent hardware side effects; the header does not encode whether bits are sticky, self-clearing, write-one-to-clear, or read-only.

## Dependencies and Integration Points

- Depends only on C preprocessing and include guard discipline.
- Integrates directly with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_7_offset.h`, whose `regDAGB0_*` and `regDAGB1_*` address macros correspond to these field macros.
- Integrates with AMDGPU MMHUB/GMC/VM initialization, memory-translation, bandwidth/credit programming, fault diagnostics, and performance/debug paths for ASICs using the MMHUB 1.7 register map.
- Names such as `L1TLB`, `ATCVM`, `UTCL2`, `HDP_CID`, `VFID`, `VF`, `TMZ`, `GMI`, `OSD`, and `GPU_SNOOP` show integration with GPU virtual memory, IOMMU/address translation, host data path, virtualization/SRIOV state, encrypted memory modes, interconnect traffic, outstanding request tracking, and snoop behavior.
- The repeated `DAGB0`/`DAGB1` layout means code can often share programming tables or loops, but offsets and available fields still need to match the exact ASIC generation.

## Risks and Edge Cases

- A mask/shift mismatch can silently program the wrong hardware bits, affecting GPU memory routing, TLB credit flow, bandwidth throttling, or fatal-error reporting.
- `DAGB0` and `DAGB1` are structurally similar. Copying a field macro across instances without also changing the register offset can target the wrong decoder.
- Read-side, write-address, and write-data DAGB tables look similar but are not interchangeable; using an address-path mask for data-path programming can misconfigure client arbitration.
- Several fields are compact encoded values rather than raw units. Examples include address fragments in fatal-error status registers, virtual-channel IDs, credit counts, bandwidth windows, max burst nibbles, and lazy timer nibbles.
- Status and control fields live in the same macro namespace. Callers must know from hardware documentation which registers are read-only, write-only, sticky, clear-on-write, or self-clearing.
- Reserved full-width registers and `RESERVE` fields should not be treated as safe scratch space. Writing non-reset values to reserved bits can cause undefined hardware behavior.
- This chunk ends mid-`DAGB1` read-control family at `DAGB1_RD_VC1_CNTL`; later chunks must cover the rest of `DAGB1` before final per-file conclusions are reconciled.

## Test Signals

- Build coverage: include regressions, misspelled macros, or duplicated/missing definitions should surface as AMDGPU compile errors.
- Generated-header validation: compare masks and shifts against AMD register source data or adjacent MMHUB 1.7 offset/default headers before accepting edits.
- Hardware smoke signals: GPU bring-up, VM setup, TLB behavior, SDMA or graphics memory traffic, display scanout under memory pressure, suspend/resume, and SRIOV/VF paths indirectly exercise these fields.
- Runtime debug signals: pending bitmaps, FIFO empty/full status, credit-full registers, fatal-error status registers, and DAGB performance counters can confirm that field decoding matches hardware behavior.
- Negative signals: memory faults after VM/MMHUB init, hangs in memory traffic, unexpected fatal-error captures, stuck pending bits, saturated credit-full bits, broken performance counter reads, or bandwidth/latency anomalies suggest either a bad field definition or a caller using the wrong field/register pairing.
