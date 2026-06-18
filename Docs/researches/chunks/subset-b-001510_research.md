# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_0_d.h lines 6044-7658

## Scope And Purpose

This chunk is the final part of AMDGPU's generated DCE 11.0 register-address header. It contains no executable C logic; it is a compile-time map from symbolic register names to numeric MMIO or indirect register indices for the Display Controller Engine used by VI/Polaris-era AMD GPUs.

The range starts in legacy VGA indirect register indices and VGA MMIO controls, then covers display PHY PLL and UNIPHY addresses, display memory interface arbitration/watermark controls, HDMI/DP audio codec registers, blender and writeback/converter registers, display front-end clock/power controls, hot-plug-detect and I2C/DDC registers, virtual CRTC/blender/timing-generator registers, and XDMA master/slave register windows. It also closes the header with `#endif /* DCE_11_0_D_H */`.

The source path is under a Ceph client source mirror, but this file is Linux AMDGPU display hardware metadata. There is no Ceph filesystem behavior in this chunk.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, or persistent software objects in this line range. The API surface is entirely preprocessor constants:

- `mm*` names are register addresses for direct MMIO-style AMDGPU register accesses, or for indexed register address/data windows.
- `ix*` names are indirect register indices used through a paired index/data register or through a block-specific indirect access path.
- Many blocks define both a generic register name and instance-specific aliases, for example `mmDPG_PIPE_URGENCY_CONTROL` plus `mmDMIF_PG0_DPG_PIPE_URGENCY_CONTROL` through `mmDMIF_PG5_DPG_PIPE_URGENCY_CONTROL`.
- Repeated per-instance aliases encode DCE 11.0's display pipe layout: six main display pipes commonly step by `0x200` across `0x1bxx`, `0x1dxx`, `0x1fxx`, `0x41xx`, `0x43xx`, and `0x45xx`, while virtual-display blocks use the `0x47xx` range.

Major register families in this chunk include:

- Legacy VGA: `ixCRT*`, `ixGRA*`, `ixATTR*`, `mmVGA_RENDER_CONTROL`, `mmVGA_SOURCE_SELECT`, `mmVGA_MODE_CONTROL`, `mmVGA_MEMORY_BASE_ADDRESS`, per-display `mmD1VGA_CONTROL` through `mmD6VGA_CONTROL`, VGA status/interrupt/debug registers, and VGA page-address registers.
- PHY and link clocks: `mmBPHYC_DAC_*`, `mmPLL_*`, `mmBPHYC_PLL0_*` through `mmBPHYC_PLL2_*`, VGA pixel PLL variants such as `mmVGA25_PPLL_*`, and `mmPPLL_*` debug/spare registers.
- UNIPHY lanes/links: `mmUNIPHY_TX_CONTROL1` through `CONTROL4`, power, PLL feedback/control/spread-spectrum, synchronization, test/BIST, TMDS/DisplayPort tuning registers `mmUNIPHY_TMDP_REG0` through `REG6`, test-pattern, and debug registers, with instance aliases `mmBPHYC_UNIPHY0_*` through `mmBPHYC_UNIPHY8_*`.
- DMIF/DPG: pipe arbitration, watermark mask, urgency, DPM, stutter, NB pstate change, repeater, pre-check, debug, and test-debug registers for `DMIF_PG0` through `DMIF_PG5`, plus virtual DPG registers `mmDPGV0_*` and `mmDPGV1_*`.
- Azalia/HD audio: root/function/converter/pin codec parameters, immediate-command index/data registers, stream descriptor index/data registers, endpoint index/data windows, input endpoints, CRC controls, DTO/SCLK/DMA/CORB/RIRB controls, cyclic buffer synchronization, payload capabilities, and memory power control/status.
- Blender/writeback/converter: per-pipe `mmBLND*` control/update/underflow/update-lock/debug/test registers, virtual `mmBLNDV_*`, writeback enable/config, converter mode/window/source/CSC coefficients/round/clamp/test CRC, and converter debug registers.
- DCFE/DCO/HPD/I2C: display front-end clock/reset/debug/memory-power registers, virtual front-end registers, HPD interrupt/control/filter/fast-train registers for six connectors, DCO scratch/interrupt/clock/power/reset/debug registers, and DC/generic I2C/DDC transaction/speed/status/data registers.
- Virtual timing generator: `mmCRTCV_*` timing, sync, blanking, status, trigger, stereo, snapshot, update-lock, master update, interrupt, color, CRC, GSL, 3D structure, and test-debug registers.
- XDMA: top-level XDMA interface/config/interrupt/clock/memory-power/status/debug/power-gating registers, master global registers, six master pipe register groups, slave global registers, and six slave channel register groups.

Consumers pair this address header with `dce_11_0_sh_mask.h`, which supplies bit masks and shifts for the fields inside these addresses. Register access usually flows through AMDGPU helpers such as `RREG32()`, `WREG32()`, `dm_read_reg()`, `dm_write_reg()`, indexed Azalia helpers, or display-core register tables.

## Control Flow

This chunk has no local control flow. Its runtime effect is indirect: it determines which hardware register a distant driver read or write touches.

A typical control sequence using these constants is:

1. Select an address macro from this file, often with a pipe-specific offset or an instance-specific alias.
2. Read the register through `RREG32()`, `dm_read_reg()`, an Azalia endpoint helper, or a display-core register abstraction.
3. Decode or modify fields with masks from the matching `dce_11_0_sh_mask.h`.
4. Write the value back with `WREG32()` or `dm_write_reg()`, often inside display-mode programming, audio setup, power-gating, hotplug, I2C/DDC, or reset sequencing.

Visible integration examples in this repository include:

- `amdgpu/vi.c`, `amdgpu/cik.c`, `amdgpu/si.c`, `gmc_v*_0.c`, and `dce_v*_0.c` reading and writing `mmVGA_RENDER_CONTROL` to disable or restore VGA legacy rendering behavior during memory/display setup.
- `amdgpu/dce_v10_0.c`, `dce_v8_0.c`, and `dce_v6_0.c` using Azalia endpoint index/data registers to program audio codec endpoint state.
- DCE display core files under `display/dc/dce110/` including this header for timing generator, compressor, transform, OPP, clock, GPIO, link encoder, audio, and IRQ support.
- `display/dc/dce110/dce110_timing_generator_v.c` directly using `mmCRTCV_*` addresses for virtual timing-generator operations such as enable, blank control, status reads, timing programming, interlace setup, color programming, and frame-count reads.
- `display/dc/hwss/dce/dce_hwseq.h` and `dce110_hwseq.c` using virtual CRTC/blender offsets for hardware sequencer register table setup.
- SI/VI/MxGPU golden register arrays referencing `mmXDMA_CLOCK_GATING_CNTL` and `mmXDMA_MEM_POWER_CNTL` for XDMA clock and memory power programming.

Because the file is generated constants, bad behavior does not manifest near this file. A wrong address silently redirects a hardware access in display initialization, mode set, link/audio programming, hotplug handling, I2C/DDC transactions, virtual display timing, or XDMA setup.

## State And Persistence Behavior

The header itself stores no state and has no persistence. It names hardware-backed state held by the DCE, PHY, audio, VGA, virtual display, and XDMA blocks. That state persists according to hardware rules until changed by the driver, firmware, display microcode, hotplug events, audio codec commands, suspend/resume, power-gating, BACO-like low-power transitions, function reset, or full ASIC reset.

The state represented by these addresses spans several categories:

- Legacy compatibility state: VGA sequencer/CRT/graphics/attribute indices, VGA render routing, memory base addresses, VGA page addresses, and per-display VGA controls.
- Clock and link state: PLL dividers, spread-spectrum controls, update locks, analog controls, UNIPHY power and PLL controls, data synchronization, transmitter test registers, and PHY debug/BIST state.
- Display pipe state: DMIF arbitration, watermark, urgency, DPM, stutter, NB pstate, repeater, and debug state for the six main pipes and virtual pipes.
- Audio state: Azalia controller clocking, DMA, CORB/RIRB, stream descriptors, endpoint codec parameters, pin/converter controls, sink information, multichannel enables, LPIB snapshots, CRC windows/results, and input endpoint controls.
- Composition and writeback state: blender controls, update locks, underflow interrupt state, writeback enable/config, converter window/source/CSC coefficients, clamps, and test CRC state.
- Front-end and connector state: DCFE clock/reset/memory-power state, DCO scratch and interrupt status, HPD interrupt/control/filtering state, and DDC/I2C transaction state.
- Timing state: virtual CRTC totals, blanks, syncs, triggers, counters, frame/vblank status, stereo/snapshot/update-lock/master-update state, color registers, vertical interrupts, CRC windows/data, and GSL controls.
- XDMA state: interface status, interrupt status, power-gating status, master pipe transfer descriptors, remote/local GPU addresses, cache base addresses, channel starts, performance counters, and slave channel addressing/status.

The macros do not encode access semantics. A register may be read-only, write-only, write-one-to-clear, self-clearing, double-buffered, locked behind an update-lock register, valid only during blanking, valid only after a clock is enabled, or protected by an indirect index/data protocol. Consumers must follow the block-specific sequencing in the display and AMDGPU code.

## Dependencies And Integration Points

This chunk depends on the generated AMDGPU DCE register ecosystem:

- `dce_11_0_sh_mask.h` supplies the field masks and shifts for many addresses defined here.
- Other DCE generation headers for `dce_6_0`, `dce_8_0`, `dce_10_0`, and `dce_11_2` provide parallel ASIC-generation layouts used by sibling driver files.
- AMDGPU register helpers (`RREG32`, `WREG32`, display-core `dm_read_reg`/`dm_write_reg`, and register-table macros) consume these addresses.
- The DRM display stack, AMD display core, audio support, hotplug/HPD handling, I2C/DDC EDID reads, power management, and virtualization/XDMA setup all depend on these constants mapping to the correct hardware addresses.

Important integration surfaces are:

- DCE 11.0 display core initialization and mode-setting: timing generator, memory input/compressor, transform, output pixel processor, regamma/CSC, link encoder, and hardware sequencer code include this header.
- Audio-over-HDMI/DP support: Azalia stream/endpoint/pin/converter registers are the address side of audio codec programming and status polling.
- Connector discovery and link management: HPD and I2C/DDC registers connect this file to monitor hotplug, EDID fetches, and DisplayPort/HDMI setup.
- Power and reset flows: DCFE, DCO, XDMA, Azalia memory power, VGA render, UNIPHY power, PLL update, and DMIF stutter/DPM registers participate in suspend/resume, clock gating, memory power gating, and ASIC golden-register programming.
- Virtual display paths: `mmCRTCV_*`, `mmBLNDV_*`, `mmDPGV*`, and `mmDCFEV_*` are consumed by virtual timing/blending and hardware-sequencer tables.
- Multi-instance display pipes: generic names plus per-pipe aliases let shared display code use offsets while ASIC-specific tables can name exact pipe instances.

## Risks And Edge Cases

The main risk is silent hardware misaddressing. The compiler will happily accept an incorrect `#define`; the resulting failure appears only when a particular display, audio, HPD, I2C, virtual CRTC, PHY, or XDMA path uses that address.

High-risk address families include:

- `mmVGA_RENDER_CONTROL` and related VGA routing registers, because mistakes can leave legacy VGA decode enabled, route display status incorrectly, or interfere with memory-controller setup.
- PLL and UNIPHY registers, because wrong addresses can break link clocks, spread-spectrum programming, PHY power sequencing, or transmitter training.
- DMIF/DPG arbitration, watermark, urgency, stutter, and pstate registers, because display underflow, flicker, hangs, or power regressions may result from programming the wrong pipe or wrong control register.
- Azalia index/data, stream, endpoint, codec, DMA, and CRC registers, because audio failures can present as missing HDMI/DP audio, wrong sink info, format-change handling bugs, DMA underruns, or broken LPIB snapshots.
- HPD and I2C/DDC registers, because wrong constants can cause missed hotplug events, interrupt storms, EDID read failures, or incorrect connector detection.
- `mmCRTCV_*` virtual timing-generator registers, because virtual display mode programming relies on exact timing, blanking, status, update-lock, and color register addresses.
- XDMA master/slave pipe and channel registers, because bad addresses can corrupt remote/local surface addressing, channel starts, performance status, or memory/PCIe client configuration.

Repeated instance aliases are vulnerable to generated-copy mistakes. For example, most six-pipe DCE aliases are separated by fixed address strides, but virtual blocks and some debug/test registers do not always follow the same pattern. A single alias with the wrong instance address can work on one CRTC and fail only on another.

Index/data pairs need special care. Several names intentionally share the same numeric address, such as Azalia immediate-command index/data or VGA attribute/index/data aliases. The value alone is not enough to infer whether a caller is accessing an index, data, read, or write path; the surrounding protocol determines the meaning.

The chunk boundary is also relevant. Earlier chunks define the beginning and middle of `dce_11_0_d.h`, while this chunk only contains the tail. The final per-file merge should present this header as one generated DCE 11.0 address map, not as independent APIs split by these artificial line ranges.

## Test Signals

Validation is mostly build-time plus hardware/display behavior:

- AMDGPU and display-core builds should compile with DCE 11.0 register names used by `display/dc/dce110/*`, `display/dc/hwss/*`, `display/dc/irq/*`, `amdgpu/vi.c`, `pm/powerplay/hwmgr/polaris_baco.c`, and related code.
- Boot and mode-set testing on DCE 11.0 hardware should show stable display bring-up, correct CRTC timing, no unexpected underflow interrupts, no blanking/update-lock stalls, and correct frame/vblank counters.
- Multi-display tests should exercise all six pipe instance ranges so alias/stride errors are caught outside pipe 0.
- Virtual display paths should exercise `mmCRTCV_*`, `mmBLNDV_*`, `mmDPGV*`, and `mmDCFEV_*` through virtual timing-generator and hardware-sequencer flows.
- HDMI/DP audio tests should verify Azalia endpoint programming, codec sink info, stream format changes, multichannel/HBR paths, LPIB snapshots, and audio CRC/debug paths where available.
- Hotplug and EDID tests should verify HPD interrupt status/control/filtering and DC/generic I2C/DDC transactions across every connector.
- Suspend/resume, runtime power, and BACO-like transitions should verify DCFE/DCO/UNIPHY/Azalia/XDMA memory-power and clock-gating registers return to valid state.
- XDMA/MxGPU tests should verify clock gating, memory power, master/slave channel setup, remote address programming, and interrupt/status reporting.

Regression symptoms from bad constants include display underflows, black screens, modeset timeouts, incorrect virtual CRTC timing, broken HDMI/DP audio, missing or noisy HPD, EDID failures, link-clock or PHY training failures, resume-only display loss, VGA decode conflicts, XDMA transfer/channel failures, or failures limited to a specific display pipe instance.

## Cross-Chunk Notes

This is chunk 3 of 3 for `dce_11_0_d.h` in the current manifest. It begins at line 6044 with the tail of legacy VGA indirect constants and ends at line 7658 with the header guard close. Earlier chunks contain the first DCE 11.0 address families for the same generated namespace. The merge lane should combine all chunks into a single source-tree-aligned report for `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_0_d.h`.
