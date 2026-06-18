# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h lines 7853-10395

## Scope

This chunk is a generated DCN 3.1.4 register-offset slice from `dcn_3_1_4_offset.h`. It contains preprocessor constants only: `reg...` macros for MMIO register offsets and matching `reg..._BASE_IDX` macros, almost all with base index `2`. There are no C functions, structs, enums, branches, loops, allocation paths, or driver-owned state objects in this range.

The range starts in the tail of the OTG0 timing-generator block at `regOTG0_OTG_FLOW_CONTROL_BASE_IDX`, covers complete OTG1, OTG2, and OTG3 offset blocks, then covers shared OPTC/GSL/ODM, display I/O scratch/control/perfmon, HPD0-HPD4, DP AUX0-AUX4, and four repeated DIG instances. For DIG0 through DIG3 it includes VPG packet offsets, AFMT audio/infoframe offsets, DME offsets, DIG/HDMI/TMDS encoder offsets, and DP link offsets. The chunk ends partway through the DP3 block at `regDP3_DP_DPHY_SYM1_BASE_IDX`; later DP3 offsets are outside this work item.

## Purpose And Hardware Surface

The purpose of this header range is to provide the address half of the AMDGPU Display Core register ABI for DCN 3.1.4 hardware. Driver code uses these constants with companion field-mask headers to access display MMIO registers through generated register tables and helper macros instead of embedding numeric addresses in functional code.

Major hardware areas represented here:

- OTG timing generators: the tail of OTG0 plus full OTG1-OTG3 register-offset maps. These cover horizontal/vertical timing, blanking and sync controls, triggers, counters, stereo/interlace state, snapshots, update locks, CRC windows and data, static-screen control, global sync, DRR, DTO, DSC start position, pipe update status, and spare registers.
- OPTC/GSL/ODM shared controls: global sync source selection, OPTC clock and spare controls, ODM memory power controls/status, and DC perfmon counter registers for display-timing instrumentation.
- DIO shared controls: I2C/DOUT control, DIO scratch registers, stream encoder selection, global DIO control/status, PHY clock selection, DIG soft reset, link enable/control registers, and DIO perfmon registers.
- HPD0-HPD4 hotplug-detect blocks: interrupt status/control and toggle filter control offsets for the five hotplug pins exposed in this slice.
- DP AUX0-AUX4 blocks: AUX transaction control, arbitration, reply/read/write data, interrupt/debug/status, low-time count, and PHY wake control offsets for five DisplayPort AUX channels.
- DIG0-DIG3 repeated display output blocks: VPG generic packet registers, AFMT audio/infoframe registers, DME control/memory-control registers, DIG frontend/backend/HDMI/TMDS registers, and DP link/stream/PHY/secondary-packet/MST/MSO/DSC/ALPM registers for DP0-DP2 plus the beginning of DP3.

## Important Definitions

The exported interface is the generated macro naming convention:

- `reg<INSTANCE>_<REGISTER>` gives the register offset used by AMD display register accessors.
- `reg<INSTANCE>_<REGISTER>_BASE_IDX` selects the register base aperture index used by the generated register table. In this chunk the value is consistently `2`.
- `// addressBlock: ...` comments identify the hardware block for the following offsets.
- `// base address: ...` comments show the block-local hardware base used by the generated offset namespace.

Important offset families in this chunk:

- `regOTG0_*`, `regOTG1_*`, `regOTG2_*`, and `regOTG3_*` identify timing-generator registers for scan timing, vblank/vsync, frame and HV counters, update locks, vertical interrupts, CRC capture, global sync, dynamic refresh rate, trigger/manual-flow controls, DTO, DSC start position, and status readbacks.
- `regGSL_*`, `regOPTC_*`, and `regODM_*` expose shared display timing controls: global sync source selection, OPTC clock control/spare state, and ODM memory power state.
- `regDC_PERFMON15_*` and `regDC_PERFMON16_*` cover counter control, config, high/low value, and counter status offsets for display perfmon blocks.
- `regDOUT_*`, `regDIO_*`, `regDIG_SOFT_RESET`, and `regDIO_LINK*` provide shared DIO register offsets for DOUT/I2C configuration, scratch state, DIO global control/status, PHY clock selection, DIG reset, and link routing/control.
- `regHPD0_*` through `regHPD4_*` map hotplug interrupt status/control and debounce/toggle filter registers.
- `regDP_AUX0_*` through `regDP_AUX4_*` map AUX channel control, request/reply payload, arbitration, interrupt, debug, status, timing, and PHY wake registers. These are separate from the DP main-link `regDP0_*` style offsets.
- `regVPG0_*` through `regVPG3_*` map video packet generator generic packet access/data/update/status and MPEG infoframe registers.
- `regAFMT0_*` through `regAFMT3_*` map audio formatter VBI/audio packet controls, infoframe payload registers, IEC 60958 channel-status words, audio CRC/ramp/result/status, interrupt status, audio source control, and AFMT memory power registers.
- `regDME0_*` through `regDME3_*` map DME control and memory-control registers for each DIG instance.
- `regDIG0_*` through `regDIG3_*` map DIG frontend/backend enable and mode controls, output CRC, clock/test/random patterns, FIFO controls, HDMI metadata/audio/ACR/VBI/infoframe/generic packet controls, HDMI general control, AFMT connection, TMDS pattern/DC-balancer controls, DIG version, and force-disable.
- `regDP0_*`, `regDP1_*`, and `regDP2_*` map complete DP main-link blocks in this slice: link control, pixel format, MSA colorimetry/misc/timing, stream control, DPHY/training/symbol/scrambler/FEC/CRC/PRBS controls, secondary-packet controls, audio M/N/timestamp, MST/MSE allocation, DSC/MSO metadata, generic stream packets, ALPM, and AUX-less ALPM controls.
- `regDP3_*` begins the next DP main-link block, from `DP_LINK_CNTL` through `DP_DPHY_SYM1`; the rest of DP3 is intentionally outside this chunk.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior appears when AMDGPU Display Core code combines these offset macros with generated shift/mask constants and register helper APIs. A typical call path is:

1. Select a DCN 3.1.4 register offset such as an OTG timing register, HPD interrupt register, AUX request register, DIG HDMI packet register, or DP link register.
2. Pair the offset with field shifts and masks from the companion `dcn_3_1_4_sh_mask.h` generated header.
3. Use display register helpers such as generated `REG_GET`, `REG_SET`, `REG_UPDATE`, or equivalent accessors to issue MMIO reads, writes, or read/modify/write operations.
4. Hardware stores, consumes, latches, clears, or reports the register-backed state according to the block semantics.

The state represented by this chunk is hardware state, not normal kernel memory:

- Persistent configuration state includes OTG timing totals, blanking/sync placement, interlace/stereo/static-screen controls, global-sync selection, DIO link routing, DIG mode/source/backend enable, HDMI packet/audio/ACR/TMDS settings, DP pixel format, MSA/VBID/timing, link framing, DPHY training/scrambler/FEC settings, MST/MSE allocation, DSC/MSO metadata, VPG packet contents, and AFMT audio/infoframe contents.
- Volatile status/readback state includes OTG positions and counters, frame/VF/HV counts, interlace/stereo/snapshot/global-sync status, pipe update status, CRC data, HPD interrupt/toggle status, AUX replies/status/debug, DIO status, DIG FIFO and output CRC status, HDMI packet/readback status, DP stream/link/FEC/CRC/MST/MSE status, and ALPM pending/status registers.
- Side-effecting write paths are implied by many offsets even though the side effects are not described in this offset header. Examples include OTG count resets, manual triggers, update locks, vertical interrupt controls, CRC controls, HPD interrupt controls, AUX transaction control/arbitration, DIG soft reset, stream/backend enables, HDMI packet send controls, DP training pattern controls, secondary-packet send controls, MSE/SAT update triggers, and ALPM controls.
- Several register families are timing-sensitive. OTG update locks and double-buffer controls, DP secondary-packet scheduling, DP stream enable/defer, MST slot updates, DSC/PPS-related packet controls, HDMI infoframe updates, and ALPM state transitions need sequencing against vblank, vupdate, link training, stream disable, or power-management flows.

The offsets do not encode safety rules. Correct callers still need the appropriate display locks, pipe/update-lock sequencing, hardware status polling, ACK/clear semantics, and instance selection before touching live display registers.

## Dependencies And Integration Points

This generated header integrates with:

- Companion DCN 3.1.4 generated mask/shift headers that define the bit layout for each offset named here.
- AMDGPU Display Core register tables that aggregate `reg...` offset macros into per-IP block structures for timing generators, link encoders, AUX, HPD, audio formatter, video packet generator, and diagnostics code.
- Display modeset and timing code that programs OTG totals, syncs, blanking, update windows, DRR parameters, CRC capture, vertical interrupts, global sync, and pipe update status.
- Link encoder and connector code that uses DIO shared controls, DIG soft reset, link routing, HPD status/interrupts, and AUX transactions for DisplayPort and HDMI connector bring-up.
- DisplayPort main-link code that programs DP0-DP2 link control, lane and pixel-format state, MSA/VBID, video M/N, DPHY training/scrambler/FEC/CRC/test patterns, secondary packets, DSC/MSO metadata, MST/MSE scheduling, and ALPM.
- HDMI and TMDS code that programs DIG frontend/backend selection, HDMI enable/status, audio and ACR packets, VBI/infoframes/generic packets, deep-color/general-control state, TMDS patterns, and DIG force-disable/version checks.
- Audio paths that use AFMT packet controls, infoframe words, IEC 60958 words, audio CRC/ramp/status, audio source selection, and AFMT memory power offsets.
- Diagnostics and validation paths using OTG CRC, DIG output CRC, DP DPHY CRC, perfmon counters, FIFO status, AUX debug/status, HPD status, and TMDS/test-pattern registers.
- Power-management paths using ODM memory power, AFMT memory power, DME memory control, DP AUX PHY wake, DP ALPM/AUX-less ALPM, and PHY clock/link controls.

Because these are preprocessor constants, a missing macro reference is caught at compile time, but a wrong numeric offset or wrong instance prefix can compile and misprogram hardware at runtime.

## Risks And Maintenance Notes

- Numeric offset drift is the primary risk. If an offset no longer matches the DCN 3.1.4 register specification, the driver can write the wrong MMIO register while the C code still compiles.
- The slice is heavily repetitive across OTG1-OTG3, HPD0-HPD4, AUX0-AUX4, and DIG/DP0-DP3 instances. Prefix mistakes can target the wrong timing generator, connector, AUX channel, encoder, or link.
- The work item starts and ends mid-block. OTG0 is missing its earlier timing offsets, and DP3 is only present through `DP_DPHY_SYM1`; adjacent chunk research is required for a complete per-file view.
- Base-index consistency matters. Most macros in this range pair an offset with `_BASE_IDX 2`; changing either side independently can redirect register-helper access into the wrong MMIO base.
- Side-effecting registers are vulnerable to generic read/modify/write misuse. Reset, trigger, ACK, clear, send, lock, and update bits should be handled with block-specific semantics rather than treated like persistent booleans.
- Timing-sensitive OTG and packet registers can cause visible glitches if programmed while active without update locks, double-buffering, or vblank/vupdate sequencing.
- AUX and HPD offsets sit on hotplug/link-management paths. Incorrect status, interrupt, or arbitration register access can break connector detection, DPCD/EDID reads, link training, or wake behavior.
- DP MST/MSE, DSC, MSO, secondary-packet, and ALPM offsets interact with live link bandwidth and packet scheduling. Bad instance selection or stale offsets can cause missed metadata, failed compressed streams, stream starvation, or link idle/resume failures.
- HDMI audio/infoframe/ACR/TMDS offsets are user-visible despite being low-level constants. Wrong values can produce a lit display with bad audio, invalid metadata, CRC failures, or TMDS test-pattern problems.

## Test Signals

Useful validation signals for this chunk are mostly generated-header consistency, compile coverage, and hardware/display smoke tests:

- Build AMDGPU with DCN 3.1.4 support and ensure all generated `reg...` names referenced by register tables and display code resolve.
- Run generated-header checks that each non-`_BASE_IDX` offset has the expected `_BASE_IDX` partner, address-block ordering matches the hardware specification, and repeated instances preserve expected offset spacing.
- Exercise modeset coverage on multiple pipes using OTG0-adjacent state and full OTG1-OTG3 state: timing totals, sync/blanking, update locks, vertical interrupts, DRR, global sync, DSC start position, and CRC readbacks.
- Validate HPD0-HPD4 interrupt/toggle handling and DP AUX0-AUX4 transactions with connector hotplug, EDID reads, DPCD reads/writes, AUX wake, and link-training setup.
- Exercise DIG0-DIG3 HDMI/TMDS paths, including frontend/backend enable, HDMI packet controls, generic/infoframe/VBI/audio packets, ACR 32/44.1/48 kHz programming, TMDS controls, output CRC, FIFO status, and force-disable behavior.
- Exercise AFMT and VPG paths for all four DIG instances with audio infoframes, IEC 60958 data, generic packets, MPEG infoframes, CRC/status readback, and memory power transitions.
- Exercise DP0-DP2 link bring-up, MST, DSC, MSO, secondary packets, GSP scheduling, DPHY training patterns, FEC, scrambler, PRBS, CRC, video M/N, MSA/VBID, ALPM, and AUX-less ALPM.
- Include at least a DP3 smoke path for the registers covered here: link control, pixel format, MSA misc/colorimetry/config, stream control, steer FIFO, video timing/M/N, link framing, HBR2 eye pattern, interrupt control, DPHY control, training pattern selection, and symbol 0/1 programming.
- Use suspend/resume and display blank/unblank tests to cover memory-power, PHY wake, ALPM, HPD, AUX, and stream reprogramming paths.

## Chunk-Specific Summary

Lines 7853-10395 define a dense DCN 3.1.4 display register-offset surface rather than executable code. The central responsibility of this slice is mapping timing generators, display I/O, hotplug/AUX channels, packet/audio helpers, digital encoders, HDMI/TMDS controls, and DP main-link registers to the numeric MMIO offsets consumed by AMDGPU Display Core. Correctness depends on exact generated offsets, matching `_BASE_IDX` values, instance-correct macro use, and validation through modeset, hotplug/AUX, HDMI/audio, DisplayPort link-training, MST/DSC/MSO, ALPM, CRC, and power-management tests.
