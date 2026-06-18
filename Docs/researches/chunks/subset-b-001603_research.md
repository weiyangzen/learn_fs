# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h lines 1-2677

## Scope And Purpose

This chunk is the opening section of the generated AMD DCN 2.0.0 register offset header. It contains C preprocessor constants only: no functions, structs, enums, storage, or executable logic. The exported symbols map symbolic `mm...` register names to numeric MMIO offsets and pair each offset with an `mm..._BASE_IDX` selector that tells AMDGPU/DC register-access helpers which base-address table entry to use.

Within lines 1-2677, the header guard and AMD license are followed by 1,189 non-`BASE_IDX` register offset macros plus matching base-index macros. The visible offset range runs from `mmVGA_MEM_WRITE_PAGE_ADDR` at `0x0000` through the partial `HUBPREQ1` VM-context region ending at `mmHUBPREQ1_DC_VM_CONTEXT0_PAGE_TABLE_END_ADDR_MSB` at `0x071e`. The larger source file continues after this chunk, so this report covers only the address blocks visible in lines 1-2677.

The source tree is a Ceph-client mirror that vendors Linux AMDGPU display-driver code. This file is AMD DCN hardware register metadata, not Ceph distributed-filesystem code. Its purpose is to let DCN 2.0 display, memory-hub, interrupt, audio, writeback, and hub-pipe code use stable names rather than raw register offsets when programming display hardware.

## Important APIs, Types, And Macro Families

There are no callable APIs or C types in this range. The interface is the macro namespace. Each hardware register normally appears as:

- `mmREGISTER_NAME`, the register offset in the selected register aperture.
- `mmREGISTER_NAME_BASE_IDX`, the register-base index, with this chunk using base index `0` for a few legacy/audio aperture registers, `1` for early display/VGA/DCCG offsets, and mostly `2` for DCN display-decode blocks.

Major visible address-block families are:

- Legacy VGA and VGA interface registers: `mmVGA_*`, `mmD[1-6]VGA_CONTROL`, `mmCRTC8_*`, `mmSEQ8_*`, `mmGRPH8_*`, `mmDAC_*`, `mmGEN*`, `mmATTR*`, `mmVGA_SOURCE_SELECT`, `mmVGA_SRC_SPLIT_CNTL`, and `mmMCIF_*`. These expose compatibility VGA page, render, sequencer, DAC, source-selection, memory-base, interrupt, and MCIF controls.
- DCCG, display clocks, and PLL/perfmon: `mmPHYPLL[A-F]_PIXCLK_RESYNC_CNTL`, `mmDP_DTO*`, `mmOTG[0-5]_PIXEL_RATE_CNTL`, `mmDPPCLK*`, `mmDSCCLK*`, `mmDCCG_*`, `mmDENTIST_DISPCLK_CNTL`, `mmPLL_MACRO_CNTL_RESERVED*`, and `mmDC_PERFMON0/1_*`. These define offsets for pixel-clock resync, DTO phase/modulo registers, clock-gating controls, audio DTOs, vsync latch/counter controls, soft reset, and display perf counters.
- DMU, DCPG, DMCU, and interrupt hub control: `mmRBBMIF_*`, `mmDOMAIN*_PG_CONFIG/STATUS`, `mmDCPG_INTERRUPT_*`, `mmDC_IP_REQUEST_CNTL`, `mmDMCU_*`, `mmMASTER_COMM_*`, `mmSLAVE_COMM_*`, `mmDISP_INTERRUPT_STATUS*`, `mmDC_GPU_TIMER_*`, and `mm*_INTERRUPT_DEST`. These cover display power domains, DMCU firmware/RAM/mailbox/interrupt registers, GPU timer read positions, and interrupt destination routing for DCCG, DMU, DCPG, MMHUBBUB, WB, DCHUB, DPP, MPC, OPP, OPTC, OTG, DIG, HPD/I2C/AUX, Azalia, and DSC sources.
- Writeback, converter, scaler, and MCIF writeback: `mmWB_ENABLE`, `mmCNV_*`, `mmWB_DEBUG_*`, `mmWB_SOFT_RESET`, `mmWB_MEM_PWR_*`, `mmWBSCL_*`, `mmDC_PERFMON3_*`, and `mmMCIF_WB0_*` / `mmMCIF_WB1_*`. These offsets describe writeback enable/debug/reset/power, conversion window/source/test CRC, writeback scaler tap/ratio/init/manual-replicate settings, and two MCIF writeback buffer managers with addresses, pitches, status, arbitration, watermark, self-refresh, QoS, security, luma/chroma sizes, high address bits, and per-buffer resolution.
- MMHUBBUB and hubbub VM/return path: `mmWBIF0_*`, `mmMMHUBBUB_*`, `mmDCHUBBUB_SDPIF_*`, `mmDCN_VM_*`, `mmDCHUBBUB_RET_PATH_DCC_CFG*`, `mmDCHUBBUB_CRC*`, `mmDCHUBBUB_ARB_*`, `mmVTG[0-5]_CONTROL`, `mmDCFCLK_CNTL`, `mmDCHUBBUB_CTRL_STATUS`, and `mmDCN_VM_CONTEXT[0-15]_*`. These are the main display memory-hub offsets for VM aperture programming, local HBM aperture, pipe security levels, DCC return-path configuration, CRC readback, arbitration watermarks, self-refresh and DRAM-clock-change policy, global timer, surface-check addresses, VM context page tables, and VM fault reporting.
- Azalia/HDA audio display registers: `mmAZF0STREAM[0-15]_*`, `mmAZF0ENDPOINT[0-7]_*`, `mmAZF0INPUTENDPOINT[0-7]_*`, `mmAZALIA_*`, and `mmAZALIA_F0_*`. These cover indirect stream and codec endpoint index/data windows, controller clock/audio DTO/global capability/payload/CRC/memory power registers, root codec parameters, function controls, converter synchronization, audio port connectivity, and GTC group offsets.
- HUBP0 and the start of HUBP1 scanout fetch pipes: `mmHUBP0_*`, `mmHUBPREQ0_*`, `mmHUBPRET0_*`, `mmCURSOR0_0_*`, `mmDC_PERFMON7_*`, `mmHUBPXFC0_*`, `mmHUBP1_*`, and the first `mmHUBPREQ1_*` offsets. These expose surface config, tiling, viewport, request-size, clock/control/debug, surface pitch/address/meta-address, flip/queue/frame-pacing, in-use and earliest-in-use address latches, TTU QoS programming, per-HUBP VM aperture and context registers, cursor surface/position/DM data registers, HUBP perfmon, XFC buffer and underflow registers, and the beginning of HUBP1's equivalent request block.

## Control Flow And Data Flow

This chunk has no internal runtime control flow. Data flow is compile-time substitution: DCN 2.0 code includes this header, obtains a numeric offset and base index from a register macro pair, combines them with matching field definitions from `dcn_2_0_0_sh_mask.h`, and performs MMIO reads or writes through AMDGPU/DC helper layers.

Representative consumers in this tree include `display/dmub/src/dmub_dcn20.c`, `display/dc/irq/dcn20/irq_service_dcn20.c`, `display/dc/gpio/dcn20/hw_factory_dcn20.c`, `display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`, `display/dc/resource/dcn20/dcn20_resource.c`, and `amdgpu/gmc_v10_0.c`. Those call sites do the actual sequencing: select a register, read or write it via register macros or generated register lists, then use the companion mask/shift header to update fields.

The address-block order also reveals intended hardware topology. Early VGA/DCCG blocks set compatibility and clocking state; DMU/DMCU/IHC blocks expose power, firmware, timer, and interrupt routing state; writeback and MCIF blocks provide capture-buffer paths; MMHUBBUB/DCHUBBUB blocks provide display memory arbitration and VM context state; HDA/Azalia blocks support display audio; HUBP/HUBPREQ/HUBPRET/CURSOR/HUBPXFC blocks program per-pipe scanout fetch, cursor, and extended-flow-control state. The header itself does not enforce this order.

## State And Persistence Behavior

The file stores no software state and performs no I/O. The mutable state represented by the constants lives in DCN 2.0 hardware registers. Writes made through these offsets may persist until a later driver write, a modeset or plane update latches new scanout state, an interrupt ack clears sticky state, a DMCU/DMUB or display firmware sequence changes state, a power-gating transition resets a block, or GPU reset/suspend/resume restores display programming.

Important state categories represented in this chunk include legacy VGA compatibility state, display clock and DTO programming, DCCG soft reset and clock gating, perf-counter control/state, display power-domain status, DMCU firmware/RAM/mailbox registers, interrupt status and destination routing, GPU timer snapshots, writeback buffer and scaler programming, MCIF writeback buffer addresses and QoS, MMHUBBUB and DCHUBBUB memory-power state, VM aperture and page-table state, DCHUBBUB watermarks and surface checks, Azalia audio stream/controller/root codec state, HUBP surface/viewport/tiling/pitch/address/flip/cursor state, and HUBP VM/fault-related programming.

Several categories are sequencing-sensitive even though the macros cannot express that. Examples include `*_SOFT_RESET`, `*_MEM_PWR_CTRL/STATUS`, `*_INTERRUPT_STATUS`, `*_INTERRUPT_DEST`, `DMCU_*` firmware/RAM access, `MCIF_WB*` buffer-manager state, `DCHUBBUB_ARB_*` watermarks, `DCN_VM_CONTEXT*` page-table programming, `DCSURF_*` surface-address and flip registers, cursor address/position registers, and writeback/XFC underflow status. Callers must know whether a target register is read-only, write-one-to-clear, latched on update, protected by update locks, or safe only while a display pipe is disabled.

## Dependencies And Integration Points

This chunk depends on the rest of `dcn_2_0_0_offset.h` for the complete DCN 2.0 register map and on `dcn_2_0_0_sh_mask.h` for field masks and shifts. It is part of a family of generated DCN headers (`dcn_1_0`, `dcn_2_0_1`, `dcn_2_1_0`, `dcn_3_*`, and later versions) with similar names but generation-specific offsets and sometimes different register coverage.

The direct include sites visible in this repository are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c`

Primary integration surfaces are DRM/KMS modesetting, DCN 2.0 resource construction, clock-manager programming, IRQ source setup and routing, GPIO/display feature registration, DMUB/DMCU display microcontroller access, memory-controller/VM setup for display fetches, writeback capture paths, display audio setup, page-flip and cursor programming, and power-management or reset flows.

`BASE_IDX` is part of the integration contract. The same hex offset can mean a different physical register depending on the base index used by the register-access layer. For example, this chunk uses base index `0` for some legacy VGA/audio descriptor style offsets, `1` for early display decode ranges such as VGA/DCCG, and `2` for most DCN display-decode blocks. Losing or mismatching a base index can send an otherwise correct offset to the wrong aperture.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. These constants are accepted by the compiler as integers; a wrong offset or base index can still build cleanly while causing reads or writes to hit the wrong register.

Generation mismatch is a high-risk edge case. DCN 2.0, DCN 2.0.1, DCN 2.1, DCN 3.x, and older DCE/DCN generations share many names such as `mmDCCG_SOFT_RESET`, `mmDMCU_CTRL`, `mmAZALIA_CONTROLLER_CLOCK_GATING`, `mmDCHUBBUB_ARB_DATA_URGENCY_WATERMARK_A`, and `mmHUBPREQ1_DCSURF_PRIMARY_SURFACE_ADDRESS`, but the correct file must match the ASIC and field mask header used by the caller.

Offset/base-index errors in clock, reset, power, and VM registers can produce severe display failures: failed modesets, blank screens, underflow, hangs waiting for power/status bits, memory faults from bad page-table/aperture programming, interrupt storms or missing vblank/HPD/audio events, broken writeback capture, or failed suspend/resume.

HUBP and DCHUBBUB registers are especially sensitive because they point at scanout surfaces and govern memory fetch timing. Bad surface-address, meta-address, pitch, VM, TTU, watermark, or flip-control offsets can fetch from the wrong memory, miss a flip, report wrong in-use state, or produce underflow. Cursor and DM data offsets have similar visible failure modes for hardware cursors or DisplayPort metadata.

The chunk boundary is artificial. It starts at the file header, but it ends in the middle of the `dce_dc_dcbubp1_dispdec_hubpreq_dispdec` address block after `mmHUBPREQ1_DC_VM_CONTEXT0_PAGE_TABLE_END_ADDR_MSB_BASE_IDX`; later lines continue HUBPREQ1 and many additional DCN blocks. The final merged per-file report should not treat this chunk as a complete DCN 2.0 register map.

## Test Signals

There are no meaningful unit tests for this header chunk alone. Useful validation starts with build coverage for DCN 2.0 AMDGPU/DC configurations that include `dcn_2_0_0_offset.h` alongside `dcn_2_0_0_sh_mask.h`.

Generated-header integrity should be checked against AMD's authoritative DCN 2.0 register database or a known-good upstream Linux header. For this chunk, focus comparison on the block boundaries and base-index values for VGA/DCCG, DMU/DMCU/IHC, writeback/MCIF, MMHUBBUB/DCHUBBUB, Azalia, HUBP0, and the partial HUBP1 range.

Runtime validation signals include successful DCN 2.0 modeset and page-flip tests, stable vblank and interrupt delivery, working clock changes, no DCHUBBUB or HUBP underflow/fault status, correct writeback capture into MCIF buffers, working display audio streams and Azalia endpoint access, correct cursor movement and hot-spot behavior, valid VM aperture/page-table programming for display surfaces, and clean suspend/resume or GPU reset recovery.

Targeted diagnostics should exercise DCHUBBUB watermark programming, VM fault reporting, HUBP0/HUBP1 primary and chroma surface address flips, cursor address and position changes, DMCU/DMUB mailbox or firmware-access paths where applicable, writeback scaler/buffer-manager setup, audio DTO/stream configuration, interrupt destination routing, and perfmon counter reads for DCCG, DMU, MMHUBBUB, HDA, writeback, and HUBP blocks.

## Cross-Chunk Notes

This report covers only lines 1-2677 of `dcn_2_0_0_offset.h`. Later chunks complete HUBPREQ1 and define additional DCN 2.0 blocks. The final per-file research document should synthesize all chunk reports into one source-tree-aligned summary that treats the whole header as a generated DCN 2.0 register offset contract.
