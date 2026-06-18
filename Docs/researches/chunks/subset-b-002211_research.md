# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h lines 1-2953

## Purpose

This chunk is the opening portion of the generated DCN 4.2.0 register offset header for AMD display hardware. It exports numeric register offsets and indirect-register indices for display core, audio, link, debug, clock, DSC, and USB4/DPIA blocks. The header is pure hardware contract data: consumers include it, combine `reg*` symbols with a base segment selected by each `*_BASE_IDX`, and pair the resulting address with field shifts/masks from `dcn_4_2_0_sh_mask.h`.

The slice starts with the MIT/SPDX banner and include guard, then defines 2,284 preprocessor symbols across 124 address blocks. Of those, 396 are direct `reg*` offset or `reg*_BASE_IDX` definitions and 1,887 are `ix*` indirect indices. The extra counted symbol is the include guard macro. The first major group covers HDA/Azalia controller command and response rings, debug buses, DP/DIG/AUX/HPD debug indices, stream/link encoder debug indices, Azalia audio endpoint and stream indices, DSC/DPIA debug indices, DCE HDA direct offsets, and DCCG clock-generator offsets. The final lines in this chunk enter the Azalia F2 input endpoint codec indirect table and stop at `ixAZALIA_F2_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL4_ENABLE`.

## Important APIs, Types, And Macros

This file does not define C functions or structs. Its exported API is the preprocessor namespace consumed by AMDGPU display register helper macros.

- `regAZCONTROLLER0_*` and later `regAZENDPOINT0_*`, `regAZINPUTENDPOINT0_*`, `regAZROOT0_*`, and `regAZSTREAM0..7_*` define direct offsets for HDA/Azalia controller, endpoint, root, and stream access registers. Each has a companion `_BASE_IDX` used to choose the DCN base segment.
- `ix*` symbols define indirect register indices for debug buses or codec tables. Examples include `ixDP0_DP_DEBUG_*`, `ixAZF0ENDPOINT0_AZALIA_F0_CODEC_PIN_CONTROL_*`, `ixDSCC_DEBUG_*`, and `ixDPIA_PORT_AUX0_DPIA_PORT_AUX_TEST_DEBUG*`.
- DCCG direct offsets such as `regDCCG_GATE_DISABLE_CNTL*`, `regDPPCLK*_DTO_PARAM`, `regSYMCLK*_CLOCK_ENABLE`, `regDCCG_AUDIO_DTO*_PHASE`, `regDCCG_AUDIO_DTO*_MODULE`, and `regDENTIST_DISPCLK_CNTL` supply the address side of display clock programming.
- The value of `_BASE_IDX` is semantically part of the register address. DCN 4.2 code maps these segment indices through `ctx->dcn_reg_offsets[seg]` or hard-coded `DCN_BASE__INST0_SEG*` constants before adding the raw offset.
- The matching field macros live in `dcn_4_2_0_sh_mask.h`. Consumers normally access these constants through `SR`, `SRI`, `SRI_ARR`, `REG_OFFSET_EXP`, `FD_MASK`, `FD_SHIFT`, `REG_READ`, `REG_WRITE`, `REG_UPDATE`, and related helper macros rather than spelling the offsets directly.

Representative address-block coverage in this chunk:

- HDA/Azalia controller and codec blocks: `dce_dc_hda_azcontroller_azdec`, `azf0stream0..15_streamind`, `azf0endpoint0..7_endpointind`, `azf0inputendpoint0..7_inputendpointind`, `azendpoint_descriptorind`, `dce_dc_hda_azendpoint_azdec`, `dce_dc_hda_azinputendpoint_azdec`, `dce_dc_hda_azroot_azdec`, `dce_dc_hda_azstream0..7_azdec`, `azroot_f2codecind`, `azendpoint_f2codecind`, and the start of `azinputendpoint_f2codecind`.
- Display/link diagnostics: `dc_perfmon`, `mcif_wb0`, `hubbub`, `odm0..3`, `rbbmif`, `ihc`, `dmu_misc`, `dc_pg`, `dp0..4`, `dig0..4`, `dio_misc`, `apg`, `dcoh_top`, `hpo_top`, HDMI stream/link/FRL debug, DP stream/sym32/link encoder debug, and DP DPHY sym32 debug blocks.
- Connector and sideband diagnostics: `dp_aux0..4`, `hpd0..4`, and `dpia_port0..5`, `dpia_port_ml0..5`, `dpia_port_aux0..5`, plus `dpia_mu0`.
- Compression and clock blocks: `dscc`, `dscc_dispclk`, `dsccif`, `dsc_top`, `dce_dc_dccg_dccg_dispdec`, and `dce_dc_dccg_dccg_dfs_dispdec`.

## Control Flow

There is no executable control flow in the header. The runtime flow is created by consumers that expand register-list macros at compile time:

1. DCN 4.2 resource construction includes this header and `dcn_4_2_0_sh_mask.h`.
2. Resource macros such as `SR`, `SRI`, `SRI_ARR`, and `SR_ARR` add the appropriate base segment to `reg*` offsets and store the results in per-block register tables.
3. Hardware objects such as stream encoders, link encoders, AUX, HPD, HPO encoders, hubbub, DCCG, DPP, HUBP, and DSC receive those tables during resource-pool creation.
4. Runtime paths call generic register helpers through those tables. The helpers operate on the resolved offsets and the matching field shifts/masks.
5. For indirect tables, common code first writes an index register and then reads or writes a data register. `dce_audio.c` uses this pattern for Azalia endpoint codec registers through `AZ_REG_READ()` and `AZ_REG_WRITE()`.

Specific DCN 4.2 consumers found in this tree include `dmub_dcn42.c`, which initializes DMUB register offsets with `REG_OFFSET_EXP`; `dcn42_resource.c`, which builds the main DC resource register tables; `dcn42_clk_mgr.c`, which uses DCN and CLKIP base mappings for clock-manager registers; `hw_translate_dcn42.c`, which translates HPD/DDC GPIO register offsets to DAL GPIO IDs; and `irq_service_dcn42.c`, which includes the same offsets for DCN 4.2 IRQ handling.

## State And Persistence

The header itself is stateless. All persistence is in hardware registers reached through the constants:

- HDA/Azalia controller state includes CORB/RIRB pointers, command status, DMA position base, immediate command/response interfaces, stream descriptors, codec function parameters, endpoint pin controls, audio descriptors, sink info, hotplug control, LPIB snapshots, format-change status, and audio enable/disable interrupt status.
- DCCG state includes clock-gating controls, display/DPP/DSC clock DTO parameters, symbol-clock enables, soft reset, audio DTO source/module/phase, vsync latch values, and Dentist clock divider control.
- AUX, HPD, DP/DIG, HDMI, DPHY, DSC, DPIA, and debug-indirect indices expose diagnostic or sideband state selected through each block's indirect debug mechanism.
- Hardware state survives as long as the relevant IP block remains powered and is otherwise reset or reprogrammed by display mode set, audio setup, DMUB boot/reset, suspend/resume, or power-management sequencing. There is no filesystem persistence.

## Dependencies And Integration Points

The main dependency is strict naming agreement between this generated offset header and the surrounding AMD display macro ecosystem:

- `dcn_4_2_0_sh_mask.h` must provide matching field masks and shifts for the same register names.
- DCN 4.2 resource code maps `_BASE_IDX` values through `ctx->dcn_reg_offsets[]`; standalone code such as GPIO translation and clock manager also defines the base segment constants it needs.
- `display/dmub/src/dmub_dcn42.c` consumes offsets for DMUB initialization, reset, boot options, framebuffer base/offset reads, scratch registers, inbox/outbox pointers, and related DMCUB control registers.
- `display/dc/resource/dcn42/dcn42_resource.c` consumes the header to initialize AUX, HPD, stream encoder, link encoder, HPO stream/link encoder, DPP, HUBP, hubbub, DCCG, DSC, and other register structures.
- `display/dc/dce/dce_audio.c` and `display/dc/dce/dce_audio.h` consume Azalia endpoint/root/function and DCCG audio DTO offsets to configure HDMI/DP audio, write sink audio information, audio descriptors, ACP support, HBR/lipsync, hotplug, and audio DTO clocks.
- `display/dc/gpio/dcn42/hw_translate_dcn42.c` uses the same offset scheme to convert HPD and DDC register addresses into GPIO IDs and line numbers.
- `display/dc/irq/dcn42/irq_service_dcn42.c` integrates the register namespace with HPD, HPDRX, vblank, vline, page-flip, vupdate, and DMCUB outbox IRQ mapping.
- DPIA and AUX constants connect to USB4 DisplayPort tunneling code paths, DMUB DPIA commands, bandwidth allocation notifications, and AUX-over-DPIA transactions.

## Risks

- Offset drift is a hardware-contract failure. A wrong `reg*` value or `_BASE_IDX` can direct a `REG_READ` or `REG_WRITE` to the wrong MMIO address, which may misprogram unrelated display state.
- Indirect index mistakes are difficult to catch at compile time. An incorrect `ixAZF0ENDPOINT*` value can make audio code write the wrong codec node while the C symbols still compile.
- Instance symmetry hides copy errors. DP/DIG/AUX/HPD/DPIA/Azalia endpoint blocks are repeated across instances; a single mismatched instance can only fail on the corresponding connector, stream, audio endpoint, or USB4 tunnel.
- Base segment mismatches are as dangerous as offset mismatches. This chunk uses base indices 0, 1, and 2 in early DCN definitions; consumers must map those to the correct per-ASIC base addresses.
- Debug and diagnostic registers can look low risk but are often used during bring-up, validation, power debugging, and failure triage. Bad debug indices reduce observability and can mask real hardware failures.
- DCCG and audio DTO offsets are timing-sensitive. Wrong values can break display clocks, DPP/DSC clock programming, symbol clocks, HDMI/DP audio clocks, or clock-gating behavior.
- The chunk is generated and broad. Manual edits risk creating local divergence from the ASIC register database and from the paired shift/mask header.

## Test Signals

Useful validation signals include:

- Build coverage with `CONFIG_DRM_AMD_DC_DCN4_2` enabled. Missing or renamed macros should fail in DMUB, resource, GPIO, IRQ, clock-manager, and audio register-table initialization.
- Register-table sanity checks or register dumps comparing resolved DCN 4.2 addresses against the ASIC specification, especially for `*_BASE_IDX` segment handling.
- Display bring-up on DCN 4.2 hardware across all physical connectors: HPD detection, DDC/AUX transactions, DP link training, HDMI stream setup, and mode set.
- HDMI/DP audio tests through every exposed audio endpoint: ELD propagation, channel allocation, audio descriptor programming, HBR/lipsync fields, ACP support, hotplug changes, and suspend/resume audio recovery.
- Clock and power-management tests covering DCCG programming, DPPCLK DTO changes, DSC clocks, symbol-clock enable/disable, clock-gating controls, DMUB reset/boot, and runtime power transitions.
- USB4/DPIA tests across six DPIA instances: AUX-over-DPIA access, HPD interrupt enablement, bandwidth allocation notifications, MST slot allocation, and link fallback behavior.
- DSC and HPO validation with high-bandwidth DP modes, because this chunk includes DSCC/DSC debug indices and HPO/link encoder related debug surfaces.
