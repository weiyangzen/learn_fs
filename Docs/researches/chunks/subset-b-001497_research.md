# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_1_sh_mask.h lines 32974-33080

## Purpose

This chunk is the final section of the generated AMD BIF 5.1 shift/mask header. It defines bit masks and bit shifts for the PSX81 PIF0 lane override registers at the end of the BIF register map, then closes the `BIF_5_1_SH_MASK_H` include guard.

The covered lines finish the lane 6 override definitions and provide the complete lane 7 override definitions. These constants describe the packed fields in `PSX81_PIF0_LANE6_OVRD2`, `PSX81_PIF0_LANE7_OVRD`, and `PSX81_PIF0_LANE7_OVRD2`. Driver code uses this style of generated header to compose and decode MMIO register values without hard-coding field positions in call sites.

## Important APIs, Types, And Functions

There are no C functions, structs, or runtime APIs in this chunk. The exported interface is a set of preprocessor constants:

- `PSX81_PIF0_LANE6_OVRD2__*_*`: masks and shifts for lane 6 override values, including gang mode, frequency divider, link speed, two-symbol enable, transmit and receive power states, pattern-generator enables, electrical-idle detection, figure-of-merit controls, tracking/training requests, and coefficient fields.
- `PSX81_PIF0_LANE7_OVRD__*_OVRD_EN_7_*`: one-bit enable masks and shifts that control whether the corresponding lane 7 field is overridden.
- `PSX81_PIF0_LANE7_OVRD__CDREN_OVRD_VAL_7_*`: lane 7 CDR enable override value field.
- `PSX81_PIF0_LANE7_OVRD2__*_*`: actual lane 7 override value fields. Multi-bit fields include `GANGMODE_7`, `FREQDIV_7`, `LINKSPEED_7`, `TXPWR_7`, `TXPGENABLE_7`, `RXPWR_7`, `RXPGENABLE_7`, `COEFFICIENTID_7`, and `COEFFICIENT_7`; single-bit fields include two-symbol enable, electrical-idle detect enable, FOM request/enable, response mode, tracking request, and training request.
- `#endif /* BIF_5_1_SH_MASK_H */`: closes the header guard that was opened at the top of the generated file.

The matching register-address constants live in `bif_5_1_d.h` as `ixPSX81_PIF0_LANE6_OVRD2`, `ixPSX81_PIF0_LANE7_OVRD`, and `ixPSX81_PIF0_LANE7_OVRD2`. This header supplies field extraction and construction constants; the companion `_d.h` header supplies the register index.

## Control Flow

This header has no executable control flow. Its operational flow is compile-time macro expansion:

1. A source file includes the AMD BIF 5.1 register definition headers.
2. Code selects the register offset from the companion register-address header.
3. Code uses the `*_MASK` and `*__SHIFT` constants from this header to clear, insert, or extract individual fields in a 32-bit register value.
4. The composed value is passed to an AMDGPU MMIO, indirect-register, or register-programming helper outside this chunk.

The register layout itself is regular. `LANE7_OVRD` uses low bits as override-enable selectors. `LANE7_OVRD2` stores the override values in the same order and bit positions as lane 6 and the preceding lanes. The file ending is also part of the compile-time control structure: the closing `#endif` completes the include guard and prevents duplicate macro definitions on repeated inclusion.

## State And Persistence Behavior

The chunk stores no software state and performs no MMIO by itself. Its state model is declarative: it records hardware bit layouts as C preprocessor definitions.

Persistent behavior appears only when another driver component uses these constants to write the PIF lane registers. Such writes affect hardware link-training and PHY lane behavior until the register is changed again, the block is reset, or the GPU is reset. The override-enable fields are especially stateful at the hardware level because setting an enable bit tells the PHY logic to use the corresponding software-provided value rather than autonomous hardware training or default behavior.

The constants must stay synchronized with the generated ASIC register database. A stale mask or shift does not fail locally in this header; it causes later register reads or writes to target the wrong bit positions.

## Dependencies

This chunk depends on the surrounding generated AMD register-header ecosystem:

- The `BIF_5_1_SH_MASK_H` include guard and file-level license/header context defined earlier in `bif_5_1_sh_mask.h`.
- Register index definitions in `bif_5_1_d.h`, especially `ixPSX81_PIF0_LANE6_OVRD2`, `ixPSX81_PIF0_LANE7_OVRD`, and `ixPSX81_PIF0_LANE7_OVRD2`.
- AMDGPU register helper conventions that pair `FIELD__MASK` and `FIELD__SHIFT` constants to build and decode register values.
- Hardware documentation for the BIF 5.1 PSX81 PIF0 lane override registers. The field names imply PHY Interface lane controls for link speed, power state, training, coefficient selection, and related PCIe/SerDes behavior.

There are no Linux kernel library dependencies in the chunk itself beyond normal preprocessor handling.

## Integration Points

The integration point is AMDGPU low-level register programming for BIF 5.1 ASICs. Consumers are expected to include this file with the matching BIF register-address header and use the lane override constants when programming or diagnosing PSX81 PIF0 lanes 6 and 7.

The constants align with the repeated lane layout used by the preceding lane definitions. This regularity is important for any code that handles lanes generically or validates generated register headers: lane 7 mirrors lane 6, with `_7` suffixes and the same masks/shifts for equivalent fields.

The chunk also integrates with the build system as a generated header endpoint. Because it contains the final `#endif`, truncation or accidental edits in this range can break every translation unit that includes `bif_5_1_sh_mask.h`.

## Risks And Edge Cases

- A wrong mask or shift can silently corrupt unrelated PHY control bits when a caller performs read-modify-write on a lane override register.
- The chunk starts at the tail of `PSX81_PIF0_LANE6_OVRD`; the first lane 6 override-enable fields are outside this range, so per-file reconciliation must merge this with the preceding chunk for a complete lane 6 view.
- Lane 7 definitions are copy-patterned from earlier lanes. Copy/paste or generation drift could leave a `_6` suffix, wrong register field name, or wrong bit position while still compiling.
- The `COEFFICIENT_7` field occupies the high six bits of the 32-bit register (`0xfc000000`, shift `0x1a`). Callers must use unsigned 32-bit arithmetic when composing values that touch this field.
- Override-enable fields and override-value fields are split between `LANE7_OVRD` and `LANE7_OVRD2`. Programming values without the matching enable bits, or enabling fields without valid values, can produce ineffective or harmful hardware configuration.
- The final include-guard close is part of this chunk. Removing or moving it would produce duplicate-definition or unterminated-conditional build failures.

## Test Signals

Useful validation signals for this chunk are mostly build-time, static, and hardware bring-up checks:

- Kernel or driver builds including `bif_5_1_sh_mask.h` should compile without preprocessor guard errors or duplicate macro diagnostics.
- Static checks can compare lane 7 masks and shifts against lane 6 and earlier lanes to verify repeated-field consistency.
- Header-generation validation should confirm that `*_OVRD2` masks do not overlap incorrectly and cover only the documented bit ranges.
- Register read-modify-write tests should verify that composing a lane 7 field with `MASK` and `SHIFT` changes only the intended bits.
- Hardware PCIe/BIF bring-up should complete without link-training regressions on ASICs using BIF 5.1 when these lane override registers are left at defaults or programmed by diagnostics.
- PHY diagnostic paths that request FOM, tracking, training, or coefficient overrides should observe expected register values when reading back `PSX81_PIF0_LANE7_OVRD` and `PSX81_PIF0_LANE7_OVRD2`.
