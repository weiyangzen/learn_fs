# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 64604-64798

## Scope

This chunk covers the final 195 lines of the DCE 12.0 generated register shift/mask header. It begins in the middle of the legacy VGA CRT controller indexed-register definitions, continues through the VGA graphics-controller and attribute-controller indexed-register blocks, and ends the file with the closing `#endif` for `_dce_12_0_SH_MASK_HEADER`.

The source contains no C functions, structs, enums, or executable logic. Its exported surface is a set of C preprocessor constants named as `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`. These constants are consumed by AMDGPU display code together with companion DCE 12.0 register offset definitions and register read/modify/write helpers.

## Purpose

The chunk describes bit layouts for the legacy VGA indexed register space preserved inside AMD display hardware:

- `CRT11` through `CRT22` fields for CRT controller vertical timing, display pitch, address counting, sync enable, line compare, graphics decode readback, and latch data.
- `vgagrphind` block entries `GRA00` through `GRA08` for VGA graphics-controller set/reset, compare, rotate/function select, read map, write/read mode, odd/even addressing, graphics/address-select mode, compare don't-care, and bit mask.
- `vgaattrind` block entries `ATTR00` through `ATTR14` for attribute palette entries, attribute mode control, overscan, plane enable/source mux, pixel pan, and color-select extension bits.

These are compatibility definitions for byte-sized VGA index/data registers, not high-level display-pipe controls. Their masks are mostly `0xFFL`, sub-byte nibbles, or single-bit values because the registers are the classic VGA CRTC/graphics/attribute indexed registers represented through DCE's generated ASIC register database.

## Important Macro Families

The CRT controller tail includes:

- `CRT11__V_SYNC_END`, `CRT11__V_INTR_CLR`, `CRT11__V_INTR_EN`, `CRT11__SEL5_REFRESH_CYC`, and `CRT11__C0T7_WR_ONLY` masks. This chunk starts at the last two `CRT11` masks, so the associated shifts are in the immediately preceding chunk.
- `CRT12__V_DISP_END`, `CRT15__V_BLANK_START`, `CRT16__V_BLANK_END`, and `CRT18__LINE_CMP`, each with full byte-width `0xFFL` masks.
- `CRT13__DISP_PITCH`, also byte-width, for the legacy display pitch field.
- `CRT14__UNDRLN_LOC`, `CRT14__ADDR_CNT_BY4`, and `CRT14__DOUBLE_WORD`, splitting underline location and addressing mode bits.
- `CRT17__RA0_AS_A13B`, `RA1_AS_A14B`, `VCOUNT_BY2`, `ADDR_CNT_BY2`, `WRAP_A15TOA0`, `BYTE_MODE`, and `CRTC_SYNC_EN`, which encode classic VGA CRTC addressing/sync behavior.
- `CRT1E__GRPH_DEC_RD1`, `CRT1F__GRPH_DEC_RD0`, and `CRT22__GRPH_LATCH_DATA` readback/latch fields.

The `vgagrphind` block defines graphics-controller fields:

- `GRA00__GRPH_SET_RESET0` through `GRPH_SET_RESET3` and `GRA01__GRPH_SET_RESET_ENA0` through `ENA3` for per-plane set/reset values and enables.
- `GRA02__GRPH_CCOMP` and `GRA07__GRPH_XCARE0` through `XCARE3` for color compare and compare don't-care masks.
- `GRA03__GRPH_ROTATE` and `GRA03__GRPH_FN_SEL` for rotate count and raster-operation/function select.
- `GRA04__GRPH_RMAP` for read-map plane selection.
- `GRA05__GRPH_WRITE_MODE`, `GRPH_READ1`, `CGA_ODDEVEN`, `GRPH_OES`, and `GRPH_PACK` for VGA read/write mode and packed/odd-even access behavior.
- `GRA06__GRPH_GRAPHICS`, `GRPH_ODDEVEN`, and `GRPH_ADRSEL` for graphics/text mode, odd/even addressing, and aperture/address select.
- `GRA08__GRPH_BMSK` as an 8-bit bit-mask register.

The `vgaattrind` block defines attribute-controller fields:

- `ATTR00` through `ATTR0F` all expose `ATTR_PAL` at shift `0x0` with mask `0x3FL`, representing the 16 internal 6-bit VGA attribute palette entries.
- `ATTR10` splits attribute mode control into graphics mode, mono enable, line graphics enable, blink enable, pan/top-only behavior, pixel-clock divide-by-two, and color-select enable bits.
- `ATTR11__ATTR_OVSC` is the 8-bit overscan/border color field.
- `ATTR12__ATTR_MAP_EN` and `ATTR12__ATTR_VSMUX` cover plane/map enable and video-status mux bits.
- `ATTR13__ATTR_PPAN` gives the 4-bit pixel-panning field.
- `ATTR14__ATTR_CSEL1` and `ATTR14__ATTR_CSEL2` provide the low and high color-select extension fields.

## APIs, Types, and Functions

There are no callable APIs, C data types, or functions in this chunk. The macros are the API contract:

- `*_SHIFT` values give the bit offset of a field inside the indexed register value.
- `*_MASK` values give the already-positioned bit mask to clear, test, or combine with shifted values.
- The address-block comments, especially `vgagrphind` and `vgaattrind`, identify which generated register-index namespace the following byte-register fields belong to.

The file-level include guard closes at line 64798. Because this chunk terminates the header, any generation or merge error here can affect every translation unit that includes `dce_12_0_sh_mask.h`.

## Control Flow

This chunk has no intrinsic runtime control flow. The operational flow exists in the AMDGPU display/VGA access paths that use these masks:

1. Select a legacy VGA indexed register through the relevant CRTC, graphics-controller, or attribute-controller index path.
2. Read or prepare the byte-sized data value.
3. Use the matching `*_MASK` and `*_SHIFT` constants to isolate or update a field.
4. Write the value back through the VGA indexed data path, or interpret readback status/latch fields.

The macros also describe order-sensitive hardware behavior indirectly. For example, vertical interrupt bits in `CRT11`, CRTC sync enable in `CRT17`, graphics write/read mode in `GRA05`, and attribute palette/index behavior in `ATTR00`-`ATTR14` are meaningful only when the caller follows the VGA register access sequence and any display-mode ownership rules already enforced by the surrounding driver.

## State and Persistence

The header stores no software state. It describes persistent hardware register state in the legacy VGA compatibility block. State represented here includes:

- CRTC vertical timing, blanking, sync-ending, pitch, line-compare, addressing, and sync-enable state.
- VGA graphics-controller per-plane set/reset, compare, read/write mode, map selection, addressing mode, and bit-mask state.
- Attribute-controller palette, mode-control, overscan, plane-enable, pixel-panning, and color-select state.

These values persist in hardware until changed by MMIO/indexed-register writes, reset, VGA disable/ownership transitions, power-management transitions, or firmware/hardware initialization. The interrupt-clear style field `CRT11__V_INTR_CLR_MASK` is especially stateful: caller code must know whether the hardware expects a write-one-to-clear or other legacy VGA clear sequence; this header only supplies the bit position.

## Dependencies and Integration Points

This chunk depends only on the C preprocessor and the rest of the same generated header. It integrates with:

- `dce_12_0_offset.h`, which is the companion DCE 12.0 offset header in this tree.
- AMDGPU/DCE 12.0 display sources that include `dce/dce_12_0_sh_mask.h`, including DCE 12.0 timing-generator, hardware-sequencer, IRQ, GPIO, resource, and GMC code.
- Shared AMD display register helper patterns that combine `REG`/address macros with `*_MASK` and `*_SHIFT` constants.
- Legacy VGA routing/control code in the display stack that still needs VGA CRTC, graphics, and attribute indexed-register compatibility even when the normal display path is driven by modern DCE blocks.

The same macro families are repeated in earlier DCE and later DCN generated mask headers, which is a useful integration signal: these fields are stable legacy VGA definitions carried across ASIC generations.

## Risks

The main risk is silent hardware misprogramming. These are small, densely packed legacy fields, so a wrong shift or mask can alter adjacent VGA timing, address, palette, or mode bits without compiler diagnostics.

Chunk-boundary risk is present because this slice begins at `CRT11` masks while the matching `CRT11` shifts are immediately before line 64604. The merge lane should reconcile the preceding chunk so `CRT11__SEL5_REFRESH_CYC_MASK` and `CRT11__C0T7_WR_ONLY_MASK` are documented with their matching shifts.

Legacy VGA register semantics are easy to misuse from modern display code. Attribute-controller registers require the correct index/data access sequence, palette entries are only 6-bit despite living in byte registers, and CRTC/graphics-controller addressing bits interact with memory aperture and text/graphics mode behavior. Treating these constants like ordinary 32-bit DCE pipe registers can produce invalid accesses or stale state.

Interrupt and sync fields have display-visible failure modes. Misprogramming `CRT11__V_INTR_CLR`, `CRT11__V_INTR_EN`, or `CRT17__CRTC_SYNC_EN` can lose vertical interrupt state, leave unexpected interrupts enabled, or affect legacy sync generation. Palette and blink/pixel-pan fields can cause visible color, cursor/blink, or alignment artifacts in VGA compatibility modes.

Because this chunk closes the include guard, truncation after these definitions or a malformed guard terminator would break all users of the header at compile time. Conversely, duplicated or renamed macros would compile only until a user includes conflicting generated headers in the same scope.

## Test Signals

Useful validation signals include:

- Basic build coverage for all translation units that include `dce_12_0_sh_mask.h`.
- Static generated-header checks that every field has both a `__SHIFT` and `_MASK`, that masks align with shifts, and that this file has a single intact `_dce_12_0_SH_MASK_HEADER` guard ending at line 64798.
- Diff checks against AMD's authoritative DCE 12.0 register-generation source and against nearby DCE/DCN generations for these stable VGA fields.
- VGA compatibility smoke tests that exercise mode set/disable paths, VGA memory aperture handling, palette writes, pixel panning, blink/line-graphics behavior, and text/graphics mode transitions.
- Interrupt/readback tests around `CRT11` vertical interrupt clear/enable and CRTC status readback where hardware access is available.
- Visual or register-readback checks after programming `GRA05`, `GRA06`, `ATTR10`, `ATTR12`, and `ATTR14`, because those fields affect memory interpretation and displayed color/mode behavior.

## Cross-Chunk Notes

This is the terminating chunk of a 64,798-line generated header. The final per-file report should merge it with earlier chunks for the full VGA section: the beginning of `CRT11` appears before this slice, and earlier portions of the file cover the modern DCE display, clocking, writeback, interrupt, DCP, and other register blocks. This chunk should be treated as the final legacy VGA indexed-register tail plus the include-guard terminator, not as a standalone hardware module.
