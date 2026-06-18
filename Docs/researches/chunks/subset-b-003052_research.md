# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 116036-118752

## Scope

This chunk is a generated AMDGPU NBIO 6.1 shift/mask header segment. It contains 1,866 `#define` macros over 2,717 source lines, representing 852 register names. There are no C functions, structs, enums, global objects, executable statements, locks, allocations, or local algorithms in this range.

The range starts on a source-split boundary with only the final `RESERVED_15_8_MASK` line for `DWC_E12MP_PHY_X4_NS_X4_3_LANE3_ANA_TX_OVRD_CLK`, then covers the tail of lane 3 analog TX/RX PHY fields. The bulk of the chunk defines `DWC_E12MP_PHY_X4_NS_X4_3_RAWCMN_DIG_MEM_*` common digital memory register windows, from `CMN2_B0_R0` through `CMN5_B2_R3`. The final register is also split by the chunk boundary: this chunk contains `RAWCMN_DIG_MEM_CMN5_B2_R3__DATA__SHIFT`, while the matching `DATA_MASK` appears on the next source line outside the requested range.

## Purpose

`nbio_6_1_sh_mask.h` is the field-layout half of AMD's generated NBIO 6.1 register interface. For each hardware register field, it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the starting bit position.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate or update the field.

The companion generated headers provide register offsets and defaults; runtime AMDGPU code combines those offsets with these masks through register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, and SOC15/NBIO SMN/MMIO accessors.

This chunk describes low-level PCIe/PHY state rather than Ceph or distributed-filesystem behavior. The lane 3 analog portion names controls and observation points for transmitter bias/reference, receiver clock/data recovery, power gating, loopback, loss-of-signal, slicer/reference selection, calibration muxes, analog test bus measurement, DFE enablement, termination, and voltage/reference measurement. The raw common digital memory portion exposes uniform 16-bit `DATA` fields for PHY common micro/register memory banks, likely used for hardware bring-up tables, diagnostics, firmware-directed training state, or low-level PHY debug access.

## Important Macro Families

The analog lane tail includes:

- `LANE3_ANA_TX_OVRD_CLK` final reserved mask from the previous chunk, preserving the high byte of a TX override clock register.
- `LANE3_ANA_TX_MISC` fields for oscillator PMOS/NMOS controls, analog test-bus TX bias measurement, RX detect reference override, and reserved high byte.
- `LANE3_ANA_RX_ATB_IQSKEW`, `ANA_RX_ATB_REGREF`, `ANA_RX_ATB_MEAS1`, `ANA_RX_ATB_MEAS2`, and `ANA_RX_ATB_VREG`, which select and enable analog test-bus paths for IQ phase, RX scope, regulation/reference, VCO, CDR, ground, slicer, DFE bypass, and IQC voltage/reference measurements.
- `LANE3_ANA_RX_DCC_OVRD`, `ANA_RX_CDR_AFE`, and `ANA_RX_SLC_CTRL`, which describe data-rate selection, duty-cycle/AFE enable override, loopback clock override, phase detector control bits, and even/odd slicer control fields.
- `LANE3_ANA_RX_PWR_CTRL1`, `ANA_RX_PWR_CTRL2`, and `ANA_RX_MISC_OVRD`, which override or force ACJT, clock, LOS, AFE, DFE, deserializer, loopback, word clock, LFPS LOS, and short-detect enablement.
- `LANE3_ANA_RX_CAL_MUXA`, `ANA_RX_CAL_MUXB`, and `ANA_RX_TERM`, which select calibration muxes, DFE tap visibility, IQ phase override, and receiver termination controls.

The raw common memory section is highly regular. Registers named `DWC_E12MP_PHY_X4_NS_X4_3_RAWCMN_DIG_MEM_CMN<N>_B<B>_R<R>` generally expose one full-width `DATA` field:

- Complete banks covered here: `CMN2_B0` through `CMN2_B7`, `CMN3_B0` through `CMN3_B7`, `CMN4_B0` through `CMN4_B7`, `CMN5_B0`, and `CMN5_B1`. Each bank has `R0` through `R31`, and each register has `DATA__SHIFT 0x0` plus `DATA_MASK 0xFFFFL`.
- Partial bank covered here: `CMN5_B2_R0` through `CMN5_B2_R2` are complete, while `CMN5_B2_R3` is truncated after the `DATA__SHIFT` macro.

## APIs, Types, And Functions

This chunk has no callable API and no C type definitions. Its public surface is the preprocessor macro namespace. The constants are untyped integer literals, usually with an `L` suffix, and encode only bit position and mask width.

The macros do not encode access width, offset, reset value, read/write permission, write-one-to-clear behavior, polling requirements, firmware ownership, register side effects, or valid sequencing. Those semantics must come from the NBIO 6.1 hardware specification, the matching generated offset/default headers, and the AMDGPU call site using the field.

## Control Flow

There is no local control flow in this header. Runtime flow is external:

1. AMDGPU code selects a matching register offset from `nbio_6_1_offset.h`.
2. It reads or composes a register value through NBIO/SOC15 hardware access helpers.
3. It uses this header's `__SHIFT` and `_MASK` macros to extract fields, preserve unrelated bits, or insert updated field values.
4. The resulting hardware operation participates in PCIe PHY bring-up, link training, analog calibration, power-state transitions, diagnostics, firmware coordination, or reset handling.

For the lane 3 analog registers, external control flow must sequence overrides, clock enables, calibration mux selection, analog test-bus routing, termination, and loopback/data-enable controls around live PHY state. For the raw common memory registers, callers normally treat each register as an opaque 16-bit value and must know the memory-bank protocol separately from this header.

## State And Persistence Behavior

The header itself stores no state. It names state held in NBIO 6.1 PHY registers. Persistence depends on the GPU reset domain, PCIe/PHY reset, suspend/resume paths, firmware or SMU initialization, SR-IOV PF/VF ownership, and explicit driver writes.

Represented lane state includes analog TX bias/reference controls, RX duty-cycle and AFE enablement, CDR/phase-detector controls, receiver clocks, LOS/LFPS and short-detect state, DFE/deserializer/loopback enables, slicer and IQ phase controls, receiver termination, calibration mux selections, and analog test-bus measurement selectors. Some of these bits are not passive storage: override and enable fields can force hardware away from normal PHY sequencing, and measurement selector fields can change what analog node is exposed to diagnostic circuitry.

Represented common-memory state is mostly opaque 16-bit `DATA` for raw digital memory locations. These locations may persist only until the relevant PHY/common reset and may be initialized by firmware or hardware tables. Because this generated header exposes only a full `0xFFFF` data field, persistence and validity cannot be inferred from the macro alone.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 6.1 register database and must stay aligned with sibling generated headers:

- `nbio_6_1_offset.h` supplies offsets for the same `DWC_E12MP_PHY_X4_NS_X4_3_*` register names.
- `nbio_6_1_default.h` supplies reset/default values where generated for these PHY register families.
- AMDGPU register-helper macros consume the field masks and shifts for decode/update operations.

The broader integration points are AMDGPU NBIO initialization, PCIe link management, reset and suspend/resume handling, SR-IOV/mxGPU policy, power management, PHY diagnostics, and low-level hardware bring-up tooling. Although this file lives under a `ceph-client` source mirror in this repository, the content is AMD GPU register metadata and has no direct Ceph filesystem control path.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while programming or decoding the wrong hardware bit. The riskiest fields in this chunk are analog override, clock, loopback, termination, CDR/AFE, LOS, DFE, and calibration mux controls.
- The chunk boundaries split two registers. `LANE3_ANA_TX_OVRD_CLK` needs the previous chunk for its field shifts and low-byte masks; `RAWCMN_DIG_MEM_CMN5_B2_R3` needs the next line/chunk for the `DATA_MASK`.
- Raw common memory registers are opaque full-width `DATA` fields. Software must not infer subfield semantics from this header; bank/register addressing, side effects, and ownership must come from the hardware programming model.
- Repetitive generated memory-window definitions are vulnerable to silent off-by-one or missing-register errors. A single wrong bank, row, or mask can affect only one PHY memory location and be difficult to detect by ordinary build tests.
- Analog test-bus and calibration selectors can perturb diagnostic routing or calibration visibility. They should be used only with appropriate link state, ownership, and restore sequencing.
- Override bits can conflict with firmware/SMU ownership or with autonomous PHY state machines, leaving a lane in an unexpected clock, power, loopback, termination, or calibration state.
- Reserved-field masks should primarily support read-modify-write preservation. Intentional writes to reserved bits require an explicit hardware sequence.

## Test Signals

- Build AMDGPU with NBIO 6.1 support enabled to catch missing or malformed generated macros used by C code.
- Run generated-header consistency checks across `nbio_6_1_sh_mask.h`, `nbio_6_1_offset.h`, and `nbio_6_1_default.h` for matching register names, field widths, and default-compatible masks.
- Validate that every complete `RAWCMN_DIG_MEM_*` register in this range has `DATA__SHIFT 0x0` and `DATA_MASK 0xFFFFL`; flag the expected boundary exception for `CMN5_B2_R3` in this chunk.
- Check raw memory coverage mechanically: `CMN2`, `CMN3`, and `CMN4` should include banks `B0` through `B7`, rows `R0` through `R31`; `CMN5` coverage in this chunk should stop at `B2_R3` because of the source range boundary.
- Runtime validation on affected NBIO 6.1 GPUs should confirm stable PCIe link training, negotiated link width/speed, absence of unexpected lane 3 LOS/loopback/termination behavior, and correct recovery after GPU reset or suspend/resume.
- PHY diagnostic tests should read lane 3 analog measurement selectors, calibration muxes, slicer/termination controls, and raw common memory windows without causing link flaps or stale ownership conflicts.
