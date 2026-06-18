# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h lines 40270-42638

## Purpose

This chunk is generated AMDGPU MMHUB 9.4.1 register bitfield metadata. It defines C preprocessor `*_SHIFT` and `*_MASK` constants for the end of the `MMEA7` register family, all visible `mmhub_pctldec1` `PCTL1` power/control fields, the `VML1_1` L1 TLB status block, L1 performance-counter configuration/result fields, the `ATCL2_1` ATC L2 translation-cache block, and the first fields of `VML2PF1_VM_L2_CNTL`.

Although this repository path is under `distributed-fs/ceph-client`, the file is Linux AMD GPU driver hardware metadata, not Ceph filesystem logic. It has no executable behavior and no filesystem persistence.

The covered range provides field layouts for:

- The tail of `MMEA7_ADDRDEC2_RM_SEL_*`, `ADDRNORM*`, IO client/group mapping, read/write IO priority, SDP arbitration, SDP credit/reserve, latency/performance-counter, EDC, DSM/error-injection, clock-gating, error-status, and address-decoder selection registers.
- `PCTL1_CTRL`, deep-sleep/override/ignore registers, per-slice deep-sleep allow/busy bits, slice/UTCL2 misc controls, register-engine execute/index/data windows, and per-slice state-controller register-save ranges/exclusion sets.
- `VML1_1_MC_VM_MX_L1_TLB0..7_STATUS` busy and parity status fields.
- `VML1PL1_MC_VM_MX_L1_PERFCOUNTER0..3_CFG`, shared result control, and `VML1PR1` low/high counter readback fields.
- `ATCL2_1_ATC_L2_*` controls, cache-data inspection words, status/parity fields, clock/memory light-sleep controls, DSM error-injection controls, active transaction limits, and MM real-time class mapping.
- The first `VML2PF1_VM_L2_CNTL` fields at the chunk boundary, covering L2 cache enable, fragment processing, endian swap modes, PDE tag generation/split mode, LRU update-by-write, and default-page-out behavior. Later `VML2PF1` fields belong to the next chunk.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, callbacks, locks, allocations, or direct MMIO reads/writes in this chunk. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset of a field in a 32-bit MMHUB register.
- `<REGISTER>__<FIELD>_MASK` gives the corresponding unshifted register mask.

High-signal macro groups include:

- `MMEA7_IO_*`: client-ID to group maps for read/write CIDs 0-31, per-group age/queue/fixed/urgency priorities, urgency masking bitmaps, priority quanta, and read/write combine flush fields.
- `MMEA7_SDP_*`: DRAM/GMI/final burst arbitration, readonly VC flags, error event/halt request controls, per-target priority maps, tag and response credits, per-VC tag/VCC/VCD reserves, and request control.
- `MMEA7_EDC_*`, `MMEA7_DSM_*`, `MMEA7_ERR_STATUS`: SEC/DED counters, fault/event disposition, FED/FUE behavior, DSM error-injection setup, and error-status clear/busy flags for DRAM, IO, GMI, return-tag, command, data, and page memories.
- `PCTL1_*`: power-gating enable, deep-sleep permissions and overrides, per-slice `DS_ALLOW` and `CFG_DAGB_BUSY` state, register-engine execution, register-engine RAM windows, critical-register locks, state-controller save ranges, and exclusion sets for UTCL2 plus slices 0-4.
- `VML1_1_*` and `VML1PL1`/`VML1PR1_*`: L1 TLB busy/parity status and performance-counter selection, mode, enable, clear, trigger, saturation, and 48-bit result/compare fields.
- `ATCL2_1_*`: ATS/ATC translation read/write request credits, host translation request credits, cache invalidation mode, bank select, cache update/VMID/tag-index controls, cache-data readback, parity status, clock/light-sleep controls, DSM injection/counters, transaction limits, and MM group real-time classes.
- `VML2PF1_VM_L2_CNTL`: the opening VM L2 control fields for cache enablement, fragment processing, PTE/PDE endian swap, PDE0 tagging/split, LRU update-by-write, and default-page-out routing.

These masks are normally paired with register offsets from `mmhub_9_4_1_offset.h` and consumed by AMDGPU SOC15 helpers such as `SOC15_REG_FIELD`, `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15`. The offset header supplies the register address; this header supplies how to pack or decode each 32-bit value.

## Control Flow

This header chunk has no runtime control flow. It affects runtime behavior only through C preprocessing.

Typical consumer flow is:

1. MMHUB 9.4.x driver code includes `mmhub_9_4_1_offset.h` and `mmhub_9_4_1_sh_mask.h`.
2. Initialization, golden-register, power-management, VM hub, diagnostics, or error-reporting code selects a register by offset macro.
3. The code constructs or decodes fields with the generated `__SHIFT` and `_MASK` constants, often through AMDGPU field helpers.
4. SOC15 MMIO helpers perform the actual read or write against MMHUB hardware.

The header does not encode sequencing rules. It does not state when queues are idle, when deep-sleep or power-gating bits are firmware-owned, when cache invalidation has completed, how to clear sticky error status safely, or when register-engine commands are allowed. Those constraints live in MMHUB implementation code, firmware protocols, hardware specifications, and companion default/offset headers.

## State And Persistence Behavior

No software state is stored here. The macros describe hardware register state.

The represented hardware state includes:

- Persistent-until-reprogrammed configuration: MMEA7 address decoding, IO client grouping, priority/burst/credit policy, SDP arbitration, PCTL1 power/deep-sleep controls, PCTL1 save/restore windows, ATCL2 translation-cache modes, and the initial VM L2 control bits.
- Live or status-like state: MMEA7 error status, L1 TLB busy/parity status, ATCL2 busy/parity status, performance-counter result registers, and EDC SEC/DED counter fields.
- Trigger/control state: performance-counter `ENABLE`, `CLEAR`, `CLEAR_ALL`, start/stop triggers, `STOP_ALL_ON_SATURATE`, PCTL register-engine execute-now fields, MMEA7 error-status clear, and DSM write/error-injection controls.
- Debug and test state: DSM index/control registers and cache-data windows expose cache internals or inject errors for 4K/2M ATC L2 cache paths and MMEA7 internal memories.

Persistence is hardware-defined. Configuration registers may survive until reset, power-gating reset, suspend/resume restore, driver reinitialization, or explicit reprogramming. Status/counter fields can change continuously with traffic. This generated mask file cannot distinguish read-only, write-one-to-clear, write-trigger, sticky, firmware-owned, debug-only, or reserved semantics beyond the field names.

## Dependencies

This chunk depends on the generated AMDGPU register stack for MMHUB 9.4.1:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_offset.h` provides the matching `mm<REGISTER>` offsets and base indices. The searched offset file contains matching entries for `PCTL1_*`, `VML1_1_*`, `ATCL2_1_*`, and `VML2PF1_*`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c` includes this mask header and uses `MMEA7_EDC_CNT*` and `MMEA7_ERR_STATUS` fields through SOC15 register-entry/field helpers for error-counter and reset/error handling tables.
- AMDGPU SOC15 register helpers and field macros consume the `*_SHIFT`/`*_MASK` constants to build register values and decode readbacks.
- Adjacent chunks of the same header are required for a complete per-file view. This chunk starts in the middle of `MMEA7_ADDRDEC2_RM_SEL_CS01` and ends inside `VML2PF1_VM_L2_CNTL`.

Sibling MMHUB generation headers are structurally similar but not interchangeable. Cross-generation names can compile while pointing at different bit layouts or offsets.

## Integration Points

Primary integration points are:

- MMHUB 9.4 driver initialization and golden-register programming for memory-hub arbitration, address decoding, VM translation caches, and power behavior.
- Error reporting and recovery paths in `amdgpu/mmhub_v9_4.c`, especially MMEA7 EDC counter reporting and error-status handling.
- GPUVM and IOMMU/ATS-related translation flows that rely on ATCL2, VML1, and VM L2 state for page translation, invalidation, cache policy, fault/default-page handling, and parity reporting.
- Power-management flows that program `PCTL1_CTRL`, deep-sleep override/ignore registers, per-slice allow registers, register save ranges, and clock/light-sleep controls.
- Diagnostics and profiling flows that use MMEA7 and L1 performance counters, TLB busy/parity status, ATCL2 status, cache-data windows, and DSM injection/counter fields.
- Multi-slice MMHUB programming. The repeated `PCTL1_SLICE0..4` field layouts imply looped or table-driven programming must pair each slice register offset with the exact same field definitions.

## Risks And Edge Cases

- Wrong-generation pairing is the main risk. Using MMHUB 9.4.1 masks with another generation's offsets or driver assumptions can silently pack the wrong bits.
- The chunk boundaries are artificial: it starts after the first two fields of `MMEA7_ADDRDEC2_RM_SEL_CS01` and ends before the rest of `VML2PF1_VM_L2_CNTL`. The later merge lane must combine adjacent chunks before treating either register family as complete.
- Repeated slice and client layouts invite text substitution bugs. `PCTL1_UTCL2_*` differs from `PCTL1_SLICE*_*` in index widths and execute pointer masks, so helpers must not assume all PCTL register-engine windows are identical.
- IO priority, urgency masking, credit, burst, and reserve fields are liveness- and performance-sensitive. Bad values can cause bandwidth throttling, unfair arbitration, downstream queue pressure, or memory-hub timeout symptoms.
- PCTL deep-sleep, power-gating, register-save, and critical-register-lock fields can interact with firmware or reset/resume sequencing. Updating them while blocks are active can lose state or destabilize access.
- ATCL2 cache invalidation, ATS request credits, bank selection, cache update mode, and VMID behavior affect translation correctness. Incorrect programming can surface as VM faults, stale translations, invalidation hangs, or host-translation stalls.
- Status/counter fields should not be treated as ordinary writable configuration unless the hardware spec explicitly says so. Error-status clear and DSM injection bits can destroy diagnostic evidence or intentionally create faults.
- `SETCLEAR`, execute-now, clear, and write-counter fields are command-like; read-modify-write helpers must preserve intended one-shot semantics.

## Test Signals

Useful validation signals include:

- Build coverage for AMDGPU MMHUB 9.4 paths that include `mmhub_9_4_1_offset.h` and `mmhub_9_4_1_sh_mask.h`.
- Static consistency checks that every field has both `__SHIFT` and `_MASK`, repeated slice/client families use expected masks, and offset/mask/default headers remain synchronized for MMHUB 9.4.1.
- Boot/init tests on ASICs using MMHUB 9.4.1, with attention to MMHUB bring-up, golden-register programming, VM hub setup, and error-counter table registration.
- GPUVM stress tests that exercise mapping/unmapping, TLB invalidation, ATS/ATC paths, mixed read/write IO traffic, page faults, and default-page-out behavior while checking for MMHUB faults or hangs.
- Power-management tests covering suspend/resume, reset, BACO/runtime power transitions, deep-sleep entry/exit, and state-controller register save/restore behavior.
- Diagnostic tests that read MMEA7 EDC/error status, L1 TLB parity/busy status, ATCL2 parity/busy status, and performance-counter results under known traffic.
- Regression indicators include ring timeouts, VM faults, stale translations after invalidation, parity/FED/FUE reports, unexpected EDC count increments, persistent busy bits after traffic drains, power-transition failures, or unexpected bandwidth/latency changes after register programming.
