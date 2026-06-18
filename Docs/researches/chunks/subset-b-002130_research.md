# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 30082-32579

## Purpose

This chunk is a generated AMD DCN 3.6.0 register field shift/mask slice. It contains no executable functions or C types; its API is preprocessor constants named as `<register>__<field>__SHIFT` and `<register>__<field>_MASK`. Display Core and DMUB code combine these constants with the matching `dcn_3_6_0_offset.h` register offsets and register helper macros to read, update, and write MMIO fields without hardcoding bit locations.

The range starts at the tail of the OTG2 block (`OTG2_OTG_PIPE_UPDATE_STATUS` and `OTG2_OTG_SPARE_REGISTER`), then covers the full `dce_dc_optc_otg3_dispdec` timing-generator block, OTG CRC32 readout blocks `OTG_CRC320` through `OTG_CRC323`, OPTC miscellaneous/global-source-lock/memory-power fields, DC perfmon counter 17, HPD0 through HPD4 hotplug detect fields, DisplayPort transmitter instance DP0, and the beginning of DIG0 frontend control.

## Important APIs and register groups

- `OTG3_OTG_H_*`, `OTG3_OTG_V_*`, and sync-control fields define horizontal/vertical totals, blanking, sync positions, sync polarity, timing division, dynamic refresh min/max/mid totals, v-total event interrupts, nominal vsync interrupt clearing, and count-stop controls for timing generator instance 3.
- `OTG3_OTG_TRIGA_CNTL`, `OTG3_OTG_TRIGB_CNTL`, manual trigger registers, and `OTG3_OTG_FORCE_COUNT_NOW_CNTL` expose trigger source selection, pipe selection, polarity, resync bypass, edge-detect mode, frequency, delay, occurred/status, clear, and force-count sequencing.
- `OTG3_OTG_CONTROL`, `OTG3_OTG_CLOCK_CONTROL`, `OTG3_OTG_MASTER_EN`, and interlace/stereo/3D fields control OTG enablement, disable/start points, output muxing, field-number behavior, clock enable/gating/reset/busy status, stereo eye selection, and 3D frame count behavior.
- `OTG3_OTG_STATUS*`, `OTG3_OTG_STATUS_POSITION`, `OTG3_OTG_STATUS_HV_COUNT`, `OTG3_OTG_STATUS_FRAME_COUNT`, `OTG3_OTG_STATUS_VF_COUNT`, snapshot registers, pixel readback registers, long-vblank/static-screen status, and manual vsync force fields provide live timing state and diagnostics.
- `OTG3_OTG_INTERRUPT_CONTROL`, `OTG3_OTG_VERTICAL_INTERRUPT0/1/2_*`, `OTG3_OTG_V_TOTAL_INT_STATUS`, and `OTG3_OTG_GLOBAL_SYNC_STATUS` define enable/type/status/clear/ack masks for vsync, vupdate, vstartup, vready, vertical interrupt lines, v-total changes, and no-lock events.
- `OTG3_OTG_CRC_CNTL`, CRC window registers, CRC data registers, signature masks, readback windows, and `OTG_CRC320` through `OTG_CRC323` data registers configure and read CRC capture for multiple CRC engines/windows, including 16-bit RG/B/C fields and 32-bit R/G/B/C/AES readouts.
- `OTG3_OTG_DOUBLE_BUFFER_CONTROL`, `OTG3_OTG_UPDATE_LOCK`, `OTG3_OTG_MASTER_UPDATE_LOCK`, `OTG3_OTG_MASTER_UPDATE_MODE`, `OTG3_OTG_VUPDATE_KEEPOUT`, and `OTG3_OTG_GLOBAL_CONTROL0` through `GLOBAL_CONTROL4` describe double-buffer, master update lock, keepout, and global update-lock timing windows.
- `OTG3_OTG_GSL_CONTROL`, `OTG3_OTG_GSL_VSYNC_GAP`, `OTG3_OTG_GSL_WINDOW_X/Y`, `GSL_SOURCE_SELECT`, `OPTC_DLPC_CONTROL`, and `OPTC_CLOCK_CONTROL` are global sync lock and OPTC misc fields for selecting GSL sources, windows, master modes, vsync-gap diagnostics, DLPC snapshot, and OPTC clock gating.
- `OTG3_OTG_DRR_*`, `OTG3_OTG_M_CONST_DTO0/1`, `OTG3_OTG_REQUEST_CONTROL`, `OTG3_OTG_DSC_START_POSITION`, and `OTG3_OTG_PIPE_UPDATE_STATUS` cover dynamic refresh rate timing interrupts, v-total range/change/trigger windows, DRR control, DTO constants, request disabling, DSC start position, and pipe update keepout status.
- `ODM_MEM_PWR_CTRL`, `ODM_MEM_PWR_CTRL3`, and `ODM_MEM_PWR_STATUS` expose per-ODM-memory power force/disable/state fields for memories 0-7 plus unassigned/vblank power modes.
- `DC_PERFMON17_*` describes one display perfmon instance: event selection, counted-value source/type, increment mode, hardware control, run enable, restart/interrupt bits, eight counter states, count-off interrupt handling, clock enable, cvalue high/low, and perfmon high/low readback.
- `HPD0_DC_HPD_*` through `HPD4_DC_HPD_*` repeat the hotplug-detect layout for five connectors: HPD sense/status, delayed sense, RX interrupt status, ack, polarity, enable, connection/RX timers, connect fast-train/AUX delays, and toggle-filter connect/disconnect delays.
- `DP0_DP_LINK_CNTL`, `DP0_DP_PIXEL_FORMAT`, `DP0_DP_CONFIG`, `DP0_DP_VID_STREAM_CNTL`, `DP0_DP_VID_TIMING`, `DP0_DP_VID_N/M`, `DP0_DP_LINK_FRAMING_CNTL`, and MSA/VBID fields encode DP link/stream setup, pixel encoding, MSA colorimetry and timing, timing offset, enhanced framing, TU/link training behavior, and stream interrupt handling.
- `DP0_DP_DPHY_*` fields define PHY internal controls, lane symbol values, 8b/10b mode, PRBS/scrambler controls, HBR2 pattern selection, CRC controls/results/status, fast-training controls/status, and BS/SR symbol-count swap controls.
- `DP0_DP_SEC_*`, `DP0_DP_GSP8_CNTL` through `GSP11_CNTL`, `DP0_DP_SEC_METADATA_TRANSMISSION`, and `DP0_DP_GSP_EN_DB_STATUS` are secondary packet controls for audio/video packets, GSP 0-11 send/enable/line-number/pending/active/deadline status, metadata packets, PPS marking, and GSP enable double-buffer status.
- `DP0_DP_MSE_*`, `DP0_DP_MSO_*`, `DP0_DP_DSC_CNTL`, and SAT status registers cover Multi-Stream Transport/Multi-Stream Operation: stream allocation table entries for sources 0-5, encryption flags/types, slot counts, SAT update/status, link timing, secondary-packet enable masks per SST link, and DSC mode.
- `DP0_DP_ALPM_CNTL`, `DP0_DP_AUXLESS_ALPM_CNTL1` through `CNTL5`, and stream/link symbol counters define low-power link sleep/standby/wakeup/FEC scheduling, AUX-less ALPM hardware mode, frame/line-number tracking, wakeup interrupts, and stream/link symbol counter enable/reset/status.
- `DIG0_DIG_FE_CNTL` and the start of `DIG0_DIG_FE_CLK_CNTL` define DIG frontend source selection, stereosync selection/gating, digital bypass, split-link pixel grouping, input-pixel selection, frontend mode, clock enable, and soft reset. The chunk stops after `DIG_FE_SOFT_RESET_MASK`, so remaining DIG0 clock masks belong to the next chunk.

## Control flow and usage model

There is no local control flow. These macros are data consumed by generated register-table initializers and block-specific helper code.

A typical use flow is:

1. Include `dcn_3_6_0_offset.h` for addresses and this header for field encodings.
2. Build ASIC-specific register, mask, and shift tables with macros such as `SR`, `SF`, `FD_MASK`, and `FD_SHIFT`.
3. Use DC register helpers such as `REG_SET`, `REG_UPDATE`, and `REG_GET` so callers can update named fields while preserving unrelated bits.

At runtime, higher-level DC code programs OTG timing and update locks during modeset; IRQ code uses interrupt status/clear masks; DP encoder/link code programs DP0 stream, PHY, secondary-packet, MST/MSO, DSC, and ALPM fields; hotplug code consumes HPD status/control fields; diagnostics and validation paths read CRC, perfmon, symbol-count, and timing-status registers.

## State and persistence behavior

The header has no mutable state. The state described by the masks lives in display hardware registers and persists according to GPU/display IP lifecycle: boot initialization, modeset, stream enable/disable, link training, runtime power management, suspend/resume, and GPU/display reset.

Important stateful areas include:

- OTG3 timing totals, blanking/sync, v-total min/max/mid, DRR windows, master update locks, and vupdate keepout fields. These must match active mode timing and be sequenced around double-buffer/master-update locks.
- Interrupt status/clear/ack fields for vstartup/vupdate/vready/vsync/vertical lines, DRR timing, HPD, DP video, secondary packets, perfmon, static screen, and ALPM wakeup. Some fields are write-one-to-clear or ack-oriented and should not be treated as ordinary persistent controls.
- CRC and snapshot state. CRC windows and selection controls are programmed by software, while CRC data/readback fields are hardware-produced diagnostics tied to frame timing.
- GSL/master-update state spans multiple timing generators; source selection and global-lock fields affect cross-pipe synchronization and can stall updates if mismatched.
- ODM memory power controls and OPTC/DIG/OTG/DP clock gates affect hardware block availability and power. Forced-on or disabled states can outlive a single modeset until reset or explicit reprogramming.
- HPD filter timers and enable/ack bits track connector presence and AUX/HPD RX interrupt flow, with repeated per-instance state for HPD0-4.
- DP0 secondary-packet, GSP, MST/MSO SAT, ALPM, and DPHY training/status fields are live protocol state. Pending/active/deadline/status bits reflect hardware progress and may change asynchronously while the link is running.
- DC perfmon counter configuration, state, interrupts, and high/low readbacks are shared diagnostic state that must be selected/read consistently.

## Dependencies and integration points

- Requires `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h` for matching register offsets. The shift/mask and offset headers are generated as a pair and must remain synchronized.
- Depends on the AMDGPU Display Core register-access infrastructure. The field names must match table initializers exactly; compile-time macros catch missing names, but they do not validate hardware semantics.
- Integrates with DCN 3.6 timing generator/OPTC code for OTG3 programming, global sync lock, double-buffering, CRC capture, static-screen detection, and dynamic refresh behavior.
- Integrates with DC IRQ and hotplug handling for vblank/vupdate/vertical interrupts and HPD0-4 sense/RX interrupt control.
- Integrates with DP encoder/link code for DP0 link configuration, DPHY training, video stream setup, MSA/VBID programming, secondary data packets, metadata, MST/MSO slot allocation, DSC, ALPM, and symbol counters.
- Integrates with diagnostics and validation paths through OTG CRC/readback registers, DP DPHY CRC, stream/link symbol counters, perfmon counter 17, and timing/status readbacks.
- Shares many repeated layouts with adjacent DCN versions and adjacent hardware instances. The chunk is instance-specific for OTG3, DP0, HPD0-4, and DIG0; callers should use the version and instance tables rather than assuming another DCN or pipe instance is bit-identical.

## Risks and edge cases

- Offset/mask drift is the primary generated-header risk. A correct field mask paired with a stale offset can silently write the wrong register.
- This chunk has two boundary truncations: it begins after the first `OTG2_OTG_PIPE_UPDATE_STATUS` shift field and ends inside `DIG0_DIG_FE_CLK_CNTL`. Final per-file analysis should reconcile the previous and next chunks for complete register coverage.
- Packed control/status registers are dense. Full-register writes can clobber interrupt status, clear bits, pending bits, readback selectors, reserved fields, or adjacent controls; read-modify-write helpers are expected for most software-owned fields.
- Field width mistakes can corrupt timing or protocol state. Many values are 7-, 8-, 10-, 11-, 13-, 15-, or 16-bit subfields packed into one register, while some control/status bitmaps occupy high bits such as `0x80000000L`.
- Status/control confusion is easy in this range. Names ending in `STATUS`, `CURRENT`, `READBACK`, `PENDING`, `ACTIVE`, `OCCURRED`, and `DEADLINE_MISSED` often represent hardware-owned state or interrupt events, not stable software-owned configuration.
- Timing-generator hazards include programming totals, blanking, update-lock windows, DRR windows, or GSL fields outside the expected modeset/vblank sequence, which can cause visible glitches, stuck updates, or cross-pipe synchronization failures.
- DP protocol hazards include enabling secondary packets at the wrong line, leaving GSP sends pending, programming MST SAT/MSO slot masks inconsistently, changing DPHY training/scrambler/PRBS controls during active video, or entering ALPM sleep/wakeup with stale line/frame scheduling.
- HPD hazards include failing to acknowledge RX or connect/disconnect interrupts, using wrong polarity, or setting filter timers too aggressively, causing missed hotplug events or interrupt storms.
- Power/clock hazards include forcing ODM memories or clocks off while the block is active, leaving clocks forced on after debug, or soft-resetting DIG/OTG paths without coordinated stream teardown.

## Test signals

- Build coverage with DCN 3.6.0 enabled should compile all register tables that include `dcn_3_6_0_sh_mask.h` together with `dcn_3_6_0_offset.h`.
- Static consistency checks should compare generated `__SHIFT`/`_MASK` pairs for representative fields and verify repeated HPD0-4 layouts remain intentionally identical.
- Modeset and timing tests should exercise OTG3 with standard, interlaced, stereo/3D, DSC-start, DRR/VRR, and multi-display global-sync-lock scenarios.
- IRQ tests should validate vblank/vsync/vupdate/vstartup/vready/vertical-line interrupt enable, status, clear, and ack behavior, plus DRR timing interrupts.
- CRC diagnostics should program OTG3 CRC windows and read both 16-bit CRC data registers and CRC320-323 32-bit data paths.
- Hotplug tests should cover HPD0-4 connect/disconnect, HPD RX interrupts, polarity handling, fast-training delay settings, and debounce/toggle filter timing.
- DP link tests should cover DP0 SST, MST/MSO, DSC, MSA timing/colorimetry, DPHY training patterns, scrambler/PRBS/CRC diagnostics, secondary audio/metadata/GSP packets, and stream/link symbol counters.
- ALPM tests should validate normal and AUX-less ALPM sleep, standby, wakeup, FEC scheduling, wakeup interrupts, pending/status bits, and resume into active video.
- Power-management and suspend/resume tests should inspect OTG/OPTC/DIG/DP clock status, ODM memory power status, and persistent update-lock or pending-packet bits after runtime PM and GPU reset.
