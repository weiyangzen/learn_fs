# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h lines 34935-37498

## Scope

This chunk covers generated shift and mask macros from the GC 11.0.3 AMD GPU register mask header. It starts in the middle of the `GDS_PERFCOUNTER3_SELECT` family and ends at the `RLC_CLK_COUNT_REFCLK_MSB` register comment, just before that register's field definitions in the next chunk. The covered range includes:

- Performance counter selector fields for GDS, TA, TD, TCP, GL2C, GL2A, GL1C, CHC, CHCG, CB, DB, RLC, RMI, GCR, PA_PH, UTCL1, GL1A, GL1H, CHA, and GUS blocks.
- CB filtering fields for render-backend performance counter filtering.
- RLC streaming performance monitor (SPM), accumulator, ring buffer, RSPM request/response, and pause/status fields.
- GDFLL and GRTAVFS dynamic frequency/voltage and EDC hysteresis fields.
- Hypervisor, SR-IOV, RLC virtualization, doorbell, semaphore, scheduler, interrupt, microcode, scratch, and memory access fields.
- Pipe steering, harvest/user configuration, shader-array, primitive, render-backend, RMI redundancy, and TCC disable masks.
- Command processor hypervisor microcode, instruction-cache, data-cache, and MES/MEC/GFX RS64 memory-bound fields.
- GRBM hypervisor selection/data registers and per-VF framebuffer aperture fields.
- RLC core control, status, timers, legacy interrupts, clock-gating, power-gating delay, GPU clock counters, GPM thread reset/cache invalidation, and GPM CP DMA completion fields.

The file is purely a generated hardware register bitfield map. It defines preprocessor constants only: no C functions, structs, variables, storage, or executable control flow live in this chunk.

## Purpose

The purpose of this header section is to provide the bit-level ABI between AMDGPU driver code and GC 11.0.3 hardware registers. Each covered field is represented by the conventional pair:

- `<REGISTER>__<FIELD>__SHIFT`, the field's bit offset.
- `<REGISTER>__<FIELD>_MASK`, the 32-bit mask used to isolate or compose that field.

Driver code combines these constants with AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`. The sibling `gc_11_0_3_offset.h` file supplies register addresses such as `regRLC_SPM_PERFMON_CNTL`, `regRLC_GPU_IOV_VF_ENABLE`, `regCP_HYP_PFP_UCODE_ADDR`, `regGRBM_GFX_INDEX_SR_SELECT`, and `regGCMC_VM_FB_SIZE_OFFSET_VF0`; this file supplies the field positions and masks for those addresses.

## Important Macro Families

### Performance Counter Selection

The first half of the chunk is dominated by performance counter selector definitions. These families share a regular encoding:

- `*_PERFCOUNTER0_SELECT` often contains `PERF_SEL`, `PERF_SEL1`, `CNTR_MODE`, `PERF_MODE1`, and `PERF_MODE`.
- `*_PERFCOUNTER0_SELECT1` often adds `PERF_SEL2`, `PERF_SEL3`, `PERF_MODE2`, and `PERF_MODE3`.
- Later counters in the same block may be narrower and expose only `PERF_SEL` plus `PERF_MODE`, depending on the hardware block.

The covered blocks include GDS, TA, TD, TCP, GL2C, GL2A, GL1C, CHC, CHCG, CB, DB, RLC, RMI, GCR, PA_PH, UTCL1, GL1A, GL1H, CHA, and GUS. The consistent 10-bit selector masks such as `0x000003FFL` and mode fields in the upper nybbles reflect hardware-controlled event selection, counter mode, and multi-event packing.

`CB_PERFCOUNTER_FILTER` is more specialized. It defines enable/selector fields for operation, format, clear, MRT, sample count, and fragment count filters. This lets profiling or debug code restrict color-buffer performance counter samples by render-backend operation shape, not just choose the event source.

GUS adds separate mode/configuration/result-control registers (`GUS_PERFCOUNTER2_MODE`, `GUS_PERFCOUNTER0_CFG`, `GUS_PERFCOUNTER1_CFG`, and `GUS_PERFCOUNTER_RSLT_CNTL`) with flags for counter mode, mode 32/32+32/64, filter enables, math operation selection, increment behavior, clamp, and level/packet-style control.

### RLC Streaming Performance Monitor and Accumulator

The `RLC_SPM_*` block describes the streaming performance monitor path owned by RLC. Important registers include:

- `RLC_SPM_PERFMON_CNTL`, with ring mode, GFX clock count disable, and sample interval fields.
- `RLC_SPM_PERFMON_RING_BASE_LO/HI`, `RLC_SPM_PERFMON_RING_SIZE`, `RLC_SPM_RING_WRPTR`, and `RLC_SPM_RING_RDPTR`, which define the memory ring buffer and producer/consumer pointers used for streamed samples.
- `RLC_SPM_SEGMENT_THRESHOLD` and `RLC_SPM_PERFMON_SEGMENT_SIZE`, which divide global and shader-engine sample streams into segments.
- `RLC_SPM_GLOBAL_MUXSEL_*` and `RLC_SPM_SE_MUXSEL_*`, which address and write mux selection RAMs for global and per-SE sampling sources.
- `RLC_SPM_ACCUM_DATARAM_*`, `RLC_SPM_ACCUM_SWA_DATARAM_*`, `RLC_SPM_ACCUM_CTRLRAM_*`, and `RLC_SPM_ACCUM_CTRLRAM_ADDR_OFFSET`, which expose accumulator data/control RAM access.
- `RLC_SPM_ACCUM_STATUS`, `RLC_SPM_ACCUM_CTRL`, `RLC_SPM_ACCUM_MODE`, thresholds, requested sample counts, data RAM write count, and 32-bit counter region selectors.
- `RLC_SPM_PAUSE`, `RLC_SPM_STATUS`, `RLC_SPM_GFXCLOCK_LOWCOUNT`, `RLC_SPM_GFXCLOCK_HIGHCOUNT`, and `RLC_SPM_MODE`, which support pausing, status polling, clock count capture, and mode control.

Several fields are command-like strobes rather than durable configuration. For example, `RLC_SPM_ACCUM_CTRL__StrobeStartAccumulation`, `StrobeResetPerfMonitors`, `StrobeStartSpm`, `StrobeRearmAccum`, and `StrobePerfmonSampleWires` trigger actions in hardware. `RLC_SPM_ACCUM_STATUS` exposes completion, overflow, armed, FIFO empty, idle, pending rearm, and aborted state that consumers should poll or use for diagnostics.

### RSPM Request/Response Access

The `RLC_SPM_RSPM_*` and `RLC_SPM_SE_RSPM_*` fields define low-level request/response windows for RSPM operations. They expose request low/high data, request operation, returned data, returned operation/status, command fields, and command acknowledgement. These definitions are integration points for debug/performance paths that need indirect access to RSPM state and must respect busy/ack sequencing.

### Dynamic Frequency, Voltage, and EDC Hysteresis

The `GDFLL_*` and `GDFLL_SE_*` blocks provide EDC hysteresis control/status masks. They define maximum hysteresis counts and observed EDC/hysteresis status.

The `GRTAVFS_*`, `GRTAVFS_SE_*`, and `RTAVFS_*` blocks provide register-address, write-data, read-data, control, status, target-frequency, target-voltage, soft-reset, PSM, and clock-control fields for real-time adaptive voltage/frequency scaling. Key fields include:

- `SET_WR_EN` and `SET_RD_EN` command bits with status bits `RTAVFS_WR_ACK` and `RTAVFS_RD_DATA_VALID`.
- `TARGET_FREQUENCY` plus `REQUEST`.
- `TARGET_VOLTAGE` plus `VALID`.
- `RESETN_OVERRIDE`, PSM count/sample enable, and forced clock mux selection.

These fields describe hardware state that is usually coordinated with SMU/power-management policy. Incorrect writes can request the wrong frequency/voltage state or desynchronize indirect register accesses.

### Hypervisor, SR-IOV, and RLC Virtualization

The `gc_hypdec` portion defines masks for virtual function enablement, scheduling, doorbells, timers, semaphores, interrupt routing, microcode/scratch access, and SDMA/VM busy status. Important groups include:

- `GFX_PIPE_PRIORITY`, selecting high-priority graphics pipe behavior.
- `RLC_GPU_IOV_VF_ENABLE`, with `VF_ENABLE` and `VF_NUM` fields for SR-IOV function state.
- `RLC_GPU_IOV_CFG_REG*`, scheduler block metadata, command type/execute, function IDs, context size/location/offset, VM busy status, active function ID, and function-32 control/reset.
- `RLC_SDMA0_STATUS` through `RLC_SDMA7_STATUS` and matching busy-status registers for virtualization-visible SDMA state.
- `RLC_RLCV_TIMER_*` and `RLC_PACE_TIMER_STAT`, defining virtualized timer values, enable bits, auto-rearm, clear bits, and synchronized status.
- `RLC_GPU_IOV_VF_DOORBELL_STATUS`, `_SET`, `_CLR`, and `RLC_GPU_IOV_VF_MASK`, representing doorbell status and masks for VFs plus the PF bit.
- `RLC_HYP_SEMAPHORE_0..3`, exposing small `CLIENT_ID` fields for hypervisor-side synchronization.
- `RLC_GPU_IOV_INT_STAT`, `RLC_IH_COOKIE`, `RLC_IH_COOKIE_CNTL`, `RLC_GPU_IOV_INT_DISABLE`, `RLC_GPU_IOV_INT_FORCE`, and `RLC_GPU_IOV_SMU_RESPONSE`, which connect RLC virtualization state with interrupt handling and SMU responses.
- `RLC_HYP_RLCG_UCODE_CHKSUM`, `RLC_HYP_RLCP_UCODE_CHKSUM`, and `RLC_HYP_RLCV_UCODE_CHKSUM`, which expose microcode checksum fields.
- `RLC_GPU_IOV_UCODE_ADDR/DATA`, `RLC_GPM_UCODE_ADDR/DATA`, `RLC_PACE_UCODE_ADDR/DATA`, RLC IRAM/DRAM/ARAM accessors, LX6 scratch/IRAM/DRAM accessors, SRM accessors, and PACE/GPM scratch windows.

These macros back privileged flows. Many are only meaningful in PF, hypervisor, or firmware-loading contexts and should not be treated as ordinary graphics queue configuration.

### Pipe Steering, Harvesting, and User Configuration

`GL2_PIPE_STEER_0..3`, `GL1_PIPE_STEER`, and `CH_PIPE_STEER` map graphics pipes to GL2/GL1/cache channels. Each GL2 register packs four pipe-to-channel mappings for two quadrants, with 3-bit channel fields spaced every four bits. GL1 and CH steering use 2-bit fields per pipe.

`GC_USER_SHADER_ARRAY_CONFIG`, `GC_USER_PRIM_CONFIG`, `GC_USER_SA_UNIT_DISABLE`, `GC_USER_RB_REDUNDANCY`, `GC_USER_RB_BACKEND_DISABLE`, `GC_USER_RMI_REDUNDANCY`, `CGTS_USER_TCC_DISABLE`, and `GC_USER_SHADER_RATE_CONFIG` provide mask fields for harvested/disabled WGPs, primitive units, shader arrays, render backends, RMI repair, TCC disable state, and shader rate configuration. These registers are tied to fuse/harvest topology and user-visible graphics configuration. Wrong field programming can expose disabled units, hide valid units, or misroute traffic.

### Command Processor Hypervisor and Instruction/Data Cache Fields

The `gc_cphypdec` block defines command processor microcode and cache fields. It includes:

- Hypervisor and non-hypervisor PFP/ME/MEC address/data ports (`CP_HYP_PFP_UCODE_ADDR/DATA`, `CP_PFP_UCODE_ADDR/DATA`, `CP_HYP_ME_UCODE_ADDR/DATA`, `CP_ME_RAM_RADDR/WADDR/DATA`, `CP_HYP_MEC1/2_UCODE_ADDR/DATA`, and `CP_MEC_ME1/2_UCODE_ADDR/DATA`).
- Microcode checksum registers for PFP, ME, and MEC engines.
- PFP, ME, CPC, MES, MEC, and GFX RS64 instruction-cache/data-cache base low/high registers, bounds, VMID, cache policy, address clamp, execute disable, invalidation, invalidation-complete, prime, and primed bits.

Observed driver integration includes `amdgpu/gfx_v11_0.c`, which writes `regCP_HYP_PFP_UCODE_ADDR` while loading/querying PFP firmware state. The masks in this chunk describe how those address/data/checksum and cache-control registers are encoded for GC 11.0.3.

### GRBM Hypervisor and Per-VF Aperture Fields

The `gc_grbm_hypdec` block defines indirect selection/data fields for graphics register broadcast manager state:

- `GRBM_GFX_INDEX_SR_SELECT` selects index and PF/VF side through `VF_PF`.
- `GRBM_GFX_INDEX_SR_DATA` carries instance, shader array, shader engine, WGP, and broadcast flag fields.
- `GRBM_GFX_CNTL_SR_SELECT` and `GRBM_GFX_CNTL_SR_DATA` expose GRBM control selection/data.
- `GC_IH_COOKIE_0_PTR` and `GRBM_SE_REMAP_CNTL` define interrupt-cookie pointer and shader-engine remapping fields.

The `gc_gcvmsharedhvdec` block defines `GCMC_VM_FB_SIZE_OFFSET_VF0` through `VF15`, each with `VF_FB_SIZE` and `VF_FB_OFFSET` fields. These per-VF framebuffer aperture fields are part of virtualization memory partitioning.

### RLC Core Control, Timers, and Clock Counts

The `gc_rlcdec` block begins with `RLC_CNTL`, defining RLC enable, central queue enable, RLCM enable, SRM enable, clock-counter enable, sleep disable, save-and-restore enable, safe-mode enable, and invalidation behavior. Other covered RLC core fields include:

- `RLC_F32_UCODE_VERSION`, with version, breakpoint, and load-status fields.
- `RLC_STAT`, exposing request type, sleep, WFI, 3D-full, command-queue available, GFX clock off, and GPM idle state.
- `RLC_REFCLOCK_TIMESTAMP_LSB/MSB` and `RLC_GPU_CLOCK_COUNT_LSB/MSB`.
- `RLC_GPM_TIMER_INT_0..4`, `RLC_GPM_TIMER_CTRL`, and `RLC_GPM_TIMER_STAT`, providing five timer intervals, enable bits, auto-rearm bits, interrupt-clear bits, and synchronized status bits.
- `RLC_GPM_LEGACY_INT_STAT` and `RLC_GPM_LEGACY_INT_CLEAR`, covering SPP PVT interrupt changes, CP/RLC invalidation-pending changes, EOF, power-gating control changes, and a store/load timer expiry status.
- `RLC_INT_STAT`, with last CP/RLC interrupt ID and pending bit.
- `RLC_MGCG_CTRL` and `RLC_CLK_CNTL`, controlling medium-grain clock gating and clock-gating override domains.
- `RLC_JUMP_TABLE_RESTORE`, `RLC_PG_DELAY_2`, `RLC_CAPTURE_GPU_CLOCK_COUNT`, and `RLC_UCODE_CNTL`.
- `RLC_GPM_THREAD_RESET`, `RLC_GPM_CP_DMA_COMPLETE_T0/T1`, and `RLC_GPM_THREAD_INVALIDATE_CACHE`, defining per-thread reset, DMA completion, and cache-invalidation command/status bits.
- `RLC_CLK_COUNT_GFXCLK_LSB/MSB` and `RLC_CLK_COUNT_REFCLK_LSB`. The chunk ends at the `RLC_CLK_COUNT_REFCLK_MSB` comment, so its actual field macros belong to the next chunk.

## Control Flow and State Behavior

This header has no runtime control flow. It affects driver behavior at compile time by determining how C code composes and decodes 32-bit MMIO register values.

The persistent state described by this chunk is hardware state, not software state in the header. Important hardware state includes performance counter event selection, RLC SPM ring base/size/pointers, accumulator RAM and status, RTAVFS target frequency/voltage requests, VF enablement and per-VF framebuffer aperture state, hypervisor semaphores and doorbell status, CP microcode address/data/checksum ports, CP cache base/bound/control registers, GRBM instance selection, harvest/pipe steering state, RLC enable/status/timers/interrupt state, and clock counters.

Some fields are latched status bits, some are sticky interrupt/status bits, and some are write-one or strobe-style command bits. Examples include SPM accumulator strobes, RTAVFS read/write enable bits, RLC timer interrupt-clear bits, doorbell set/clear fields, instruction-cache invalidate/prime bits, GPM thread reset and cache-invalidate bits, and GPU clock capture. Consumers must use the sequencing rules in the owning AMDGPU code and hardware specification; the macros alone do not encode ordering, polling, or timeout policy.

## Dependencies and Integration Points

The chunk depends on the generated AMD register-header convention:

- `gc_11_0_3_offset.h` supplies register addresses and base indices for the names defined here.
- `gc_11_0_3_default.h` supplies reset/default values where available.
- AMDGPU register helper macros consume `__SHIFT` and `_MASK` definitions to build register values without hard-coded bit positions.

Observed or implied integration points in this source tree include:

- `amdgpu/gfx_v11_0.c`, which writes command processor hypervisor microcode address registers such as `regCP_HYP_PFP_UCODE_ADDR` during GFX initialization/firmware handling.
- GFX RLC initialization paths across `gfx_v*_0.c`, which use `RLC_CNTL__RLC_ENABLE_F32_MASK`-style definitions to enable, stop, or query RLC firmware state.
- KFD and queue-management code for GFX 11, which includes GC 11 register headers and relies on CP/MEC/MES register definitions when configuring compute queues and firmware-visible queues.
- Virtualization and SR-IOV code paths that pair `RLC_GPU_IOV_*`, per-VF `GCMC_VM_FB_SIZE_OFFSET_VF*`, `GRBM_*_SR_*`, and doorbell/status masks with PF/VF scheduling and partitioning.
- Performance/debug tooling paths that configure block-local perf counters and RLC SPM through selector, muxsel, ring, accumulator, and status registers.

Cross-generation similarity is high but not exact. For example, older GC 9/10 headers expose similar RLC GPM timer and SPM fields with different layouts, and GC 12 changes some CP and RLC doorbell/cache fields. Consumers must include the matching GC 11.0.3 offset/mask/default set.

## Risks

- Bitfield drift is high impact. A wrong mask or shift can write unrelated hardware fields, causing hangs, incorrect performance data, lost interrupts, firmware load failure, bad VF partitioning, or graphics/compute misconfiguration.
- Repeated performance counter families are easy to corrupt mechanically. Many blocks share similar names and layouts, but some counters omit `PERF_SEL1`, `CNTR_MODE`, or secondary select fields.
- RLC SPM and accumulator fields include both RAM address/data windows and strobe/status fields. Treating strobe bits as persistent configuration or missing busy/done/overflow polling can produce incomplete samples or deadlock debug flows.
- Virtualization fields are privilege-sensitive. Incorrect `VF_ENABLE`, `VF_NUM`, per-VF framebuffer aperture, doorbell, scheduler, or semaphore fields can break PF/VF isolation or scheduling.
- Power and frequency fields are not ordinary debug knobs. RTAVFS target frequency/voltage, PSM, soft-reset, and clock-control fields must remain coordinated with SMU and power-management policy.
- CP microcode and cache-control fields can affect firmware execution. Incorrect address widths, checksum handling, cache base/bounds, VMID, execute-disable, invalidate, or prime bits can prevent PFP/ME/MEC/MES firmware from running correctly.
- Harvest and steering fields must match actual hardware topology. Exposing disabled WGPs/RBs/TCCs or changing GL2/GL1/CH steering incorrectly can misroute traffic or cause hard-to-debug rendering faults.
- The chunk ends mid-family at `RLC_CLK_COUNT_REFCLK_MSB`; a final merged report must connect this document to the next chunk for the remaining clock-count and RLC doorbell fields.

## Test and Validation Signals

Useful validation is primarily build and integration coverage:

- Build AMDGPU, KFD, and display code paths that include `gc/gc_11_0_3_sh_mask.h`; this catches missing or renamed macros.
- GFX firmware-load tests should cover PFP/ME/MEC/MES address/data/checksum fields and CP instruction-cache/data-cache invalidation/prime behavior.
- RLC bring-up, suspend/resume, reset, and clock-gating tests should exercise `RLC_CNTL`, `RLC_STAT`, `RLC_MGCG_CTRL`, `RLC_CLK_CNTL`, timers, legacy interrupt status/clear, GPM thread reset, and clock counters.
- Performance-counter validation should verify block-local event selection for GDS/TA/TD/TCP/GL*/CH*/CB/DB/RLC/RMI/GCR/PA_PH/UTCL1/CHA/GUS and confirm CB filter fields restrict events as expected.
- RLC SPM tests should verify ring base/size/pointers, muxsel programming, accumulator mode/control/status, overflow reporting, pause/resume, and sample clock counts.
- SR-IOV validation should exercise VF enablement, function selection, per-VF framebuffer size/offset, doorbell set/clear/mask, scheduler state, SDMA busy/status, and interrupt cookie paths.
- Power-management or SMU-coordinated tests should confirm RTAVFS frequency/voltage requests, read/write acknowledge bits, and EDC hysteresis status do not regress.

## Unresolved Cross-Chunk References

This chunk starts after `GDS_PERFCOUNTER3_SELECT` has already begun and therefore does not include that register's comment or all of its field definitions. It also ends exactly at the `RLC_CLK_COUNT_REFCLK_MSB` comment and does not include the `COUNTER` shift/mask for that register or the following `RLC_CLK_COUNT_CTRL`, `RLC_CLK_COUNT_STAT`, and `RLC_RLCG_DOORBELL_CNTL` fields. The merge/reconciliation lane should stitch this chunk to adjacent chunks to describe complete register families.
