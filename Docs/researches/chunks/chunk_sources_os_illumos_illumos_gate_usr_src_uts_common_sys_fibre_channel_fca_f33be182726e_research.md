# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lpe11000.h lines 19925-23242

## Scope And Artifact

- Scope: `Docs/research_subset_a.md` includes `sources/os/illumos/illumos-gate`.
- File role: embedded Emulex LPe11000 Fibre Channel adapter firmware image header, not normal illumos host driver logic.
- Enclosing artifact: `static uint8_t emlxs_lpe11000_image[]`, emitted only when `EMLXS_FW_IMAGE_DEF` is defined.
- Firmware identity from file context: `LPe11000-S: v2.82a4 (zd282a4.all)`.
- Chunk coverage: source lines 19925-23242, image byte rows `0x26DD8` through `0x2D580`; the covered bytes end at `0x2D587`.
- Size represented in this chunk: 3,318 initializer rows, 26,544 image bytes.

## APIs And Host Surface

- No C functions, structs, typedefs, enums, ioctls, callbacks, or illumos kernel APIs are declared in this range.
- The host-visible surface is only a contiguous slice of `emlxs_lpe11000_image[]`.
- `emlxs_fw.h` includes `fw_lpe11000.h` while building `EMLXS_FW_TABLE` and associates this image with `LPe11000_FW`, `emlxs_lpe11000_size`, `emlxs_lpe11000_label`, and the `kern`/`stub`/`sli1`/`sli2`/`sli3`/`sli4` constants.
- The host driver treats these bytes as opaque firmware payload. Source-level call graph tools will see an array initializer, while the adapter executes the bytes as on-card firmware.

## Firmware Control Flow

- The range starts mid-routine at `0x26DD8`; adjacent previous context ends at row `0x26DD0` and shows ongoing fixed-offset field updates before control enters this chunk.
- The bytes are ARM-like executable firmware mixed with literal pools and embedded diagnostics. In this range there are many branch/call patterns, including `BL` helper calls, conditional branches, table dispatches, stack-save prologues, and returns.
- Early code around `0x26DD8`-`0x27218` continues a command/status path that updates fields around offsets such as `+0x0A`, `+0x0B`, `+0x0C`, `+0x18`, `+0x1C`, `+0x24`, `+0x26`, `+0x27`, `+0x2C`, `+0x3C`, `+0x40`, `+0x44`, and `+0x64`.
- The region around `0x27120`-`0x27558` contains several visible routine boundaries. It copies or normalizes descriptor fields, toggles packed flags in a `+0x0C` word, and writes byte status values such as `0x26`, `0x58`, `0x59`, and `0x5A` at object offset `+0x07`.
- The larger middle region manipulates queue/list-like state and control blocks through repeated loads/stores at offsets including `+0x00`, `+0x04`, `+0x08`, `+0x10`, `+0x14`, `+0x18`, `+0x1C`, `+0x20`, `+0x24`, `+0x28`, `+0x2C`, `+0x30`, `+0x3C`, `+0x40`, `+0x44`, `+0x4C`, `+0x50`, and `+0x6C`.
- Embedded printable diagnostics in this chunk identify Fibre Channel login and link-initialization paths: `REG_LOGIN %02x %06x`, `UNREG_LOGIN %02x`, `INIT %08x`, `INIT_LINK %02x`, `ENDEC PCFG:`, `Our SID: %08x`, and `DWNL %08x`.
- Near the end, code around `0x2D008`-`0x2D580` dispatches on byte-status/opcode values and branches to many out-of-range targets. The visible branch table assigns status bytes including `0x53`, `0x5F`, `0x55`, `0x56`, `0x57`, `0x58`, `0x50`, `0x51`, `0x59`, `0x5A`, `0x5E`, `0x52`, and `0x54`.

## State And Data Dependencies

- Host-side state is immutable image data plus file-level metadata outside the range.
- Firmware-side state is opaque adapter memory. The fixed-offset accesses imply per-command, per-exchange, queue, port/login, and hardware-status structures, but their C layouts are not present in this header.
- Repeated accesses to object byte fields such as `+0x06`, `+0x07`, `+0x08`, `+0x09`, `+0x0A`, `+0x0B`, `+0x0F`, `+0x24`, `+0x26`, `+0x27`, and `+0x3C` suggest compact firmware state machines and flag bytes.
- Repeated accesses to word fields such as `+0x0C`, `+0x10`, `+0x14`, `+0x18`, `+0x1C`, `+0x20`, `+0x28`, `+0x30`, `+0x40`, `+0x44`, `+0x4C`, `+0x50`, `+0x58`, `+0x64`, and `+0x6C` suggest descriptor pointers, counters, hardware status words, or list links.
- Runtime dependencies include the LPe11000 adapter processor, its firmware memory map, DMA/ring hardware, Fibre Channel link/login state, and the SLI firmware ABI expected by the `emlxs` driver.

## Risks And Invariants

- Byte accuracy is the main invariant. Any edit can corrupt ARM instruction alignment, branch displacements, literal pools, embedded diagnostics, or hardware register programming.
- Apparent data rows, strings, zero-like values, and address-like constants may be referenced by nearby instructions; they cannot be treated as unused from this chunk alone.
- The visible login/register and link-initialization diagnostics indicate direct manipulation of fabric/session identity and source-ID state. Corruption here could surface as link initialization failures, stale login mappings, dropped I/O, or adapter hangs rather than host-side compile errors.
- Source-level C tests cannot validate this chunk. Meaningful validation requires full firmware image integrity checks and runtime adapter/driver testing.
- The enclosing header aligns `emlxs_lpe11000_image[]` to 8 bytes and reports total image size `0x8A5CC`; chunk-local changes must preserve the full image layout and size.

## Cross-Chunk References

- Previous chunk 6 covers lines 16607-19924 and ends at byte row `0x26DD0`; this chunk begins at `0x26DD8` in the same firmware control-flow region.
- Next chunk 8 covers lines 23243-26560 and begins at byte row `0x2D588`; this chunk ends mid-dispatch at `0x2D580`.
- Branches and calls in this range target many locations outside the requested lines, so no routine here should be treated as independently complete.
- Final per-file merge should preserve this as one contiguous opaque firmware image tied to the LPe11000 metadata and `emlxs_fw.h` firmware-table contract, not as independent source-level APIs.