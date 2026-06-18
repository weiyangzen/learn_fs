# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lpe11002.h lines 19925-23242

## Scope And Artifact

- Scope: `Docs/research_subset_a.md` includes `sources/os/illumos/illumos-gate`.
- File role: embedded Emulex LPe11002 Fibre Channel adapter firmware image header, not normal illumos host driver source.
- Enclosing artifact: `static uint8_t emlxs_lpe11002_image[]`, emitted only when `EMLXS_FW_IMAGE_DEF` is defined.
- Firmware identity from file context: `LPe11002-S: v2.82a4 (zf282a4.all)`.
- Chunk coverage: source lines 19925-23242, image byte rows `0x26DD8` through `0x2D580`.
- Size represented in this chunk: 3,318 rows, 26,544 image bytes.

## APIs And Host Surface

- No C functions, structs, typedefs, enums, ioctls, callbacks, or illumos kernel interfaces are declared in this range.
- The host-visible surface is only the continuation of `emlxs_lpe11002_image[]`.
- `emlxs_fw.h` includes `fw_lpe11002.h` when building the firmware table and associates this image with `LPe11002_FW`, `emlxs_lpe11002_size`, `emlxs_lpe11002_label`, and SLI/kern/stub entry constants.
- Driver code should treat this range as opaque firmware data. Source-level call graph tools will see an initializer, while the adapter executes the bytes as firmware.

## Firmware Control Flow

- The range starts mid-routine at `0x26DD8`; adjacent context shows the prior chunk already executing firmware instructions and branches into this chunk.
- The bytes are ARM-like executable firmware mixed with literal pools and strings. Common patterns include conditional branches, `BL`-style helper calls, register loads/stores, table dispatches, and returns.
- Early code around `0x26DD8`-`0x27218` updates fixed-offset fields and uses a compact branch table beginning near `0x26F58`, suggesting command/status decoding inside an existing firmware state machine.
- Code around `0x27218`-`0x275B8` manipulates queue/list-like objects: it copies blocks of words, updates head/tail/count-like fields at offsets such as `+0x20`, `+0x24`, `+0x28`, `+0x2C`, and branches on status bits.
- Mid-chunk routines compare command/status constants and ASCII-like command bytes, including visible comparisons against `0x41` (`A`), `0x43` (`C`), `0x48` (`H`), and `0x46` (`F`) around `0x279D0`-`0x27A00`.
- Literal/table data appears around `0x27B58` and other address-like rows. These rows are interleaved with executable code and are branch/literal-pool dependencies, not removable padding.
- Later code around `0x2A000`-`0x2A388` constructs or updates command descriptor fields, status bytes, and control flags, with repeated writes to offsets including `+0x06`, `+0x07`, `+0x08`, `+0x0A`, `+0x0C`, `+0x10`, `+0x14`, `+0x1C`, `+0x24`, `+0x26`, `+0x27`, `+0x28`, `+0x40`, `+0x44`, and `+0x64`.
- Near the end, routines around `0x2D008`-`0x2D580` expose login-management diagnostics. Embedded strings include `REG_LOGIN %02x %06x` and `UNREG_LOGIN %02x`, indicating firmware paths for registering and unregistering login/RPI-like state.

## State And Data Dependencies

- Host-side state is immutable image bytes and file-level metadata outside the chunk.
- Firmware-side state is opaque adapter memory. Visible fixed-offset loads/stores imply per-command, per-exchange, queue, port/login, and hardware-status structures.
- The chunk depends on firmware address/layout contracts from the whole `emlxs_lpe11002_image[]`; branch targets and literal references cross both previous and next chunk boundaries.
- Runtime dependencies include the LPe11002 on-adapter processor, its memory map/registers, Fibre Channel link/login state, and the SLI firmware ABI expected by the `emlxs` driver.

## Risks

- Any byte-level edit can break firmware instruction alignment, branch targets, literal pools, embedded diagnostics, or hardware register programming.
- Apparent data rows, strings, zero-like values, and address-like constants may be referenced by nearby instructions; they cannot be classified as unused from this chunk alone.
- The visible login/register paths suggest direct manipulation of fabric/session identity state. Corruption here could surface as link login failures, stale RPI mappings, or adapter hangs rather than host-side compile errors.
- Source-level tests cannot validate this code path. Meaningful validation requires firmware image integrity checks and adapter/driver runtime testing.

## Cross-Chunk References

- Previous chunk 6 covers lines 16607-19924 and ends at byte row `0x26DD0`; this chunk begins at `0x26DD8` in the same control-flow region.
- Next chunk 8 covers lines 23243-26560 and begins at byte row `0x2D588`; this chunk ends mid-routine at `0x2D580`.
- Final per-file merge should preserve this as one contiguous opaque firmware image tied to the LPe11002 metadata and not infer independent C APIs from this chunk.