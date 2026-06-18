# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h lines 12941-15538

## Scope

This chunk is a generated register-offset portion of the AMD DCN 2.0.0 ASIC register map. It contains only C preprocessor constants: `mm...` register offset macros and matching `mm..._BASE_IDX` segment-index macros. The slice starts inside the `dce_dc_dcio_dcio_uniphy0_dispdec` block at `mmDCIO_UNIPHY0_UNIPHY_MACRO_CNTL_RESERVED10_BASE_IDX` and ends inside the `dce_dc_dpp5_dispdec_dscl_dispdec` block at `mmDSCL5_SCL_MODE`; both boundary blocks are partial and require neighboring chunks for the full per-file view.

The file-level contract supplied by this chunk is address resolution, not executable logic. Consumers combine `BASE(mmREG_BASE_IDX)` with `mmREG` to produce absolute MMIO offsets for DCN 2.0 display hardware.

## Purpose

The macros in this range map DCN 2.0 display sub-block registers for:

- UNIPHY display PHY macro reserved controls for PHY instances 0-6.
- Display Stream Compression instances DSC0-DSC5, including top-level DSC, DSC CIF, DSCC configuration/PPS/error/rate-buffer registers, and per-DSC performance monitors.
- DMCUB display microcontroller address windows, interrupts, inbox/outbox mailboxes, scratch/status registers, GPINT registers, and timers.
- MMHUBBUB writeback and XFC/XFCP buffer-control blocks.
- DPP4 and the beginning of DPP5: top control, CNVC format/cursor, scaler, color-management/gamma/3D LUT, and perfmon offsets.

Each non-`_BASE_IDX` macro is a register offset, for example `mmDMCUB_INBOX1_WPTR 0x3280`. Each paired `_BASE_IDX` macro identifies the SoC register-base segment to use with the offset, almost always `2` in this chunk.

## Important APIs, Types, And Macros

This header defines no functions, structs, enums, or storage. Its public API is the macro namespace consumed by AMD display code:

- `mmDCIO_UNIPHY<n>_UNIPHY_MACRO_CNTL_RESERVED<m>` and `_BASE_IDX`: 48 reserved control offsets per complete UNIPHY instance. This chunk contains UNIPHY0 reserved 10-47 and complete UNIPHY1-6 reserved 0-47 blocks.
- `mmDSC_TOP<n>_*`, `mmDSCCIF<n>_*`, and `mmDSCC<n>_*`: offsets for DSC top control/debug, CIF config, DSCC config/status/interrupt, 23 PPS config registers, memory power control, squared and absolute error counters, rate-buffer fullness, rate-control fullness, and debug bus rotation for DSC instances 0-5.
- `mmDC_PERFMON21_*` through `mmDC_PERFMON27_*`: per-block display performance counter control/state/value registers. PERFMON21-26 align with DSC0-5; PERFMON27 aligns with DPP4.
- `mmDMCUB_*`: DMCUB region offset/top/base registers, region3 CW0-CW7 windows, interrupt enable/ack/status/type, fault addresses, security/memory control, inbox/outbox ring descriptors, timers, scratch registers, `DMCUB_CNTL`, GPINT data, memory power, and processor ID.
- `mmMCIF_WB2_*`: MCIF writeback instance 2 buffer manager, buffer addresses/status, pitch, arbitration, watermark, clock gating, self-refresh, QoS, luma/chroma sizes, high address bits, and buffer resolution offsets.
- `mmXFCP<n>_MMHUBBUB_XFC_*` and `mmMMHUBBUB_XFC*`: six XFC pipe windows plus global XFC memory power, surface/write config, VM init, GPU base addresses, and XFC monitor counters.
- `mmDPP_TOP4_*`, `mmCNVC_CFG4_*`, `mmCNVC_CUR4_*`, `mmDSCL4_*`, `mmCM4_*`: DPP4 top, converter, cursor, scaler, output buffer, color matrix, degamma, blend gamma, shaper, 3D LUT, memory power, and debug registers.
- `mmDPP_TOP5_*`, `mmCNVC_CFG5_*`, `mmCNVC_CUR5_*`, and partial `mmDSCL5_*`: the beginning of equivalent DPP5 definitions.

The key integration macros are defined in consumers rather than here. For DCN20 resource construction, `SR(reg_name)` expands to `.reg_name = BASE(mm ## reg_name ## _BASE_IDX) + mm ## reg_name`; instance macros such as `SRI(reg_name, block, id)` do the same for `block id` register names. DMUB uses `REG_OFFSET(reg_name) (BASE(mm##reg_name##_BASE_IDX) + mm##reg_name)` through `dmub_reg.h`.

## Address-Block Inventory

Complete address blocks in this chunk:

- `dce_dc_dcio_dcio_uniphy1_dispdec` through `uniphy6`, base addresses `0x360`, `0x6c0`, `0xa20`, `0xd80`, `0x10e0`, `0x1440`, each with 48 reserved register offsets and 48 `_BASE_IDX` entries.
- `dce_dc_dsc0` through `dce_dc_dsc5` groups. Each instance includes a top block, DSCCIF block, DSCC block, and a DC perfmon block. DSC instance base comments progress by `0x170`; perfmon base comments progress from `0xc140` to `0xc870`.
- `dce_dc_dmu_dmcub_dispdec`, base `0x0`, 216 macro definitions covering DMCUB register offsets from `0x3238` through `0x32a9`.
- `dce_dc_mmhubbub_mcif_wb2_dispdec`, base `0xc6b8`, 108 macros covering writeback instance 2 offsets `0x3460` through `0x3496`.
- `dce_dc_mmhubbub_xfcp0_dispdec` through `xfcp5`, plus global `dce_dc_mmhubbub_xfc_dispdec`, covering per-pipe XFC control/config/size and global XFC memory/monitor registers.
- `dce_dc_dpp4_dispdec_*` blocks for DPP top, CNVC config, cursor, DSCL, color management, and perfmon.
- `dce_dc_dpp5_dispdec_dpp_top_dispdec`, `cnvc_cfg`, and `cnvc_cur`.

Partial blocks:

- UNIPHY0 is continued from the previous chunk. This slice begins after `mmDCIO_UNIPHY0_UNIPHY_MACRO_CNTL_RESERVED10`.
- DPP5 DSCL continues into the next chunk. This slice includes only tap select, tap data, and `SCL_MODE` plus the first two `_BASE_IDX` pairs before stopping at line 15538.

## Control Flow

There is no runtime control flow in this header. The effective flow is compile-time macro expansion:

1. A DCN20-specific C file includes `dcn_2_0_0_offset.h`, `dcn_2_0_0_sh_mask.h`, and a SoC IP offset header such as `navi10_ip_offset.h`.
2. Register-list macros in display blocks name logical registers without hardcoding offsets.
3. Resource initialization macros expand each logical name to `BASE(mm..._BASE_IDX) + mm...`.
4. Runtime helper macros such as `REG_READ`, `REG_WRITE`, `REG_GET`, and `REG_UPDATE` use the computed offsets to touch MMIO registers.

Examples visible in the tree include `dmub/src/dmub_dcn20.c`, `dc/resource/dcn20/dcn20_resource.c`, `dc/gpio/dcn20/hw_factory_dcn20.c`, `dc/irq/dcn20/irq_service_dcn20.c`, and `dc/clk_mgr/dcn20/dcn20_clk_mgr.c`.

## State And Persistence Behavior

The header itself has no mutable state and no persistence. It describes hardware state locations. The represented hardware registers do hold volatile state:

- DMCUB region, mailbox, scratch, GPINT, interrupt, timer, and fault registers track firmware boot, command transport, interrupt handling, and debug state across driver operations and hardware resets.
- DSCC and DSC_TOP registers hold stream-compression configuration, PPS values, error counters, rate-buffer telemetry, memory-power state, and interrupt status.
- MCIF_WB2 and XFC registers hold display writeback buffer descriptors, watermarks, QoS, VM initialization, monitor counters, and memory-power state.
- DPP4/DPP5 CNVC, DSCL, and CM registers hold pipe-local pixel format, cursor color, scaling, color-space conversion, gamma, shaper, 3D LUT, and memory power state.

Because these are MMIO offsets, persistence semantics come from the hardware and driver reset paths. The header must match the ASIC register spec exactly; stale or shifted constants cause reads and writes to hit the wrong hardware location.

## Dependencies And Integration Points

Primary dependencies:

- `navi10_ip_offset.h` supplies segment base constants such as `DCN_BASE__INST0_SEG2`, used by `BASE(mm..._BASE_IDX)`.
- `dcn_2_0_0_sh_mask.h` supplies field masks and shifts for the same register names.
- AMD display register helpers (`reg_helper.h`, `dmub_reg.h`, and related block headers) provide `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_UPDATE`, `SR`, `SRI`, and DMUB register table construction.

Integration signals in this chunk:

- `dmub/src/dmub_dcn20.c` builds `dmub_srv_dcn20_regs` from this header and uses DMCUB offsets for reset, mailbox pointer zeroing, firmware boot, GPINT, scratch, timer, and fault/debug access.
- `dc/resource/dcn20/dcn20_resource.c` imports this header when constructing DCN20 resources, including DSC, DPP, DWB/MMHUBBUB, GPIO, IRQ, and clock objects.
- `dc/irq/dcn20/irq_service_dcn20.c` imports this header and uses address macros through IRQ register-list expansion.
- Sibling generated headers for DCN 2.1 and 3.x carry similar macro names with sometimes different offset values, so consumers must include the ASIC-matched offset header.

## Risks

- Register-map correctness is high risk. An incorrect numeric offset or `_BASE_IDX` can silently redirect MMIO access to a different register, causing display corruption, hangs, firmware mailbox failure, bad interrupt handling, or memory writeback faults.
- Boundary chunks are easy to mismerge. UNIPHY0 and DPP5 DSCL are incomplete in this slice and must be reconciled with adjacent chunk reports before writing the final per-file report.
- The repeated instance patterns invite copy/paste or generator errors. DSC0-5 and XFCP0-5 should maintain consistent stride and register ordering unless the hardware spec intentionally diverges.
- Most macros in this chunk use `_BASE_IDX 2`; any exception would be significant. Mechanical validation should catch accidental segment-index drift.
- Reserved UNIPHY macro names are opaque. They should not be inferred as safe to program without matching field definitions and ASIC documentation.
- DMCUB mailbox and region-window offsets are especially sensitive because the firmware command channel and memory windows depend on correct base/top/offset pairing.

## Test And Validation Signals

Useful validation for this chunk is mostly compile-time and hardware/integration oriented:

- Compile all DCN20 display objects that include `dcn_2_0_0_offset.h`; macro-name mismatches are caught as build failures.
- Build with corresponding `dcn_2_0_0_sh_mask.h`; register names used by `REG_GET`/`REG_UPDATE` must have both offset and field mask/shift definitions.
- Run display bring-up tests on DCN2.0/Navi10-class hardware: modeset, hotplug, vblank/vupdate IRQs, DSC-enabled modes, cursor display, scaling, color-management/gamma programming, and display writeback.
- Exercise DMUB boot/reset and mailbox paths: DMCUB soft reset, inbox/outbox pointer reset, GPINT command/ack, scratch register status, timer reads, and debug fault collection.
- Check register-map generator consistency: paired `mm...` and `mm..._BASE_IDX` definitions, monotonic offsets inside repeated blocks, correct instance strides for DSC and XFCP, and no duplicate or missing macros relative to the ASIC source data.
- Runtime failures likely surface as `REG_READ`/`REG_WRITE` timeouts, display pipe programming failures, missing interrupts, DMCUB firmware non-response, DSC visual corruption, or writeback buffer/address errors.

## Research Notes

This chunk contains 2,402 `#define` lines in the requested range. The first line is the `_BASE_IDX` for `mmDCIO_UNIPHY0_UNIPHY_MACRO_CNTL_RESERVED10`, confirming a previous-chunk boundary. The last requested line is `#define mmDSCL5_SCL_MODE 0x3762`, and the next source line outside scope supplies its `_BASE_IDX`, confirming a next-chunk boundary.
