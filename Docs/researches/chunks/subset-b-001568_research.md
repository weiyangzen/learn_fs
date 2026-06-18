# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_8_0_d.h lines 1-3028

## Scope And Purpose

This chunk is the first half of the generated AMD DCE 8.0 register-address header. It contains copyright/license text, the `DCE_8_0_D_H` include guard, and preprocessor constants mapping symbolic register names to MMIO register offsets for the DCE 8 display engine. There are no functions, structs, enums, inline helpers, or storage definitions in this range.

The purpose is to give AMDGPU and Display Core code stable names for DCE 8.0 display hardware registers. The constants are consumed together with `dce_8_0_sh_mask.h`, which defines field shifts and masks for the same register names. This source tree is a Ceph-client mirror that includes Linux GPU driver code; this file is not Ceph filesystem logic.

The assigned range covers display pipe power gating, ABM/backlight, the six CRTC timing-generator instances, legacy DAC, display performance counters, display clock generator and PLL controls, DMIF/MCIF/DCI memory-interface controls, DCIO/GPIO/UNIPHY/output PHY controls, most of the replicated DCP plane/color/cursor/LUT/regamma register block for six display pipes, and the beginning of the replicated DIG/HDMI/AFMT encoder block through `DIG4_AFMT_ISRC2_0`. The file continues after this chunk with the rest of AFMT/DIG and later display blocks, so this report should be merged with later chunk reports before drawing whole-file conclusions.

## Important APIs, Types, And Macro Families

There are no callable APIs or C types. The exported interface is the macro namespace. Register-address macros use the generated forms `mmREGISTER`, `mmINSTANCE_REGISTER`, and a few indexed/debug forms such as `ixDMIF_DEBUG02_CORE0` or `ixDCIO_DEBUG1`. The `mm` constants are register offsets; the companion shift/mask header provides bitfield layout.

The opening lines define per-pipe power-gating registers for pipes 0 through 5: `mmPIPE*_PG_CONFIG`, `mmPIPE*_PG_ENABLE`, and `mmPIPE*_PG_STATUS`, followed by global display power-gating/request/status/debug registers such as `mmDC_IP_REQUEST_CNTL`, `mmDC_PGFSM_CONFIG_REG`, `mmDC_PGFSM_WRITE_REG`, `mmDC_PGCNTL_STATUS_REG`, `mmDCPG_TEST_DEBUG_INDEX`, and `mmDCPG_TEST_DEBUG_DATA`.

The ABM/backlight group includes `mmBL1_PWM_*` user, target, current, final, minimum, control, sample-rate, and lock registers, plus `mmDC_ABM1_*` ambient/backlight management controls, ACE slopes and thresholds, histogram and luma statistics, sample rates, histogram-bin shift configuration, histogram results 1 through 24, overscan pixel value, master lock, and ABM debug-index/data registers.

The CRTC section defines one unqualified alias plus explicit `CRTC0` through `CRTC5` addresses for timing-generator registers. It covers DCFE clock/debug/light-sleep controls, horizontal and vertical totals, blanking, sync A/B controls, variable vertical total limits/control, timing interrupt status, trigger controls, force-count/flow control, stereo/interlace state, CRTC enable/blank/status/counters, snapshot registers, update locks, double-buffering, VGA capture, test pattern registers, master update lock/mode, MVP in-band/status controls, vertical update status, overscan/blank/black colors, vertical interrupt 0/1/2 position and control, CRTC CRC windows and data, external timing-sync windows and interrupts, static-screen control, 3D structure, GSL vsync/window/control, and CRTC test-debug index/data.

The analog and performance sections define legacy DAC control, CRC, autodetect, comparator, power, DFT, and FIFO-status registers, then `PERFCOUNTER_*` and `PERFMON_*` addresses replicated across `DC_PERFMON0` through `DC_PERFMON9`. These perfmon macros include counter control/state, perfmon control, current-value interrupt status/misc, low/high readback, and debug index/data.

The clocking section includes VGA PPLL aliases, global DCCG controls for DP reference clock, scan-in soft reset, GTC and DS DTO programming, DMCU/SMU interrupt/control, DAC/DVO/SYMCLK/DVOACLK clock enables, clock-gating controls, time-base divisors, DISPCLK frequency-change/light-sleep/perfmon controls, per-CRTC pixel-rate and DP DTO phase/modulo registers, DCFE/DCI/DCCG/DIG/UNIPHY/DCO resets, audio DTO source/phase/module registers, DCCG debug/test registers, four replicated display PLL register sets, and `mmDENTIST_DISPCLK_CNTL`.

The DMIF/MCIF/DCI section defines display memory-interface configuration/status/arbitration/debug registers, pipe-specific arbitration and max-request controls, MCIF write-combine/buffer-manager/buffer-address/status controls, pipe DMIF buffer controls, memory power and clock controls, XDMA interface controls, RBBMIF read/write controls, and low-power tiling support.

The DCIO/GPIO/PHY section defines generic display IO, reference clock, DCO memory/power/clock, impedance calibration for UNIPHY/AUX links, panel power sequencing and backlight PWM, genlock/swaplock pads, GPU timer start/read controls, GPIO mask/A/enable/Y groups for generic, DVODATA, DDC1 through DDC6, DDCVGA, SYNCA, GENLK, HPD, PWRSEQ, I2C pad, and I2S/SPDIF pins, pad strength/skew/vref controls, UNIPHY test-pattern generators, indexed DCIO debug registers, DAC macro reserved registers, and seven replicated UNIPHY control/address blocks for TX control, power, PLL, spread spectrum, synchronization, test output, BIST, link, and channel crossbar.

The DCP plane and color section begins at `mmGRPH_ENABLE` and is replicated across `DCP0` through `DCP5`. It covers primary graphics plane enable/control, LUT bypass, swap, primary/secondary surface addresses and high-address registers, pitch, offsets, start/end coordinates, input gamma, update and flip control, address-in-use readback, DFQ control/status, graphics interrupts, compressed surface address/pitch, overlay enable/control/swap/address/pitch/position/update/DFQ, overlay scaler edge control, graphics and overlay prescale values, input and output CSC matrices, common matrix A/B transforms, denorm/round/clamp controls, key range controls, degamma, gamut remap matrices, spatial dithering/random seeds, converted-field status, cursor 1 and cursor 2 address/size/position/hotspot/color/update controls, cursor request filtering and stereo controls, DC LUT read/write/index/data/autofill/control/offset controls, DCP CRC control/mask/current/last registers, DCP debug, flip-rate/GSL/LB-gap controls, stereo flip controls, hardware rotation, XDMA cache-underflow detection and status, regamma LUT and piecewise region controls for CNTLA/CNTLB, alpha control, and XDMA recovery surface addresses.

The chunk ends in the beginning of the DIG/HDMI/AFMT encoder register block. It defines `DIG0` through `DIG6` variants for DIG front-end control, output CRC, clock/test/random pattern, FIFO status, display-clock switch control/status, HDMI control/status, audio and ACR packet controls, VBI and infoframe controls, generic packet control, AFMT interrupt status, HDMI general control, AFMT audio packet control 2, and ISRC1 packet words through `AFMT_ISRC2_0` for DIG instances 0 through 4.

## Control Flow And Data Flow

This header has no runtime control flow. Data flow is compile-time macro substitution: C source includes `dce_8_0_d.h`, combines an address macro with masks from `dce_8_0_sh_mask.h`, and reads or writes the hardware register through AMDGPU/MMIO helpers.

DCE 8 display code uses these constants in two common patterns. First, code selects a pipe or engine by computing an instance offset from replicated macros, for example `mmDCPn_GRPH_CONTROL - mmDCP0_GRPH_CONTROL`, and then adds that offset to a base register such as `mmGRPH_PRIMARY_SURFACE_ADDRESS` or `mmCRTC_H_TOTAL`. Second, DC helper macros pass the register name and field descriptors into generic register update helpers that perform masked MMIO writes.

The local tree shows direct integration from `amdgpu/dce_v8_0.c`, `amdgpu/cik.c`, `amdgpu/gmc_v7_0.c`, `amdgpu/gfx_v7_0.c`, powerplay `ci_baco.c` and `ci_smumgr.c`, `display/dc/dce80/dce80_timing_generator.c`, `display/dc/hwss/dce80/dce80_hwseq.c`, `display/dc/irq/dce80/irq_service_dce80.c`, `display/dc/gpio/dce80/*`, `display/dc/resource/dce80/dce80_resource.c`, and `display/dc/clk_mgr/dce100/dce_clk_mgr.c`. Later-generation files also use overlapping `mmGRPH_*` and `mmCRTC_*` names with different headers, so include selection is ASIC-generation-sensitive.

## State And Persistence Behavior

The file itself stores no mutable state and performs no I/O. The mutable state represented by these constants resides in DCE 8.0 display hardware registers. Once a caller writes the corresponding MMIO register, the hardware state can persist until another modeset, page flip, cursor update, LUT/color update, interrupt acknowledgement, power-gating event, clock change, suspend/resume restore, GPU reset, or display block reset rewrites it.

Important state classes in this chunk include per-pipe power-gating state, ABM/backlight PWM and histogram/luma readback state, CRTC timing/blanking/sync/counter/interrupt/CRC/test-pattern state, clock generator and PLL programming, display memory-interface watermarks/arbitration/buffer addresses, GPIO/DDC/HPD/panel-power pins, PHY/link/UNIPHY programming, primary and overlay plane scanout addresses and formats, compression/XDMA recovery state, cursor surfaces and positions, color-space conversion matrices, degamma/gamut/regamma/LUT state, CRC diagnostic state, and HDMI/AFMT packet/control state.

Several represented registers are explicitly synchronization-sensitive. Examples include `*_UPDATE`, `*_UPDATE_LOCK`, `MASTER_UPDATE_LOCK`, `MASTER_UPDATE_MODE`, `CRTC_DOUBLE_BUFFER_CONTROL`, flip controls, surface-address-in-use readbacks, cursor update controls, PLL update controls, power-gating enable/status, clock-switch status, and vertical/timing interrupt controls. The macros do not enforce ordering or waiting; callers must follow the hardware programming sequence.

## Dependencies And Integration Points

This chunk depends on the rest of the same header for a complete include-guarded register map and on `dce_8_0_sh_mask.h` for bitfield definitions. It is used with AMDGPU register access helpers such as `RREG32`, `WREG32`, DC register-update macros, IRQ service tables, power-management register programming, and display resource construction.

Integration surfaces include DRM/KMS modeset programming, CRTC timing generation, vblank/vupdate/range timing interrupt handling, page flips and surface address programming, cursor programming, color management, LUT/regamma programming, scaler/overlay paths that use DCP plane state, display clock and PLL programming, display memory fetch/DMIF/MCIF configuration, display power gating and BACO/SMU transitions, GPIO/DDC/HPD/panel-power handling, encoder/HDMI/AFMT packet programming, CRC/test-pattern diagnostics, and GPU memory-controller diagnostics involving display clients.

The replicated instance layout is itself an integration contract. For example, `DCP0` through `DCP5`, `CRTC0` through `CRTC5`, `DIG0` through `DIG6`, `DC_PERFMON0` through `DC_PERFMON9`, `DCCG_PLL0` through `DCCG_PLL3`, and `DCIO_UNIPHY0` through `DCIO_UNIPHY6` have regular but not universally identical address spacing. Code that computes offsets relies on these constants being exact.

## Risks And Edge Cases

The main risk is silent hardware misprogramming if a generated address drifts from the authoritative ASIC register database. These are integer constants; the compiler will not detect a register value that points at the wrong block, wrong pipe instance, or wrong clear/status register.

Unqualified aliases such as `mmCRTC_H_TOTAL`, `mmGRPH_CONTROL`, `mmDIG_FE_CNTL`, and `mmPERFMON_CNTL` usually map to instance 0. Callers must add the correct pipe or engine offset or use the explicit instance macro. Mixing an unqualified base with the wrong offset family can program another pipe or an unrelated display block.

The chunk contains multiple similar replicated domains with different instance counts and spacing: six CRTCs/DCPs, seven DIG/UNIPHY instances, ten perfmons, four PLLs, and several one-off global registers. A generic loop that assumes all display instances share the same count or stride would be fragile.

Timing, clock, PLL, power-gating, DMIF/MCIF, and PHY registers are high-impact. Wrong values can blank displays, destabilize vblank accounting, break HDMI audio/infoframes, trigger underflow, wedge display clock changes, cause hotplug/DDC failure, leave blocks powered down, or make suspend/resume restore unreliable.

Address-split registers require paired programming. Primary/secondary surface addresses, overlay addresses, cursor addresses, compressed surface addresses, MCIF buffer addresses, and XDMA recovery addresses have low/high halves or related pitch/status registers. Programming only one half or using the wrong alignment can point display fetches at the wrong memory.

This chunk ends mid-DIG/AFMT block at `DIG4_AFMT_ISRC2_0`; later chunk reports must cover the remainder of the encoder/audio packet register set. The final merged report should not treat the DIG/AFMT section here as complete.

## Test Signals

There are no unit tests for this header chunk alone. The first validation signal is build coverage for DCE 8.0 AMDGPU/DC configurations that include both `dce_8_0_d.h` and `dce_8_0_sh_mask.h`, especially `amdgpu/dce_v8_0.c`, DCE80 timing generator, IRQ service, hardware sequencing, GPIO factory/translator, resource construction, powerplay BACO/SMU, GMC, and GFX code.

Generated-header integrity should be checked against the authoritative DCE 8.0 register database or a known-good upstream header. The comparison should focus on repeated instance address families, chunk boundaries, unqualified aliases, clock/PLL/PHY registers, power-gating registers, and address pairs for scanout/cursor/overlay/compression/XDMA surfaces.

Runtime test signals include successful modesets on all available DCE 8 pipes, stable vblank/vupdate interrupts, correct page flips, cursor movement and cursor stereo behavior, correct primary and overlay scanout, no display underflow or XDMA cache-underflow events, correct LUT/degamma/gamut/regamma/color-key behavior, stable display clock and PLL transitions, successful suspend/resume and BACO transitions, working DDC/HPD/panel power/backlight controls, and correct HDMI audio/infoframe/AFMT packet behavior.

Diagnostic validation should exercise CRTC CRC and test patterns, DCP CRC, DIG output CRC, performance counter readback, ABM histogram/luma readback, DMIF/MCIF buffer status, CRTC snapshot/counter registers, interrupt clear/mask/status paths, and UNIPHY/debug-index paths. These signals catch wrong address selection and instance-offset mistakes that compile-time checks cannot see.
