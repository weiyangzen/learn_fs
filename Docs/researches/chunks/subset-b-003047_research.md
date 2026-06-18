# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 103688-106430

## Purpose

This chunk is part of AMDGPU's generated NBIO 6.1 shift/mask register header. It describes bit geometry for `DWC_E12MP_PHY_X4_NS_X4_2_RAWCMNX_DIG_MEM_*` registers, a dense set of DesignWare E12MP PCIe PHY common digital-memory rows under the `RAWCMNX` naming family.

The slice starts mid-bank at `DWC_E12MP_PHY_X4_NS_X4_2_RAWCMNX_DIG_MEM_CMN2_B1_R20`, covers all remaining rows for common-memory group `CMN2`, all rows for `CMN3` and `CMN4`, most of `CMN5`, and ends on the boundary comment for `DWC_E12MP_PHY_X4_NS_X4_2_RAWCMNX_DIG_MEM_CMN5_B6_R6`. Every complete register in this range exposes a single field named `DATA` with shift `0x0` and mask `0xFFFFL`, meaning the generated interface treats each row as a 16-bit payload value.

## Important APIs, Types, and Macros

There are no C functions, structs, enums, or typedefs in this chunk. The exported interface is a set of C preprocessor constants:

- `<REGISTER>__DATA__SHIFT`: always `0x0` for the complete entries in this range.
- `<REGISTER>__DATA_MASK`: always `0xFFFFL` for the complete entries in this range.

The chunk contains 915 register comments, 914 complete shift/mask pairs, and no other nonblank content. The final comment at line 106430 names `CMN5_B6_R6`; its `__DATA__SHIFT` and `__DATA_MASK` definitions are immediately after the requested range, so this chunk should be merged with the following chunk before making whole-file coverage claims.

Register coverage by bank in this slice:

- `CMN2_B1_R20` through `CMN2_B1_R31`: 12 complete rows, continuing a bank started before this chunk.
- `CMN2_B2` through `CMN2_B7`: 6 full banks, 32 rows each.
- `CMN3_B0` through `CMN3_B7`: 8 full banks, 32 rows each.
- `CMN4_B0` through `CMN4_B7`: 8 full banks, 32 rows each.
- `CMN5_B0` through `CMN5_B5`: 6 full banks, 32 rows each.
- `CMN5_B6_R0` through `CMN5_B6_R5`: 6 complete rows, followed by the boundary comment for `R6`.

The companion `nbio_6_1_default.h` contains reset/default values for the exact register names, for example `smnDWC_E12MP_PHY_X4_NS_X4_2_RAWCMNX_DIG_MEM_CMN2_B1_R20_DEFAULT` and `smnDWC_E12MP_PHY_X4_NS_X4_2_RAWCMNX_DIG_MEM_CMN5_B6_R6_DEFAULT`. A quick search did not find exact matching offset or SMN address defines for these names in `nbio_6_1_offset.h` or `nbio_6_1_smn.h`, so consumers may reach these PHY rows through indirect access paths or generated tables outside this local name match.

## Control Flow and Runtime Behavior

This header chunk has no runtime control flow. Including it only makes constants available to compile-time macro expansion. Runtime behavior occurs in AMDGPU code that combines NBIO register identifiers, offsets or indirect-address mechanisms, and field helpers to read, modify, or compare hardware registers.

For every complete entry here, field manipulation is simple: the whole low 16 bits are the `DATA` field. A typical helper using the generated constants would extract `value & 0xFFFF` or write a new 16-bit value at bit position zero. There are no subfields, flags, conditionals, enable bits, status bits, or embedded sequencing rules described inside this slice.

## State and Persistence

The header itself owns no state, allocates no memory, and persists nothing. The represented state is hardware state in the NBIO/PCIe PHY common digital-memory area for the `X4_2` PHY instance. The paired defaults in `nbio_6_1_default.h` suggest these rows have hardware reset values used for bring-up, diagnostics, or register dump comparisons.

Any persistence characteristics, reset behavior, latch behavior, or access restrictions belong to the ASIC register implementation. If these constants are wrong, the persistent effect is at the compiled-driver level: all code using this header would encode or decode the affected PHY row incorrectly until rebuilt with corrected generated headers.

## Dependencies and Integration Points

This file is one member of the generated NBIO 6.1 register-header set:

- `nbio_6_1_sh_mask.h` supplies field masks and shifts.
- `nbio_6_1_default.h` supplies reset/default values for the same `DWC_E12MP_PHY_X4_NS_X4_2_RAWCMNX_DIG_MEM_*` naming family.
- `nbio_6_1_offset.h` and `nbio_6_1_smn.h` normally supply register addressing for many NBIO registers, though exact matches for this chunk's names were not found in those two files during this pass.

In-tree includes of `nbio_6_1_sh_mask.h` include `amdgpu/nbio_v6_1.c`, `amdgpu/mxgpu_ai.c`, and the Vega10/Vega12 PowerPlay include aggregators. Those files pull in the full NBIO 6.1 field namespace for register access, virtualization support, and power-management register programming. This specific chunk is most aligned with low-level PCIe PHY common-memory programming or validation rather than high-level DRM control flow.

## Risks

- Generated-header drift is the main risk. A wrong `DATA_MASK` or shift would make every consumer read or write the wrong bits for a PHY memory row.
- The chunk is highly repetitive and easy to damage with manual edits. Missing one row, duplicating a row, or changing a bank/index suffix could affect only a narrow PHY memory location and be hard to detect from ordinary functional tests.
- The requested range cuts through register groups at both ends. `CMN2_B1_R0` through `R19` are before this slice, and `CMN5_B6_R6` is only named by a boundary comment inside this slice while its constants continue after line 106430.
- The exact register names have defaults but no exact offset/SMN matches found in the nearby generated address headers. That may be intentional for indirect PHY RAM access, but it is a useful cross-header validation point.
- Because every field is a 16-bit `DATA` value with no semantic subfields, the header cannot protect callers from writing invalid training, calibration, or PHY configuration payloads. Correct values must come from ASIC tables, firmware guidance, or validated hardware programming sequences.

## Test and Validation Signals

Useful validation is mostly generated-header consistency and hardware bring-up coverage:

- Build AMDGPU with NBIO 6.1 users enabled to catch missing or malformed macro names.
- Run a static consistency check that every complete `DWC_E12MP_PHY_X4_NS_X4_2_RAWCMNX_DIG_MEM_*` entry has exactly one `__DATA__SHIFT` of `0x0` and one `__DATA_MASK` of `0xFFFFL`.
- Cross-check this chunk against `nbio_6_1_default.h` to confirm defaults exist for each row in the covered `CMN2` through `CMN5` bank ranges.
- Reconcile chunk boundaries during merge: include preceding `CMN2_B1_R0-R19` definitions and following `CMN5_B6_R6+` definitions before producing final per-file conclusions.
- On affected ASICs, validate PCIe PHY initialization, link training, suspend/resume, reset, and any NBIO register-dump tooling that compares PHY memory rows against generated default values.
