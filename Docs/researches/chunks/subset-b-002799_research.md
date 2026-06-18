# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_0_sh_mask.h lines 2378-4760

## Scope And Purpose

This chunk is the second slice of the AMDGPU MMHUB 3.0.0 register shift/mask header. It is a generated-style hardware definition file: every exposed bitfield is represented by preprocessor constants named `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. There are no C functions, structs, enums, variables, branches, loops, or executable initialization in this range.

The covered range starts at the tail of the `DAGB0_SDP_CGTT_CLK_CTRL` masks, then defines the full `DAGB0_SDP_LATENCY_SAMPLING` register. It then covers the `DAGB1` read-side DAGB client, arbitration, virtual-channel, pending/status, performance-counter, and SDP interface fields. The middle of the chunk switches to the `mmhub_pctldec` power/control block, including deep-sleep controls, power-gating/deep-sleep allow masks for UTCL2 and slices, RENG/stctrl save ranges, PCTL status, PCTL performance counters, and reserved registers. The final part covers L1 TLB status and performance-counter masks, `MM_ATC_L2` translation/cache controls, fixed-frame-buffer mapping (`MMUTCL2_FFBM`) controls, and the beginning of `MMVM_L2` cache/invalidation controls.

The chunk ends at line 4760 after the first four `MMVM_L2_CNTL3` shift macros. The rest of `MMVM_L2_CNTL3` masks and later MMVM L2 registers are intentionally outside this chunk and must be reconciled with the next chunk.

## Important APIs, Types, And Constants

There are no callable APIs or C types. The public interface is the macro namespace consumed by AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15*`, and `WREG32_SOC15*` after this header is included with its companion offset header.

Important macro families in this chunk:

- `DAGB0_SDP_LATENCY_SAMPLING`: sampler enable and selector fields for DRAM, GMI, IO, read, write, atomic-return, atomic-no-return, and virtual-channel latency sampling. This completes the small DAGB0 tail inherited from the previous chunk boundary.
- `DAGB1_RDCLI0` through `DAGB1_RDCLI23`: per-read-client policy registers. Each client uses the same layout: `VIRT_CHAN`, `CHECK_TLB_CREDIT`, urgency high/low thresholds, max/min bandwidth enable and value fields, OSD limiter enable, and max outstanding request limit.
- `DAGB1_RD_CNTL`, `DAGB1_RD_IO_CNTL`, and `DAGB1_RD_GMI_CNTL`: shared read-path arbitration and fabric controls, including client/VC max-bandwidth windows, shared VC count, round-robin enable, IO level-compliance/override controls, GMI credits, GMI level, max burst, and lazy timer.
- `DAGB1_RD_ADDR_DAGB`, `DAGB1_RD_ADDR_DAGB_MAX_BURST0-2`, and `DAGB1_RD_ADDR_DAGB_LAZY_TIMER0-2`: read-address DAGB enablement, jump-ahead, self-init-disable, `WHOAMI`, and packed per-client burst/lazy-timer fields.
- `DAGB1_RD_VC0_CNTL` through `DAGB1_RD_VC5_CNTL`, plus `DAGB1_RD_IO_VC_CNTL` and `DAGB1_RD_GMI_VC_CNTL`: read virtual-channel credit and QoS controls, including storage credits, EA credits, max/min bandwidth controls, OSD limiter fields, and max outstanding counts. MMHUB 3.0.0 exposes six numbered read VCs here rather than a full `VC0-VC7` sequence in this chunk.
- `DAGB1_RD_CNTL_MISC`, `DAGB1_RD_TLB_CREDIT`, `DAGB1_RD_RDRET_CREDIT_CNTL`, and `DAGB1_RD_RDRET_CREDIT_CNTL2`: storage-pool credits, UTCL2 VCI, legacy read-return cache-coherency mode, packed TLB0-TLB5 credits, and read-return per-VC credits.
- `DAGB1_RDCLI_*_PENDING`, `DAGB1_FIFO_EMPTY`, `DAGB1_FIFO_FULL`, and `DAGB1_RD_CREDITS_FULL`: full-width or packed status bitmaps for internal read-client pipeline stages, FIFO state, and credit-full conditions.
- `DAGB1_RDCLI_NOALLOC_OVERRIDE` and `DAGB1_RDCLI_NOALLOC_OVERRIDE_VALUE`: 16-bit enable/value maps for no-allocate override policy.
- `DAGB1_CNTL_MISC`, `DAGB1_CNTL_MISC2`, and clock-gating controls such as `DAGB1_RD_CGTT_CLK_CTRL`, `DAGB1_L1TLB_RD_CGTT_CLK_CTRL`, and `DAGB1_SDP_CGTT_CLK_CTRL`: delay, bandwidth-gap/init cycles, parity, urgent halt/boost, clock-gating disable, and busy-override fields.
- `DAGB1_PERFCOUNTER_LO/HI`, `DAGB1_PERFCOUNTER0_CFG` through `2_CFG`, and `DAGB1_PERFCOUNTER_RSLT_CNTL`: DAGB1 performance-counter result, compare, event select, mode, enable, clear, trigger, global clear/enable, and stop-on-saturate fields.
- `DAGB1_SDP_*`: SDP read bandwidth, priority override, read priority, client-to-SDP VC map, enable, credits, tag reserve, VCC reserve, error status, request control, misc, arbitration, clock-gating, and latency-sampling fields. `DAGB1_SDP_ERR_STATUS` is especially stateful because it includes status nibbles, data-parity flag, clear bit, fatal-interrupt controls, level interrupt, and busy-on-error controls.
- `PCTL_CTRL`: MMHUB power-control fields for power-gating enable, deep-sleep mode, stctrl idle thresholds, protection-fault ignore, UTCL2 legacy mode, SDP disconnect mode, ZSC timer, Z9 power down/up, SNR disable, and write-ack guard.
- `PCTL_MMHUB_DEEPSLEEP_IB`, `PCTL_MMHUB_DEEPSLEEP_OVERRIDE`, `PCTL_MMHUB_DEEPSLEEP_OVERRIDE_IB`, `PCTL_PG_IGNORE_DEEPSLEEP`, and `PCTL_PG_IGNORE_DEEPSLEEP_IB`: bitmaps for deep-sleep input bits, override bits, and power-gating ignore-deep-sleep bits across `DS0-DS16`, `DS_ATHUB`, and `ALLIPS` variants. Some include `SETCLEAR` high-bit semantics.
- `PCTL_SLICE0_*` and `PCTL_SLICE1_*`: per-slice DAGB write/read busy selectors, deep-sleep allow/allow-IB masks, misc controls, RENG execution controls, RENG RAM index/data, and STCTRL register-save ranges/exclusion sets.
- `PCTL_UTCL2_*`: UTCL2 misc, RENG execution, RENG RAM index/data, and STCTRL register-save range/exclusion fields.
- `PCTL_STATUS`: status bits for MMHUB config done, interlock enable, fence request/ack, MMHUB idle, power-gating FSM command status, MMHUB power, and stale RENG RAM indicators for global, UTCL2, slice0, and slice1 RAMs.
- `PCTL_PERFCOUNTER_LO/HI`, `PCTL_PERFCOUNTER0_CFG`, `PCTL_PERFCOUNTER1_CFG`, and `PCTL_PERFCOUNTER_RSLT_CNTL`: PCTL counter results, compare value, event selection, enable/clear controls, start/stop triggers, and stop-on-saturate control.
- `PCTL_RESERVED_0` through `PCTL_RESERVED_3`: reserved register fields. They preserve generated register-map shape and should not be treated as safe write targets without hardware guidance.
- `MMMC_VM_MX_L1_TLB0_STATUS` through `TLB5_STATUS`: per-L1-TLB busy, parity-error-found, and aperture-fault-found status fields.
- `MMMC_VM_MX_L1_PERFCOUNTER0_CFG` through `3_CFG`, `MMMC_VM_MX_L1_PERFCOUNTER_RSLT_CNTL`, and `MMMC_VM_MX_L1_PERFCOUNTER_LO/HI`: L1 TLB performance-counter controls and readback fields.
- `MM_ATC_L2_CNTL`, `CNTL2`, `CACHE_DATA0-2`, `CNTL3-5`, `MM_GROUP_RT_CLASSES`, `STATUS`, `STATUS2`, `MISC_CG`, `MEM_POWER_LS`, `CGTT_CLK_CTRL`, and `SDPPORT_CTRL`: ATC L2 translation request counts, cache invalidation mode, default-page behavior, GPA request fragmentation, bank/cache update controls, cache-data readback fields, fragment sizes, ATS request credit, transaction limits, real-time class bitmap, busy/outstanding-request status, parity error info, clock/memory power controls, and SDP port clock-enable handshakes.
- `MMUTCL2_FFBM_CONFIG`, `ACCESS_CNTL`, `ADDRESS`, `DATA`, `INVALIDATE_REQUEST`, and `INVALIDATE_RESPONSE`: fixed-frame-buffer mapping TLB page size, request/grant handshake, VFID/address selection, valid/read/write/fragment/FB_SPA data fields, and invalidate request/ack fields.
- `MMVM_L2_CNTL`, `MMVM_L2_CNTL2`, and the beginning of `MMVM_L2_CNTL3`: MMVM L2 cache enable, fragment processing, endian swap modes, PDE0 tag generation, LRU update behavior, default page-out behavior, split/queue/cache-address modes, PDE fault classification, identity mode, L1/L2 invalidation request bits, per-domain invalidate disable, big-K optimization disable, VMID/cache invalidation modes, PDE cache size, and the first `MMVM_L2_CNTL3` update/bank fields.

## Control Flow And State Behavior

This header has no direct runtime control flow. It provides constants that compile into call sites performing MMIO register reads, writes, or read-modify-write sequences. The effective control flow is in AMDGPU MMHUB implementation files, especially code that uses `REG_SET_FIELD` and `WREG32_SOC15` against offsets from `mmhub_3_0_0_offset.h`.

Runtime state lives in GPU MMHUB hardware registers, not in this file. The DAGB1 read-path fields configure routing and QoS for read clients: virtual-channel selection, urgency thresholds, max/min bandwidth windows, outstanding request limits, TLB-credit checking, read-return credits, and SDP request/priority/VC mapping. Pending, FIFO, credit-full, and error-status fields expose live hardware pipeline state. Performance-counter fields are stateful controls for hardware accumulation, clearing, event selection, and result latching.

The PCTL fields drive power-management state for MMHUB blocks. `PCTL_CTRL` and deep-sleep/ignore/allow bitmaps affect whether MMHUB, UTCL2, and slice blocks can enter or ignore deep-sleep/power-gated states. RENG RAM and STCTRL save-range fields are part of register-engine/save-restore behavior around low-power transitions. `PCTL_STATUS` exposes the observable handshake state: config completion, interlock, fences, idle state, power state, command status, and stale RAM indicators.

The L1 TLB and ATC/MMVM L2 fields describe the virtual-memory translation path. L1 status registers report busy and fault/error findings. L1/PCTL/DAGB counters expose hardware event counts. ATC L2 and MMVM L2 controls configure translation request credits, cache update behavior, cache invalidation, fragment sizes, default-page behavior, status polling, and fixed-frame-buffer mapping. `MMUTCL2_FFBM_ACCESS_CNTL` and invalidate request/response pairs represent hardware handshakes: software requests access or invalidation and must observe grant/ack bits according to the hardware programming sequence.

Persistence is hardware-local and reset/power-state dependent. This header does not save register state, restore it after suspend, serialize MMIO access, poll status, or distinguish read-only, write-one-to-clear, sticky, or reserved fields. Those semantics must come from the ASIC programming guide and the driver code using these constants.

## Dependencies And Integration Points

The direct companion file is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_0_offset.h`, which supplies the `reg*` offsets and base indices for the register names used here. Examples from that offset file include `regDAGB1_RDCLI0` at `0x00b8`, `regPCTL_CTRL` at `0x0380`, `regMM_ATC_L2_CNTL` at `0x06c0`, `regMMUTCL2_FFBM_CONFIG` at `0x06d4`, and `regMMVM_L2_CNTL` at `0x0700`.

The main in-tree consumer for this exact generation is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0.c`, which includes `mmhub/mmhub_3_0_0_offset.h` and `mmhub/mmhub_3_0_0_sh_mask.h`. Its VM initialization path programs `MMVM_L2_CNTL`, `MMVM_L2_CNTL2`, and `MMVM_L2_CNTL3` using these masks, then writes the corresponding MMHUB registers. Later suspend/disable paths clear `MMVM_L2_CNTL` and `MMVM_L2_CNTL3`. The same conceptual MMVM L2 fields are used by adjacent generation implementations such as `mmhub_v3_0_2.c`, `mmhub_v3_3.c`, and `mmhub_v4_1_0.c`, but those must include their own generation-specific register headers.

DAGB1, PCTL, SDP, L1 TLB, ATC L2, and FFBM macros may be used by firmware bring-up code, debug/register-dump paths, power-management flows, performance-counter tooling, or future driver changes even when this tree's active MMHUB v3.0 code only uses a subset. The generated macro namespace must therefore stay aligned with the hardware offset file, the ASIC IP discovery data, and any scripts or tools that decode register dumps.

## Risks And Edge Cases

- The file is a hardware ABI. A wrong mask or shift can silently program the wrong bitfield while compiling cleanly, causing VM translation failures, stale TLB/cache contents, incorrect power transitions, or distorted performance counters.
- The repeated `DAGB1_RDCLI0-23` layout is easy to misread. A single copied field with the wrong client number could affect only one read client and be hard to diagnose without per-client traffic tests.
- Packed fields are common: client, VC, deep-sleep, TLB, counter, and cache-fragment fields often occupy adjacent 1-, 2-, 3-, 4-, 5-, 6-, 7-, 8-, or 10-bit ranges. Off-by-one shifts can produce plausible register values that target a neighboring client or selector.
- Full-width masks such as `0xFFFFFFFFL` should be handled as unsigned 32-bit register values. Signed promotion or debug formatting can make register dumps misleading.
- Status and control fields are mixed in the same header without access-mode metadata. Fields named `CLEAR`, `ACK`, `REQUEST`, `GRANT`, `BUSY`, `STATUS`, `FOUND_*`, and `*_ERROR_*` may be read-only, sticky, write-one-to-clear, pulse, or handshake fields depending on hardware semantics.
- PCTL power/deep-sleep fields are high risk because incorrect writes can prevent MMHUB from idling, power down an active block, lose register-engine state, or mask a protection fault during power transitions.
- Translation-cache and invalidation fields are high risk because stale VM/ATC/MMVM state can produce DMA to stale physical pages or persistent page faults. `INVALIDATE_ALL_L1_TLBS`, `INVALIDATE_L2_CACHE`, FFBM invalidation request bits, and status/ack bits must be sequenced by real driver logic, not blindly toggled from masks.
- Reserved PCTL fields preserve generated map shape, not software permission to write those bits.
- The chunk boundary splits `MMVM_L2_CNTL3`; whole-file research must use the next chunk before making complete statements about that register's masks.

## Test And Validation Signals

There are no direct unit tests for this macro-only header. Useful validation signals are compile-time, static, and hardware-facing:

- Build AMDGPU code paths that include `mmhub_3_0_0_sh_mask.h`, especially `drivers/gpu/drm/amd/amdgpu/mmhub_v3_0.c`, and treat warnings or undefined macro errors as integration failures.
- Run static mask/shift consistency checks: each mask should be contiguous after right-shifting by its shift value; single-bit masks should match `1U << shift`; repeated packed fields should not overlap; full-width fields should have shift zero.
- Cross-check every register-comment group in this chunk against `mmhub_3_0_0_offset.h` for a matching `reg*` offset and base index.
- Compare the repeated `DAGB1_RDCLI*`, deep-sleep bitmap, slice0/slice1, L1 TLB status, and performance-counter layouts against adjacent MMHUB generation headers only as a sanity check. Exact values remain generation-specific.
- On supported hardware, verify MMHUB v3.0 VM bring-up by observing `mmhub_v3_0.c` writes to `MMVM_L2_CNTL`, `MMVM_L2_CNTL2`, and `MMVM_L2_CNTL3`, then checking that VM/GART initialization, page-table updates, and TLB/cache invalidation paths do not report MMHUB protection faults.
- For PCTL changes, exercise suspend/resume, runtime power management, deep-sleep entry/exit, and register dumps around `PCTL_STATUS` to confirm fence, idle, power, and stale-RAM bits transition as expected.
- For DAGB1/SDP/performance-counter changes, run memory/display workloads with register dumps or perf-counter reads to confirm traffic counters, error status, and latency-sampling fields behave monotonically or clear as expected.

## Chunk Notes For Merge Lane

This chunk covers the DAGB1 read-side and SDP section, the full PCTL block present in this range, L1 TLB status/performance counters, ATC L2 and FFBM controls, and the start of MMVM L2 controls for `mmhub_3_0_0_sh_mask.h`. It is not a whole-file report. The final per-file document should merge this with chunk 1 for the beginning of DAGB0, chunk 3 for the rest of `MMVM_L2_CNTL3` and later MMVM/MMEA sections, and chunk 4 for the file tail and include-guard closure.
