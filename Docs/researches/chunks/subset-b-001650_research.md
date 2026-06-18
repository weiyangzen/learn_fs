# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h lines 1-2687

## Scope And Purpose

This chunk is the first 2,687 lines of the generated DCN 2.1.0 register-offset header used by the AMDGPU display stack. It contains only preprocessor definitions: an include guard, AMD's permissive license block, address-block comments, `mm...` register-offset constants, and matching `mm..._BASE_IDX` segment selectors. The assigned range starts at legacy VGA/MMHUBBUB offsets and ends partway through the second HUBP cursor register block at `mmCURSOR0_1_DMDATA_STATUS_BASE_IDX`.

The header's purpose is to give DCN 2.1 display code stable symbolic register names. Consumer code combines each `mm` offset with a SoC base segment, typically through macros such as `SR()`, `SRI()`, `SRII()`, `DCCG_SRII()`, and `REG_OFFSET()`, to populate per-block register tables. Runtime display code then reads or writes the resulting absolute register addresses through AMDGPU register helpers. This file does not define behavior by itself; it is a hardware ABI map between DCN 2.1 register names and numeric offsets.

## Important Definitions

Every hardware register in this chunk is represented as a pair:

- `#define mmREGISTER_NAME 0xNNNN` gives the register offset within the block's selected MMIO aperture.
- `#define mmREGISTER_NAME_BASE_IDX N` selects the generated base segment, later expanded through `DMU_BASE__INST0_SEG<N>` in DCN resource code or equivalent DMUB helpers.

The main block families in this range are:

- VGA and VGA indexed register windows: `mmVGA_MEM_WRITE_PAGE_ADDR`, `mmVGA_MEM_READ_PAGE_ADDR`, indexed CRTC/SEQ/DAC/GRPH aliases, `mmVGA_RENDER_CONTROL`, `mmD1VGA_CONTROL` through `mmD6VGA_CONTROL`, `mmVGA_STATUS`, interrupt/status clear, cache/security, and source-select registers.
- DCCG display clock generation: PHY PLL pixel-clock resync controls, DP DTO phase/modulo, DPPCLK and DSCCLK DTO parameters, DISPCLK frequency change, time-base dividers, clock-gating control, audio DTOs, SYMCLK enables, VSYNC latch/counter controls, soft reset, and `mmDENTIST_DISPCLK_CNTL`.
- DC performance monitor blocks: `DC_PERFMON0` through `DC_PERFMON7` register groups appear across DCCG, DMU, writeback, MMHUBBUB, HDA, DCHUBBUB, and HUBP regions. Each group exposes counter control, state, current value, high, and low registers.
- DMU/DMCU/interrupt infrastructure: RBBMIF timeout/status registers, display power-gating domain config/status registers, DMU misc clock and memory power controls, DMCU firmware RAM/control/interrupt/mailbox registers, GPU timer registers, display interrupt status continuations, and interrupt-destination registers for DCCG, DMU, DCPG, MMHUBBUB, WB, DCHUB, DPP, MPC, OPP, OPTC, OTG, DIG, HPD, AUX, AZ, and DSC.
- Writeback path: `WB_ENABLE`, CNV window/source/test/debug registers, writeback scaler coefficient/tap/filter/clamp/status registers, and MCIF writeback buffer manager, address, watermark, QoS, security, and self-refresh controls for `MCIF_WB0` and `MCIF_WB1`.
- Audio/HDA/Azalia: stream index/data registers for streams 0-15, endpoint index/data registers, input endpoint index/data registers, controller clock/DMA/RIRB/CORB/payload/CRC/memory power registers, and root codec parameter/control registers.
- DCHUBBUB and VM request path: SDPIF config, physical VM request and framebuffer/AGP/HBM location registers, ret-path DCC/CRC/memory power registers, arbitration watermarks A-D, DRAM clock/self-refresh controls, global timer, timeout/debug/status, host VM controls, VM context 0-15 page-table base/start/end registers, default address, fault control/status, and fault address registers.
- HUBP/HUBPREQ/HUBPRET/cursor for instances 0 and 1: surface configuration, tiling, viewports, request-size and control registers, surface pitch/address/meta-address pairs, flip and in-use registers, TTU/QoS/deadline/prefetch/vblank/nominal/flip parameter registers, VM aperture/L1 TLB controls, read-line controls, cursor position/size/hotspot/surface-address/DMDATA controls, and HUBP perfmon.

The chunk boundary matters: it includes complete HUBP0/HUBPREQ0/HUBPRET0/cursor0 instance definitions, most of HUBP1/HUBPREQ1/HUBPRET1, and only the beginning of `dce_dc_dcbubp1_dispdec_cursor0_dispdec`. Later HUBP1 DMDATA SW registers and subsequent DCN blocks are outside this work item.

## Consumers And Integration Points

Direct include sites for this DCN 2.1 offset header include:

- `display/dc/resource/dcn21/dcn21_resource.c`, which combines these offsets with `renoir_ip_offset.h` base segments and `dcn_2_1_0_sh_mask.h` field masks to build static register tables for DCCG, DMCU, ABM, audio, OPP, timing generators, MPC, HUBP, HUBBUB, DIO, VMID, DSC, DPP, AUX, and stream encoders.
- `display/dmub/src/dmub_dcn21.c`, which uses the same offsets through DMUB register macros to expose DMCUB common/internal registers to the display microcontroller service.
- `display/dc/irq/dcn21/irq_service_dcn21.c`, which needs DCN 2.1 offsets and masks to describe interrupt sources and acknowledge/enable them.
- `display/dc/gpio/dcn21/hw_factory_dcn21.c` and `display/dc/gpio/dcn21/hw_translate_dcn21.c`, which translate DCN 2.1 GPIO/AUX/DDC/HPD hardware identities into register-backed objects.

Important downstream register-list macros include `DCCG_COMMON_REG_LIST_DCN_BASE()`, `DCCG_MASK_SH_LIST_DCN2_1()`, `HUBP_REG_LIST_DCN21(id)`, `HUBP_MASK_SH_LIST_DCN21()`, `HUBBUB_REG_LIST_DCN21()`, `HUBBUB_MASK_SH_LIST_DCN21()`, `DMCU_DCN20_REG_LIST()`, `AUD_COMMON_REG_LIST(id)`, and `DCN20_VMID_REG_LIST(id)`. These macros depend on the naming convention in this header: for example `SRI(FLIP_PARAMETERS_3, HUBPREQ, 0)` expands to `mmHUBPREQ0_FLIP_PARAMETERS_3` and `mmHUBPREQ0_FLIP_PARAMETERS_3_BASE_IDX`.

## Control Flow

There is no function-level control flow in this header. The effective control flow is compile-time macro expansion followed by runtime register access:

1. A DCN 2.1 source file includes `renoir_ip_offset.h`, this offset header, and the matching `dcn_2_1_0_sh_mask.h`.
2. Resource macros such as `SR(reg)` or `SRI(reg, block, id)` concatenate tokens to find `mm...` and `mm..._BASE_IDX` definitions from this header.
3. The macro adds the selected MMIO base segment to the register offset and initializes a typed register table field.
4. Block constructors receive those register tables and matching shift/mask tables.
5. Runtime block methods use generic read/modify/write helpers against the precomputed register addresses to program clocks, display surfaces, VM, cursor state, watermarks, interrupts, audio, writeback, and power management.

The correctness contract is therefore mostly structural. Register names, instance suffixes, base indexes, and matching shift/mask names must line up exactly with the token-pasting macros used by the consumer block headers.

## State And Persistence

This file contains no mutable software state and persists nothing. It does, however, define addresses for registers that control persistent hardware-visible state while the GPU is powered:

- Surface state: HUBP/HUBPREQ registers hold framebuffer, chroma, metadata, pitch, viewport, tiling, flip, VMID, and cursor addresses.
- Clock and timing state: DCCG registers hold DPPCLK, DISPCLK, DP DTO, audio DTO, pixel-rate, time-base, and clock-gating configuration.
- Memory and VM state: DCHUBBUB/VMRQ registers describe framebuffer/AGP aperture ranges, VM contexts, page-table address ranges, fault status, and default fault handling.
- Power-management state: DMU, DMCU, DCHUBBUB, HUBP, HUBPREQ, HUBPRET, MMHUBBUB, MCIF_WB, Azalia, and cursor memory power registers coordinate gating, requests, status, and reset behavior.
- Diagnostics state: DC perfmon, CRC, debug index/data, timeout, interrupt-status, GPU timer, read-line, and fault-status registers expose transient hardware state for debugging and validation.

Because these are MMIO offsets, a wrong constant can cause writes to the wrong hardware register rather than a local software failure. The source tree's state is fixed at build time, while the actual hardware state changes only when consumer code uses these offsets.

## Dependencies

The header depends on C preprocessor token concatenation and on generated SoC base definitions from `renoir_ip_offset.h`. It is paired with `dcn_2_1_0_sh_mask.h`, which defines field shifts and masks for many of the same register names. Its constants are interpreted by AMD display core abstractions under `drivers/gpu/drm/amd/display/dc`, DMUB service code under `drivers/gpu/drm/amd/display/dmub`, and AMDGPU low-level register access helpers.

The `BASE_IDX` values seen in this chunk are significant:

- `0` is used for the small VGA memory page address aperture at base `0x48`.
- `1` is used for VGA legacy aliases and early DCCG/display clock registers.
- `2` is used for most DCN display engine blocks in this range, including perfmon, DMU, DMCU, writeback, MMHUBBUB, HDA/Azalia, DCHUBBUB, VMRQ, HUBP, HUBPREQ, HUBPRET, and cursor registers.

The header has no direct dependency on Ceph or distributed filesystem code despite living under this repository's mirrored `sources/distributed-fs/ceph-client` tree. Its functional owner is the vendored Linux AMDGPU display driver.

## Risks And Edge Cases

- Offset/header mismatches are high impact. A typo in either an `mm...` value or `_BASE_IDX` silently redirects runtime MMIO access and can manifest as display bring-up failures, corrupted scanout, bad cursor programming, broken audio, interrupt storms, VM faults, hangs, or power-management instability.
- The consumer macros rely on exact token naming. Renaming a register, changing an instance prefix such as `HUBPREQ0_` or `CURSOR0_1_`, or dropping a matching `_BASE_IDX` breaks compile-time expansion.
- This chunk includes duplicate numeric offsets for legacy indexed VGA aliases such as CRTC/SEQ/DAC/ATTR/GEN registers. That aliasing is intentional; treating duplicate offsets as a generation bug would be misleading.
- The assigned chunk cuts through a logical block. Research or automated validation for HUBP1 cursor support must include later lines of the file before concluding that all cursor/DMDATA registers are present.
- Register-list macros often cover only supported pipes or hardware instances. For DCN 2.1, `dcn21_resource.c` instantiates four HUBPs and four timing generators even though this chunk contains offsets for more global interrupt destinations and many shared blocks. Tests should validate the resource caps, not just the existence of offset constants.
- The DCCG macro set for DCN 2.1 programs OTG pixel-rate fields for instances 0-3, while older DCN2 lists include additional OTG instances. Mixing DCN 2.0 and DCN 2.1 offset/mask/list macros could compile but program unsupported or wrong registers.
- Several register families encode security, VM, and fault controls. Incorrect writes can disable fault reporting or set an invalid aperture, making subsequent GPU faults harder to diagnose.
- Generated headers are easy to review mechanically but hard to validate semantically. The best source of truth is a cross-check against the ASIC register database or known-good upstream Linux header for the same DCN version.

## Test Signals

Useful validation for this chunk includes:

- Build AMDGPU display code with DCN 2.1 enabled and warnings treated as errors; token-pasting failures in `SR`, `SRI`, `SRII`, `DCCG_SRII`, `REG_OFFSET`, and field-mask macros should surface immediately.
- Compile `dcn21_resource.c`, `dmub_dcn21.c`, `irq_service_dcn21.c`, and the DCN21 GPIO translation/factory files together with this header and `dcn_2_1_0_sh_mask.h`.
- Compare generated register tables for DCCG, HUBBUB, HUBP0/HUBP1, VMID, DMCU, audio, writeback, and perfmon against a known-good DCN 2.1 table or upstream Linux AMDGPU source.
- On Renoir/DCN 2.1 hardware, smoke-test display modeset, page flip, cursor update, blank/unblank, hotplug interrupt, audio over DP/HDMI, suspend/resume, and basic writeback paths.
- Exercise VM/fault instrumentation by enabling display VM paths and checking DCHUBBUB fault-status/debug output after valid and invalid surface-address programming in a controlled test.
- Verify watermark and deadline programming through HUBBUB/HUBPREQ registers under memory clock changes, stutter/self-refresh entry and exit, and multi-plane scanout.
- Run perfmon/debug tests that read `DC_PERFMON*` and debug index/data registers to catch base-index mistakes that may not affect ordinary modesets.
- Run DMUB initialization and mailbox tests on DCN 2.1, because DMUB uses the same offset header for DMCUB common/internal register access.
