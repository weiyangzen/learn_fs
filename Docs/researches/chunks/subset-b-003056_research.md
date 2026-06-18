# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 126139-128880

## Scope

This chunk covers a generated AMD NBIO 6.1 shift/mask header segment for `DWC_E12MP_PHY_X4_NS_X4_3_RAWCMNX_DIG_MEM_*` registers. It contains 2,742 source lines from the end of `CMN2_B3_R10`'s mask through `CMN5_B7_R28`. There are no C functions, structs, enums, variables, locks, allocations, branches, or direct MMIO/SMN accesses in this range.

The visible pattern is mechanical: each commented register name is followed by a `__DATA__SHIFT` macro set to `0x0` and a `__DATA_MASK` macro set to `0xFFFFL`. These macros describe whole 16-bit data words in a raw common-memory view of the DWC E12MP x4 PHY instance `NS_X4_3`. The chunk starts mid-register-family, so `CMN2_B3_R10` began in the previous chunk, and it ends before the full `CMN5_B7` bank is complete.

## Purpose

`nbio_6_1_sh_mask.h` is the bitfield half of the generated NBIO 6.1 register interface. For normal decoded registers it supplies one shift and one mask per named field. For this chunk, every register has only one exposed field:

- `<REGISTER>__DATA__SHIFT`, always `0x0`.
- `<REGISTER>__DATA_MASK`, always `0xFFFFL`.

That means the register interface intentionally treats each raw common-memory cell as an opaque 16-bit payload rather than exposing semantic subfields. The matching register offsets live in `nbio_6_1_offset.h`, and reset values for these raw memory cells live in `nbio_6_1_default.h`. Runtime AMDGPU code includes these generated headers so register helper macros and SMN/MMIO accessors can address the ASIC generation without hard-coded bit constants.

This source tree is a Ceph/distributed-filesystem mirror, but this file is unrelated to Ceph logic. It is AMD GPU hardware metadata under the mirrored Linux driver tree.

## Register Families Covered

The chunk covers 914 register-comment blocks, mostly full 32-register banks:

- `CMN2_B3_R11` through `CMN2_B3_R31`, plus banks `CMN2_B4` through `CMN2_B7`.
- `CMN3_B0` through `CMN3_B7`.
- `CMN4_B0` through `CMN4_B7`.
- `CMN5_B0` through `CMN5_B6`.
- `CMN5_B7_R0` through `CMN5_B7_R28`.

The family naming suggests a raw common-memory organization: common-memory page or region `CMN2` to `CMN5`, bank `B0` to `B7`, and row/register `R0` to `R31`. The `DWC_E12MP_PHY_X4_NS_X4_3` prefix identifies the fourth x4 PHY namespace instance in this generated register map. Other chunks in this file cover neighboring `RAWCMNX_DIG_MEM` windows for other `NS_X4_*` instances and adjacent `CMN*` ranges.

## Important APIs, Types, and Functions

There are no callable APIs, C types, or functions here. The public contract is the preprocessor macro namespace.

The only field-level API exposed by this chunk is the `DATA` field for each raw memory register. The full-word mask makes extraction and update straightforward:

- Extracting with `REG_GET_FIELD(value, REGISTER, DATA)` should return bits 15:0.
- Updating with `REG_SET_FIELD(value, REGISTER, DATA, new_value)` should replace only bits 15:0, assuming the helper follows the generated shift/mask convention.
- Code that writes these cells directly should still pair the mask with the correct offset macro from `nbio_6_1_offset.h`.

The macros do not encode access permissions, side effects, reset-domain behavior, polling requirements, or meaning of the 16-bit data words. Those semantics must come from the hardware register database, firmware expectations, or the code that uses the PHY raw-memory window.

## Control Flow

This header segment has no local control flow. It participates in external register-access flows:

1. Driver, firmware-facing code, or diagnostics select an NBIO 6.1 raw common-memory register offset.
2. The caller uses the generated `DATA` shift/mask to extract, compose, or replace the 16-bit value.
3. The caller reads from or writes to the NBIO/SMN/MMIO register space.
4. The PHY hardware interprets the raw memory word according to its internal microarchitecture.

Likely high-level flows include PCIe/PHY bring-up, PHY patch-table programming, link-training support, PHY reset/reinitialization, suspend/resume restoration, board- or ASIC-specific workarounds, and diagnostic dumps of raw PHY common memory. This range itself cannot reveal the word-level semantics; it only supplies the bitfield envelope.

## State and Persistence Behavior

The header stores no software state. It names hardware-visible storage in the NBIO PHY. Persistence is determined by the hardware reset domains, PHY power states, firmware initialization, driver save/restore paths, and any runtime writes performed through generated offset and mask macros.

Because these are raw common-memory cells, each `DATA` value may represent persistent configuration, calibration seed data, microcode/table data, status snapshots, or reserved implementation state. The reset defaults in `nbio_6_1_default.h` show that related raw common-memory cells have nontrivial 16-bit values, so software should not assume zero-initialized or spare storage. Writes may survive some soft transitions but be lost across GPU reset, PCIe function reset, suspend/resume, or PHY-specific reset depending on NBIO ownership.

The chunk exposes no explicit command bits, counters, or status flags. Any command-like or status-like behavior is hidden inside the opaque 16-bit `DATA` payloads and must be handled by the owning programming sequence.

## Dependencies and Integration Points

This chunk depends on the generated NBIO 6.1 register header set:

- `nbio_6_1_offset.h` supplies the matching register addresses for the `DWC_E12MP_PHY_X4_NS_X4_3_RAWCMNX_DIG_MEM_*` names.
- `nbio_6_1_default.h` supplies reset/default constants for many matching raw common-memory registers.
- AMDGPU register helper macros consume the `__SHIFT` and `_MASK` naming convention for field extraction and read-modify-write updates.

Observed include integration in the mirrored source tree includes:

- `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, the generation-specific NBIO implementation.
- `drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c`, which includes NBIO 6.1 definitions for SR-IOV/MxGPU paths on this ASIC family.
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_inc.h` and `vega12_inc.h`, which pull generated NBIO definitions into Vega power-management include stacks.

The raw-memory macros may also be consumed indirectly by generated tables or by debug/bring-up code that is not easy to identify through direct macro-name searches, because the register names are highly regular and can be selected mechanically.

## Risks and Edge Cases

- A wrong offset-to-mask pairing can compile cleanly because every field in this chunk has the same shift and mask. The main safety property is the register name, not field shape.
- These macros expose opaque 16-bit cells. Treating the payload as a normal decoded register without the hardware memory map can corrupt PHY configuration, training data, or reserved implementation state.
- The chunk starts after `CMN2_B3_R10__DATA__SHIFT` and includes only that register's mask plus later registers. The previous chunk is required for a complete view of the `CMN2_B3_R10` definition.
- The chunk ends at `CMN5_B7_R28`; `CMN5_B7_R29` through later raw-memory regions continue in the next chunk. Final source-file research should stitch these boundaries before describing complete bank coverage.
- Because all masks are `0xFFFFL`, tests that only validate mask width are weak. More useful validation must check the generated register names, sequence, offsets, defaults, and instance prefix.
- Raw PHY memory writes can be timing- and ownership-sensitive. Firmware, PSP, SMU, or hardware state machines may own parts of the PHY during boot, reset, link training, or power transitions.
- Read-modify-write operations should preserve any upper bits in the containing register if the actual access width is wider than 16 bits, even though this generated field only names bits 15:0.
- Diagnostic dumps may read side-effectful or changing hardware state depending on the underlying PHY implementation, even though the header does not mark any side effects.

## Test Signals

- Build AMDGPU configurations that include NBIO 6.1, Vega10/Vega12 powerplay, MxGPU, and related PSP/display include paths; this catches missing or renamed generated symbols.
- Run generated-header consistency checks against the authoritative NBIO 6.1 register database: every raw common-memory register in this range should have `DATA__SHIFT == 0`, `DATA_MASK == 0xFFFF`, and a matching offset/default entry where the database expects one.
- Validate sequence continuity across chunk boundaries: `CMN2_B3_R10` is split at the start, and `CMN5_B7` continues after `R28` in the next chunk.
- On affected AMD GPU hardware, verify PCIe link bring-up, negotiated speed/width, warm reset, GPU reset, and suspend/resume after any change to these generated constants.
- For firmware or table-programming paths that touch raw PHY memory, compare programmed values against known-good dumps and reset defaults.
- Use hardware diagnostics or debugfs-style register dumps, where available, to confirm that `NS_X4_3` raw common-memory reads return stable values and that writes are restricted to documented sequences.
- Regression tests should include offset/name/default alignment, not just compilation, because the uniform `DATA` masks make many generation errors syntactically invisible.

## Unresolved Cross-Chunk References

The previous chunk contains the beginning of `DWC_E12MP_PHY_X4_NS_X4_3_RAWCMNX_DIG_MEM_CMN2_B3_R10`, including its register comment and `DATA__SHIFT`. The next chunk continues after `DWC_E12MP_PHY_X4_NS_X4_3_RAWCMNX_DIG_MEM_CMN5_B7_R28`, beginning with later `CMN5_B7` entries and then `CMN6` raw-memory registers. The final per-file document should merge those boundaries to describe the complete `RAWCMNX_DIG_MEM` map for `NS_X4_3`.
