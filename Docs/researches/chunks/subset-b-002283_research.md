# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h lines 1-2473

## Scope

This chunk is the opening slice of AMDGPU's generated DPCS 4.2.0 register-offset header. It contains preprocessor constants only: no callable functions, structs, enums, storage objects, or local executable control flow. The exported contract is a set of `reg*` MMIO register offsets, paired `reg*_BASE_IDX` constants, and `ix*` indirect control-register indices for DPCS/RDPCS/UNIPHY display PHY programming.

The covered range starts with the license and include guard, then defines direct display register blocks for DPCSSYS CR address/data windows, two panel power sequencers, five RDPCSTX instances, DCIO global/chip GPIO blocks, and UNIPHY1-4 reserved macro-control offsets. It then begins the `dpcssys_cr0_rdpcstxcrind` indirect register space and continues through CR0 supervisor/common registers, lane 0-3 PHY/PCS register indices, raw common indices, raw lane 0-3 indices, and the first nine raw always-on lane 0 indices. The CR0 indirect block continues after line 2473 in the next chunk.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMD display hardware metadata. It has no Ceph, filesystem, distributed-storage, network, or persistent-disk behavior.

## Purpose

The purpose of this header range is to bind logical DPCS 4.2.0 display PHY register names to ASIC-specific numeric offsets. Runtime display code can include this header, usually with the companion shift/mask header and register helper macros, to program DisplayPort/HDMI PHY, link, AUX/DDC, GPIO, panel power, clock, PLL, lane training, calibration, and diagnostic registers without hard-coding raw addresses in C code.

The direct `reg*` blocks in this chunk cover:

- `DPCSSYS_CR0` through `DPCSSYS_CR4` address/data apertures at direct offsets `0x2934/0x2935`, `0x2a0c/0x2a0d`, `0x2ae4/0x2ae5`, `0x2bbc/0x2bbd`, and `0x2c94/0x2c95`.
- `PWRSEQ0` and `PWRSEQ1` panel power-sequencer and backlight/PWM registers, including GPIO enable/control/mask/Y, panel power control/state/delays/reference dividers, PWM control/period/lock, and spare registers.
- `RDPCSTX0` through `RDPCSTX4`, each with control, clock, interrupt, PLL update, CR address/data, SRAM control, scratch/spare, debug, PHY control 0-17, PHY fuse 0-3, RX load value, DP-alt-mode/DMCU controls, and PLL override offsets.
- Global DCIO control: generic registers, DCIO and reference clock control, UNIPHY A-E link and channel crossbar control, write-command delay, pin straps, intercept state, backlight PWM frame-start display select, genlock/swaplock pads, and soft reset.
- DCIO chip GPIO/AUX/DDC controls: generic GPIO, DDC1-5, DDCVGA, genlock, HPD, power-sequencer GPIO enables, pad strength, PHY AUX control, TX/RX/pull-up enables, AUX control 0-5, and AUX/I2C pad power-good.
- UNIPHY1-4 reserved macro-control ranges, each exposing `UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED57` at instance-strided direct offsets.

The `ixDPCSSYS_CR0_*` block maps the indirect CR register indices reached through the CR0 address/data window. In this chunk it covers supervisor digital/analog MPLL and RTUNE controls, lane 0-3 ASIC override/status and TX/RX power/calibration/equalization registers, raw common registers, raw lane PCS/FSM/IRQ/PMA/TX/RX controls, and the start of raw always-on lane calibration/adaptation state.

## Important APIs, Types, And Macros

There are no C APIs or concrete types in this chunk. The important interface is the generated macro namespace:

- `reg...` constants are direct register offsets used by AMD display register-access helpers.
- `reg..._BASE_IDX` constants select the register aperture/base index. Every direct register in this chunk uses base index `2`.
- `ixDPCSSYS_CR0_...` constants are indirect register indices, not direct MMIO offsets. They are selected through a CR address register such as `regDPCSSYS_CR0_DPCSSYS_CR_ADDR` or `regRDPCSTX0_RDPCS_TX_CR_ADDR` and read/written through the matching data register.

The most important direct register families are the repeated RDPCSTX instances. Each instance has the same shape and an instance stride in direct address space: control and clock registers, interrupt control for DP-alt-mode and FIFO conditions, PLL update data/address override registers, SRAM control, scratch/debug, PHY controls 0-17, fuse registers used for lane tuning data, and DP-alt-mode/DMCU handoff controls. These offsets are the top-level access points for RDPCS transmitter setup and status.

The DPCSSYS CR address/data aliases are notable. For example, the CR0 address/data definitions are numerically identical to `regRDPCSTX0_RDPCS_TX_CR_ADDR` and `regRDPCSTX0_RDPCS_TX_CR_DATA`; CR1-CR4 similarly line up with RDPCSTX1-4. Consumers must treat these as access-window aliases over the same hardware offsets rather than independent storage.

The power-sequencer registers are the panel and backlight control surface in this chunk. `PANEL_PWRSEQ_CNTL`, `PANEL_PWRSEQ_STATE`, `PANEL_PWRSEQ_DELAY1`, `PANEL_PWRSEQ_DELAY2`, `PANEL_PWRSEQ_REF_DIV1/2`, `BL_PWM_CNTL`, `BL_PWM_CNTL2`, `BL_PWM_PERIOD_CNTL`, and `BL_PWM_GRP1_REG_LOCK` define the offsets used by panel enable/disable and backlight PWM programming.

The DCIO and GPIO registers are the connector-side integration surface. `UNIPHY*_LINK_CNTL` and `UNIPHY*_CHANNEL_XBAR_CNTL` bind logical links to physical channel routing. `DC_GPIO_DDC*`, `DC_GPIO_HPD_*`, `PHY_AUX_CNTL`, `DC_GPIO_AUX_CTRL_*`, `DC_GPIO_RXEN`, `DC_GPIO_PULLUPEN`, and `AUXI2C_PAD_ALL_PWR_OK` are the offset metadata for AUX, DDC, HPD, and pad-power programming.

The CR0 indirect index map is grouped by address ranges. Supervisor indices start at `0x0000` and include ID code, reference clock overrides, MPLLA/MPLLB override, spread-spectrum, ASIC input/output, analog bandgap, prescaler, RTUNE, MPLL power/timer/calibration, and status registers. Lane indices use `0x1000`, `0x1100`, `0x1200`, and `0x1300` regions. Raw common indices start at `0x2000`. Raw lane indices use `0x3000`, `0x3100`, `0x3200`, and `0x3300`. Raw always-on lane 0 begins at `0x4000` and is cut off by this chunk.

## Control Flow

This header has no executable control flow. Runtime behavior is created by code that includes generated offset and shift/mask headers, expands register tables, and issues MMIO or indirect CR reads and writes through AMDGPU display helpers.

A typical use path is:

1. Display resource or PHY code selects the DPCS 4.2.0 register set for the ASIC.
2. Register-list macros paste logical names onto generated constants such as `regRDPCSTX0_RDPCSTX_PHY_CNTL0`, `regDC_GPIO_HPD_A`, or `ixDPCSSYS_CR0_LANE1_DIG_RX_CDR_STAT`.
3. Direct offsets are passed to normal register helpers for MMIO reads/writes; field layout comes from the matching shift/mask header rather than this offset file.
4. Indirect CR accesses first write an `ixDPCSSYS_CR0_*` index through the selected CR address register, then access the corresponding CR data register.
5. Higher-level link, PHY, AUX/DDC, HPD, panel-power, backlight, DP-alt-mode, or diagnostics code decides sequencing, delays, polling, and error handling.

The file therefore encodes address identity, not policy. It does not describe when clocks must be enabled, when a PLL is stable, how long panel power delays must run, or how DP link training should react to status.

## State And Persistence Behavior

The file itself stores no runtime state and persists nothing. It describes hardware state whose lifetime is controlled by display initialization, modesets, hotplug events, link training, AUX/DDC transactions, panel power transitions, runtime power management, suspend/resume, and GPU reset.

State represented by this chunk includes:

- RDPCS transmitter enable/reset, clock, FIFO, SRAM, interrupt, debug, scratch, PLL update, DP-alt-mode, and PHY control state.
- PHY tuning and calibration state, including MPLLA/MPLLB override and spread-spectrum values, RTUNE, TX equalization, termination, DCC DAC, RX CDR/VCO/adaptation, lane status, and raw FSM/IRQ/PMA/PCS state.
- Connector routing and pad state: UNIPHY link/channel crossbars, AUX/DDC GPIO state, HPD GPIO state, genlock/swaplock pads, pull-ups, RX/TX enables, and AUX/I2C pad power-good.
- Panel and backlight state: power-sequencer GPIO state, panel control/state/delay/reference-divider registers, PWM control/period, group lock, and spare state.
- Diagnostic/readback state such as ID code, ASIC input/output mirrors, analog status, load values, lane counters/status, FIFO status, and IRQ status/clear indices.

Bad register values can remain active until the affected block is reprogrammed, reset, power-cycled, or the GPU is reset. Some state is reconstructed by normal modeset or resume paths, but this generated header has no save/restore logic.

## Dependencies And Integration Points

The direct companion is the DPCS 4.2.0 shift/mask header in the same generated register family, which defines bit positions and masks for these offsets. This header supplies addresses and indices; the companion supplies field geometry.

Important integration points visible in the tree include:

- AMD display register helper and resource construction patterns that consume generated `reg*`, `*_BASE_IDX`, `*_SHIFT`, and `*_MASK` constants to build typed register tables.
- AMD ASIC enum headers such as `soc24_enum.h`, which define symbolic values for RDPCSTX controls including clock enables, soft resets, FIFO state, DP-alt-mode interrupt conditions, PHY reference ranges, DP TX rate/width/pstate, and PHY control enumerations.
- Atom firmware data structures that map board or VBIOS tuning values such as TX equalization main/pre/post and vboost level to RDPCSTX PHY fuse/control registers.
- DCIO/AUX/DDC/HPD code paths that depend on `DC_GPIO_*`, `PHY_AUX_CNTL`, and `DC_GPIO_AUX_CTRL_*` offsets to drive connector detection and sideband communication.
- Panel power and backlight code paths that depend on the `PWRSEQ*` and `BL_PWM*` offsets when sequencing embedded panels.
- PHY/link programming code that must distinguish direct RDPCSTX offsets from indirect CR indices and pair each instance with the correct CR address/data window.

The namespace is generation-specific. Similar DPCS/RDPCS/UNIPHY names appear in other AMD register headers, but offsets, instance counts, reserved ranges, and indirect index maps are not interchangeable across ASIC versions.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. Offset constants compile cleanly even when wrong, but a bad address can read or write a different register, route the wrong link, leave clocks or resets in an unexpected state, or make status polling look valid while observing the wrong hardware.

Direct-versus-indirect confusion is a high-risk edge case. `reg*` constants are direct offsets with base indices, while `ixDPCSSYS_CR0_*` values are CR-space indices. Passing an `ix*` constant to a direct MMIO helper, or writing a `reg*` offset through a CR index path, would target the wrong address space.

Instance aliasing is also important. The DPCSSYS CR address/data registers overlap the RDPCSTX CR address/data names for each instance. That is useful for macro compatibility, but consumers must not assume duplicated definitions represent separate hardware registers.

Lane asymmetry is visible in this slice. Lanes 1 and 2 include expanded RX power, VCO calibration, CDR, adaptation, analog RX, MPHY RX, and AON-related state, while lanes 0 and 3 in this region expose a smaller TX/status-oriented set. Code that blindly assumes identical lane register availability can reference missing macros or program unsupported lane controls.

Panel power and backlight registers are user-visible and timing-sensitive. Incorrect offsets or mismatched fields can produce blank panels, incorrect backlight PWM, unsafe panel sequencing, stuck panel-power state, or lock bits that prevent later brightness changes.

AUX/DDC/HPD offsets are connector-critical. Errors can break EDID reads, hotplug detection, AUX transactions, or pad power sequencing, which may present as missing displays rather than obvious register failures.

PHY/PLL/lane-training offsets are link-stability-sensitive. Bad MPLL, spread-spectrum, RTUNE, TX equalization, RX CDR/adaptation, power-state, or IRQ indices can cause intermittent link training failures, high error rates, blanking, or failures isolated to particular link rates, lane counts, cables, connectors, or DP-alt-mode paths.

Chunk-boundary risk is real. The document covers only lines 1-2473. It stops inside the CR0 raw always-on lane 0 register list at `ixDPCSSYS_CR0_RAWAONLANE0_DIG_DFE_ODD_REF_LVL`; the rest of CR0 and all later CR1-CR4 indirect spaces are outside this chunk and must be merged before drawing complete-file conclusions.

## Test Signals

Useful validation is mostly generated-header, build, and hardware-behavior oriented:

- Compile coverage for all AMDGPU display code that includes DPCS 4.2.0 generated offset and shift/mask headers.
- Generated-register consistency checks that every direct `reg*` used by resource tables exists, has the expected `_BASE_IDX`, and has matching fields in the companion shift/mask header.
- Indirect-access tests that verify CR address/data windows select expected `ixDPCSSYS_CR0_*` indices and that direct MMIO helpers are not used for indirect indices.
- Cross-generation and register-database diffs against AMD's authoritative DPCS 4.2.0 source to catch offset drift, missing reserved entries, incorrect instance strides, or accidental reuse from a neighboring ASIC.
- Panel tests for power-on/off, suspend/resume, backlight PWM enable/period/duty programming, lock/unlock behavior, and eDP panel timing.
- Connector tests for HPD, DDC/EDID, AUX transactions, pad power-good, pull-up/RX/TX enable state, UNIPHY link routing, and channel crossbar programming.
- Link/PHY tests across DisplayPort and HDMI rates, lane counts, training patterns, DP-alt-mode transitions, hotplug, runtime PM, and GPU reset.
- Diagnostics tests for RDPCSTX interrupt status/clear behavior, FIFO error paths, scratch/debug access, PHY fuse readback, PLL update override paths, and lane/raw FSM status.

Regression symptoms from bad constants include missing displays, failed EDID/AUX/HPD, black or flickering panels, incorrect backlight, stuck panel power state, DP link training failures, HDMI/DP rate-specific instability, DP-alt-mode failures, broken suspend/resume restore, misleading PHY diagnostics, or failures isolated to DPCS 4.2.0 ASICs.

## Cross-Chunk Notes

This is not a standalone source module. It is a generated register-layout slice inside `dpcs_4_2_0_offset.h`. The following chunk owns the rest of `DPCSSYS_CR0_RAWAONLANE0` and later CR0 indices, and later chunks own CR1-CR4 indirect spaces plus tail special cases. The merge/reconciliation lane should treat this document as the direct DPCSSYS/PWRSEQ/RDPCSTX/DCIO/UNIPHY opening plus the beginning of the CR0 indirect register map.
