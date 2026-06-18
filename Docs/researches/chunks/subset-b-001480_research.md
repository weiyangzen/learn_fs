# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_4_1_sh_mask.h

Chunk: `subset-b-001480`
Covered source range: lines 4516-8504 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_4_1_sh_mask.h`

## Purpose

This chunk is the middle section of AMD's generated BIF 4.1 register field mask header. It is not executable driver logic; it supplies preprocessor constants that identify bit masks and shift positions for fields inside BIF/PCIe physical bus interface registers.

The covered range is centered on the physical bus interface, or PB, register space:

- the tail of `PB0_RX_LANE*_CTRL_REG0` and `PB0_RX_LANE*_SCI_STAT_OVRD_REG0` definitions for RX lanes 5-15;
- all covered `PB0_TX_*` global and per-lane transmitter fields, including TX global control, lane skew, coefficient accept tables, global overrides, and TX lanes 0-15;
- a large `PB1_*` block covering global controls, SCI status overrides, straps, DFT/jitter injection, PLL controls/status overrides, RX global/lane controls, and TX global/per-lane fields;
- the beginning of the `PB0_PIF_*` block, including PIF scratch/debug/program timing controls, lane pairing, power-down controls, sequence controls, programmed delay fields, and the first part of per-lane PDNB override definitions.

The chunk begins in the middle of `PB0_RX_LANE5_CTRL_REG0`: the matching `PB0_RX_LANE5_CTRL_REG0__RX_BACKUP_5_MASK` is in the previous chunk, while this range starts at its shift constant. The chunk also ends in the middle of `PB0_PIF_PDNB_OVERRIDE_3`: later constants for lane 3 and lanes 4-15 are in the next chunk. The final file-level report must reconcile these boundaries.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or runtime APIs in this range. The interface is entirely macro constants.

The generated naming contract is:

- `<REGISTER>__<FIELD>_MASK` gives the 32-bit mask for a field;
- `<REGISTER>__<FIELD>__SHIFT` gives the right-shift count used to encode or decode that field;
- register prefixes match address macros in `bif_4_1_d.h`, such as `ixPB0_TX_GLB_CTRL_REG0`, `ixPB1_RX_LANE15_SCI_STAT_OVRD_REG0`, and `ixPB0_PIF_CNTL2`.

Important macro families in this range include:

- `PB0_RX_LANE5..15_CTRL_REG0`: per-lane RX backup/debug/test and power-sense override fields, including `RX_DBG_ANALOG_SEL_*`, `RX_TST_BSCAN_EN_*`, and `RX_CFG_OVR_PWRSF_*`.
- `PB0_RX_LANE5..15_SCI_STAT_OVRD_REG0`: per-lane RX SCI status override fields for RX power, electrical-idle detection enable, preset hint, figure-of-merit request/enable, and response mode.
- `PB0_TX_GLB_CTRL_REG0`: global transmitter delay, reset value, stagger, clock-gating, preset table bypass, coefficient rounding, LSx clock, and TX frontend power behavior.
- `PB0_TX_GLB_LANE_SKEW_CTRL`: lane-group enable fields for x1, x2, x4, x8, and x16 grouping. These fields describe how lanes are grouped for TX skew management across the physical link width.
- `PB0_TX_GLB_SCI_STAT_OVRD_REG0`: global TX SCI update ignore and status override controls across lane groups.
- `PB0_TX_GLB_COEFF_ACCEPT_TABLE_REG0..3`: coefficient acceptance tables for per-lane TX equalization/preset behavior. These are dense packed fields, with table slots encoded as repeated multi-bit fields.
- `PB0_TX_GLB_OVRD_REG0..4`: global TX override controls for driver data, transmit detect, reset, power, data enable, disable/valid signaling, coefficient command values, and post-cursor/pre-cursor coefficient fields.
- `PB0_TX_LANE0..15_CTRL_REG0`, `PB0_TX_LANE0..15_OVRD_REG0`, and `PB0_TX_LANE0..15_SCI_STAT_OVRD_REG0`: per-lane TX backup, debug, override, power, reset, enable, coefficient, de-emphasis, margin, and deemphasis-related fields.
- `PB1_GLB_CTRL_REG0..5`, `PB1_GLB_SCI_STAT_OVRD_REG0..4`, and `PB1_GLB_OVRD_REG0..2`: matching global control and override fields for physical bus interface instance 1.
- `PB1_STRAP_*`: strap-derived global, TX, RX, PLL, and pin configuration fields, including lane reversal, debug muxing, spread-spectrum, common-mode, and PLL mode settings.
- `PB1_DFT_*`: design-for-test and jitter injection control/status fields.
- `PB1_PLL_RO*` and `PB1_PLL_LC*`: ring-oscillator and LC PLL control, override, and SCI status fields, including PLL power, frequency mode, divider, bypass, lock, calibration, and test controls.
- `PB1_RX_GLB_*` and `PB1_RX_LANE0..15_*`: RX global and per-lane control/status/override fields for data enable, equalization, termination, electrical idle, offset calibration, power states, preset hints, and response modes.
- `PB1_TX_GLB_*` and `PB1_TX_LANE0..15_*`: the instance-1 counterpart to the PB0 TX global/per-lane transmitter fields.
- `PB0_PIF_*`: PIF scratch/debug fields, programmable timing values, lane-pairing controls, power-down policy for lanes 0-3, TX PHY status bits, sequence-control phase/lane-resume bits, serial per-lane disable bits, and early PDNB/RXEN/TXPWR/RXPWR override fields.

## Control Flow

The chunk has no runtime control flow. It is a sequence of `#define` constants inside the include guard established at the top of the header.

Runtime control flow appears in consumers that include this header and use the masks with AMDGPU register access helpers. Typical usage is:

1. read a 32-bit register through direct MMIO or indexed PCIE access, for example `RREG32_PCIE(ixPB0_PIF_PWRDOWN_0)`;
2. clear a field with the generated `_MASK`;
3. encode a new value by shifting with the generated `__SHIFT`;
4. write the register back with `WREG32_PCIE`, `WREG32`, or command-table read/modify/write helpers;
5. optionally poll a status bit or field until hardware reports the expected state.

Concrete tree integration includes `amdgpu/cik.c`, which manipulates PIF power-down fields around PCIe link behavior. For example, it reads `ixPB0_PIF_PWRDOWN_0` and `ixPB0_PIF_PWRDOWN_1`, clears `PB0_PIF_PWRDOWN_*__PLL_POWER_STATE_IN_OFF_*_MASK` and `PB0_PIF_PWRDOWN_*__PLL_POWER_STATE_IN_TXS2_*_MASK`, then writes values shifted by the matching `__SHIFT` constants. Other CIK files include this header for BIF 4.1 register definitions used during interrupt setup, GMC setup, SDMA setup, graphics setup, BACO power management, and SMU/PowerPlay initialization.

The TX/RX/PLL/PIF constants in this chunk are meant for low-level link bring-up and service flows: lane power sequencing, L0s/L1/L2 behavior, speed changes, PLL ramp timing, electrical idle handling, link-width grouping, coefficient updates, and per-lane override/debug paths. The macros do not enforce sequencing; callers must follow ASIC programming requirements.

## State And Persistence Behavior

The header itself is stateless and persistent only as compiled constants. It does not allocate memory, keep state, perform I/O, or persist data.

The fields described by these constants map to persistent hardware register state in the GPU's BIF/PCIe block. Writes made through these masks can remain active until changed by driver code, firmware, link retraining, hot reset, function reset, BACO transition, suspend/resume, or full ASIC reset.

State categories represented in this range include:

- per-lane RX and TX power/enable/reset/status override state;
- PLL power, lock, divider, and calibration state;
- PIF sequence, lane pairing, lane disable, power-down, and programmable delay state;
- strap-derived configuration state copied from hardware straps or firmware-visible settings;
- debug/test state, including analog debug selection, boundary scan, DFT jitter injection, and override controls;
- scratch/debug fields such as `PB0_PIF_SCRATCH`, which can be used for diagnostics or firmware/driver coordination depending on platform conventions outside this header.

Incorrect writes to these fields can leave the PCIe link in a degraded or unusable state until reset. Because the macros are just constants, they do not record ownership, restore original values, or distinguish safe status fields from disruptive override fields.

## Dependencies And Integration Points

The direct dependency is the C preprocessor. The practical dependency is the matching BIF 4.1 address header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_4_1_d.h`

That address header defines the corresponding `ixPB0_*`, `ixPB1_*`, and `mm*` register addresses. In the covered range, examples include `ixPB0_TX_GLB_CTRL_REG0` at `0x1208000`, `ixPB1_TX_GLB_CTRL_REG0` at `0x2208000`, `ixPB0_PIF_CNTL2` at `0x1100014`, and `ixPB0_PIF_PDNB_OVERRIDE_*` addresses starting at `0x1100020`.

Known consumers in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cik.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cik_sdma.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cik_ih.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v7_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v7_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/ci_baco.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/ci_smumgr.c`

The main integration pattern is inclusion alongside other generated ASIC register headers and use through AMDGPU helper macros such as `RREG32`, `WREG32`, `RREG32_PCIE`, `WREG32_PCIE`, `REG_GET_FIELD`, and `REG_SET_FIELD`. PowerPlay BACO tables use the same generated mask/shift style for read/modify/write and wait-for command entries, although the specific BACO fields are outside this chunk.

This header is generation-specific. Same-named PB/PIF/PLL/RX/TX fields exist in adjacent BIF generations, but masks, semantic details, and addresses can differ. Consumers must include the BIF 4.1 header only for ASICs using the BIF 4.1 register layout.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. The compiler cannot verify that a `PB0` mask is used with a `PB0` address, that a `PB1` mask is used with `PB1`, or that a field value fits in the mask before shifting.

Mask/shift pairs must remain synchronized. A stale mask with a new shift, or a field copied from another generation, can update the wrong bits while producing valid C. This is especially risky for packed lane group fields, TX coefficient tables, PLL power/frequency fields, PIF programmable delays, and per-lane power overrides.

The chunk boundaries split two field families. Line 4516 starts with a `__SHIFT` whose matching `_MASK` is in chunk `subset-b-001479`. Line 8504 ends before most of `PB0_PIF_PDNB_OVERRIDE_3` and all later PDNB override lanes, which are expected in chunk `subset-b-001481`. Any automated validation at chunk granularity must tolerate these incomplete pairs at the boundaries while the final file-level merge should validate the full header.

Many constants are replicated across 16 lanes and across PB0/PB1 instances. Off-by-one lane selection, lexicographic confusion around lanes 10-15, or mixing PB0 and PB1 prefixes can pass review and builds but target the wrong physical lane.

Several fields are disruptive: PIF lane disable, sequence control, PLL power overrides, TX/RX power-state overrides, TX/RX enable/reset overrides, boundary scan/test enables, and DFT/jitter injection. Driver changes using these fields should be reviewed as hardware sequencing changes, not as ordinary bit cleanup.

Some fields describe status or strap-derived values while nearby fields are override enables or override values. Updating status-like macros is safe only as constants, but runtime writes to similarly named registers may not be safe. Callers need register-spec knowledge to distinguish read-only status from writable override paths.

The constants are untyped. Callers should use unsigned 32-bit arithmetic for field assembly and avoid relying on signed promotion, especially for high-bit masks such as lane 15 resume or PLL override values near bit 31.

## Test Signals

Useful validation signals include:

- build coverage for CIK-era AMDGPU and PowerPlay translation units that include `bif_4_1_sh_mask.h`;
- generated-header consistency checks that every `_MASK` has a matching `__SHIFT` across the complete file, with known chunk-boundary exceptions resolved after merge;
- duplicate-definition checks that no macro name is redefined with a different value;
- consistency checks against `bif_4_1_d.h`, verifying that register prefixes in field macros have matching address macros;
- static review of PB0/PB1 use sites to ensure instance prefixes match the addressed register;
- PCIe link tests on supported CIK hardware, including boot, link training, Gen2/Gen3 speed changes, link-width negotiation, ASPM/L0s/L1 transitions, suspend/resume, hot reset, and driver reset;
- BACO and low-power transition tests, because this header is included by CIK BACO/PowerPlay code and adjacent BIF fields can affect resume and link recovery;
- controlled readback tests for representative PIF power-down fields, PIF programmed delay fields, TX global control fields, and RX/TX lane status fields after known-safe writes;
- hardware-lab validation for per-lane TX coefficient/equalization and RX electrical-idle/preset-hint fields, because lane-indexed values can compile cleanly while degrading signal integrity;
- negative testing around invalid or out-of-range field values in call sites, ensuring callers mask and shift values rather than ORing raw constants into registers.
