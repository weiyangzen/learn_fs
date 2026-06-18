# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h lines 27047-29638

## Purpose

This chunk is generated AMD GC 11.0.3 register bitfield metadata. It contains 2,134 preprocessor definitions across 426 register names and no executable C. The public contract is a set of `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` constants used by AMDGPU register helpers to compose or decode 32-bit MMIO values for this graphics IP revision.

The range begins at the tail of shader debug/trap address registers (`SQ_SHADER_TBA_*`, `SQ_SHADER_TMA_*`), then covers PF-only command processor, HPD queue, DIDT/EDC, SPI debug, TCP, GDS, UTCL1, PMM/GCR, GC CAC/EDC/throttle, per-SE CAC weighting, PF-only2 SPI compute-unit resource reservation, and a large `gc_gfxudec` command-processor user-data/control section. It ends inside `CP_ME_COHER_CNTL`; the remaining coherency-size/base/status fields continue after this chunk boundary.

Although the repository subtree is named `ceph-client`, this file is AMD GPU driver hardware metadata, not distributed filesystem logic.

## Important APIs, Types, and Macros

This header defines no functions, structs, enums, callbacks, locks, allocations, or runtime variables. Its API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit for a field.
- `<REGISTER>__<FIELD>_MASK` gives the in-register mask.
- Address-block comments such as `// addressBlock: gc_pfonly_cpdec` and register comments such as `//CP_DFY_CNTL` preserve the generated hardware grouping.

The companion address metadata for this ASIC lives in `gc_11_0_3_offset.h`. In this tree, exact include users are `amdgpu/gfx_v11_0_3.c`, `amdgpu/imu_v11_0_3.c`, and `amdgpu/gfxhub_v3_0_3.c`. Consumers typically reach these constants through `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and related SOC15 helpers.

Major register groups in this chunk:

- Shader trap/debug base registers: `SQ_SHADER_TBA_LO/HI`, `SQ_SHADER_TMA_LO/HI`, and the preceding `SQ_DEBUG` tail define trap base/memory address halves and trap enable state.
- PF-only CP decode: `CP_DEBUG_2`, `CP_FETCHER_SOURCE`, and the `CP_DFY_*` register set describe secure/debug override bits, packet/discard controls, DFY address/data windows, burst/tag status, and command size.
- HPD queue decode: `CP_HPD_MES_ROQ_OFFSETS`, `CP_HPD_ROQ_OFFSETS`, and `CP_HPD_STATUS0` expose IQ/PQ/IB offsets, queue state, mapped queue, availability, fetch state, offload checking, freeze, and force-queue controls.
- DIDT/EDC decode: `DIDT_INDEX_AUTO_INCR_EN`, `DIDT_EDC_*`, `DIDT_IND_INDEX`, and `DIDT_IND_DATA` describe dynamic power/thermal throttling, error detection controls, stall patterns, thresholds, status, overflow, rolling power delta, and indirect register access.
- SPI/TCP/GDS/UTCL1/PMM blocks: `SPI_CDBG_*`, `SPI_GDBG_*`, `SPI_RESET_DEBUG`, `SPI_ARB_CNTL_0`, `SPI_FEATURE_CTRL`, `SPI_SHADER_RSRC_LIMIT_CTRL`, `SPI_COMPUTE_WF_CTX_SAVE_STATUS`, `TCP_*`, `GDS_*`, `UTCL1_*`, `GCR_*`, and `PMM_CNTL2` provide shader debug, arbitration, resource-limit, wave context-save, texture-cache, global data-share, L1 translation, and global cache request controls/status.
- GC CAC/EDC/throttle block: `GC_CAC_*`, `SE*_CAC_*`, `GC_EDC_*`, `GC_THROTTLE_*`, `PCC_*`, `PWRBRK_*`, and `DIDT_STALL_PATTERN_*` define activity counter windows, aggregate counters, power/EDC throttle controls, stall-pattern generators, hysteresis, counters, status, overflow, and clock monitor controls.
- CAC weight tables and indirect windows: `GC_CAC_WEIGHT_*`, `SE_CAC_WEIGHT_*`, `GC_CAC_IND_INDEX/DATA`, and `SE_CAC_IND_INDEX/DATA` encode per-block activity weights for CP, EA, UTCL2, GDS, GE, PMM, GL2C, PH, SDMA, RLC, GRBM, TA, TD, TCP, SQ, SP, LDS, SQC, CU, CB/DB, SPI, PA/SC, and related graphics blocks.
- PF-only2 SPI resource reservation: `SPI_RESOURCE_RESERVE_CU_0..15` and `SPI_RESOURCE_RESERVE_EN_CU_0..15` reserve VGPR, SGPR, LDS, wave, and barrier resources per CU and enable reservation categories/accumulation behavior.
- GFX user decode command-processor registers: `CP_EOP_DONE_*`, many graphics pipeline statistic counters, scratch registers and atomics, append/fence/GDS atomic preop registers, ME MC read/write address/data registers, semaphore wait/signal addresses, DMA PFP/ME controls and commands, IB/ST command buffer controls, indirect draw/dispatch/index/GDS backup addresses, sample status, and the start of CP ME coherency controls.

## Control Flow

There is no runtime control flow in this header. Runtime control flow belongs to consumers that include this generated metadata:

1. A GFX11.0.3-specific driver file includes `gc_11_0_3_offset.h` and `gc_11_0_3_sh_mask.h`.
2. The code chooses a register offset with generated `reg*`/`mm*` symbols from the offset header.
3. It uses the shift/mask constants in this file to build or decode a 32-bit register value.
4. It reads or writes the register through SOC15 MMIO helpers, indirect register windows, firmware-programmed RLC RAM entries, interrupt handlers, debug paths, or reset/recovery logic.

For this ASIC, `gfx_v11_0_3.c` uses the same generated family to decode RLC FED interrupt status and dispatch RAS handling. `imu_v11_0_3.c` programs RLC RAM golden settings through GC register addresses and masks, including generated debug mask constants outside this specific line range. `gfxhub_v3_0_3.c` uses the GC 11.0.3 mask contract for VM invalidation and fault-status decoding. This chunk supplies adjacent CP, SPI, EDC, CAC, UTCL1, and GFX user-register field layouts that those same include environments can use for initialization, diagnostics, and ASIC workarounds.

## State and Persistence Behavior

The macros themselves have no state and persist nothing. They describe volatile hardware state exposed through GC 11.0.3 MMIO registers.

Some represented registers are durable configuration until reset, suspend/resume, power gating, SR-IOV transition, or explicit driver/firmware reprogramming. Examples include SPI resource reservation, shader trap base addresses, CP debug overrides, UTCL1/GCR controls, CAC/EDC thresholds, throttle controls, command buffer base/size registers, indirect draw/dispatch/index addresses, and CP coherency destination enables.

Other registers are live status or latched diagnostic state. HPD queue state, DIDT/EDC status, TCP status, GCR command status, CAC aggregate counters, EDC/performance counters, overflow bits, throttle status, scratch atomics, append/fence state, CP DMA command status, PFP completion status, and sample activity bits can change as firmware and GPU work progress. The header does not encode read-only, write-one-to-clear, self-clearing, firmware-owned, or reserved-bit semantics, so consumers must use hardware-specific sequencing and preserve unrelated fields on mixed control registers.

Indirect windows such as `DIDT_IND_INDEX/DATA`, `GC_CAC_IND_INDEX/DATA`, and `SE_CAC_IND_INDEX/DATA` have ordering-sensitive state: the index register selects which underlying register the data register targets. Interleaved reads/writes without the driver-side serialization expected by the register access path can decode or update the wrong target.

## Dependencies and Integration Points

Direct dependencies and integration points:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h` provides matching register offsets and base indices. This chunk is not useful by itself without the address metadata.
- `amdgpu/gfx_v11_0_3.c` includes this header for GC 11.0.3 RAS/FED interrupt handling and generated register access.
- `amdgpu/imu_v11_0_3.c` includes this header while programming GC 11.0.3 RLC RAM golden register settings used during initialization.
- `amdgpu/gfxhub_v3_0_3.c` includes this header for VM hub setup, invalidation request construction, FB/aperture programming, and protection-fault status decoding.
- Common AMDGPU register helpers (`REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`) consume the generated shift/mask names.
- RAS, debugfs/register dump, firmware, power-management, SR-IOV, KFD/debug, shader trap, performance counter, and GPU reset paths can depend on these field definitions even if a given macro is not referenced by the small GC 11.0.3 wrapper files directly.

The `gc_pfonly_*` and `gc_pfonly2_*` blocks are especially tied to privileged/PF-only access. Driver code must respect virtualization and firmware ownership boundaries; a macro being visible in the header does not imply it is legal for a VF or all runtime paths to write.

## Risks and Edge Cases

- Generated metadata can fail silently if numeric values are wrong. A bad mask or shift usually still compiles but can enable the wrong bit, truncate an address, poll the wrong status, or corrupt a power/throttle policy.
- The chunk has artificial boundaries. It starts after the first `SQ_DEBUG` fields and ends before the rest of the CP ME coherency register family, so complete per-register analysis requires adjacent chunks.
- Register/ASIC mismatches are high risk. Pairing GC 11.0.3 masks with another generation's offset header can compile while accessing different hardware fields.
- PF-only registers must not be treated as ordinary userspace or VF-safe controls. CP debug overrides, DIDT/EDC throttle controls, CAC weights, SPI resource reservation, and coherency controls can affect global GPU behavior.
- Address fields are often split into low/high halves and may have alignment semantics. CP EOP, pipe stats, append, DMA command, IB/ST, doorbell-buffer, indirect draw/dispatch/index, GDS backup, semaphore, and coherency base/size fields can misaddress memory if low-bit masks or shifts are misapplied.
- Indirect register pairs are ordering-sensitive. DIDT and CAC index/data windows can return stale or unintended data if accessed concurrently without the expected locking or hardware access discipline.
- Power and reliability controls have non-obvious side effects. DIDT/EDC, CAC, PCC, PWRBRK, throttle, hysteresis, stall pattern, and clock-monitor fields can change performance, thermal behavior, RAS visibility, or validation reproducibility.
- CP DMA, semaphore, append, scratch atomic, EOP, and coherency fields are synchronization-critical. Incorrect programming can break fence completion, cache flush/invalidation, indirect-buffer execution, draw/dispatch setup, or GPU reset recovery.
- Status bits are live. Queue availability, busy/idle, overflow, throttle, sample activity, completion, and counter fields can race with active GPU work, so tests and diagnostics need stable quiescing or repeated polling.

## Test Signals

Useful validation is mostly build-time, static consistency, and hardware/runtime coverage:

- Build all GC 11.0.3 paths that include `gc_11_0_3_sh_mask.h`, especially `gfx_v11_0_3.c`, `imu_v11_0_3.c`, and `gfxhub_v3_0_3.c`.
- Run generated-header consistency checks: each referenced field has both shift and mask definitions, masks align with shifts, register names match `gc_11_0_3_offset.h`, and artificial chunk boundaries are reconciled by adjacent research chunks.
- Boot/probe GC 11.0.3 hardware and confirm GFX, IMU/RLC RAM programming, gfxhub VM setup, and RAS/FED interrupt paths initialize without register-access faults.
- Exercise VM invalidation and protection-fault reporting through gfxhub workloads; fault status should decode plausible client IDs and permission/mapping bits.
- Run graphics and compute workloads that stress CP EOP fences, indirect draw/dispatch, IB/ST command buffers, CP DMA, semaphores, scratch registers, append buffers, GDS atomic preops, and sample-status reporting.
- Validate suspend/resume, GPU reset, and SR-IOV/PF-VF scenarios, watching for illegal PF-only access, stuck queue/status bits, missing fences, or RLC/CP recovery failures.
- Check power/RAS diagnostics under stress: DIDT/EDC counters and overflows, CAC aggregate and weight readbacks, throttle status, PCC/PWRBRK/DIDT stall pattern behavior, and RAS error paths should be coherent and recoverable.
- Debug/profiling signals include sane SPI resource reservation state, shader trap base address handling, TCP/GDS/UTCL1/GCR status readbacks, CP pipe statistics, scratch atomic behavior, PFP completion status, and CP ME coherency status once adjacent coherency fields are included.
