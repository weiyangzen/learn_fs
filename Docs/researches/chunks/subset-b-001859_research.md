# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h lines 1-2652

## Scope

This chunk covers lines 1-2652 of the generated AMD DCN 3.1.5 register offset header. The range starts at the file license and include guard `_dcn_3_1_5_OFFSET_HEADER`, then defines generated `reg*` register-offset constants grouped by `// addressBlock:` comments.

The source is a C preprocessor interface only. It contains no C functions, structs, enums, variables, inline helpers, allocation paths, or executable statements. The requested range contains 2,357 `reg*` `#define` entries: 1,179 register-offset macros and 1,178 `reg*_BASE_IDX` companion macros. The count is intentionally uneven for this chunk because line 2652 is `regHUBPREQ1_DCSURF_FLIP_CONTROL2`; its `_BASE_IDX` companion is the next line outside the assigned range.

## Purpose

This header provides the offset half of the generated DCN 3.1.5 display-controller register ABI used by AMDGPU display code. Consumers combine these offsets with DCN base segment constants, register access helper macros, and the companion `dcn_3_1_5_sh_mask.h` field definitions to read or program display hardware.

Although the tree path is under a local `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed-filesystem behavior.

This opening chunk maps low-address DCN 3.1.5 hardware areas:

- Display clock generator (`DCCG`) and DCCG perfmon: pixel/DP/DSC/DPP/DTB/audio DTO controls, PHY PLL pixel-rate/resync controls, clock gates, GTC/current time-base registers, vsync latch/count registers, soft reset, and perfmon instances 0-1.
- DMU, DMCU, RBBMIF, interrupt-host-controller, foreground-security, display power-gating, and DMCUB: firmware memory windows, ERAM/IRAM access, master/slave communication, interrupt routing, power state, DMCUB region/code-window/inbox/outbox/timer/scratch/fault/control registers, and DMU perfmon.
- Display writeback and MCIF/MMHUBBUB: DWB top controls, DWB color/gamut/OGAM programming, writeback perfmon, MCIF writeback buffer address/status/pitch/watermark/QoS/VMID registers, MMHUBBUB warmup, memory power, clocks, reset, outstanding counters, and error status.
- Legacy VGA direct MMHUBBUB/VGA aliases: VGA memory page, render/control/status, CRTC/ATTR/GRPH/SEQ/DAC/GEN register windows, source-select, source-split, and related compatibility controls.
- Azalia/HDA audio direct registers: controller clock/DMA/CORB/RIRB/CRC controls, F0 codec root parameters, stream index/data windows for streams 0-15, endpoint index/data windows for output endpoints 0-7 and input endpoints 0-7, plus AZ perfmon.
- DCHUBBUB and request/return paths: arbitration watermarks A-D, self-refresh/DRAM clock-change controls, host VM and SDPIF address-window registers, DCC return-path config/statistics, CRC, compbuf/DET controls, VM context page-table registers, VM fault/status registers, hubbub perfmon, HUBP0 and HUBP1 surface/viewport/request registers, HUBPREQ0/HUBPREQ1 address/flip/prefetch/timing registers, HUBPRET0 read-line registers, and cursor0/DMDATA registers.

## Important APIs, Types, And Macros

There are no callable APIs or type definitions in this range. The public interface is the generated macro namespace:

- `reg<REGISTER_NAME>`: a direct DCN 3.1.5 register offset.
- `reg<REGISTER_NAME>_BASE_IDX`: the base-address segment selector used by helpers that compute the final MMIO address.
- `// addressBlock: ...` and `// base address: ...`: generated grouping comments that identify the hardware block and local block base represented by the following register names.

The main access contract is visible in DCN315 consumers. They define segment constants such as `DCN_BASE__INST0_SEG0` through `DCN_BASE__INST0_SEG5`, then use token-pasting helpers equivalent to `BASE(regNAME_BASE_IDX) + regNAME`. `display/dmub/src/dmub_dcn315.c` names this pattern explicitly as `REG_OFFSET_EXP(reg_name)`.

All direct registers in this chunk use base index values 0, 1, or 2:

- Base index 0 appears on early VGA memory page registers.
- Base index 1 appears on DCCG and many direct VGA compatibility registers.
- Base index 2 dominates DMU/DMCUB/DWB/MMHUBBUB/AZ/DCHUBBUB/HUBP/HUBPREQ/HUBPRET/cursor and perfmon registers.

The chunk does not contain `ix*` indexed-register constants. Every visible hardware symbol in the assigned range is a `reg*` direct offset, with the one line-boundary exception noted above for `regHUBPREQ1_DCSURF_FLIP_CONTROL2_BASE_IDX`.

## Control Flow

This header has no local runtime control flow. Runtime behavior is supplied by AMDGPU display code that includes this offset header with its matching shift/mask header.

The normal flow is:

1. DCN315-specific code includes `dcn/dcn_3_1_5_offset.h` and `dcn/dcn_3_1_5_sh_mask.h`.
2. A register-list macro chooses a symbolic register, such as `DMCUB_INBOX0_WPTR`, `DCHUBBUB_ARB_WATERMARK_CHANGE_CNTL`, `HUBP0_DCSURF_SURFACE_CONFIG`, `HUBPREQ0_DCSURF_PRIMARY_SURFACE_ADDRESS`, or `AZALIA_CONTROLLER_CLOCK_GATING`.
3. Token-pasting helpers form the final MMIO address from `BASE(reg..._BASE_IDX) + reg...`.
4. Field helpers from `dcn_3_1_5_sh_mask.h` pack or unpack individual bits.
5. Driver paths use register helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, and wait/poll helpers to program clocks, firmware mailboxes, power domains, interrupts, audio, writeback, memory arbitration, scanout surfaces, cursor, and VM state.

The macros do not encode hardware ordering. Consumers must still sequence clock enables, power gating, firmware setup, DMCUB mailbox initialization, interrupt clear/ack, display hub watermarks, VM context programming, surface flips, cursor updates, writeback buffer programming, and Azalia stream/endpoint setup according to the hardware spec.

## State And Persistence Behavior

The header stores no software state and persists nothing to disk. It describes MMIO-backed GPU display state.

State domains represented in this range include:

- DCCG clock state: DTO phase/modulo values, clock enables/gates, pixel-rate controls, GTC/current time-base counters, audio DTOs, vsync latch/count state, and soft reset.
- DMU/DMCU/DMCUB firmware state: firmware address ranges, ERAM/IRAM access windows, checksums, scratch registers, interrupt masks/status/selectors, master/slave communication registers, region/code-window mappings, inbox/outbox pointers, timers, GPINT data, undefined-address fault reporting, wake interrupt state, and DMCUB control registers.
- Writeback/MMHUBBUB state: DWB flow/color/CRC/output controls, OGAM/gamut/LUT programming, MCIF writeback buffer addresses and status, watermarks, VMID/QoS, DRAM/SCLK speed-change handling, warmup controls, memory power, clocks, reset, and outstanding counters.
- HDA/Azalia state: controller clock and DMA controls, codec root parameters, stream index/data windows, endpoint index/data windows, audio DTO, CRC controls/results, memory power, and stream/endpoint codec access.
- DCHUBBUB/HUBP state: arbitration watermarks, self-refresh and DRAM-clock-change gating, host VM policy, VM context page-table base/start/end registers, fault status/address, return-path DCC and compbuf/DET controls, surface format/tiling/viewport, primary/secondary/meta surface addresses, flip control, prefetch/timing/watermark parameters, cursor surface/position/hotspot/DMDATA, and read-line/interrupt status.

Persistence is hardware-defined. Configuration registers usually retain values until modeset, reprogramming, power gating, suspend/resume, firmware action, or ASIC reset. Status, counter, interrupt, fault, debug, clear/ack, mailbox, and power-status registers may be read-only, sticky, self-clearing, write-one-to-clear, or asynchronously updated by hardware or firmware. This offset header does not express access type or side effects.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h`, which supplies field shifts and masks for the registers addressed here. The offset and mask headers must come from the same generated DCN 3.1.5 register database.

Observed direct include sites in this source tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c`, which builds `dmub_srv_dcn315_regs` using `REG_OFFSET_EXP(reg_name)` and field tables from the matching mask header.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`, which includes the offset/mask pair while constructing DCN315 resource tables for DCCG, hubbub, HUBP, audio, GPIO/AUX/I2C, stream encoders, IRQ, DMUB, and related display blocks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c`, which includes the pair for interrupt-service register programming and maps DCN interrupt source IDs to DAL IRQ sources.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_factory_dcn315.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_translate_dcn315.c`, which use generated register metadata for GPIO, DDC, AUX, HPD, panel, and related pin translation/factory setup.

Additional integration is through shared DCN31/DCN314/DCN315 display block code. Many names in this chunk are consumed by common register-list macros for DCCG, hubbub, HUBP, DMCUB, DWB, HDA/audio, perfmon, power-gating, and hardware sequencing. DCN315-specific resource selection is what binds those shared block implementations to these generated numeric offsets.

## Risks And Edge Cases

- Offset or base-index drift is the main risk. These are untyped integer constants, so an incorrect `reg...` value or `reg..._BASE_IDX` can compile successfully while accessing the wrong MMIO segment or register.
- The base index is part of the address, not metadata for humans. A correct hex offset paired with the wrong base index can target a different register aperture.
- The chunk boundary creates one apparent pair mismatch: `regHUBPREQ1_DCSURF_FLIP_CONTROL2` is in this range and its `_BASE_IDX` is immediately outside it. Whole-file reconciliation should treat this as a chunking artifact.
- Repeated instance families are copy-sensitive. DCCG perfmons, DMCUB regions/code windows, streams 0-15, endpoints 0-7, input endpoints 0-7, VM contexts, watermarks A-D, HUBP0/HUBP1, HUBPREQ0/HUBPREQ1, and perfmon instances are similar but not interchangeable.
- DMCUB registers are firmware-contract sensitive. Inbox/outbox offsets, scratch registers, GPINT, fault, security, timer, region, and control registers must match both the host driver and the firmware image.
- VM and surface-address registers are high-impact. A wrong VM context or HUBPREQ surface/meta address offset can cause GPU page faults, scanout corruption, stale flips, memory-security issues, or display hangs.
- Interrupt/status/clear registers are side-effect-sensitive. Wrong offsets can miss vblank/page-flip/HPD/AUX/DCHUBBUB/DMCUB/AZ events or clear the wrong status bit.
- Clock, power, and watermark registers are sequencing-sensitive. Bad DCCG, power-gating, MMHUBBUB, DCHUBBUB, or HUBPREQ offsets can appear as intermittent underruns, blanking, resume failures, audio loss, writeback corruption, or display instability under multi-display and low-power transitions.

## Test Signals

Useful validation for this chunk is mostly build, generated-data, and hardware smoke coverage:

- Build coverage for DCN315 translation units that include this header, especially `dmub_dcn315.c`, `dcn315_resource.c`, `irq_service_dcn315.c`, `hw_factory_dcn315.c`, and `hw_translate_dcn315.c`.
- Static/generated checks that each direct `reg*` offset has the expected `reg*_BASE_IDX`, accounting for the line-boundary exception at `regHUBPREQ1_DCSURF_FLIP_CONTROL2`.
- Diff or regeneration checks against AMD's authoritative DCN 3.1.5 register database, with special attention to base indices, repeated instance strides, and differences from neighboring DCN 3.1.4/DCN 3.1.6 headers.
- DMUB/DMCUB bring-up tests that exercise firmware load/control, region/window programming, inbox/outbox traffic, GPINT handling, scratch registers, timer reads, fault reporting, and wake interrupts.
- Display clock tests covering DCCG DTO programming, DP/DSC/DPP/DTB/audio clocks, pixel-rate controls, GTC/current time-base reads, vsync latch/count programming, clock gating, and soft reset.
- IRQ tests for vblank, vupdate, page flip, HPD, AUX, DIO/DCIO, DCCG, DMU, MMHUBBUB, writeback, DCHUB, MPC/OPP/OPTC, DSC, HPO, and AZ interrupt routing/status behavior.
- Plane and memory tests covering HUBP/HUBPREQ surface format, tiling, viewport, pitch, primary/secondary/meta addresses, DCC, VMID, prefetch/timing parameters, flips, cursor position/surface/DMDATA, and HUBPRET read-line interrupts.
- Low-power and bandwidth tests covering DCHUBBUB watermarks A-D, self-refresh entry/exit, DRAM clock-change gating, host VM controls, compbuf/DET state, memory power, and warmup behavior.
- HDMI/DP audio and writeback tests covering Azalia controller/stream/endpoint access, audio DTO, CRC, memory power, DWB flow/color/OGAM/gamut/CRC/output controls, and MCIF writeback buffer programming/readback.

## Cross-Chunk Notes

This is the opening chunk of a 15,195-line generated offset header. It establishes the file guard and covers common low-address DCN 3.1.5 register maps through the beginning of `dce_dc_dcbubp1_dispdec_hubpreq_dispdec`. Later chunks are required to complete HUBPREQ1 and cover additional HUBP instances, DPP/DSCL/CM, MPC/OPP/OPTC, DIO/AUX/I2C/HPD, DSC/HPO, panel/backlight, and remaining generated register spaces before making whole-file claims.
