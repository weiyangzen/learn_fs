# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 78467-80956

## Chunk Scope

This chunk is a generated AMD DCN 3.2 register field shift/mask header segment. It contains preprocessor constants only: no functions, structs, storage declarations, or executable control flow. The range covers 2,077 `#define` entries for C20 PHY `CR0` raw-lane always-on digital registers, spanning the tail of `RAWLANEAON0`, a broad `RAWLANEAON1` lane block, and the start of `RAWLANEAON2`.

The constants follow the AMD register-access convention used by DCN display code: each hardware field has a `...__FIELD__SHIFT` constant and a matching `...__FIELD_MASK` constant. Downstream code can pass these constants through helper macros such as `FD(reg__field)`, `FN(reg, field)`, `REG_SET*`, and `REG_UPDATE*` to compose MMIO reads/writes without hardcoding bit positions.

## Purpose

The purpose of this range is to describe bit layouts for C20 PHY lane calibration, adaptation, override, and status registers. It is part of the static hardware contract for the DCN 3.2 display/IP block, especially DisplayPort/PHY bring-up and tuning paths. The file does not decide policy itself; it lets other driver components address named bitfields safely.

Major hardware concerns represented here include:

- RX DCC and IQ calibration fields, including banked full-rate and half-rate values.
- RX adaptation results for ATT, VGA, CTLE, DFE taps, DFE offsets, IQ, reference error, and adaptation-complete status.
- RX adaptation-control registers that tune calibration thresholds, step sizes, muxing, tap behavior, watchdog/error modes, wait counts, figure-of-merit behavior, and CDR behavior.
- RX/TX override and input/output control fields for lane disable, termination, signal-detect, VREF, and PMA override signals.
- TX firmware state, SRAM recovery, CCA timing, startup/continuous algorithm controls, DCC calibration, MPLLA/MPLLB DCC banks, and TX disable fields.
- RX startup, continuous, and fast-path algorithm controls for later lanes.

## Important APIs, Types, and Macros

There are no C APIs or types in this chunk. The important exported symbols are macro families:

- `C20_PHY_CR0_RAWLANEAON0_DIG_RX_*`: tail of lane AON0 RX calibration/adaptation/control/status fields. The first line in scope continues `DIG_RX_IQ_CAL_BANK_3`, followed by calibration-done, bank select, DCC code, IQ calibration, adaptation-bank, DFE offset, RX/TX threshold, adaptation-control, CDR, override, and RX input/output field masks.
- `C20_PHY_CR0_RAWLANEAON1_DIG_TX_*`: lane AON1 TX firmware, SRAM recovery, CCA, startup/continuous algorithm, high-power protection, transceiver mode, power-up, override, PLL DCC bank, calibration-done, DCC code, bank-select, and TX input fields.
- `C20_PHY_CR0_RAWLANEAON1_DIG_RX_*`: lane AON1 RX startup calibration controls, analog offset/calibration fields, DCC and IQ bank fields, adaptation result fields, adaptation controls, CDR, signal-detect, PMA override, and RX input/output fields.
- `C20_PHY_CR0_RAWLANEAON2_DIG_TX_*`: beginning of lane AON2 TX block, analogous to the AON1 TX fields.
- `C20_PHY_CR0_RAWLANEAON2_DIG_RX_*`: beginning of lane AON2 RX control block, ending in this chunk at `C20_PHY_CR0_RAWLANEAON2_DIG_RX_AFE_RTRIM__AFE_RTRIM__SHIFT`.

The constants are named after the hardware register and field. For example, `C20_PHY_CR0_RAWLANEAON2_DIG_RX_STARTUP_CAL_ALGO_CTL_0__SKIP_RX_DFE_CAL_STARTUP_MASK` identifies the bit used to skip RX DFE calibration during startup for AON2. The companion `__SHIFT` macro gives the field's least-significant bit position.

## Control Flow

This chunk has no direct control flow. Runtime behavior is created by code that includes this header and calls register helper macros. Typical use is:

1. Select a register and field name in a DCN component.
2. The helper macro expands the field name into this header's shift and mask constants.
3. The register framework masks, shifts, and writes or reads the hardware MMIO register.
4. Hardware state machines for PHY calibration/adaptation respond to the bitfield values.

The closest implicit control-flow surfaces are the algorithm-control and skip-bit registers. These fields can enable or bypass hardware-managed startup calibration, continuous calibration, continuous adaptation, VCO wait/calibration shortcuts, margining, FOM generation, DCC calibrations, and bank reload behavior. The header only names the bits; sequencing, polling, and error handling live in other driver code or firmware.

## State and Persistence Behavior

The macros are compile-time constants and do not hold process state. The state they describe resides in GPU hardware registers and can be volatile, sticky, or reset-dependent according to the ASIC specification.

State categories visible in this chunk:

- Banked calibration state: many RX/TX DCC, IQ, MPLLA, and MPLLB values are split across banks 0-3, with bank-select and per-bank done flags. Driver or firmware code must select/read/write the intended bank consistently.
- Adaptation state: ATT, VGA, CTLE, DFE tap, IQ, reference-error, and adaptation-done fields expose learned PHY tuning results for banks 0 and 1.
- Override state: RX/TX override fields can force lane disable, termination, signal-detect, VREF, PMA, high-power-protection, and transceiver-mode behavior; incorrect writes may persist until reset or an explicit override clear.
- Status state: calibration-done, adapt-done, init-powerup-done, signal-detect output, and fast flag fields expose hardware progress or shortcuts.

The chunk does not indicate which registers are read-only, write-only, sticky, or reset-cleared. That must be inferred from the register address header, ASIC programming guide, or caller behavior.

## Dependencies and Integration Points

Primary dependencies are external to this chunk:

- The sibling address header for DCN 3.2 provides register offsets; this file provides field shifts and masks.
- AMD display/DCN code includes `dcn/dcn_3_2_0_sh_mask.h` from components such as DMUB support, IRQ service, DCN32 resource setup, DCN32 clock manager, GPIO factory/translation, and GMC setup.
- Register helper layers in AMD display code use `FD`, `FN`, `REG_SET*`, `REG_UPDATE*`, and similar macros to consume `reg__field` shift/mask definitions.
- A similar field set appears in `include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h`, suggesting duplicated/generated register metadata across related IP header families.

This chunk specifically integrates with PHY lane bring-up and debug/tuning paths. It is likely consumed indirectly through generated register table structs or macro expansions rather than by direct references to every symbol.

## Risks and Edge Cases

- Generated-header drift: any mismatch between these masks/shifts and the hardware register specification can cause silent MMIO corruption. The compiler will not catch semantically wrong bit positions.
- Reserved-bit writes: most registers include `RESERVED_*` masks. Callers must preserve reserved bits during updates unless the hardware spec explicitly permits writes.
- Bank selection errors: calibration/adaptation values are banked. Reading a done flag from one bank while using values from another can report false readiness or apply stale tuning.
- Full-rate/half-rate ambiguity: many fields pack half-rate in low bits and full-rate in high bits. Callers must use the correct field and shift for the active link rate.
- Cross-lane copy/paste hazards: AON0, AON1, and AON2 blocks are structurally similar. Using the wrong lane prefix will target the wrong lane register if the address side also matches the wrong lane.
- Override hazards: RX/TX disable, signal-detect, termination, PMA, and high-power-protection override bits can force electrical behavior that breaks link training or power sequencing.
- Truncated chunk boundary: this range begins in the middle of `RAWLANEAON0_DIG_RX_IQ_CAL_BANK_3` and ends at the first field of `RAWLANEAON2_DIG_RX_AFE_RTRIM`; surrounding chunks are required for complete per-file synthesis.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware-integration checks:

- The AMDGPU/display driver should build with this header included by DCN32 modules; missing or renamed macros should fail compilation where field helpers expand them.
- Register access unit tests or static checks can verify that every used field has both `__SHIFT` and `_MASK` constants.
- Hardware smoke tests should cover link bring-up, DP/PHY training, hotplug, suspend/resume, and mode set paths on DCN 3.2 hardware.
- Debugfs/register-dump comparisons can confirm that calibration-done/adaptation-done/status fields decode as expected.
- ASIC register-generation tests should compare these constants against the authoritative register database, especially for reserved masks and banked calibration fields.

## Cross-Chunk Notes

This chunk is one piece of a very large generated header. A final per-file research document should merge it with adjacent chunks to identify complete register families, address-to-mask pairing, include guards, whole-file generation patterns, and all consumer modules. The findings here should be treated as the local interpretation of lines 78467-80956 only.
