# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_offset.h lines 1-2680

## Purpose

This chunk is the opening portion of AMD's generated DCN 3.0.3 register-offset header for the display driver. It does not implement executable logic; it supplies preprocessor constants that map display hardware register names to register offsets and base-segment indices. Driver code combines each `mm...` offset with the corresponding `mm..._BASE_IDX` entry and the ASIC base table from `sienna_cichlid_ip_offset.h` to compute absolute MMIO addresses for DCN303 display programming.

The header is guarded by `_dcn_3_0_3_OFFSET_HEADER`, uses the MIT SPDX identifier, and starts the DCN303 address map at the VGA/MMHUBBUB, DCCG, DMU/DMCU/DMCUB, writeback, HDA/Azalia audio, DCHUBBUB, HUBP/HUBPREQ, and DPP0 blocks. The full file is longer, but this chunk ends in the DPP0 color-management register group.

## Important definitions and block coverage

The only public "API" in this chunk is a large set of C macros:

- `mm<REGISTER>`: the register's block-local offset value, for example `mmDCCG_GTC_CNTL`, `mmDMCUB_INBOX0_BASE_ADDRESS`, `mmHUBP0_DCSURF_SURFACE_CONFIG`, and `mmCM0_CM_GAMCOR_LUT_DATA`.
- `mm<REGISTER>_BASE_IDX`: the base segment selector used by helper macros such as `BASE(mm..._BASE_IDX)` or `REG_OFFSET(...)`. In this chunk the values are mainly `0`, `1`, or `2`.

Major register groups covered in lines 1-2680:

- VGA and legacy display decode registers: `mmVGA_*`, indexed DAC/CRTC/SEQ/GRPH names, and per-pipe `mmD1VGA_CONTROL` through `mmD6VGA_CONTROL`.
- DCCG display clock generation: PHY pixel-clock resync, DP DTO phase/modulo, DISPCLK/DPPCLK/DSCCLK controls, GTC counters, audio DTOs, vsync latch/counter controls, clock gating, and soft reset.
- DC perfmon instances 0-6: repeated `PERFCOUNTER_CNTL`, `PERFMON_CNTL`, current value, high, and low counter registers for DCCG, DMU, MMHUBBUB, HDA, DCHUBBUB, and HUBP instances.
- DMU/DMCU/DMCUB control: DMCU firmware address/checksum/interrupt/communication registers; DMCUB region offsets and top addresses; code-window region 3 mappings; inbox/outbox queues; scratch registers; GPINT registers; timers; memory/security/fault controls.
- Interrupt hub/control: `mmDISP_INTERRUPT_STATUS*`, GPU timer start/read registers, and interrupt-destination registers for DCCG, DMU, DCHUB, HUBBUB, WB, MPC, OPP, OPTC, OTG, DIG, I2C/DDC/HPD, DCIO, AUX, DSC, and audio.
- MCIF writeback and MMHUBBUB: writeback buffer manager status/control, Y/C buffer addresses and high-address registers, arbitration, watermarks, VMID control, warmup configuration, memory power, clock, soft reset, and VGA interface controls.
- HDA/Azalia audio: stream index/data registers for streams 0-15, endpoint and input-endpoint index/data windows, controller clock/DTO/DMA/RIRB/CORB controls, codec root parameters, CRC registers, cyclic-buffer sync, payload capabilities, and memory power.
- DCHUBBUB memory path: SDPIF configuration and VM aperture registers, return-path DCC/CRC/memory-power registers, hubbub arbitration watermarks A-D, DRAM/self-refresh clock-change controls, timeout detection, surface-check addresses, VTG controls, performance measurement, and VM request context programming for contexts 0-15.
- HUBP/HUBPREQ/HUBPRET and cursor for instances 0 and 1: surface configuration, tiling, viewport dimensions, request sizing, surface pitch, primary/secondary luma/chroma and metadata addresses, flip control/status, TTU/QoS parameters, VM aperture/L1 TLB controls, prefetch/vblank/flip/nominal timing parameters, cursor addresses/position/hot spot/DMDATA, and read-line controls.
- DPP0 front-end processing through the start of CM: DPP top control/reset/CRC, CNVC pixel format, format conversion bias/scale, color keyer, pre-CSC matrices, cursor conversion colors, DSCL coefficient RAM and scaler ratios/inits, line-buffer and output-buffer controls, and CM post-CSC/gamut/gamma-correction LUT registers.

There are a few intentional-looking aliases where multiple symbolic names share the same offset, such as legacy VGA index/data windows and `mmFMON_CTRL`/`mmFMON_CTRL_1`. These allow common helper tables to use semantic names even when the hardware decodes them at the same address.

## Control flow and runtime behavior

This file has no functions, branches, loops, storage, or runtime control flow. Its behavior happens entirely at C preprocessing and compile time.

The runtime register access flow is supplied by including code:

1. DCN303 resource, IRQ, and DMUB sources include this header together with `sienna_cichlid_ip_offset.h` and `dcn_3_0_3_sh_mask.h`.
2. Local macros such as `SR(reg_name)`, `SRI(reg_name, block, id)`, and DMUB's `REG_OFFSET(reg_name)` expand `BASE(mm..._BASE_IDX) + mm...`.
3. `BASE(seg)` expands through `DCN_BASE__INST0_SEG<seg>` from the ASIC IP offset header, producing an absolute register offset for the ASIC instance.
4. The resulting constants initialize register tables, for example hubbub/HUBP/DCCG register structs, DMUB common register offsets, and IRQ source descriptors.
5. Later driver register helpers use those tables with field masks/shifts from the companion `_sh_mask.h` header to perform MMIO reads, writes, interrupt acknowledgement, watermarks, flips, power state changes, and firmware mailbox operations.

## State and persistence

This header stores no driver state and persists nothing by itself. The constants point at hardware stateful registers. Writes by the display driver affect volatile hardware state such as DMCUB mailbox pointers, display VM context page table bases, surface addresses, flip status, memory power controls, clock controls, watermarks, perfmon counters, audio stream windows, and color/scaler LUT/index data. That state lives in GPU display hardware and, for some firmware-facing registers, in DMCUB/DMCU-managed SRAM or queue memory configured elsewhere.

Because the macros are compile-time constants, a wrong offset or base index becomes a persistent binary-level defect: every runtime access through the affected table targets the wrong MMIO address until the driver is rebuilt.

## Dependencies and integration points

Direct companion dependencies:

- `sienna_cichlid_ip_offset.h`: provides `DCN_BASE__INST0_SEG*` base values selected by `_BASE_IDX`.
- `dcn/dcn_3_0_3_sh_mask.h`: provides bit-field masks and shifts for the same register names.
- `dpcs/dpcs_3_0_3_offset.h` and `dpcs/dpcs_3_0_3_sh_mask.h`: included beside this file for DisplayPort/DPCS blocks in DCN303 resource code, although not defined in this chunk.

Observed integration points:

- `display/dc/resource/dcn303/dcn303_resource.c` includes this header and uses `SR`, `SRI`, `SRII`, `DCCG_SRII`, and related macros to populate DCN303 register structures. The resource file advertises `num_timing_generator = 2`, `num_video_plane = 2`, `num_audio = 2`, and `num_vmid = 16`, matching the two HUBP/HUBPREQ instances, two OTG-facing paths, audio support, and VM context range seen in this chunk.
- `display/dmub/src/dmub_dcn303.c` includes this header and expands `REG_OFFSET(...)` into `dmub_srv_dcn303_regs`, especially for DMCUB internal, inbox/outbox, scratch, interrupt, timer, memory, and fault registers.
- `display/dc/irq/dcn303/irq_service_dcn303.c` includes this header and uses `SRI(...)` to build IRQ source metadata. In this chunk, the `HUBPREQ0/1_DCSURF_SURFACE_FLIP_INTERRUPT` offsets back page-flip IRQ entries, while HPD/OTG registers are also resolved through the same base-plus-offset pattern.

## Risks and correctness concerns

- The file is generated-style hardware data. Manual edits are high risk because a single incorrect hex value or `_BASE_IDX` can redirect register access to another block, causing display bring-up failures, hangs, missed interrupts, incorrect flips, firmware mailbox breakage, audio malfunction, or memory/power sequencing bugs.
- The names and companion field masks must stay synchronized. If `dcn_3_0_3_offset.h` and `dcn_3_0_3_sh_mask.h` come from different register generations, the driver can write valid addresses with invalid field encodings.
- The repeated instance blocks have dense patterns, but they are not safe to infer mechanically without the hardware source: offsets for HUBP0/HUBP1, stream 0-15, endpoints, perfmon instances, and VM contexts must match the ASIC address map exactly.
- Alias definitions are expected for some legacy windows; tools looking for duplicate offsets should distinguish intentional aliases from accidental overlap.
- Registers that program 64-bit addresses are split into low/high pairs. Using only one half or mixing pair order in consumers would corrupt display VM, DMCUB region, cursor, surface, or writeback buffer addresses.
- The chunk includes both control and status/ack registers. Consumer code must preserve hardware write-one-to-clear and polling semantics from the field definitions and block programming guides; the offset header alone does not encode access type.

## Test signals and validation

Useful validation signals for this chunk are mostly build-time and hardware/driver runtime signals:

- Compile the AMD display driver path with DCN303 enabled; failures in register table initialization usually expose missing or renamed macros.
- Check that `dcn303_resource.c`, `dmub_dcn303.c`, and `irq_service_dcn303.c` still compile with this header and the matching `_sh_mask.h`.
- Boot or load the driver on matching DCN 3.0.3 hardware and verify display modeset, page flips, vblank/vupdate IRQs, HPD/HPDRX events, DMCUB firmware communication, audio stream setup, cursor updates, and memory power transitions.
- Exercise multi-plane scanout on both HUBP instances; this stresses `HUBP0/1`, `HUBPREQ0/1`, cursor, flip, prefetch, TTU, and VM context offsets.
- Use debug/perfmon paths to confirm DC perfmon counters and timeout/fault status registers are readable at the expected addresses.
- Compare generated offsets against the vendor register database or adjacent known-good DCN 3.0.x offset headers when updating, while treating DCN303-specific differences as authoritative only if sourced from the correct ASIC data.
