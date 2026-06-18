# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 66757-69113

## Chunk Scope

This chunk covers 2,357 lines of generated AMD DPCS 4.2.2 register bitfield metadata from `DPCSSYS_CR3_LANE1_DIG_ASIC_TX_OVRD_OUT` through the beginning of `DPCSSYS_CR3_LANE2_DIG_ASIC_TX_ASIC_IN_1`. It contains 216 register comment blocks and 2,141 `#define` entries, almost entirely paired `__SHIFT` and `_MASK` constants. The chunk is part of the `dpcssys_dpcssys_cr3_dispdec` register address block and describes DisplayPort/PHY control and status fields for CR3 lane 1 plus the opening lane 2 digital ASIC fields.

## Purpose

The header provides compile-time field layout constants for AMD display code that needs to read, write, or compose DPCS register values. The companion `dpcs_4_2_2_offset.h` file supplies `ix...` register addresses, while this file supplies the field shift and mask constants for those registers. In this range, the constants model:

- Lane 1 digital ASIC override inputs and outputs for TX/RX request, data enable, rate, width, reset, low-power detect, inversion, equalization, CDR, alignment, loopback, async data, and clock-shift handshakes.
- Lane 1 TX and RX power-control states, power-up timings, DCC calibration bank/DAC controls, clock alignment, and LBERT test controls.
- Lane 1 RX VCO calibration, CDR, DPLL bounds, adaptation-control configuration/status, DFE tap status, slicer/VDAC offsets, statistic/match counters, MPHY low-speed controls, and analog override/status surfaces.
- Lane 1 analog TX/RX direct control registers for measurement buses, DCC, termination, clocks, miscellaneous TX/RX tuning, signal detect, scope, ATB measurement, and reserved analog fields.
- The start of lane 2 digital ASIC override and live input/output fields, mirroring the lane 1 digital ASIC pattern for a second physical lane.

## Important APIs, Types, and Macros

There are no C functions, structs, enums, or runtime APIs in this chunk. The public interface is the macro namespace itself:

- `DPCSSYS_CR3_LANE1_*__<FIELD>__SHIFT` defines the bit position for a field in a 16-bit DPCS register payload.
- `DPCSSYS_CR3_LANE1_*__<FIELD>_MASK` defines the field mask already shifted into register position.
- `DPCSSYS_CR3_LANE2_*__<FIELD>__SHIFT` and `_MASK` start the same scheme for CR3 lane 2.
- Register comments such as `//DPCSSYS_CR3_LANE1_DIG_RX_ADPTCTL_ADPT_CFG_0` delimit a set of field macros belonging to a single hardware register.

The dominant field families are:

- Override enable pairs, for example `REQ` with `REQ_OVRD_EN`, `PSTATE` with `PSTATE_OVRD_EN`, and many analog `*_OVRD_EN` fields. These indicate that writing code must usually set both a desired value field and its override-enable bit to force hardware behavior.
- Power-state fields under `DIG_TX_PWRCTL_TX_PSTATE_P0/P0S/P1/P2` and `DIG_RX_PWRCTL_RX_PSTATE_P0/P0S/P1/P2`, which define per-state analog/digital enable, reset, calibration, and data-enable bits.
- Timing fields under `TX_PWRUP_TIME_*` and `RX_PWRUP_TIME_*`, where masks span small counters plus fast/skip control bits.
- Calibration/status fields such as `RX_VCOCAL_RX_VCO_STAT_*`, `RX_ADPTCTL_*_STATUS`, `RX_STAT_STAT_CNT_*`, and `ANA_STATUS_*`, which are likely read paths rather than write-only configuration.

## Control Flow

This chunk has no executable control flow. Its practical control flow is preprocessor substitution into AMD display register helper macros. The include site for this exact header is `drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`, which includes both `dpcs/dpcs_4_2_2_offset.h` and `dpcs/dpcs_4_2_2_sh_mask.h`. Downstream display code typically combines an `ix...` register offset with `FD(register__field)`-style descriptors and `REG_SET`, `REG_UPDATE`, or related helpers; those helpers rely on the generated `__SHIFT` and `_MASK` tokens to isolate and place bitfield values.

Because the header is data-only, sequencing is enforced by the callers and hardware programming model rather than by this file. For example, a TX override sequence may need to write request, rate, width, data-enable, and override-enable fields in a hardware-defined order; this chunk only supplies the numeric bit locations needed by that sequence.

## State and Persistence Behavior

The macros are immutable compile-time constants and do not allocate memory or persist state. The state they describe exists in memory-mapped DPCS hardware registers. Important state categories visible in this range include:

- Control state: TX/RX request, reset, data enable, power state, rate, width, MPLL selection, low-power, inversion, CDR/SSC/alignment, termination, adaptation, and analog enable bits.
- Calibration state: TX DCC DAC selection/ack/address/data, RX VCO calibration controls and stats, RX adaptation controls, DFE tap status, CTLE/VGA/ATT status, and signal-detect calibration fields.
- Diagnostic state: LBERT control/error, RX statistic sample and counter registers, match-pattern controls, OCLA enables, scope data, analog status, ATB measurement routing, and reserved/NC fields.

Persistence across boot, suspend, reset, and link training depends on hardware register retention and the AMD display driver code that programs these registers. This header does not define reset values, polling loops, or save/restore policy.

## Dependencies and Integration Points

- Include guard `_dpcs_4_2_2_SH_MASK_HEADER` makes the header safe for repeated inclusion.
- The header is licensed MIT and marked AMD-generated/owned in the file prologue.
- `dpcs_4_2_2_offset.h` is the required companion for address constants; this chunk's lane 1 offsets around `0x1120` to `0x11ff` and lane 2 offsets beginning at `0x1200` match the register names in this chunk.
- `dcn315_resource.c` includes this exact DPCS 4.2.2 offset/mask pair, establishing the ASIC integration target.
- Nearby generated headers for other DPCS/DCN versions contain the same or similar register names with version-specific masks and literal formatting, so code must include the correct ASIC version header rather than mixing variants.

## Risks and Edge Cases

- Bit layout correctness is hardware-critical. A wrong mask or shift can silently program the wrong PHY bit, potentially breaking link training, power sequencing, calibration, or display bring-up.
- Many fields are only 16-bit wide within `0x0000FFFFL` masks even though they are represented as C long literals. Callers must not assume a 32-bit register field unless the companion register definition says so.
- Override fields are easy to misuse: setting a value field without its corresponding override-enable bit may have no effect, while leaving an override enabled can force stale PHY behavior.
- Reserved and `NC` masks are exposed like normal fields. Driver writes should preserve reserved bits unless hardware documentation explicitly requires a value.
- Lane names are embedded in macro names. Accidentally using lane 1 fields with lane 2 offsets, or vice versa, can compile if helper macros are manually assembled but would encode the wrong field layout if lanes ever diverge.
- This chunk starts in the middle of the broader file and ends during lane 2 register definitions. Whole-file research must reconcile adjacent chunks to avoid treating lane 2 coverage as complete here.

## Test Signals

Useful validation signals for this chunk are mostly build-time and hardware-regression oriented:

- Compile `dcn315_resource.c` and any DC register helper users with this header included; missing or renamed macros should fail at compile time.
- Compare every register block in this chunk against the matching `ixDPCSSYS_CR3_*` names in `dpcs_4_2_2_offset.h`; the offset names should exist for each register comment block.
- Run static checks for duplicate field names within a register, masks that do not match their declared shift/width, masks outside 16 bits, and overlapping non-reserved fields.
- Exercise AMD display link training, hotplug, suspend/resume, and multi-lane DisplayPort paths on DCN 3.1.5-class hardware that uses `dpcs_4_2_2`.
- Hardware tests around TX/RX power-state transitions, RX adaptation, CDR/VCO calibration, LBERT, and lane 2 bring-up are especially relevant because those are the main control surfaces described in this chunk.

## Cross-Chunk Notes

This chunk is a continuation of the larger generated DPCS mask header. It likely follows earlier CR3 lane 0 and lane 1 definitions and is followed by the remainder of lane 2 and later lanes/blocks. The merge lane should combine this report with adjacent chunks to produce a single source-tree-aligned research document for `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h`.
