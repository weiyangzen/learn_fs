# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 1-2378

## Purpose

This chunk is generated AMD DPCS 4.2.2 register-field metadata. It contains no executable C logic; it defines C preprocessor constants that map hardware register fields to bit positions and masks for the AMDGPU display DPCS/DPCSSYS block. Runtime display code combines these constants with the matching offset/header data to build MMIO register reads and writes for DisplayPort/HDMI PHY control, DPCS transmitter setup, panel power sequencing, backlight PWM, debug, interrupt, and DP Alt Mode access control.

The range begins at the file header, SPDX/license, and include guard, then covers 2,169 `#define` entries: 1,089 `__SHIFT` definitions and 1,079 `_MASK` definitions. The chunk has 168 register-comment groups across 11 address blocks. It covers CR address/data windows `CR0` through `CR4`, two panel power-sequencer/PWM instances `PWRSEQ0` and `PWRSEQ1`, complete generated field layouts for `RDPCSTX0`, `RDPCSTX1`, and `RDPCSTX2`, and the start of `RDPCSTX3` through the first `RDPCSTX3_RDPCSTX_CLOCK_CNTL` mask. The final register is intentionally partial because line 2378 is a chunk boundary; the following chunk is required for the rest of `RDPCSTX3` and later DPCS instances.

Although this repository subtree is named `distributed-fs/ceph-client`, this file is AMDGPU display hardware metadata, not Ceph or filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or direct MMIO operations in this range. The public interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: the low bit position for a field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for that field in a 32-bit register value.

The main register families are:

- `DPCSSYS_CR0` through `DPCSSYS_CR4`: 16-bit CR address/data windows via `DPCSSYS_CR*_DPCSSYS_CR_ADDR` and `DPCSSYS_CR*_DPCSSYS_CR_DATA`.
- `PWRSEQ0` and `PWRSEQ1`: GPIO, panel power sequence, and backlight PWM fields. These include `DC_GPIO_VARY_BL`, `DC_GPIO_DIGON`, `DC_GPIO_BLON`, panel target state, sync/digon/blon override and polarity bits, power-up/down delays, reference dividers, PWM period/duty/fractional enablement, frame-start update controls, group lock/update-pending fields, and spare registers.
- `RDPCSTX0`, `RDPCSTX1`, and `RDPCSTX2`: complete mirrored transmitter register field sets for DPCS transmitter instances 0-2.
- `RDPCSTX3`: partial field coverage for transmitter instance 3, ending inside `RDPCSTX3_RDPCSTX_CLOCK_CNTL`.

The complete `RDPCSTX0`-`RDPCSTX2` field sets include control, clocking, interrupt, CR access, SRAM power, scratch/spare, debug, PHY control, PHY fuse/readback, DP Alt Mode, generic PHY bus, byte-order, and PLL update override registers. Representative fields include DPCS CBUS/SRAM/TX soft reset bits, lane bit-order and byte-order controls, lane FIFO enables, FIFO start/read delay, interrupt status/clear/mask bits for register FIFO overflow, DPALT toggles, and per-lane FIFO errors, plus `RDPCS_TX_PLL_UPDATE_REQ/PENDING` and PLL update data/address overrides.

The PHY fields cover resets, TCA/APB reset, HDMI mode enable, reference range, reference clock detection, SRAM init/load/bypass status, power-gating mode, PCS/PMA/analog power enables and stable status, DP4 power-on-reset, lane loopback controls, per-lane TX reset/disable/clock-ready/data-enable/request/ack handshakes, termination/inversion/equalization-bypass/high-protection bits, low-power/rate/width/detect-RX controls, lane P-state and MPLL enablement, DP Alt Mode disable/ack, reference clock request/enable, MPLLB fractional denominator/quotient/remainder, SSC peak/step/up-spread, multiplier/divider/clock-enable/calibration controls, PHY fuse equalization and PLL tuning fields, RX load values, DPALT reserved copies for DMCU, and PHY generic input/output bus selectors.

## Control Flow

This header has no runtime control flow. Its effect is compile-time token expansion:

1. ASIC-specific AMDGPU display code includes the DPCS 4.2.2 offset and shift/mask headers for the selected GPU generation.
2. Register access tables and helper macros token-paste register and field names into shift/mask descriptors.
3. Runtime driver paths use those descriptors with MMIO helpers to update or poll hardware fields.
4. Hardware state machines perform the actual sequencing for panel power, PWM updates, DPCS transmitter reset/clock/FIFO operation, PHY power and PLL control, DP Alt Mode ownership, and interrupt/debug/status capture.

The mirrored `RDPCSTX0`-`RDPCSTX2` macro sets show that software can often reuse instance-generic programming flows while binding to per-instance register prefixes. `RDPCSTX3` is only partially represented in this chunk, so complete control-flow conclusions for instance 3 require the next chunk.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It describes encodings for hardware-visible state:

- CR windows persist the selected 16-bit CR address/data values according to hardware behavior.
- Power sequencer fields encode panel enable/target state, visible state bits, power-up/down timing, GPIO input/output state, and PWM duty/period/update state.
- Transmitter control fields encode DPCS soft reset state, lane/FIFO enablement, lane packing and byte ordering, register-block enablement, DP Alt Mode block status, and PLL update request/pending status.
- Clock fields encode external reference, TX lane clocks, global TX clock, SRAM clock, and OCLA/debug clock gate/enable/on status.
- Interrupt fields encode observed errors/toggles, clear bits, and interrupt masks.
- SRAM and PHY fields encode memory power forcing/state, PHY power mode/stability, lane handshake status, PLL and spread-spectrum settings, fuse/readback values, loopback/test controls, and debug-bus selections.
- Scratch, spare, and generic bus fields expose hardware-defined full-width or packed diagnostic state.

Persistence, volatility, access direction, reset values, and side effects are hardware-defined and are not represented in this generated mask header. Some fields are likely read-only status, write-one-to-clear, self-clearing request bits, sticky error status, or only valid while clocks/power domains are enabled. Driver code must rely on the hardware programming guide and higher-level register definitions for those semantics.

## Dependencies And Integration Points

The direct dependency is the C preprocessor plus AMD's generated register-header convention. This file is intended to be paired with the corresponding DPCS 4.2.2 offset/base-index header in the same `asic_reg/dpcs` area, because masks without register addresses are not sufficient for MMIO programming.

Important integration points include:

- AMDGPU display register access helpers and generated register tables that combine `*_offset.h` register addresses with these `*_sh_mask.h` field constants.
- Display Core link encoder and transmitter programming paths that configure DPCS TX clocks, lane enables, FIFO start, lane packing, byte order, reset sequencing, and PHY link parameters.
- Embedded DisplayPort and panel/backlight paths that program `PWRSEQ0`/`PWRSEQ1` panel sequencing delays, GPIO signals, PWM period/duty, frame-start PWM updates, and backlight reference dividers.
- DP Alt Mode and DMCU/firmware coordination paths that use allow-driver-access, driver-access-blocked, DMCU DPALT disable-block, force-TX-clock-disable, and reserved PHY-control mirror fields.
- Interrupt and diagnostic paths that read or clear DPCS register FIFO overflow, DPALT toggle, per-lane TX FIFO errors, debug counter, OCLA source selection, scratch/spare, and PHY generic bus fields.
- PHY/PLL programming code that needs the MPLLB fractional, multiplier, divider, SSC, calibration, power, lane P-state, and fuse/readback encodings.

Because these constants are a silicon ABI, manual edits must stay synchronized with AMD's authoritative generated register database and with the matching offset header. A wrong mask or shift can compile cleanly while causing writes to the wrong hardware bits.

## Risks And Edge Cases

- The macros are untyped preprocessor constants. A wrong field width, shift, or mask will not be caught by the C type system and can corrupt adjacent hardware fields.
- The chunk boundary is not semantically aligned. `RDPCSTX3_RDPCSTX_CLOCK_CNTL` is incomplete here, and the 1,089 shift versus 1,079 mask count reflects boundary and generated-field asymmetry. Whole-instance analysis for `RDPCSTX3` requires the following chunk.
- Instance symmetry matters. `RDPCSTX0`, `RDPCSTX1`, and `RDPCSTX2` mirror many fields; a generated-name drift or copy/paste mistake can break only one physical transmitter and appear topology-dependent.
- Status, clear, and mask fields use similar names in interrupt registers. Confusing observed status bits, clear bits, and interrupt mask bits can leave faults latched, hide errors, or clear evidence before diagnostics read it.
- Power, reset, and clock fields are sequencing-sensitive. Programming PHY reset, SRAM bypass/load, PCS/PMA/analog power, TX clock gates, FIFO start, or PLL update request/pending bits out of order can cause blank displays, link-training failures, hangs waiting for stable bits, or intermittent resume failures.
- Panel power and PWM fields directly affect user-visible backlight and panel sequencing. Wrong delay/ref-divider/PWM masks can create flicker, no-backlight, panel power timing violations, or delayed updates tied to frame-start synchronization.
- DP Alt Mode ownership fields are coordination points between driver, DMCU/firmware, and hardware. Incorrect access-block handling can race firmware or program PHY registers while driver access is blocked.
- Full-width scratch/spare/debug fields such as `0xFFFFFFFFL` should not be treated as general policy storage unless the hardware guide explicitly permits it.
- The CR address/data windows are only 16 bits in this range; code must not assume the surrounding 32-bit register word is fully payload.

## Test Signals

Useful validation is a mix of generated-header consistency and hardware behavior:

- Build AMDGPU display code that includes the DPCS 4.2.2 offset and shift/mask headers. Missing or renamed macros should surface in register-table construction and display link/encoder code.
- Mechanically compare lines 1-2378 against AMD's authoritative DPCS 4.2.2 register source, treating the final `RDPCSTX3_RDPCSTX_CLOCK_CNTL` register as a partial-boundary case.
- Check that normal fields have matching `__SHIFT` and `_MASK` macros, then reconcile expected imbalances with neighboring chunks before drawing whole-file conclusions.
- Diff mirrored `RDPCSTX0`, `RDPCSTX1`, and `RDPCSTX2` field layouts where the hardware database expects identical layouts.
- Exercise panel power and backlight flows: enable/disable panel, suspend/resume, brightness changes, PWM fractional mode, frame-start synchronized updates, and power-up/down delay handling.
- Exercise DisplayPort/HDMI link bring-up through transmitter instances 0-2, including lane-count changes, link retraining, hotplug, mode-set, clock gating, reset recovery, and DP Alt Mode ownership transitions.
- Validate interrupt/status handling by checking that FIFO errors, DPALT toggles, register FIFO overflow, clear bits, and mask bits behave as expected without stale or accidentally cleared status.
- Use debug/OCLA/generic bus and scratch/spare readback only under documented diagnostic flows, verifying that reads do not depend on disabled clocks or powered-down PHY domains.

## Cross-Chunk Notes

This is the first chunk for `dpcs_4_2_2_sh_mask.h`, so it includes the file guard and initial DPCSSYS/PWRSEQ/DPCS transmitter definitions. It fully covers `RDPCSTX0`, `RDPCSTX1`, and `RDPCSTX2` register-field groups but stops after the first mask in `RDPCSTX3_RDPCSTX_CLOCK_CNTL`. The next chunk is required to complete `RDPCSTX3` and continue the generated DPCS 4.2.2 field map before any final per-file report can make complete claims about all transmitter instances.
