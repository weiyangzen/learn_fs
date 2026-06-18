# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 48857-51607

## Scope And Purpose

This chunk is a generated AMDGPU NBIO 6.1 shift/mask header segment for the DesignWare E12MP x4 PCIe PHY common-side register namespace `DWC_E12MP_PHY_X4_NS_X4_0_RAWCMN_DIG_*`. It contains preprocessor constants only: no C functions, types, enums, storage, or executable control flow are defined here.

The range begins in the middle of the `RAWCMN_DIG_MEM_CMN3_B2` table at register `R15`, continues through common memory banks `CMN3` to `CMN6`, and ends after the first named common-digital PLL override register. These macros provide bit positions and masks used by AMDGPU register-field helpers and by generated/default register metadata to pack, extract, or validate PHY register fields.

The chunk contains 915 register comment blocks and 1,836 `#define` entries. Most of the chunk is regular generated table material: each `RAWCMN_DIG_MEM_CMN*_B*_R*` register exposes a single 16-bit `DATA` field with shift `0x0` and mask `0xFFFFL`. The last two registers are semantic common-control fields:

- `DWC_E12MP_PHY_X4_NS_X4_0_RAWCMN_DIG_CMN_CTL`, with `PHY_FUNC_RST` at bit 0 and bits 15:1 reserved.
- `DWC_E12MP_PHY_X4_NS_X4_0_RAWCMN_DIG_MPLLA_BW_OVRD_IN`, with `MPLLA_BW_OVRD_VAL` in bits 10:0, `MPLLA_BW_OVRD_EN` at bit 11, and bits 15:12 reserved.

## Register Families Covered

The `RAWCMN_DIG_MEM_CMN*` portion describes opaque common-side PHY memory/register banks. The selected line range covers:

- `CMN3_B2_R15` through `CMN3_B2_R31`, then full `CMN3_B3` through `CMN3_B7` banks.
- Full `CMN4_B0` through `CMN4_B7` banks.
- Full `CMN5_B0` through `CMN5_B7` banks.
- Full `CMN6_B0` through `CMN6_B6` banks.

For each full bank, register indices `R0` through `R31` are present. Because the chunk starts at line 48857, `CMN3_B2_R0` through `CMN3_B2_R14` belong to the previous chunk. Because this chunk ends at line 51607, the next chunk continues with subsequent `RAWCMN_DIG_MPLLA_*` fields.

The banked memory entries are intentionally field-poor: every register in those groups has only `DATA__SHIFT 0x0` and `DATA_MASK 0xFFFFL`. Their semantic meaning comes from the hardware register database and matching default/offset/SMN headers, not from descriptive field names in this file.

The named control tail is more directly interpretable. `RAWCMN_DIG_CMN_CTL` exposes a PHY functional reset bit and reserves the rest of the 16-bit field. `RAWCMN_DIG_MPLLA_BW_OVRD_IN` exposes an 11-bit MPLLA bandwidth override value, a one-bit enable, and reserved upper bits. The matching default header defines defaults for these registers, including `RAWCMN_DIG_CMN_CTL_DEFAULT` as zero and `RAWCMN_DIG_MPLLA_BW_OVRD_IN_DEFAULT` as `0x43`.

## APIs, Types, And Functions

There are no callable APIs in this chunk. The exported interface is the macro namespace:

- `DWC_E12MP_PHY_X4_NS_X4_0_RAWCMN_DIG_MEM_CMN*_B*_R*__DATA__SHIFT`
- `DWC_E12MP_PHY_X4_NS_X4_0_RAWCMN_DIG_MEM_CMN*_B*_R*__DATA_MASK`
- `DWC_E12MP_PHY_X4_NS_X4_0_RAWCMN_DIG_CMN_CTL__PHY_FUNC_RST__SHIFT`
- `DWC_E12MP_PHY_X4_NS_X4_0_RAWCMN_DIG_CMN_CTL__PHY_FUNC_RST_MASK`
- `DWC_E12MP_PHY_X4_NS_X4_0_RAWCMN_DIG_MPLLA_BW_OVRD_IN__MPLLA_BW_OVRD_VAL__SHIFT`
- `DWC_E12MP_PHY_X4_NS_X4_0_RAWCMN_DIG_MPLLA_BW_OVRD_IN__MPLLA_BW_OVRD_VAL_MASK`
- `DWC_E12MP_PHY_X4_NS_X4_0_RAWCMN_DIG_MPLLA_BW_OVRD_IN__MPLLA_BW_OVRD_EN__SHIFT`
- `DWC_E12MP_PHY_X4_NS_X4_0_RAWCMN_DIG_MPLLA_BW_OVRD_IN__MPLLA_BW_OVRD_EN_MASK`

AMDGPU code normally combines these generated shift/mask constants with offset or SMN constants from the matching NBIO 6.1 headers and helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15`, `RREG32_SOC15`, `WREG32_SOC15`, or SMN access helpers. This chunk supplies the bit-level contract; address selection and hardware access live outside this file.

Observed integration includes `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c`, and Vega10/Vega12 powerplay aggregate headers, all of which include `nbio_6_1_sh_mask.h` alongside related offset/default headers. Direct named references to this exact PHY-memory slice are not visible in the searched C files, which is expected for generated PHY table fields that may be used indirectly, retained for register-database completeness, or consumed by hardware bring-up paths not present in this slice.

## Control Flow

This header has no runtime control flow. At compile time, the C preprocessor makes the shift and mask constants available to any translation unit that includes the generated NBIO 6.1 register headers.

Runtime sequencing is entirely in consumers. A typical field update sequence reads a register, clears a mask, inserts a shifted value, and writes the register back. For the `DATA` banks, the consumer treats the register as a 16-bit payload. For `RAWCMN_DIG_CMN_CTL`, a consumer would toggle or inspect `PHY_FUNC_RST` while preserving reserved bits. For `RAWCMN_DIG_MPLLA_BW_OVRD_IN`, a consumer would program the 11-bit override value and enable bit according to PHY initialization or tuning rules.

The chunk does not express ordering requirements, reset delays, PLL lock waits, or reserved-bit preservation. Those requirements must come from the PHY programming sequence in the consumer or from hardware documentation.

## State And Persistence Behavior

The macros are immutable compile-time constants and do not store software state. The state represented by these definitions is hardware state in the NBIO 6.1 PCIe PHY common digital block.

The memory-bank registers likely hold common PHY microcode, tuning, or register-table payloads exposed as 16-bit `DATA` words. Their values persist only in hardware register state and follow normal GPU reset, PCIe link reset, suspend/resume, and power-management behavior. The source file acts as persistent metadata for how to address fields inside those registers, not as a runtime persistence mechanism.

`RAWCMN_DIG_CMN_CTL` controls PHY functional reset state. Misprogramming it can hold the PHY in reset or release it at the wrong time. `RAWCMN_DIG_MPLLA_BW_OVRD_IN` controls MPLLA bandwidth override state. When enabled, it can alter PLL behavior for the common PHY, affecting link training, clock stability, and PCIe reliability.

Reserved fields are explicitly represented with masks in this chunk. Consumers should preserve reserved bits during read-modify-write unless hardware documentation says a full write is required.

## Dependencies And Integration Points

This chunk depends on naming and generation consistency across the NBIO 6.1 register header set:

- `nbio_6_1_offset.h` and `nbio_6_1_smn.h` provide addresses or SMN identifiers for the same `DWC_E12MP_PHY_X4_NS_X4_0_RAWCMN_DIG_*` register names.
- `nbio_6_1_default.h` provides reset/default values for the same register names, including the common-control and MPLLA bandwidth override defaults adjacent to this range.
- AMDGPU register helper macros use the shift/mask naming convention to build field-level read-modify-write operations.
- NBIO, PCIe, SR-IOV, and power-management code includes this header through `nbio_v6_1.c`, `mxgpu_ai.c`, `vega10_inc.h`, and `vega12_inc.h`.

The primary integration surface is hardware-facing PCIe PHY setup rather than high-level source call graphs. These masks support bring-up, diagnostics, reset handling, PLL override programming, and generated register completeness for Vega/NBIO 6.1-era hardware.

## Risks And Edge Cases

Generated shift/mask headers are mechanically simple but high impact. A wrong mask or shift can cause writes to affect the wrong bit field, fail to set an enable bit, corrupt reserved bits, or silently truncate a value.

The repeated `DATA` banks are opaque. Since all entries expose the same `0xFFFFL` field, review cannot infer register intent from field names. Safety depends on the generated register database staying synchronized with the matching offset, SMN, and default headers.

The selected range starts and ends inside larger logical groups. `CMN3_B2_R0` through `R14` are outside this chunk, and the MPLLA SSC override fields after `MPLLA_BW_OVRD_IN` are outside this chunk. File-level conclusions about all common-memory banks or all MPLLA override controls must merge adjacent chunk research.

Reserved-bit handling matters in the named control registers. A write that uses only a literal value rather than preserving reserved fields may be acceptable for documented reset values but risky for runtime updates, especially after firmware, BIOS, or earlier driver stages have configured PHY state.

PLL and PHY reset fields are sequencing-sensitive even though the header does not encode sequencing. Changing `PHY_FUNC_RST` or enabling MPLLA bandwidth override without respecting hardware ordering, lock time, and link-state constraints can cause PCIe link training failures, intermittent AER errors, suspend/resume regressions, or GPU initialization failures.

## Test Signals

Useful validation signals for this region include:

- Build coverage for AMDGPU NBIO 6.1, Vega10, and Vega12 paths, catching missing or renamed generated macros.
- Static diff against regenerated `nbio_6_1_sh_mask.h`, `nbio_6_1_offset.h`, `nbio_6_1_smn.h`, and `nbio_6_1_default.h` from the same hardware register database.
- Boot/probe logs on NBIO 6.1/Vega-class hardware showing AMDGPU initialization completes without SMN/MMIO access faults.
- PCIe link training checks: negotiated generation and width, retrain events, link-down events, and AER error counters.
- Suspend/resume, GPU reset, and runtime power-management tests that exercise PHY reset and PLL reinitialization paths.
- Hardware register traces or diagnostics confirming `DATA` bank programming remains 16-bit clean and that `MPLLA_BW_OVRD_IN` writes preserve reserved bits while setting only the documented value and enable fields.

Because this is one generated chunk of a very large header, the merge lane should combine it with adjacent `nbio_6_1_sh_mask.h` chunks before drawing final conclusions about the full `DWC_E12MP_PHY_X4_NS_X4_0_RAWCMN_DIG_*` register family.
