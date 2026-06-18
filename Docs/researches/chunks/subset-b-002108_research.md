# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 46514-48830

## Purpose

This chunk is a generated shift/mask register-field slice for AMD DCN 3.5.1 display hardware. It has no executable functions or C types; its API surface is a large set of `#define` constants named as `<register>__<field>__SHIFT` and `<register>__<field>_MASK`. Consumers pair these constants with the matching `dcn_3_5_1_offset.h` register offsets and AMDGPU/DC register helper macros such as `FD_MASK`, `FD_SHIFT`, `REG_SET`, and `REG_UPDATE_*`.

The covered lines span several hardware areas: DisplayPort/USB4 DPIA RBBMIF status, Azalia/HDA controller 1 command and response rings, generic HDA global registers, DCCG and DMU clock/power controls, DMCUB security/scratch/interrupt fields, DWB/MCIF writeback watermark and pstate fields, DCHUBBUB memory arbitration and SDPIF security fields, HUBP/HUBPREQ/HUBPRET pipe memory status for pipes 0-3, DPP top-level pipe enables, MPCC movable color-management placement, and the beginning of MPCC MCM shaper/3DLUT/1DLUT color-management fields for instance 0 plus the start of MCM1 shaper fields.

## Important APIs and register groups

- `DPIA_MU_RBBMIF_STATUS` exposes invalid-access and timeout reporting fields, including `RBBMIF_INVALID_ACCESS_FLAG`, access type/address, timeout readback, and `RBBMIF_INVALID_ACCESS_STATUS_CLEAR`.
- `AZCONTROLLER1_*`, `GLOBAL_*`, `INTERRUPT_*`, `STREAM_SYNCHRONIZATION`, `CORB_*`, `RIRB_*`, and endpoint immediate-command fields describe HDA/Azalia control surfaces: command output ring buffer (CORB), response input ring buffer (RIRB), immediate verb writes, response reads, DMA position buffer base addresses, stream interrupt enable/status bits 0-15, wall clock, wake/state-change, global reset/flush, and 64-bit address/stream-count capabilities.
- `DCE_VERSION`, `DCCG_GATE_DISABLE_CNTL2/5/6`, `SYMCLK*`, `DSCCLK_DTO_CTRL`, `DPPCLK_CTRL`, `PHY*SYMCLK_CLOCK_CNTL`, `DMU_CLK_CNTL`, `DMU_*CGTT_BLK_CTRL_REG`, and `ZPR_CLK_UNGATE_DELAY` define clock gating, root gating, dynamic clock, symbol-clock, DSC, DPP, PHY, and DMU clock-control bits.
- `DISP_INTERRUPT_STATUS_CONTINUE23/25`, `DCPG_INTERRUPT_DEST2`, `DCPG_INTERRUPT_STATUS_3`, and `DCPG_INTERRUPT_CONTROL_2/3` define display interrupt status, routing, and enable fields for idle/power-gating domains and additional display events.
- `DOMAIN22` through `DOMAIN25` provide power-gating config/status bits (`DOMAIN_POWER_FORCEON`, `DOMAIN_POWER_GATE`, `DOMAIN_PGFSM_PWR_STATUS`, and `DOMAIN_PGFSM_READ_DATA`), while `LONO_MEM_PWR_REQ_CNTL`, `AZ_MEM_GLOBAL_PWR_REQ_CNTL`, `COMPBUF_MEM_PWR_CTRL_2`, and `MPCC_MCM0_MPCC_MCM_MEM_PWR_CTRL` expose memory power request/disable/state controls.
- `DMCUB_RBBMIF_SEC_CNTL`, `DMCUB_SEC_CNTL`, `DMCUB_REGION3_TMR_AXI_SPACE`, `DMCUB_INTERRUPT_STATUS`, `DMCUB_SMU_INTERRUPT_CNTL`, and `DMCUB_SCRATCH16` through `DMCUB_SCRATCH23` are the DMUB/DMCUB integration fields for trusted-region access, security mode, SMU interrupts, and firmware scratch mailboxes.
- `MCIF_WB_*`, `DWB_ENABLE_CLK_CTRL`, and `MMHUBBUB_CLOCK_CNTL` cover display writeback, MCIF writeback pstate/watermark latency, and MMHUBBUB clock gating.
- `DCHUBBUB_ARB_*` defines display memory arbitration controls: QoS force during pstate transitions, DRAM/cstate policy, UCLK/FCLK/user-retraining watermarks A-D, HostVM threshold control, watermark-change mode, and MALL enable/power policy.
- `DCHUBBUB_SDPIF_*` defines SDPIF config/security classification per pipe for normal data, no-allocate, metadata, DCC metadata, cursor, and GPUVM requests, plus request-rate limiting.
- `HUBP0` through `HUBP3` and `HUBPREQ0` through `HUBPREQ3` define per-pipe HUBP clock, virtual memory page, MALL/SubVP, debug/status, UCLK pstate force, request-status, and read-line control fields. The `HUBP*_HUBP_MALL_STATUS` groups are dense status bitmaps for MALL requests, responses, local/cursor prefetch, SubVP retrieve, outstanding DRQ/MRQ/CRQ work, and static-screen or pstate-related MALL use.
- `DPP_TOP0_DPP_CONTROL` through `DPP_TOP3_DPP_CONTROL` expose per-pipe DPP top-level enable bits.
- `MPCC0` through `MPCC3_MPCC_MOVABLE_CM_LOCATION_CONTROL` describe movable color-management placement: output CM, 3D LUT, shaper, and 1D LUT location selection.
- `MPCC_MCM0_*` is the largest group in this chunk. It defines shaper offsets/scales/index/data/write enables, shaper RAMA/RAMB piecewise-linear region start/end tables, 3DLUT mode/index/data/read-write/output-normalization/output-offset fields, 1DLUT mode/select/PWL-disable/current-state, LUT index/data/control fields, 1DLUT RAMA/RAMB start slopes/bases/ends/offsets/region tables, and MCM memory power controls. `MPCC_MCM1_*` begins the same shaper layout and reaches `MPCC_MCM1_MPCC_MCM_SHAPER_RAMA_REGION_12_13__...SHIFT` at the chunk boundary.

## Control flow and usage model

There is no local control flow. The generated constants are data for higher-level register tables. A typical consumer flow is:

1. Include `dcn_3_5_1_offset.h` and this shift/mask header for ASIC-specific addresses and bit encodings.
2. Build per-block register, mask, and shift tables with macros such as `SR`, `SF`, `HUBBUB_SF`, `DMUB_SF`, `FD_MASK`, and `FD_SHIFT`.
3. Let block code call register helpers to read, modify, or write fields without hardcoding bit positions.

The DCN 3.5.1 DMUB path includes this header in `display/dmub/src/dmub_dcn351.c`; `dmub_srv_dcn351_regs_init()` copies offsets, masks, and shifts into `dmub->regs_dcn35`. Hubbub code uses fields from this chunk through the DCN35/DCN32 register lists; for example `hubbub32_force_usr_retraining_allow()` updates `DCHUBBUB_ARB_ALLOW_USR_RETRAINING_FORCE_VALUE` and `DCHUBBUB_ARB_ALLOW_USR_RETRAINING_FORCE_ENABLE` in `DCHUBBUB_ARB_USR_RETRAINING_CNTL`. MPC headers for DCN32/DCN42 use the MPCC MCM fields to populate color-management register tables, including shaper, 3DLUT, and 1DLUT masks.

## State and persistence behavior

The header itself has no mutable state. The state lives in MMIO or indexed hardware registers and persists according to display hardware lifecycle: boot initialization, modeset/reprogramming, DC/DMCUB firmware init, runtime power-management transitions, suspend/resume, GPU reset, and display IP reset.

Several groups are explicitly stateful in hardware:

- HDA/Azalia CORB/RIRB pointers, DMA enables, base addresses, response interrupts, global reset/flush, and immediate-command busy/result bits track live audio-controller command flow.
- DCCG/DMU/DCPG/domain fields affect clock and power-gating state. Incorrect persistence can leave blocks gated while in use or force blocks on and increase power.
- DCHUBBUB watermarks and pstate/cstate policy fields control when memory clocks, fabric clocks, and user retraining may change. These values must track active timing, bandwidth, and safe-to-lower policy.
- HUBP MALL/SubVP status fields reflect transient cache/prefetch/retrieve/outstanding-request state. Some fields are diagnostic/status readbacks rather than software-owned controls.
- MPCC MCM shaper/3DLUT/1DLUT RAM index/data/control fields represent programmed color pipeline tables. The instance, RAM bank, channel, index, and write-enable fields must stay consistent while programming LUT contents.
- DMUB scratch/security/interrupt fields are shared with firmware and the SMU, so persistence and ordering matter across firmware handshakes.

## Dependencies and integration points

- Requires `dcn_3_5_1_offset.h` for the corresponding register addresses and base indices. Representative matches in that file include `regDCHUBBUB_ARB_USR_RETRAINING_CNTL`, `regHUBP0_HUBP_MALL_STATUS`, `regMPCC_MCM0_MPCC_MCM_SHAPER_CONTROL`, and `regAZCONTROLLER1_CORB_CONTROL`.
- Depends on AMDGPU/DC register macro infrastructure to turn generated names into table entries and field operations. The names must match exactly; there is no type checking for a misspelled field beyond compilation failures or unused orphan defines.
- Integrates with DMUB service initialization for DCN 3.5.1, the DC IRQ service for DCN 3.5.1, DC Hubbub watermarks/memory arbitration, HUBP memory/cache behavior, DCCG/DMU clock and power management, HDA display-audio control, and MPC color-management programming.
- Shares layouts with nearby DCN versions. Many fields in this chunk appear in DCN 3.2, 3.5.0, 4.1, and 4.2 generated headers, but some bitmaps differ by generation, especially MALL status fields and added/removed power/security controls. Cross-version copy assumptions are risky.

## Risks and edge cases

- Generated-header drift: offset and shift/mask headers must be regenerated as a pair. A valid mask with a stale offset silently targets the wrong hardware register.
- Packed-field corruption: many registers have adjacent control/status bits. Full-register writes can clobber reserved or status bits; callers should use read-modify-write helpers where appropriate.
- Width and sign errors: fields such as 8-bit ring pointers, 14-bit user-retraining watermarks, 16-bit UCLK/FCLK watermarks, 19-bit shaper offsets, 9-bit LUT offsets, and 3-bit segment counts require clamping before shifting.
- Instance mismatch: HUBP0-3, HUBPREQ0-3, DPP_TOP0-3, MPCC0-3, and MCM0/MCM1 fields repeat similar names. Using the wrong instance can make a bug look like a timing, cache, or color issue on only one pipe.
- Status versus control confusion: `*_STATUS`, `*_CURRENT`, `*_READBACK`, and MALL/HUBPREQ status fields are not necessarily software-owned. Writing status masks as if they were controls can acknowledge interrupts, clear diagnostics, or do nothing depending on hardware semantics.
- Power and clock hazards: `*_FORCEON`, `*_POWER_GATE`, clock-gating disable, low-power-mode, and memory-power fields can create hangs or excess power if changed outside the expected sequencing.
- Firmware handshake hazards: DMUB scratch, security, SMU interrupt, and RBBMIF fields may be accessed by firmware or secure paths. Reordering or unsynchronized host writes can break firmware-visible protocols.
- Color pipeline artifacts: MPCC MCM shaper/3DLUT/1DLUT programming is table- and bank-oriented. Wrong write-enable masks, bank selection, index increments, or region segment counts can cause visible color errors that only appear with HDR, color-managed, or multi-plane configurations.
- Boundary truncation: this chunk ends in the middle of the `MPCC_MCM1` shaper RAMA region definitions, so final per-file analysis must reconcile the continuation in the next chunk before drawing complete conclusions for MCM1.

## Test signals

- Build with DCN 3.5.1 enabled and ensure all consumers of `dcn_3_5_1_sh_mask.h` compile with matching `dcn_3_5_1_offset.h` symbols.
- Static consistency checks can compare field masks/shifts against generated offsets for representative registers and verify repeated pipe/instance groups have expected bit-identical layouts where the hardware block is repeated.
- Display bring-up and modeset tests should exercise pipes 0-3, HUBP MALL/SubVP paths, DPP enables, and MPCC color-management placement.
- Watermark and power tests should cover UCLK/FCLK pstate transitions, user retraining force/allow behavior, cstate/deepsleep policy, suspend/resume, and safe-to-lower watermark paths.
- Audio tests should cover HDMI/DP HDA enumeration, CORB/RIRB DMA operation, immediate command response handling, stream interrupts, and DMA position buffer behavior.
- DMUB/SMU tests should validate scratch mailbox handshakes, SMU interrupt signaling, DMCUB security enablement, and RBBMIF invalid-access reporting/clear behavior.
- Color-management tests should load shaper, 3DLUT, and 1DLUT tables, verify RAM bank/channel/index programming, and compare rendered output for SDR/HDR and color-managed modes.
- Runtime diagnostics should inspect register dumps around `HUBP*_HUBP_MALL_STATUS`, `HUBPREQ*_HUBPREQ_STATUS_REG*`, `DCHUBBUB_ARB_*`, and `MPCC_MCM*_MEM_PWR_CTRL` when debugging pstate stalls, MALL issues, power regressions, or color artifacts.
