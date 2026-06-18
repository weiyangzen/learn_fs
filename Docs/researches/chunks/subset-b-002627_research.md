# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_sh_mask.h lines 29721-30033

## Scope

This chunk is the final segment of the generated AMD GC 9.0 shift/mask register header. It contains C preprocessor constants only: hardware register fields are represented as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros for composing and decoding 32-bit GPU register values. There are no functions, structs, enums, variables, allocations, locks, branches, or callbacks in this range.

The selected range begins at the tail of `DIDT_TCP_EDC_STALL_DELAY_4`, after the corresponding shift definitions from the previous chunk, then covers the complete DBR DIDT/EDC control families, DIDT stall event counters, and the final texture/cache EDC counter registers (`TA_EDC_CNT`, `TCI_EDC_CNT`, `TCP_EDC_CNT_NEW`, and `TD_EDC_CNT`). It ends with the file's `#endif`.

Although the repository is under a `ceph-client` mirror, this file is AMDGPU DRM graphics-core hardware metadata and is unrelated to Ceph distributed filesystem behavior.

## Purpose

`gc_9_0_sh_mask.h` supplies bit layouts for GC 9.0 graphics hardware. Driver code pairs these macros with register addresses from the matching GC 9.0 offset header and uses AMDGPU field helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, indexed-register helpers, and MMIO accessors to pack or extract field values without hard-coding bit positions.

This chunk describes two related hardware surfaces:

- DIDT and EDC control for the DBR block and the tail of TCP EDC state. DIDT is dynamic power/throttle logic; EDC tracks error/power-delta/throttle state and can force or qualify stalls through programmable patterns and delays.
- End-of-file EDC counter decoding for TA, TCI, TCP, and TD memories/FIFOs. These fields are consumed by AMDGPU RAS/EDC reporting tables to name and extract correctable, detectable, and double-error counters from GC register dumps.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public interface is the generated macro contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the raw mask for that field inside the 32-bit register.
- Register address symbols live in the matching GC 9.0 offset header, for example `ixDIDT_DBR_EDC_CTRL` for DIDT indirect registers and `mmTA_EDC_CNT`/`mmTCP_EDC_CNT_NEW` for SOC15 GC registers.

Important macro groups in this range include:

- `DIDT_TCP_EDC_STALL_DELAY_4` masks for `EDC_STALL_DELAY_TCP12` through `EDC_STALL_DELAY_TCP15`, plus `DIDT_TCP_EDC_OVERFLOW` and `DIDT_TCP_EDC_ROLLING_POWER_DELTA`. These are the tail of the TCP EDC family and expose per-TCP stall delay bytes, rolling power-delta overflow state, throttle-level overflow count, and the full 32-bit rolling power-delta value.
- `DIDT_DBR_CTRL0`, `DIDT_DBR_CTRL1`, `DIDT_DBR_CTRL2`, `DIDT_DBR_STALL_CTRL`, `DIDT_DBR_TUNING_CTRL`, `DIDT_DBR_STALL_AUTO_RELEASE_CTRL`, and `DIDT_DBR_CTRL3`. These define DBR DIDT enable/reset/clock override fields, phase offset, stall and tuning enables, high/min/max power thresholds, interval sizing, long-term ratio, stall delays, max stall counts, throttle policy, level-combine enables, stall qualification, force-stall, and stall-delay enable bits.
- `DIDT_DBR_STALL_PATTERN_1_2` through `DIDT_DBR_STALL_PATTERN_7`. These pack seven 15-bit stall patterns across four registers, with reserved upper bits where only one pattern is present.
- `DIDT_DBR_WEIGHT0_3`, `DIDT_DBR_WEIGHT4_7`, and `DIDT_DBR_WEIGHT8_11`. These expose twelve 8-bit weights used by DBR DIDT power/throttle calculations.
- `DIDT_DBR_EDC_CTRL`, `DIDT_DBR_EDC_THRESHOLD`, `DIDT_DBR_EDC_STALL_PATTERN_1_2` through `DIDT_DBR_EDC_STALL_PATTERN_7`, `DIDT_DBR_EDC_STATUS`, `DIDT_DBR_EDC_STALL_DELAY_1`, `DIDT_DBR_EDC_OVERFLOW`, and `DIDT_DBR_EDC_ROLLING_POWER_DELTA`. These mirror the EDC control/status surface for DBR: enable/reset/clock override/force-stall, trigger throttle low bit, stall pattern size, write-power-delta permission, GC and shader-engine level combine, stall policy, 32-bit threshold, seven 15-bit stall patterns, FSM state, throttle level, two 3-bit DBR stall delays, overflow state, overflow counter, and rolling power delta.
- `DIDT_SQ_STALL_EVENT_COUNTER`, `DIDT_DB_STALL_EVENT_COUNTER`, `DIDT_TD_STALL_EVENT_COUNTER`, `DIDT_TCP_STALL_EVENT_COUNTER`, and `DIDT_DBR_STALL_EVENT_COUNTER`. Each is a full-width 32-bit stall-event counter for one DIDT-controlled graphics block.
- `TA_EDC_CNT`. This register defines 2-bit counters for TA front-end FIFO and RAM events: `TA_FS_DFIFO_SEC_COUNT`, `TA_FS_DFIFO_DED_COUNT`, `TA_FS_AFIFO_SED_COUNT`, `TA_FL_LFIFO_SED_COUNT`, `TA_FX_LFIFO_SED_COUNT`, and `TA_FS_CFIFO_SED_COUNT`.
- `TCI_EDC_CNT`. In this GC 9.0 header it exposes only `WRITE_RAM_SED_COUNT` as a 2-bit field.
- `TCP_EDC_CNT_NEW`. This decodes 2-bit counters for TCP cache RAM, LFIFO RAM, command FIFO, VM FIFO, DB RAM, and UTCL1 LFIFO0/LFIFO1 events. Cache/LFIFO/VM/UTCL1 fields have paired SEC/DED counters where present; command FIFO and DB RAM are single SED counters in this header.
- `TD_EDC_CNT`. This defines 2-bit counters for TD shader-stream FIFO low/high SEC/DED events and a CS FIFO SED event.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow in consumers is:

1. Select the GC 9.0 register offset and shift/mask headers for the active ASIC.
2. Pick a register address, either from DIDT indirect-register names such as `ixDIDT_DBR_EDC_CTRL` or SOC15 GC names such as `mmTCP_EDC_CNT_NEW`.
3. Read the current value or prepare a full-register programmed value.
4. Use these shift/mask macros through helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, or `SOC15_REG_FIELD`.
5. Write control registers, decode status/counter registers, or build RAS/diagnostic tables.

Concrete consumers found in this tree include `vega10_powertune.c`, where `vega10_didt_set_mask()` toggles DBR DIDT and DBR EDC fields through `CGS_WREG32_FIELD_IND`, `cgs_read_ind_register()`, `REG_SET_FIELD()`, and `cgs_write_ind_register()`. The same file programs TCP EDC stall pattern, delay, and threshold register lists that border this chunk. `gfx_v9_0.c` consumes the TA/TCI/TCP/TD counter masks through `SOC15_REG_FIELD()` inside EDC/RAS counter tables and uses matching `SOC15_REG_ENTRY()` entries to enumerate the registers for reads.

## State And Persistence Behavior

The macros themselves hold no state and persist nothing. They describe hardware state owned by the GPU, firmware, and driver:

- DBR DIDT control fields persist in the DIDT indirect register space until reset, power-gating loss, firmware reinitialization, or explicit driver reprogramming. Enable, reset, clock override, stall control, tuning, auto-release, threshold, interval, and policy fields directly affect hardware throttle behavior.
- DBR/TCP EDC status, overflow, rolling power delta, and stall-event counters are live hardware observation points. Some values can change asynchronously while graphics workloads run.
- Stall pattern, weight, delay, and threshold registers are programmable policy state. Drivers can write whole-register values during power-management setup, but later read-modify-write paths should preserve reserved fields unless the hardware programming sequence specifies otherwise.
- TA/TCI/TCP/TD EDC count registers are hardware-maintained error counters. The masks only decode packed 2-bit fields; counter lifetime, clearing semantics, overflow behavior, and RAS aggregation policy live in hardware and higher-level AMDGPU code.
- The chunk ends at `#endif`, closing the include guard for the whole generated header.

## Dependencies And Integration Points

This chunk depends on generated GC 9.0 register metadata remaining synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_offset.h` supplies the matching register addresses and base-index information.
- AMDGPU field helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_FIELD`, and SOC15 register-entry helpers consume the shift/mask names.
- DIDT indirect register access uses CGS helpers and the `CGS_IND_REG__DIDT` space in power-management code.
- RAS/EDC reporting in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_0.c` uses the TA, TCI, TCP, and TD counter fields to attach names and SEC/DED/SED field masks to hardware counters.
- Vega10 power-management code in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_powertune.c` uses this DIDT family when platform capabilities such as DBR ramping and DIDT EDC are enabled.
- Nearby GC 9.x headers are similar but not interchangeable. For example, later GC 9.4 variants add or rename several EDC counter fields, so consumers must include the header that matches the detected IP version.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask can compile cleanly while enabling the wrong throttle bit, clearing the wrong reset bit, or decoding the wrong error counter.
- The chunk starts mid-register family. `DIDT_TCP_EDC_STALL_DELAY_4` shift definitions are in the previous chunk, while this chunk begins with only the four masks. Final file-level research must merge that boundary.
- DIDT/EDC control fields are side-effect sensitive. Enable/reset, force-stall, clock override, auto-release, throttle policy, and stall-delay fields can alter live GPU power and scheduling behavior.
- Several DBR control registers contain reserved or `UNUSED_*` fields. Full-register writes must be limited to documented programming tables or preserve reserved bits during read-modify-write.
- Pattern fields are 15 bits, not 16 bits, even though they are paired in 16-bit lanes with one reserved bit. Treating them as two full 16-bit values would set reserved bits.
- EDC stall delays differ by block. TCP delay fields in the tail of the previous family are 8-bit lanes, while DBR EDC delay fields in this chunk are two 3-bit fields plus reserved bits.
- Overflow and event counters can be live, sticky, saturating, or clear-sensitive depending on hardware semantics not encoded in this header. Sampling order matters for diagnostics.
- GC 9.0 EDC counter naming differs from later GC 9.4 headers. For example, this chunk has `TA_FS_AFIFO_SED_COUNT` and `TCI_WRITE_RAM_SED_COUNT`, while newer headers split some events into SEC/DED pairs. Blindly sharing decode tables across IP versions can misreport RAS events.
- The final `#endif` means accidental edits around this chunk can break the include guard for every GC 9.0 consumer, not just DIDT or RAS code.

## Test Signals

Useful validation should combine generated-data checks, build coverage, and hardware/runtime behavior:

- Build AMDGPU code paths that include `gc_9_0_sh_mask.h`, especially `gfx_v9_0.c`, `gmc_v9_0.c`, `soc15.c`, AMDKFD GFX v9 files, and Vega10 power-management files. Missing or renamed field macros should fail at compile time.
- Mechanically compare this range against AMD's authoritative GC 9.0 register database. Every complete field should have matching shift and mask values, masks should align to shifts, and reserved masks should cover only documented unused bits.
- Cross-check every register family in this chunk against `gc_9_0_offset.h` for matching `ixDIDT_*` or `mm*` address definitions.
- Run static sanity checks for repeated layouts: DBR stall-pattern registers should use 15-bit pattern masks plus one reserved bit per lane, DBR weight registers should contain four 8-bit lanes, and full-width counters should use `0xFFFFFFFFL`.
- Exercise Vega10 DIDT enable/disable paths with DBR ramping and DIDT EDC platform capabilities enabled. Expected signals include successful `PPSMC_MSG_ConfigureGfxDidt`, stable graphics operation, no unexpected forced stalls, and no reset loops.
- Validate EDC/RAS counter decoding on GC 9.0 hardware or simulator traces by injecting or observing TA, TCI, TCP, and TD SEC/DED/SED events and confirming the named fields in `gfx_v9_0.c` report the expected packed 2-bit values.
- During graphics stress and power-management tests, sample DIDT stall-event counters, EDC overflow state, throttle level, and rolling power delta to verify fields move plausibly and do not report impossible reserved-bit values.
- Regression signals include GPU hangs during DIDT setup, unexpected throttling or performance collapse, incorrect RAS counter names/counts, stale overflow reporting, or compile failures in SOC15 field helpers.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002627`. It covers lines 29721-30033 of `gc_9_0_sh_mask.h`, the final chunk of the file. The previous chunk owns the beginning of `DIDT_TCP_EDC_STALL_DELAY_4` and earlier TCP EDC definitions. The final per-file research should reconcile that artificial boundary and then treat this chunk as the DBR DIDT/EDC and terminal EDC-counter section of the generated GC 9.0 shift/mask header.
