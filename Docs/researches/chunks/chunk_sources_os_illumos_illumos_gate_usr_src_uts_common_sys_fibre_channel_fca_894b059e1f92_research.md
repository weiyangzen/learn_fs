# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lp11000.h lines 49788-53105

## Scope And Artifact

- Scope: `Docs/research_subset_a.md` includes `sources/os/illumos/illumos-gate`.
- File role: generated/embedded Emulex LP11000 firmware image header, not normal illumos host driver logic.
- Enclosing artifact: `static uint8_t emlxs_lp11000_image[]`, compiled only when `EMLXS_FW_IMAGE_DEF` is defined.
- Firmware identity from file context: `LP11000-S: v2.82a4 (bd282a4.all)`.
- Chunk coverage: source lines 49788-53105, firmware byte rows `0x61310` through `0x67AB8`, ending at byte `0x67ABF`.
- Size represented in this chunk: 3,318 rows, 26,544 image bytes.

## APIs And Host Surface

- No new C functions, structs, typedefs, enums, ioctls, callbacks, or illumos kernel APIs are defined in this range.
- The only host-visible object extended by these lines is the enclosing `emlxs_lp11000_image[]` firmware initializer.
- `emlxs_fw.h` includes `fw_lp11000.h` and places `emlxs_lp11000_size`, image, label, and SLI version constants into the `LP11000_FW` firmware table entry.
- `emlxs_adapters.h` maps LP11000/LP11000-S adapter IDs to `LP11000_FW`.

## Firmware Layout And Flow

- The first part from `0x61310` is predominantly zero-filled; first nonzero row in this chunk is `0x62148`.
- Sparse literal/table rows appear between `0x62148` and `0x62980`.
- Dense ARM-like firmware code begins around `0x62990`, with load/compare/return patterns, branches, helper calls, and literal references.
- Table/configuration data around `0x62A10`-`0x62C18` includes address-like words and repeated small records.
- Embedded format strings near `0x62C20`: `XTIME: %08x  %s`, `%08x:`, `%08x %08x`, `%08x %08x\n`.
- From `0x62C58` onward, the chunk is mostly executable firmware bytes.
- Near `0x67890`-`0x67AB8`, bytes form a broad dispatch/decision path over many command/status-like constants.
- The chunk ends mid-control-flow at `0x67AB8`; next chunk continues at `0x67AC0`.

## State, Dependencies, Risks

- Host-side state is only immutable firmware bytes plus file-level image metadata outside this chunk.
- Firmware-side state is opaque adapter memory/register state, with many fixed-offset accesses suggesting queues, tables, status, and control fields.
- Dependencies: `EMLXS_FW_IMAGE_DEF`, `emlxs_fw.h`, `emlxs_adapters.h`, LP11000 hardware/firmware ABI.
- Risk: byte order, alignment, literal pools, zero regions, strings, and branch spacing are contractual. Editing or trimming apparent padding may corrupt firmware loading or adapter behavior.
- Chunk-local analysis cannot prove reachability or dead data because branches and tables cross chunk boundaries.

## Cross-Chunk References

- Previous chunk lines 46470-49787 ends at row `0x61308`; this chunk begins at `0x61310`.
- Next chunk lines 53106-56423 starts at row `0x67AC0`.
- Final merge should preserve the single `emlxs_lp11000_image[]` array, `EMLXS_FW_IMAGE_DEF` behavior, LP11000 firmware table linkage, and total image size.