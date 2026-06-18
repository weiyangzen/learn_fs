# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_3_0_sh_mask.h lines 1-2367

## Purpose

This chunk is generated AMDGPU MMHUB 9.3.0 register bitfield metadata for the opening portion of `mmhub_9_3_0_sh_mask.h`. It defines C preprocessor `*_SHIFT` and `*_MASK` constants for the `mmhub_dagbdec` address block, covering all visible `DAGB0` read/write arbitration fields and the beginning of `DAGB1` read arbitration fields.

Although the repository path is under `distributed-fs/ceph-client`, this file is Linux AMD GPU driver hardware metadata, not Ceph filesystem code. It has no executable logic and no filesystem persistence behavior.

The covered range provides field layouts for:

- `DAGB0_RDCLI0..15`: per-read-client virtual-channel routing, TLB-credit checking, urgency thresholds, max/min bandwidth controls, OSD limiter enablement, and max outstanding depth.
- `DAGB0_RD_CNTL`, `DAGB0_RD_GMI_CNTL`, and `DAGB0_RD_ADDR_DAGB`: read-side clock/window, GMI credit/level/burst/timer, DAGB enable/jump-ahead/self-init, and identity fields.
- `DAGB0_RD_OUTPUT_DAGB_*`, `DAGB0_RD_ADDR_DAGB_*`: per-VC and per-client max-burst and lazy-timer field maps for read outputs and read address routing.
- `DAGB0_RD_CGTT_CLK_CTRL`, `DAGB0_L1TLB_RD_CGTT_CLK_CTRL`, and `DAGB0_ATCVM_RD_CGTT_CLK_CTRL`: read-side clock-gating and light-sleep override fields for the DAGB, L1 TLB, and ATC/VM paths.
- `DAGB0_RD_VC0..7_CNTL`, `DAGB0_RD_CNTL_MISC`, `DAGB0_RD_TLB_CREDIT`, and read pending status registers: read virtual-channel credits, storage/EA/IO pools, legacy modes, UTCL2 client ID, TLB credits, and outstanding busy bitmaps.
- `DAGB0_WRCLI0..15`: write-client equivalents of the per-client virtual-channel, TLB-credit, urgency, bandwidth, OSD limiter, and max outstanding fields.
- `DAGB0_WR_CNTL`, `DAGB0_WR_GMI_CNTL`, `DAGB0_WR_ADDR_DAGB`, `DAGB0_WR_OUTPUT_DAGB_*`, `DAGB0_WR_ADDR_DAGB_*`, and `DAGB0_WR_DATA_DAGB*`: write-side arbitration, address/data DAGB, burst, and timer layouts.
- `DAGB0_WR_VC0..7_CNTL`, `DAGB0_WR_CNTL_MISC`, `DAGB0_WR_TLB_CREDIT`, `DAGB0_WR_DATA_CREDIT`, `DAGB0_WR_MISC_CREDIT`, and write pending status registers: write virtual-channel and data/atomic/OSD credit fields plus busy bitmaps.
- `DAGB0_DAGB_DLY`, `DAGB0_CNTL_MISC`, `DAGB0_CNTL_MISC2`, FIFO/credit-full flags, performance counter result/configuration registers, and reserved full-width placeholders.
- `DAGB1_RDCLI0..15` through `DAGB1_RD_CNTL_MISC`: the start of the second DAGB instance's read-side client, common control, GMI, address DAGB, output burst/timer, clock-gating, address burst/timer, VC control, and misc credit fields. This chunk ends immediately after `DAGB1_RD_CNTL_MISC__STOR_POOL_CREDIT_MASK`; the rest of `DAGB1_RD_CNTL_MISC` and following DAGB1 write-side/register groups belong to later chunks.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, variables, callbacks, locks, allocations, or direct MMIO accesses in this chunk. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for a field in a 32-bit MMHUB register.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted field mask in the register word.
- Repeated register families intentionally share identical field layouts across clients or virtual channels. For example, every `DAGB0_RDCLI<n>` and `DAGB1_RDCLI<n>` in this range exposes `VIRT_CHAN`, `CHECK_TLB_CREDIT`, `URG_HIGH`, `URG_LOW`, `MAX_BW_ENABLE`, `MAX_BW`, `MIN_BW_ENABLE`, `MIN_BW`, `OSD_LIMITER_ENABLE`, and `MAX_OSD`.

High-signal field families include:

- Arbitration routing and priority: `VIRT_CHAN`, `URG_HIGH`, `URG_LOW`, `EA_VC<n>_REMAP`, `SHARE_VC_NUM`, `IO_LEVEL`, and `IO_LEVEL_COMPLY_VC`.
- Bandwidth and outstanding-request limiting: `MAX_BW_ENABLE`, `MAX_BW`, `MIN_BW_ENABLE`, `MIN_BW`, `OSD_LIMITER_ENABLE`, `MAX_OSD`, `CLI_MAX_BW_WINDOW`, `VC_MAX_BW_WINDOW`, `BW_INIT_CYCLE`, and `BW_RW_GAP_CYCLE`.
- Credit and deadlock controls: `STOR_CREDIT`, `EA_CREDIT`, `STOR_POOL_CREDIT`, `EA_POOL_CREDIT`, `IO_EA_CREDIT`, `TLB0..3`, `VMC0..1`, `VM_L2`, `ATOMIC_CREDIT`, `DLOCK_VC_NUM`, `OSD_CREDIT`, and `OSD_DLOCK_CREDIT`.
- Clock/power gating controls: `ON_DELAY`, `OFF_HYSTERESIS`, `SOFT_STALL_OVERRIDE`, `LS_OVERRIDE`, per-direction light-sleep override bits, and `DISABLE_*_CG` fields.
- DAGB datapath setup: `DAGB_ENABLE`, `ENABLE_JUMP_AHEAD`, `DISABLE_SELF_INIT`, `WHOAMI`, per-VC/per-client `MAX_BURST`, and `LAZY_TIMER`.
- Observability and debugging: `*_PENDING__BUSY`, FIFO empty/full flags, credit-full flags, `PERFCOUNTER_LO/HI`, `PERFCOUNTER<n>_CFG`, `PERFCOUNTER_RSLT_CNTL`, and full-width `RESERVE<n>` placeholders.

These masks are normally paired with register offsets from `mmhub_9_3_0_offset.h` and consumed by AMDGPU helpers/macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and table-driven golden-setting or diagnostics code. The offset header supplies where to read/write; this header supplies how to pack or decode fields in the 32-bit value.

## Control Flow

This chunk has no runtime control flow. Its effect is through C preprocessing.

Typical consumer flow is:

1. MMHUB 9.3.0-specific driver code includes `mmhub_9_3_0_offset.h` and `mmhub_9_3_0_sh_mask.h`.
2. Code reads a register value with a SOC15 MMIO helper or constructs a new value for a register such as a `DAGB*_*_CNTL`/credit/control register.
3. It packs or extracts fields with the generated `__SHIFT`/`_MASK` constants, often through AMDGPU field helpers.
4. Runtime MMHUB init, golden-register programming, power/clock-gating setup, VM hub bring-up, debugging, or performance-counter code performs the actual MMIO transaction.

The header itself does not encode sequencing constraints. It does not say when DAGB clients are idle, when it is safe to change arbitration or credit limits, how to drain pending bitmaps, whether a field is sticky, or whether a register is firmware-owned. Those rules live in the MMHUB implementation files, firmware protocols, hardware specifications, and companion default/offset headers.

## State And Persistence Behavior

No software state is stored here. The macros describe hardware state in MMHUB DAGB decoder registers.

The represented hardware state includes:

- Persistent-until-reprogrammed configuration: client-to-VC routing, urgency thresholds, max/min bandwidth policy, OSD limits, SCLK/window fields, GMI credits, DAGB enable/jump-ahead/self-init, VC remapping, burst limits, lazy timers, credit pools, and clock-gating overrides.
- Live or status-like state: pending busy bitmaps, FIFO empty/full fields, read/write credit-full indicators, and performance counter low/high result values.
- Trigger/control state: performance counter `ENABLE`, `CLEAR`, `CLEAR_ALL`, `START_TRIGGER`, `STOP_TRIGGER`, and `STOP_ALL_ON_SATURATE` fields can alter counter collection behavior.
- Reserved placeholders: `DAGB0_RESERVE0..17` expose full-width masks for reserved registers/slots. Their presence preserves generated register-map shape but does not imply safe software use.

Persistence is hardware-defined. Configuration fields may survive until ASIC reset, suspend/resume, power-gating reset, driver reinitialization, or explicit reprogramming. Status and counter fields may change continuously with traffic. The generated mask file cannot distinguish read-only, write-one-to-clear, write-trigger, debug-only, or reserved semantics.

## Dependencies

This chunk depends on the generated AMDGPU/SOC15 register stack:

- `mmhub_9_3_0_offset.h` provides the matching MMHUB 9.3.0 register offsets for the field names described here.
- Later chunks of `mmhub_9_3_0_sh_mask.h` complete the same header, including the rest of `DAGB1_RD_CNTL_MISC` and later DAGB1/MMHUB field families.
- SOC15 register helpers and AMDGPU field helpers consume these macros to build register values and decode readbacks.
- MMHUB implementation files, VM hub setup, power-management code, diagnostics, and golden-register programming depend on these field definitions matching the hardware register database for MMHUB 9.3.0.

The sibling MMHUB headers (`mmhub_9_1`, `mmhub_9_4_1`, `mmhub_4_*`, `mmhub_3_*`, and older `mmhub_1_*`/`2_*`) are structurally similar but not interchangeable. Cross-generation field names can compile while producing invalid bit packing if paired with the wrong ASIC generation.

## Integration Points

Primary integration points are:

- MMHUB 9.3.0 driver code that includes the corresponding offset and mask headers for initialization, register programming, suspend/resume restore, and debug paths.
- GPUVM/MMHUB setup paths that rely on the memory hub to arbitrate read/write traffic between memory clients, virtual channels, ATC/VM, L1 TLB, VM L2, storage/EA pools, and GMI/IO paths.
- Clock and power management flows that program `*_CGTT_CLK_CTRL`, light-sleep override, soft-stall override, and clock-gating disable fields.
- Performance and diagnostic flows that inspect `*_PENDING`, FIFO/full-credit status, and `DAGB0_PERFCOUNTER*` fields to diagnose stalls, bandwidth limits, or arbitration behavior.
- Golden-register or bring-up tables that write conservative hardware-recommended defaults for DAGB arbitration, credit, burst, timer, and clock-gating fields.
- Multi-instance MMHUB code. The nearly mirrored `DAGB0` and `DAGB1` names imply instance-like programming patterns; later code may compute register distances or loop over instances using paired offset macros while using these masks for common fields.

## Risks And Edge Cases

- Wrong generation pairing is the main risk. Using `mmhub_9_3_0_sh_mask.h` with offsets or driver code for a different MMHUB generation can silently pack the wrong bits.
- This chunk boundary is artificial and cuts through `DAGB1_RD_CNTL_MISC`; any per-file summary must merge later chunks before treating the DAGB1 field set as complete.
- Repeated layouts invite copy/paste or looped programming, but read-client, write-client, address-DAGB, data-DAGB, and VC-control registers have different field sets. A shared helper must select the exact register family, not just substitute `RD`/`WR` or `DAGB0`/`DAGB1` textually.
- Credit, bandwidth, and outstanding-depth fields are performance- and liveness-sensitive. Bad values can throttle memory traffic, overcommit downstream queues, create unfair arbitration, or contribute to timeout/deadlock symptoms.
- `CHECK_TLB_CREDIT`, TLB credit fields, ATC/VM clock controls, and VM L2 credit fields affect address translation paths. Incorrect programming can surface as VM faults, invalidation stalls, or memory-access hangs rather than obvious register errors.
- Clock-gating and light-sleep overrides can cause power regressions or access instability if toggled while queues are active or if firmware expects ownership.
- Pending/FIFO/credit-full fields are status-like; treating them as ordinary writable configuration would be unsafe unless the hardware spec explicitly says otherwise.
- Performance counter clear/enable fields can lose diagnostic state or skew profiling if written during active collection.
- Reserved full-width fields should not be used as a license to write arbitrary values. They are generated placeholders for reserved register slots.

## Test Signals

Useful validation signals include:

- Build coverage for MMHUB 9.3.0 AMDGPU paths that include `mmhub_9_3_0_offset.h` and `mmhub_9_3_0_sh_mask.h`.
- Static consistency checks that every field has both `__SHIFT` and `_MASK`, that repeated client/VC families use expected masks, and that this header remains synchronized with the generated offset/default headers for MMHUB 9.3.0.
- Boot/init tests on ASICs using MMHUB 9.3.0, with attention to VM hub setup, memory hub init, golden-register programming, and power-management transitions.
- GPUVM stress tests that allocate mappings, trigger TLB/VM traffic, perform invalidations, and run mixed read/write workloads while checking for VM faults, invalidation timeouts, or MMHUB hangs.
- Suspend/resume, BACO, reset, and runtime power-management tests that confirm DAGB arbitration and clock-gating settings are restored correctly.
- Performance-counter/debug tests that program `DAGB0_PERFCOUNTER*`, read low/high results, clear counters, and correlate pending/FIFO/credit status with known traffic.
- Regression indicators include ring timeouts, memory-client stalls, MMHUB/GPUVM faults, unexpected bandwidth throttling, power-management failures, incorrect performance-counter readings, or debug status that shows persistent pending/credit-full conditions after traffic drains.
