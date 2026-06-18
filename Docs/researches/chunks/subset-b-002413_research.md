# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 65643-68055

## Purpose

This chunk is generated AMD DPCS 4.2.3 register bitfield metadata. It contains no executable C logic; it publishes preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for DPCS CR3 PHY lane registers. Consumers combine these field macros with matching register offsets from `dpcs_4_2_3_offset.h` and the display-core register helper macros to read, update, or poll individual hardware fields.

The selected range covers the end of CR3 lane 2 receive override output metadata, the rest of CR3 lane 2 digital and analog PHY field definitions, and the beginning of CR3 lane 3 digital PHY field definitions through `DPCSSYS_CR3_LANE3_DIG_ANA_TX_OVRD_OUT`. Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata, not distributed filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or callbacks in this range. The exposed interface is the generated macro namespace:

- `DPCSSYS_CR3_<...>__<FIELD>__SHIFT`: bit offset for a field inside a DPCS indirect register.
- `DPCSSYS_CR3_<...>__<FIELD>_MASK`: mask for the same field, suitable for AMD register helpers that compose shifted values.
- Companion offset macros live in `dpcs_4_2_3_offset.h` as `ixDPCSSYS_CR3_<...>` constants. For this chunk, lane 2 offsets span roughly `0x120f` through `0x12ff`, and lane 3 offsets visible in the chunk span `0x1300` through `0x13a0`.

Major field families in this slice:

- Lane 2 ASIC interface and override fields: lane loopback, TX/RX reset, invert, data enable, request/ack, low-power detect, pstate, rate, width, MPLL selection, RX adaptation status, async data, weak-keep output, TX/RX override enables, and OCLA observability.
- Lane 2 TX power/control fields: TX pstate `P0`, `P0S`, `P1`, and `P2` configuration, TX power-up timing registers, DCC CR bank address/data, DCC DAC control/range/select/ack/address, TX clock alignment, and TX LBERT pattern/error injection control.
- Lane 2 RX power/control fields: RX pstate `P0`, `P0S`, `P1`, and `P2` configuration, RX power-up timing, VCO calibration controls/timing/status, RX alignment mask, RX LBERT control/error reporting, CDR control/status, DPLL frequency/bounds, and receive adaptation control/status for ATT/VGA/CTLE/DFE taps and slicers.
- Lane 2 RX statistic and monitor fields: pattern match controls, sample count load/start/stop, data masks, statistic source and clock selection, per-counter enable bits, counter outputs, pause/valid-loss controls, and calibration comparator clock controls.
- Lane 2 MPHY and analog override fields: MPHY PWM/termination controls, analog TX clocks/data/refgen/reset/serial/rate/termination/equalization/DCC DAC overrides, analog RX control/power/VCO/calibration/DAC/AFE/scope/slicer/phase/sense controls, signal-change enables, status registers, signal-detect overrides, and raw analog TX/RX measurement or reserved registers.
- Lane 3 digital fields: the chunk begins lane 3 with ASIC lane/TX override inputs and outputs, RX override/status output, TX ASIC inputs/outputs, TX power pstate and DCC controls, TX clock alignment/LBERT control, RX statistic match/stat/counter controls, and the first analog TX override output register.

Most masks in the requested range describe 16-bit DPCS control-register fields. Reserved-field masks are present and must be treated as documentation of bit layout, not as permission for driver code to write arbitrary reserved values.

## Control Flow

This header has no runtime control flow. Runtime sequencing is imposed by the AMD display driver:

1. DCN316 resource setup includes both `dpcs/dpcs_4_2_3_offset.h` and `dpcs/dpcs_4_2_3_sh_mask.h`.
2. Register-list and field-list macros in display-resource, link-encoder, PHY, or diagnostics code token-paste symbolic register and field names into `ixDPCSSYS_CR3_...` offsets and `DPCSSYS_CR3_...__...` shifts/masks.
3. Register helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, and polling helpers perform the actual MMIO or indirect-register operation through the DCN/DPCS access path.
4. Hardware sequencing around those operations, such as enabling clocks, asserting/deasserting resets, selecting rates, waiting for ACK/status bits, running VCO calibration, training links, and collecting statistics, is implemented by the consuming display code and firmware contracts rather than by this header.

The chunk itself does not encode ordering, delays, retries, locking, or error handling. Field names such as `ACK`, `REQ`, `RESET`, `*_START`, `*_DONE`, `*_CLR`, and `*_OVRD_EN` are signals that consumers need sequencing discipline.

## State And Persistence Behavior

The file stores no software state and persists nothing to disk. It describes hardware state in DPCS CR3 lane registers.

The represented state includes transient handshake bits, persistent PHY configuration bits, calibration settings, power-state profiles, counter enable and counter value fields, loopback/test controls, analog override settings, and status indicators. Persistence is determined by the GPU hardware: configuration registers may retain values until a modeset, link reconfiguration, power-gate event, suspend/resume cycle, or ASIC reset; status and counter fields may be read-only, sticky, self-clearing, write-one-to-clear, or latch-on-read depending on the underlying register definition. This generated mask header does not identify those access classes, so consumers must use the programming sequence associated with each PHY block.

## Dependencies And Integration Points

This chunk depends on the generated DPCS 4.2.3 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h`, which provides the `ixDPCSSYS_CR3_*` register indices for these masks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which includes the DPCS 4.2.3 offset and mask headers for DCN316 hardware.
- AMD display-core register helper layers that combine offsets, shifts, and masks into register-table entries and field updates.

Important integration surfaces are PHY/link bring-up, DisplayPort/USB-C lane mapping, link training, low-power transitions, diagnostics, compliance testing, and debug tools. The lane 2 and lane 3 repetition is deliberate: CR3 exposes per-lane controls, and instance-specific register indices from the offset header choose which physical lane is targeted.

## Risks And Edge Cases

- Header/offset mismatch is the main correctness risk. A mask from `dpcs_4_2_3_sh_mask.h` must be paired with the matching `dpcs_4_2_3_offset.h`; mixing versions can compile while programming the wrong field.
- These constants are untyped macros. A typo in a field macro, an incorrect shift, or a copy/paste error between lane 2 and lane 3 can silently break only one physical lane or link width.
- Override-enable fields are hazardous. Setting `*_OVRD_EN` without the intended data field can force analog or digital PHY state and cause link training failure, blank display, high error counts, unstable low-power transitions, or incorrect loopback/test behavior.
- Handshake and calibration fields are sequencing-sensitive. `REQ`/`ACK`, VCO calibration start/status, DCC DAC ack, statistic start/done/stop, and valid-loss clear fields require consumer-side polling and timeout handling.
- Reserved masks appear throughout the range. Driver updates must preserve reserved bits unless the hardware programming guide explicitly says otherwise.
- The chunk boundary is artificial. It begins after the comment for `DPCSSYS_CR3_LANE2_DIG_ASIC_RX_OVRD_OUT_0` and ends inside the broader lane 3 analog TX section; adjacent chunks are required for complete per-file analysis.

## Test Signals

Useful validation is mostly integration or hardware-facing rather than unit-level:

- Build coverage for DCN316/AMDGPU display code that includes `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h`.
- Static checks that every field macro used by consuming code has a matching register offset in `dpcs_4_2_3_offset.h` and that generated shifts/masks do not overlap unexpectedly within a register.
- Display bring-up tests across lane counts and rates, especially configurations using CR3 lane 2 and lane 3.
- Link training, hotplug, suspend/resume, power-gating, and low-power idle tests that exercise reset, pstate, request/ack, RX/TX power-up timing, CDR/DPLL, and VCO calibration fields.
- PHY diagnostics and compliance tests: LBERT pattern/error tests, RX statistic counters, DCC DAC acknowledgement, analog override debug reads, and error-counter stability under known-good links.
- Regression signals include blank displays, intermittent DP link retraining, high bit-error or statistic counters, bad RX adaptation status, failed VCO/DCC calibration, AUX/link-training timeouts, or failures limited to one connector/lane mapping.
