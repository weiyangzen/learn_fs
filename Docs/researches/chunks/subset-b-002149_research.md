# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h lines 12729-15420

## Purpose

This chunk is a generated AMD DCN 4.1.0 register-offset slice. It contains no executable C functions or types; its API is a large set of preprocessor constants that map symbolic display/audio/debug register names to MMIO offsets plus companion `<name>_BASE_IDX` constants. DCN 4.0.1 display code combines these offsets with `dcn_4_1_0_sh_mask.h` field masks and register helper macros to build ASIC-specific register tables.

The covered range starts at the high-performance output (HPO) DisplayPort stream mapper and HDMI/FRL encoder blocks, then enumerates repeated HPO DP stream, APG audio-packet-generator, DME metadata, VPG generic-packet, DP Sym32 stream encoder, DP link encoder, and DP DPHY Sym32 blocks for instances 0-3. It then covers DLPC and DPCS/RDPCSTX PHY/control offsets, host HDA/Azalia controller and stream descriptor offsets, duplicate HDA `*_1` offsets in the high address range, an empty HDCP 1.x key database address block marker, and the beginning of indirect debug-index (`ix*`) registers for CNVC, CM, MCIF writeback, MPC OCSC, MPCC, MPCC OGAM, and MPCC MCM.

## Important APIs and register groups

- `regDP_STREAM_MAPPER_CONTROL0` through `CONTROL5` expose HPO DP stream-to-link mapping controls under base index 3. These are top-level HPO mapper registers used to route up to six streams or mapper slots.
- `regHDMI_LINK_ENC_*`, `regHDMI_FRL_ENC_*`, `regHDMI_STREAM_ENC_*`, `regAFMT4_*`, `regDME4_*`, `regVPG4_*`, and `regHDMI_TB_ENC_*` describe the HPO HDMI path: link/clock control, FRL configuration and meter-buffer status, stream input mux and clock-ramp FIFO status, audio formatter packets and CRC/ramp status, DME metadata controls, VPG generic/ISRC/MPEG packet access, and transport-bus packet/ACR/buffer/CRC/encryption/timing controls.
- `regDP_STREAM_ENC[0-3]_DP_STREAM_ENC_*` define per-DP-stream encoder controls: stream clock, input mux, audio enable/control, FIFO ramp status, and spare registers.
- `regAPG[0-3]_APG_*` define DisplayPort audio packet generator offsets for each stream instance: control, debug generator, packet control, ACP/audio info/IEC60958 debug payloads, audio CRC controls/results, ramp controls, status/status2, audio DTO debug, memory power, and spare.
- `regDME[5-8]_DME_*` provide DME control and memory-control offsets associated with the four DP stream encoder instances.
- `regVPG[5-8]_VPG_*` expose generic-packet and ISRC/MPEG packet access for DP stream instances: access/data registers, frame/immediate update controls, status, and VPG memory power.
- `regDP_SYM32_ENC[0-3]_DP_SYM32_ENC_*` are the largest repeated groups in this chunk. Each instance includes video FIFO control, MSA double buffering, pixel format, MSA0-8, hblank control, generic secondary-data packet controls `SDP_GSP_CONTROL0` through `14`, SDP audio/metadata/framing/ATP controls, idle pattern, MSA/VBID/video stream controls, panel replay controls, video CRC controls/results/status, symbol counters, ALPM sleep/wake/request/ready/hardware/status/start/interrupt controls, memory power, and spare.
- `regDP_LINK_ENC[0-3]_DP_LINK_ENC_*` define minimal per-link encoder clock-control and spare offsets for HPO DP links.
- `regDP_DPHY_SYM32[0-3]_DP_DPHY_SYM32_*` describe the 32-symbol DP PHY block for each link: control/status, encryption config, SAT update and virtual-channel rate/count/status registers for VC0-5, eDP/ASSR registers, ALPM sleep/wake/control, test-pattern configuration, PRBS seeds, square-pulse/custom pattern words, error/default override, and symbol-count status/control.
- `regDLPC_*` covers display low-power/controller counters and power-up/resync controls, including current count, OPTC snapshot, DCN ZSC/LONO power-up, spare, and counter init value.
- `regDPCSSYS_CR[0-3]_DPCSSYS_CR_ADDR/DATA` and `regRDPCSTX[0-3]_*` cover DPCS/RDPCS transmitter access and PHY controls. RDPCSTX instances include control/clock/interrupt, PLL update data, CR address/data, SRAM control, scratch/spare registers, pattern detect/debug controls, PHY control 0-17, PHY fuses, RX load value, RDPCS control, and PLL update override address/data.
- `regAZCONTROLLER0_*`, `regAZENDPOINT0_*`, `regAZINPUTENDPOINT0_*`, `regAZROOT0_*`, and `regAZSTREAM[0-7]_0_*` define host HDA/Azalia controller and stream descriptor offsets in low base-index ranges. They include CORB/RIRB pointers/control/status/size, immediate command/response interfaces, DMA position base address, wall-clock alias, endpoint command interfaces, and eight output stream descriptors.
- `regAZALIA_F0_*`, `regAZENDPOINT*_1_*`, `regAZROOT*_1_*`, and `regAZSTREAM[0-7]_1_*` repeat HDA/Azalia codec, endpoint, root, and stream descriptor offsets in the high `0x4b70xx` address region using base index 3. The stream descriptor pattern includes control/status, link position, cyclic buffer length, last valid index, FIFO size/format aliasing, BDL pointer lower/upper, and link-position aliases.
- `ixID2_CNVC_*`, `ixID*_CM_*`, `ixID*_WB_*`, `ixID*_MPC_OUT*`, `ixMPCC[0-3]_*`, `ixMPCC_OGAM[0-3]_*`, and `ixMPCC_MCM[0-2]_*` are indirect debug-index constants rather than normal MMIO register names. They name debug selector IDs for converter, color-management, writeback, MPC output CSC, MPCC composition state, MPCC output gamma, and MPCC MCM 3D LUT/gamut-remap debug views.

## Control flow and usage model

There is no local control flow. These constants are consumed at compile time by register-table initializers and by token-pasting helper macros.

The common usage model in DCN 4.0.1 code is:

1. Include `dcn_4_1_0_offset.h` with `dcn_4_1_0_sh_mask.h`.
2. Define a `BASE(seg)`/`BASE_INNER(seg)` mapping, such as `DCN_BASE__INST0_SEG2` in DCN 4.0.1 consumers.
3. Build offsets as `BASE(regNAME_BASE_IDX) + regNAME` or `BASE(regBLOCKid_REGISTER_BASE_IDX) + regBLOCKid_REGISTER`.
4. Pair the offset with generated shift/mask fields from the matching sh/mask header.
5. Use Display Core, GPIO, IRQ, DMUB, or encoder helper code to read/update/write the resulting hardware register.

Concrete consumers in this tree include `display/dmub/src/dmub_dcn401.c`, `display/dc/gpio/dcn401/hw_factory_dcn401.c`, `display/dc/gpio/dcn401/hw_translate_dcn401.c`, `display/dc/irq/dcn401/irq_service_dcn401.c`, `display/dc/clk_mgr/dcn401/dcn401_clk_mgr.c`, and `display/dc/resource/dcn401/dcn401_resource.c`. The specific registers in this chunk are mostly exercised by display output, link, audio, packet, debug, and HDA/HPO paths rather than by the DMUB reset/window subset shown in `dmub_dcn401.c`.

## State and persistence behavior

The header itself has no mutable state. The named offsets address state held by display, audio, PHY, and debug hardware. That state persists according to GPU/display IP lifetime: boot and firmware initialization, resource-pool construction, modeset, stream enable/disable, link training, audio enablement, runtime power management, suspend/resume, and GPU or display reset.

Important stateful areas are:

- HPO HDMI and DP controls are programming state for active display links. Stream mapper, input mux, link encoder clock, FRL configuration, transport-bus mode, packet controls, encryption controls, and stream/video controls must be sequenced with link setup and teardown.
- AFMT/APG, VPG, DME, and HDMI/DP packet registers hold sideband and audio packet configuration. Some associated status/CRC/result registers are hardware-produced and can change while the stream is running.
- DP Sym32 stream encoder state includes MSA timing/colorimetry, pixel format, SDP scheduling, metadata, panel replay, CRC, symbol counters, ALPM, and memory-power controls. Many controls are per-instance and must match the stream-to-link mapping.
- DP DPHY Sym32 state includes encryption, virtual-channel/SAT allocation, eDP ASSR, ALPM, test patterns, PRBS/custom pattern state, error status, and symbol counters. Training or diagnostic controls are live PHY/link state and may be unsafe to change during active video.
- RDPCSTX/DPCSSYS registers include transmitter PLL/CR access, PHY controls, fuses, debug, scratch, and override state. These can affect physical output and low-level link stability.
- HDA/Azalia controller state includes CORB/RIRB queues, immediate command/response paths, DMA position buffers, wall-clock aliases, stream descriptor control/status, BDL base addresses, cyclic buffer lengths, and link position aliases. Descriptor registers bridge display audio programming with host audio DMA semantics.
- `ix*` debug IDs are selector values for indirect debug reads. They do not store state by themselves, but selecting an ID exposes live debug state from CNVC, CM, writeback, MPC/MPCC, OGAM, and MCM blocks.

## Dependencies and integration points

- Must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h`. Offset macros identify registers; sh/mask macros identify fields. Either side drifting breaks generated register tables.
- Depends on AMDGPU Display Core register helpers such as `REG`, `REGI`, `SRI`, `REG_OFFSET_EXP`, `REG_READ`, `REG_WRITE`, `REG_UPDATE`, and generated table macros that paste `reg`/block/id tokens into names from this header.
- Integrates with DCN 4.0.1 resource setup, IRQ service, GPIO/HPD/DDC factory and translation, clock manager, DMUB register table setup, HPO HDMI/DP stream/link encoder code, audio packet programming, and HDA/Azalia display-audio handling.
- The `_BASE_IDX` values select address segments. In this chunk, base index 2 is common for DCN/DPCS/HPO DP blocks, base index 3 appears for HPO HDMI and high HDA/Azalia addresses, base index 0/1 appears in host HDA low-register and alias regions, and the `ix*` entries are indirect debug IDs without `_BASE_IDX` companions.
- Repeated instance naming is part of the contract. DP stream/Sym32/link/DPHY groups are encoded as explicit instance numbers; generic code should use the proper per-instance tables rather than deriving offsets arithmetically outside the generated macros.
- The HDA stream descriptors intentionally contain address aliases, such as FIFO size and format sharing the same offset and link-position alias registers using a different base index/address. Consumers must rely on the paired field masks to distinguish packed or aliased meanings.

## Risks and edge cases

- Generated-header drift is the main risk. A stale offset paired with correct field masks can silently target the wrong register, and a correct offset paired with stale masks can corrupt adjacent fields in packed registers.
- Segment/base-index mistakes are especially hazardous because the same numeric offset can mean different hardware depending on `BASE_IDX`. HDA low-register aliases and high `0x4b70xx` addresses make this visible in the same chunk.
- Several register names deliberately alias the same offset, including HDA CORB/RIRB control/status/size groupings, immediate command data/index, stream descriptor FIFO size/format, and link-position aliases. Full-register writes can clobber unrelated packed fields.
- Per-instance repetition creates copy/paste hazards. Using `APG1` with `DP_STREAM_ENC0`, `VPG8` with the wrong stream, or `DP_DPHY_SYM322` with the wrong link would compile if names exist but misprogram the hardware path.
- Status/result registers should not be handled like stable controls. Meter-buffer status, FIFO status, AFMT/APG CRC results, VPG generic status, DP Sym32 CRC/status/symbol counters, DPHY error/status/SAT status, RDPCSTX debug/fuse values, and Azalia link position are hardware-owned or diagnostic.
- ALPM and panel replay controls cross timing, link, and power domains. Incorrect sleep/wake/request/ready sequencing can produce link wake failures, blank frames, or missed interrupts.
- DPHY test-pattern and PRBS/custom pattern registers are powerful diagnostics. Accidentally enabling test patterns or stale custom seeds during active video can break link training or visible output.
- RDPCSTX PHY fuse/control/PLL override writes can affect physical-layer calibration. Tests should avoid changing these outside hardware bring-up or tightly controlled link-training paths.
- The chunk has boundary truncation: it begins after the previous HPO top block and ends at the `mpcc_mcm3_mpcc_mcmdebugind` address-block header before its `ixMPCC_MCM3_*` defines. Final per-file reconciliation should join adjacent chunks for complete block coverage.

## Test signals

- Build tests with DCN 4.0.1 enabled should compile all consumers that include `dcn_4_1_0_offset.h` and `dcn_4_1_0_sh_mask.h`, especially `dmub_dcn401.c`, `dcn401_resource.c`, `irq_service_dcn401.c`, and the DCN401 GPIO factory/translate code.
- Static generation checks should verify every `reg*` offset used by a DCN401 register-table macro has a matching `_BASE_IDX`, and every field use has a matching sh/mask entry in `dcn_4_1_0_sh_mask.h`.
- Instance-layout checks should compare repeated DP stream encoder, APG, DME, VPG, DP Sym32, DP link encoder, DP DPHY, RDPCSTX, and Azalia stream groups for expected stride and intentional aliases.
- Display validation should exercise HPO HDMI FRL and HPO DP output on all supported instances, including stream mapper routing, input mux changes, MSA/pixel-format programming, sideband packet delivery, metadata packets, panel replay, and stream disable/re-enable.
- Audio validation should cover AFMT/APG packet programming, IEC60958/audio-info paths, audio CRC diagnostics, HDA stream descriptors, BDL pointer programming, link-position reporting, and DMA position buffer aliases.
- Link diagnostics should cover DP DPHY training/test-pattern paths, PRBS/custom pattern registers, encryption/SAT/VC controls, DPHY error status, stream/link symbol counters, and ALPM sleep/wake/resume.
- Packet validation should verify VPG generic packets, ISRC, MPEG info, HDMI transport-bus generic packets, ACR packets, metadata packet controls, and update/status behavior across vblank updates.
- PHY and DPCS bring-up tests should validate RDPCSTX clock/control, CR address/data access, PLL update override, SRAM control, pattern detect, PHY control/fuse readouts, and debug-config behavior.
- Suspend/resume and GPU reset tests should confirm HPO link/stream state, memory-power controls, HDA stream descriptors, ALPM state, and packet-generator state are restored or reset as expected.
- Debug tooling tests should verify `ix*` indirect debug IDs select the intended CNVC, CM, writeback, MPC OCSC, MPCC, OGAM, and MCM views without treating them as direct MMIO offsets.
