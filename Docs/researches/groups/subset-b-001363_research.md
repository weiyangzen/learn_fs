# subset-b-001363 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/tonga_sdma_pkt_open.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/tonga_sdma_pkt_open.h

## Purpose

This generated-style header is the packet layout contract for Tonga-era SDMA command streams. It defines SDMA operation and sub-operation IDs plus bit masks, shifts, dword offsets, and helper macros used by ring emitters to pack packet fields into 32-bit command words.

## Important APIs, Types, and Functions

There are no functions or runtime types. The public API is macro-only: `SDMA_OP_*` opcodes, `SDMA_SUBOP_*` selectors, base header helpers such as `SDMA_PKT_HEADER_OP()`, and packet-specific helpers for copy, write, indirect buffer, semaphore, fence, SRBM write, pre-execute, conditional execute, constant fill, poll reg/mem, atomic, timestamp, trap, and nop packets. Each field has an `_offset`, `_mask`, `_shift`, and uppercase pack macro.

## Control Flow

The file has no executable control flow. Consumers build SDMA packets by writing dwords in the documented order: header at dword 0, then address, count, geometry, tiling, mask, data, or synchronization fields depending on packet family. Header op/sub-op fields select how the SDMA engine interprets the remaining dwords.

## State and Persistence Behavior

The header persists no state. It describes command stream state that becomes persistent only after another driver component places the packed dwords into an SDMA ring or indirect buffer. Address fields are split into low/high dwords, so callers own address validity, alignment, and VMID context.

## Dependencies and Integration Points

The file is self-contained apart from the include guard. It integrates with AMDGPU SDMA ring code that emits hardware command buffers. Its constants must match the Tonga SDMA packet ABI and are indirectly tied to firmware/hardware parser behavior.

## Risks

The macros mask input values but do not validate ranges, alignment, packet length, ordering, or mutually exclusive fields. A wrong field definition can corrupt GPU memory, hang a ring, or silently misprogram synchronization. Generated packet definitions are also easy to drift from newer SDMA generations if reused outside the intended ASIC family.

## Test Signals

Primary signals are successful SDMA ring tests, IB submission tests, copy/fill correctness, fence and semaphore completion, VM fault absence, and no ring timeout under tiled/linear copy paths. Compile coverage catches missing macro names but not semantic packet packing errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/tonga_sdma_pkt_open.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v12_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v12_0.c

## Purpose

This file implements UMC v12.0 RAS support for AMDGPU memory controllers. It queries correctable, uncorrectable, and deferred ECC status, converts MCA error addresses to physical addresses, logs bad pages, integrates with ACA bank parsing, and registers the `amdgpu_umc_ras` callbacks for this hardware generation.

## Important APIs, Types, and Functions

Important exported or callback-facing symbols are `umc_v12_0_is_deferred_error`, `umc_v12_0_is_uncorrectable_error`, `umc_v12_0_is_correctable_error`, `umc_v12_0_ras_hw_ops`, `umc_v12_0_aca_info`, and `umc_v12_0_ras`. Core helpers include `get_umc_v12_0_reg_offset`, `umc_v12_0_query_error_count`, `umc_v12_0_query_error_address`, `umc_v12_0_convert_error_address`, `umc_v12_0_update_ecc_status`, and `umc_v12_0_query_ras_ecc_err_addr`.

## Control Flow

RAS count and address queries iterate channels via `amdgpu_umc_loop_channels`. Count flow reads `MCUMC_STATUS`, classifies it through the three status predicates, accumulates socket/die-scoped statistics, then resets OdEcc counters. Address flow reads status and address registers, filters for UE or deferred errors, asks PSP RAS services to translate MCA addresses to physical addresses, expands retired-page candidates by flipping generation-specific PA bits, fills RAS error records, and clears status registers.

## State and Persistence Behavior

The driver mutates hardware ECC counters, MCA status registers, UMC flip-bit configuration, `adev->umc.retire_unit`, and the RAS context's ECC log radix tree. Deferred errors are cached as `ras_ecc_err` entries, tagged as newly detected, reserved through `amdgpu_ras_reserve_page`, and may be flushed to EEPROM by delayed page-retirement work after GPU reset recovery.

## Dependencies and Integration Points

Dependencies include AMDGPU RAS, UMC helpers, PSP RAS address translation, SMUIO socket/die identity, ACA error cache logging, MCA register definitions, radix-tree locking, and GMC partition/VRAM metadata. Integration is through `amdgpu_umc_ras`, `amdgpu_ras_block_hw_ops`, ACA bank ops, and common page retirement logic.

## Risks

Address conversion is sensitive to NPS mode, HBM/HBM3E type, UMC count, IP version, and flip-bit tables. Incorrect classification can undercount deferred poison events or misclassify replay-mode parity. Host-inaccessible poison mode is forced true, so hardware/firmware contract drift would be hard to detect. Bad page logging allocates memory and depends on radix-tree uniqueness and lock discipline.

## Test Signals

Useful signals are injected MCA status tests for CE/UE/DE classification, PSP address query success/failure logs, RAS sysfs/error counters, page retirement records and EEPROM persistence, ACA cache entries, no leaked ECC log entries, and no spurious reset loops after deferred-error recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v12_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v12_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v12_0.h

## Purpose

This header defines the UMC v12.0 register spacing, channel geometry, ECC counter constants, physical-address bit positions, MCA/IPID decode helpers, error classifier prototypes, and the exported `umc_v12_0_ras` registration object.

## Important APIs, Types, and Functions

Important constants include `UMC_V12_0_NODE_DIST`, `UMC_V12_0_INST_DIST`, `UMC_V12_0_CROSS_NODE_OFFSET`, `UMC_V12_0_CHANNEL_INSTANCE_NUM`, `UMC_V12_0_UMC_INSTANCE_NUM`, `UMC_V12_0_TOTAL_CHANNEL_NUM`, `UMC_V12_0_NA_MAP_PA_NUM`, `UMC_V12_0_BAD_PAGE_NUM_PER_CHANNEL`, PA bit definitions for column/row/channel/bank bits, and MCA hardware identifiers. Public helpers include `MCA_IPID_2_DIE_ID`, `MCA_IPID_2_UMC_CH`, `MCA_IPID_2_UMC_INST`, and `MCA_IPID_2_SOCKET_ID`.

## Control Flow

The header has no runtime flow. It controls implementation behavior by giving `umc_v12_0.c` the constants needed for channel iteration, register offset calculation, MCA IPID parsing, ECC counter initialization, and bad-page address expansion.

## State and Persistence Behavior

It stores no state. Its macros shape how runtime state in `adev->umc`, MCA status registers, and RAS page-retirement logs is interpreted.

## Dependencies and Integration Points

The header includes `soc15_common.h` and `amdgpu.h`, and depends on register field macros for MCA/IPID extraction. It is consumed by the UMC v12 implementation and any generation dispatch code that references `umc_v12_0_ras`.

## Risks

Wrong distance or bit-position constants directly affect register access and bad-page retirement. The total-channel macro depends on `adev->gmc.num_umc`, so platform setup must initialize GMC topology before UMC RAS registration. The IPID decode macros encode generation-specific assumptions that are unsafe to reuse for unrelated MCA layouts.

## Test Signals

Compile coverage validates macro availability. Runtime signals include correct channel enumeration, valid socket/die/UMC/channel reporting in RAS logs, correct bad-page fanout counts, and absence of invalid MMIO reads during UMC scans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v12_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v6_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v6_0.c

## Purpose

This minimal UMC v6.0 file provides a hardware initialization hook that writes a fixed value to a grid of UMC registers. It exposes that hook through `umc_v6_0_funcs`.

## Important APIs, Types, and Functions

The only implementation function is `umc_v6_0_init_registers`. The public integration object is `const struct amdgpu_umc_funcs umc_v6_0_funcs`, with `.init_registers` assigned to the initializer.

## Control Flow

Initialization loops four UMC instances by four channels. For each pair it computes `(i * 0x100000 + 0x5010c + j * 0x2000) / 4` and writes `0x1002` via `WREG32`.

## State and Persistence Behavior

The file mutates hardware register state only. It keeps no software state, performs no readback, and exposes no RAS counters or address persistence.

## Dependencies and Integration Points

It depends on `amdgpu.h`, `umc_v6_0.h`, and the AMDGPU register write macro. The object is selected by ASIC setup code through the common `amdgpu_umc_funcs` dispatch.

## Risks

The register address arithmetic is literal and undocumented in this file. If the topology or base offsets differ, the loop can write unintended registers. There is no status check, no locking, and no test for whether writes took effect.

## Test Signals

Signals are successful device initialization, no MMIO faults, stable memory-controller behavior after init, and low-level register traces confirming the expected sixteen writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v6_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v6_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v6_0.h

## Purpose

This header declares the UMC v6.0 function table used by generation dispatch code.

## Important APIs, Types, and Functions

The only public symbol is `extern const struct amdgpu_umc_funcs umc_v6_0_funcs`.

## Control Flow

There is no control flow. Including this header lets platform setup bind the v6.0 `.init_registers` callback implemented in `umc_v6_0.c`.

## State and Persistence Behavior

The header stores no state and defines no persistent data. It exposes a const callback table that drives hardware register initialization elsewhere.

## Dependencies and Integration Points

It includes `soc15_common.h` and `amdgpu.h` for AMDGPU types and register infrastructure. It integrates with common UMC setup, not with the newer RAS `amdgpu_umc_ras` interface.

## Risks

The header is intentionally small; the main risk is dispatch mismatch if ASIC setup selects v6.0 functions for hardware with a different register layout.

## Test Signals

Compile-time symbol resolution and successful UMC initialization on v6.0 devices are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v6_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v6_1.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v6_1.c

## Purpose

This file implements RAS support for UMC v6.1 hardware, including correctable and uncorrectable ECC counting, UE address conversion, error counter initialization, and channel indexing for Vega20/Arcturus-era layouts.

## Important APIs, Types, and Functions

Important symbols are `umc_v6_1_channel_idx_tbl`, `umc_v6_1_ras_hw_ops`, and `umc_v6_1_ras`. Key helpers manage RSMU UMC index mode, compute UMC register offsets, clear counters for lower and higher chips, query CE/UE counts, translate UE addresses to retired pages, and initialize interrupt/counter state.

## Control Flow

Count and address paths save the RSMU index-mode state, disable index mode when needed, optionally disallow DF C-state on Arcturus, loop `LOOP_UMC_INST_AND_CH`, read generation-specific UMC 6.1.1 or Arcturus 6.1.2 registers, update `ras_err_data`, restore DF C-state, restore index mode, and clear CE counters after count queries. Address queries only fill records when `err_data->err_addr` is requested and `MCUMC_STATUS` indicates a valid UECC error.

## State and Persistence Behavior

The implementation mutates RSMU index-mode state, DF C-state policy, ECC counter select registers, ECC counter registers, and MCA status registers. It stores no long-lived software error cache; reported retired pages are added directly to `ras_err_data`.

## Dependencies and Integration Points

Dependencies include AMDGPU RAS/UMC helpers, RSMU register definitions, UMC 6.1 register headers, DPM DF C-state control, `amdgpu_umc_fill_error_record`, and channel-index data from `adev->umc.channel_idx_tbl`. Integration is through `amdgpu_umc_ras` with `.err_cnt_init` and `amdgpu_ras_block_hw_ops`.

## Risks

Register selection depends on `adev->asic_type == CHIP_ARCTURUS`. Missed DF C-state protection can make UMC access unreliable. The function name typo `querry` is harmless but visible. Address conversion is simpler than later generations and assumes the 8KB/256B block mapping and channel table are correct.

## Test Signals

Signals include CE counter deltas on both chip selects, UE status detection, status clearing, stable DF C-state warnings, correct retired page addresses, and no regressions in RAS sysfs counters on Vega20/Arcturus systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v6_1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v6_1.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v6_1.h

## Purpose

This header defines UMC v6.1 geometry, ECC counter constants, per-channel offsets for Vega20 and Arcturus, and public declarations for the v6.1 RAS object and channel index table.

## Important APIs, Types, and Functions

Important constants are `UMC_V6_1_HBM_MEMORY_CHANNEL_WIDTH`, `UMC_V6_1_CHANNEL_INSTANCE_NUM`, `UMC_V6_1_UMC_INSTANCE_NUM`, `UMC_V6_1_TOTAL_CHANNEL_NUM`, `UMC_V6_1_PER_CHANNEL_OFFSET_VG20`, `UMC_V6_1_PER_CHANNEL_OFFSET_ARCT`, and `UMC_V6_1_CE_CNT_INIT`. Public symbols are `umc_v6_1_ras` and `umc_v6_1_channel_idx_tbl`.

## Control Flow

There is no executable flow. The constants drive v6.1 channel loops, channel-index lookups, counter setup, and ASIC-specific offset selection in `umc_v6_1.c`.

## State and Persistence Behavior

The header stores no state. Its declarations expose static topology and threshold policy to runtime code that mutates hardware counters and RAS records.

## Dependencies and Integration Points

It includes SOC15 and AMDGPU common definitions. It integrates with ASIC initialization and common UMC/RAS dispatch through `umc_v6_1_ras`.

## Risks

Topology constants must match the selected channel table and hardware register map. An incorrect CE initial value or per-channel offset makes counter deltas wrong or causes invalid register access.

## Test Signals

Compile coverage, correct channel count reporting, valid CE counter initialization, and correct channel ordering in retired-page reports are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v6_1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v6_7.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v6_7.c

## Purpose

This file implements UMC v6.7 RAS behavior. It supports direct register scans and firmware-provided ECC info tables, converts normalized UMC addresses into possible physical bad pages, queries poison mode, and exposes generation callbacks through `umc_v6_7_ras`.

## Important APIs, Types, and Functions

Public symbols include `umc_v6_7_channel_idx_tbl_first`, `umc_v6_7_channel_idx_tbl_second`, `umc_v6_7_convert_error_address`, and `umc_v6_7_ras`. Important helpers include `get_umc_v6_7_reg_offset`, ECC-info query functions, direct CE/UE count functions, reset-counter callbacks, UE address query callbacks, and `umc_v6_7_query_ras_poison_mode`.

## Control Flow

The direct path loops channels with `amdgpu_umc_loop_channels`, reads Gecc counters and MCA status, logs CE/UE counts, optionally prints diagnostic MCA IPID/SYND/MISC0 values, then resets lower and higher chip counters. Address queries read `MCUMC_STATUS` and `ADDRT0`, then call `umc_v6_7_convert_error_address` for valid UECC records. ECC-info paths read cached firmware table entries from `ras->umc_ecc.ecc` instead of MMIO.

## State and Persistence Behavior

The code mutates ECC counter select/count registers and MCA status registers. It reads cached ECC info from the RAS context but does not persist a separate software tree. Address conversion fills multiple `ras_err_data` records because one normalized address can map to eight column candidates and an additional R14-flipped set.

## Dependencies and Integration Points

Dependencies include AMDGPU RAS/UMC helpers, UMC 6.7 register headers, `adev->umc.channel_idx_tbl`, DF hash status for channel hashing, and common RAS poison/error record APIs. It integrates via direct `hw_ops`, ECC-info query callbacks, and poison-mode callback.

## Risks

The register address layout is non-linear and remapped in `get_umc_v6_7_reg_offset`. Physical address expansion depends on channel hash status and PA bit definitions. ECC-info and direct MMIO paths must remain consistent. Diagnostic `dev_info` logging can be noisy during error storms.

## Test Signals

Signals include CE/UE counter deltas, correct reset of both chip-select counters, valid ECC-info table indexing, expected number of retired-page candidates, poison-mode reporting from `UCFatalEn`, and no false channel hashes in reported PA values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v6_7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v6_7.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v6_7.h

## Purpose

This header defines UMC v6.7 RAS constants, channel geometry, bad-page expansion dimensions, PA bit positions, channel-hash helpers, channel index table exports, and the address conversion function prototype.

## Important APIs, Types, and Functions

Key definitions include `UMC_V6_7_INST_DIST`, `UMC_V6_7_UMC_INSTANCE_NUM`, `UMC_V6_7_CHANNEL_INSTANCE_NUM`, `UMC_V6_7_NA_MAP_PA_NUM`, `UMC_V6_7_BAD_PAGE_NUM_PER_CHANNEL`, `UMC_V6_7_PA_CH4_BIT`, `UMC_V6_7_PA_C2_BIT`, `UMC_V6_7_PA_R14_BIT`, `CHANNEL_HASH`, and `SET_CHANNEL_HASH`. Public symbols are both channel index tables, `umc_v6_7_ras`, and `umc_v6_7_convert_error_address`.

## Control Flow

There is no executable flow, but the `SET_CHANNEL_HASH` macro performs a small address rewrite sequence when used by the implementation.

## State and Persistence Behavior

The header stores no state. The hash macro reads `adev->df.hash_status` from the caller context and mutates the passed physical-address lvalue.

## Dependencies and Integration Points

It includes SOC15 and AMDGPU definitions and assumes callers have an `adev` identifier in scope for `CHANNEL_HASH`. It integrates with UMC RAS address conversion and channel-index setup.

## Risks

`CHANNEL_HASH` is not a pure function because it references `adev` implicitly. That makes it fragile if reused outside the current implementation style. Incorrect bit constants or hash masks directly affect retired-page addresses.

## Test Signals

Signals are correct macro expansion at compile time, correct bad-page candidate count, channel hash behavior under 64K/2M/1G hash settings, and valid channel table selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v6_7.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v8_10.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v8_10.c

## Purpose

This file implements UMC v8.10 RAS support, including multi-node register offsets, status-based CE/UE counting, swizzle-mode normalized-address to physical-address conversion, ECC-info table support, poison-mode reporting, and counter initialization.

## Important APIs, Types, and Functions

Important public data includes `umc_v8_10_channelnum_map_colbit_table`, `umc_v8_10_channel_idx_tbl_ext0`, `umc_v8_10_channel_idx_tbl`, `umc_v8_10_ras_hw_ops`, and `umc_v8_10_ras`. Key helpers include `get_umc_v8_10_reg_offset`, `umc_v8_10_get_col_bit`, `umc_v8_10_swizzle_mode_na_to_pa`, `umc_v8_10_convert_error_address`, direct count/address callbacks, ECC-info count/address callbacks, and `umc_v8_10_err_cnt_init`.

## Control Flow

Direct count flow loops all nodes, UMCs, and channels, reads `MCUMC_STATUS` for CE/UE signals, updates `ras_err_data`, and clears Gecc counts. Direct address flow requires `err_data->err_addr`, valid status, `AddrV`, and `UECC` before reading `ADDRT0`. Address conversion clears low bits using `AddrLsb`, enumerates possible C5/C6 normal-address values, maps each through swizzle mode, logs the PA, and fills RAS records. ECC-info paths use cached table entries and CE count fields.

## State and Persistence Behavior

The code mutates Gecc counter registers, MCA status registers, interrupt selection, and `ras_err_data`. It does not persist a local bad-page cache. Poison mode is forced true because the Gecc control register is not host accessible.

## Dependencies and Integration Points

Dependencies include UMC 8.10 register headers, AMDGPU RAS/UMC helpers, channel-index tables configured in `adev->umc`, `hweight32(adev->gmc.m_half_use)` in total-channel calculations, and common loop/channel callbacks. Integration is through `amdgpu_umc_ras` direct and ECC-info callbacks.

## Risks

The swizzle mapping only supports channel counts present in the col-bit table; unsupported counts fail address conversion. Channel index selection across node/UMC/channel dimensions must match topology, including half-disabled memory. Forced poison mode can hide hardware accessibility changes.

## Test Signals

Signals include supported channel-count mapping, expected PA output for injected normalized addresses, CE count accumulation from ECC-info and direct paths, status clearing, correct behavior with disabled memory halves, and no failed `Failed to map pa from umc na` logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v8_10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v8_10.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v8_10.h

## Purpose

This header defines UMC v8.10 topology, total-channel calculation, ECC counter constants, normalized-address column handling, swizzle-mode mapping macros, and public RAS/channel-table declarations.

## Important APIs, Types, and Functions

Important constants are `UMC_V8_10_CHANNEL_INSTANCE_NUM`, `UMC_V8_10_UMC_INSTANCE_NUM`, `UMC_V8_10_TOTAL_CHANNEL_NUM`, `UMC_V8_10_PER_CHANNEL_OFFSET`, `UMC_V8_10_CE_CNT_INIT`, `UMC_V8_10_NA_COL_2BITS_POWER_OF_2_NUM`, and `UMC_V8_10_NA_C5_BIT`. Swizzle helpers include `SWIZZLE_MODE_TMP_ADDR`, `SWIZZLE_MODE_ADDR_HI`, `SWIZZLE_MODE_ADDR_MID`, `SWIZZLE_MODE_ADDR_LOW`, and `SWIZZLE_MODE_ADDR_LSB`.

## Control Flow

There is no runtime flow. The swizzle macros are composed by `umc_v8_10.c` to map normalized addresses to physical addresses.

## State and Persistence Behavior

No state is stored. `UMC_V8_10_TOTAL_CHANNEL_NUM` reads runtime `adev->gmc` topology, including half-use masks, when expanded.

## Dependencies and Integration Points

It includes SOC15 and AMDGPU headers and exports `umc_v8_10_ras`, `umc_v8_10_channel_idx_tbl`, and `umc_v8_10_channel_idx_tbl_ext0` for generation setup.

## Risks

There is a typo in `UUMC_V8_10_CE_INT_THRESHOLD`; it is internally used by `UMC_V8_10_CE_CNT_INIT`, so compile succeeds, but the name is inconsistent. Swizzle macros assume valid `col_bit` values and can produce bad shifts if called without prior validation.

## Test Signals

Compile coverage, correct total-channel counts under `m_half_use`, valid swizzle PA results, and successful binding of the v8.10 RAS object are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v8_10.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v8_14.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v8_14.c

## Purpose

This file implements a compact UMC v8.14 RAS backend focused on counter-based CE and UE reporting. It initializes Gecc counters, queries correctable and uncorrectable count fields, clears counters, and registers count-only RAS hardware operations.

## Important APIs, Types, and Functions

Important public symbols are `umc_v8_14_ras_hw_ops` and `umc_v8_14_ras`. Key helpers are `get_umc_v8_14_reg_offset`, `umc_v8_14_clear_error_count_per_channel`, `umc_v8_14_query_correctable_error_count`, `umc_v8_14_query_uncorrectable_error_count`, `umc_v8_14_query_error_count_per_channel`, and `umc_v8_14_err_cnt_init_per_channel`.

## Control Flow

The count path loops channels with `amdgpu_umc_loop_channels`, computes channel register offsets, reads `regUMCCH0_GeccErrCnt`, adds CE and uncorrectable counter deltas to `ras_err_data`, then clears the counter to `UMC_V8_14_CE_CNT_INIT`. Initialization sets the Gecc interrupt mode to APIC-based and seeds the counter.

## State and Persistence Behavior

The implementation only mutates hardware Gecc count/select registers and in-memory `ras_err_data` counters. It does not query MCA addresses, clear MCA status, or persist bad-page records.

## Dependencies and Integration Points

Dependencies include UMC 8.14 register headers, AMDGPU RAS/UMC helpers, `amdgpu_umc_loop_channels`, and SOC15 MMIO access macros. Integration is through `amdgpu_umc_ras` with `.err_cnt_init` and count-only `amdgpu_ras_block_hw_ops`.

## Risks

The UE query subtracts `UMC_V8_14_CE_CNT_INIT` from `GeccUnCorrErrCnt`; this assumes the uncorrectable field uses the same initialization baseline. No address callback means this backend cannot directly retire pages from queried errors. Register offsets ignore node argument and rely on v8.14 topology matching `umc_inst`/`ch_inst`.

## Test Signals

Signals include CE/UE count deltas, successful counter reset after queries, APIC interrupt setting, absence of invalid MMIO, and expected behavior when RAS frameworks request an address query that is not provided.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v8_14.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v8_14.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v8_14.h

## Purpose

This header defines UMC v8.14 channel geometry, register spacing, ECC counter constants, and the exported RAS object declaration.

## Important APIs, Types, and Functions

Important constants include `UMC_V8_14_CHANNEL_INSTANCE_NUM`, `UMC_V8_14_UMC_INSTANCE_NUM(adev)`, `UMC_V8_14_TOTAL_CHANNEL_NUM(adev)`, `UMC_V8_14_PER_CHANNEL_OFFSET`, `UMC_V8_14_INST_DIST`, `UMC_V8_14_CE_CNT_MAX`, `UMC_V8_14_CE_INT_THRESHOLD`, and `UMC_V8_14_CE_CNT_INIT`. The public object is `umc_v8_14_ras`.

## Control Flow

There is no executable flow. The macros guide channel enumeration, offset computation, and counter baseline calculation in `umc_v8_14.c`.

## State and Persistence Behavior

No state is stored. Some macros read runtime topology from `adev`, so callers need initialized UMC/GMC fields.

## Dependencies and Integration Points

It includes SOC15 and AMDGPU headers and integrates with AMDGPU generation dispatch through `umc_v8_14_ras`.

## Risks

`UMC_V8_14_UMC_INSTANCE_NUM(adev)` maps to `adev->umc.node_inst_num`, which is unusual compared with several other generations and must match setup code. Wrong topology values lead to incomplete or invalid counter scans.

## Test Signals

Compile coverage, correct total-channel count, successful v8.14 RAS registration, and valid Gecc counter reads during RAS queries are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v8_14.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v8_7.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v8_7.c

## Purpose

This file implements UMC v8.7 RAS support for Sienna-style memory controllers. It handles direct register CE/UE scans, ECC-info table scans, UE address conversion, counter initialization, and RAS callback registration.

## Important APIs, Types, and Functions

Important public symbols are `umc_v8_7_channel_idx_tbl`, `umc_v8_7_ras_hw_ops`, and `umc_v8_7_ras`. Important helpers include `get_umc_v8_7_reg_offset`, ECC-info count/address functions, `umc_v8_7_convert_error_address`, direct Gecc count functions, direct address query functions, and `umc_v8_7_err_cnt_init`.

## Control Flow

Direct count flow loops UMC instances and channels, reads lower and higher chip Gecc counters, checks MCA status for SRAM CE and UE-like conditions, updates `ras_err_data`, then clears counters. Direct address flow reads status and address registers, masks low address bits according to `LSB`, converts valid UECC errors to retired pages, fills error records, and clears status. ECC-info paths read cached MCA status/address entries from `ras->umc_ecc.ecc`.

## State and Persistence Behavior

The code mutates Gecc counter select/count registers, MCA status registers, and `ras_err_data`. It does not persist a separate ECC tree. Address conversion maps one UMC address to one retired page using a 4KB block plus channel and 256B offset fields.

## Dependencies and Integration Points

Dependencies include RSMU headers, UMC 8.7 register headers, AMDGPU RAS/UMC helpers, `adev->umc.channel_idx_tbl`, and RAS ECC-info storage. Integration is through direct `hw_ops`, `.err_cnt_init`, and ECC-info callbacks in `umc_v8_7_ras`.

## Risks

DF C-state protection is marked TODO for ECC-info paths, so safe access depends on firmware/interface readiness. Direct and ECC-info paths use different sources and must agree. Address conversion is simpler than later HBM mappings and depends heavily on channel table correctness.

## Test Signals

Signals include direct and ECC-info CE/UE counter agreement, correct lower/higher chip counter reset, valid retired page output for injected UECC, status clearing, and no access instability around DF C-state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v8_7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v8_7.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v8_7.h

## Purpose

This header defines UMC v8.7 geometry, counter constants, per-channel offset, and public declarations for the v8.7 RAS object and channel index table.

## Important APIs, Types, and Functions

Important constants are `UMC_V8_7_HBM_MEMORY_CHANNEL_WIDTH`, `UMC_V8_7_CHANNEL_INSTANCE_NUM`, `UMC_V8_7_UMC_INSTANCE_NUM`, `UMC_V8_7_TOTAL_CHANNEL_NUM`, `UMC_V8_7_PER_CHANNEL_OFFSET_SIENNA`, and `UMC_V8_7_CE_CNT_INIT`. Public symbols are `umc_v8_7_ras` and `umc_v8_7_channel_idx_tbl`.

## Control Flow

No executable flow is present. The constants feed v8.7 channel iteration, offset calculation, counter setup, and channel-index conversion in `umc_v8_7.c`.

## State and Persistence Behavior

The header stores no state. It exposes topology constants used to interpret hardware state.

## Dependencies and Integration Points

It includes SOC15 and AMDGPU headers and is consumed by generation setup and the v8.7 RAS implementation.

## Risks

The total channel count and Sienna offset must match platform setup. Wrong table dimensions would break flattened channel-index lookups.

## Test Signals

Signals include compile-time table dimension checks, successful v8.7 RAS binding, correct channel count, and stable Gecc counter queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v8_7.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umsch_mm_v4_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umsch_mm_v4_0.c

## Purpose

This file implements UMSCH MM v4.0 support, wiring the multimedia micro-scheduler to VCN/VPE hardware. It loads scheduler firmware, configures instruction/data memory windows, starts and stops the scheduler ring, initializes aggregated doorbells, and submits scheduler API packets for hardware resources and queue management.

## Important APIs, Types, and Functions

The public entry point is `umsch_mm_v4_0_set_funcs`. Important callbacks are `umsch_mm_v4_0_load_microcode`, `umsch_mm_v4_0_ring_start`, `umsch_mm_v4_0_ring_stop`, `umsch_mm_v4_0_set_hw_resources`, `umsch_mm_v4_0_add_queue`, `umsch_mm_v4_0_remove_queue`, and `umsch_mm_v4_0_set_regs`. It uses API unions from `umsch_mm_4_0_api_def.h`, including `UMSCHAPI__SET_HW_RESOURCES`, `UMSCHAPI__ADD_QUEUE`, and `UMSCHAPI__REMOVE_QUEUE`.

## Control Flow

Microcode load allocates code and data buffers, optionally powers DLDO for VCN 4.0.5+, resets/halt-primes MES state, programs instruction/data base and mask registers, primes and invalidates caches, optionally asks PSP to execute the command buffer, and waits for `regVCN_MES_MSTATUS_LO == 0xAAAAAAAA`. Ring start programs doorbell and ring-buffer registers, disables the audio ring bit, and enables aggregated doorbells for four priority levels. API calls fill a frame, set a completion fence address/value, submit the packet, then query the fence.

## State and Persistence Behavior

The code mutates UMSCH firmware BOs, command buffer pointers, VCN/MES registers, ring write pointer, doorbell ranges, scheduler context GPU addresses, fence sync sequence, and firmware-visible queue/resource state. Error paths free allocated firmware buffers.

## Dependencies and Integration Points

Dependencies include AMDGPU core, SOC15/VCN register definitions, NBIO doorbell functions, PSP firmware loading mode, debugfs logging addresses, UMSCH common helpers, VPE collaboration mode, and fence driver GPU addresses. It integrates through `struct umsch_mm_funcs`.

## Risks

Firmware load sequencing is register-order sensitive. PSP and non-PSP firmware load modes require different base addresses. Missing fence completion indicates firmware/API failure. Doorbell offsets and priority-level aggregated doorbells must match userspace queue setup. Power gating changes for VCN 4.0.5+ can hang if status waits fail.

## Test Signals

Signals include successful firmware status magic, no buffer leaks on load failure, valid ring write/read pointer registers, working add/remove queue fence completions, VCN/VPE workload scheduling, correct doorbell interrupts, and clean ring stop/power transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umsch_mm_v4_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umsch_mm_v4_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umsch_mm_v4_0.h

## Purpose

This header declares the UMSCH MM v4.0 function-table binding entry point.

## Important APIs, Types, and Functions

The only public symbol is `void umsch_mm_v4_0_set_funcs(struct amdgpu_umsch_mm *umsch);`, which installs the v4.0 implementation callbacks into an `amdgpu_umsch_mm` instance.

## Control Flow

There is no executable flow. Including this header lets initialization code call the setter implemented in `umsch_mm_v4_0.c`.

## State and Persistence Behavior

The header stores no state. The declared function mutates `umsch->funcs` at runtime.

## Dependencies and Integration Points

It depends on the caller having `struct amdgpu_umsch_mm` declared by common UMSCH headers. It integrates v4.0 code with the generic UMSCH MM dispatch layer.

## Risks

The header does not include the struct definition itself, so include ordering must provide it. A wrong generation dispatch would install incompatible VCN/MES register programming callbacks.

## Test Signals

Compile-time prototype visibility, successful UMSCH initialization, and correct callback table selection for v4.0 hardware are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umsch_mm_v4_0.h -->
