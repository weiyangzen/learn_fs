# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lpe11002.h lines 3335-6652

## Scope

This report covers only lines 3335-6652 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/fw_lpe11002.h` in learn_fs subset A (`Docs/research_subset_a.md`). The range is a contiguous slice of the generated `emlxs_lpe11002_image[]` firmware byte array, spanning image offsets roughly `0x06768` through `0x0CF17`. Adjacent context was used only to identify the header-level firmware contract and the chunk boundaries.

This is not ordinary C source logic. The bytes are ARM-style firmware instructions, literal pools, jump tables, register constants, and embedded diagnostic strings for the Emulex LPe11002 Fibre Channel adapter.

## APIs And Exported Data

No C functions, structs, enums, or callable symbols are declared inside this chunk. Its public surface is the surrounding header-level firmware image API:

- `emlxs_lpe11002_label` identifies the blob as `LPe11002-S: v2.82a4 (zf282a4.all)`.
- `emlxs_lpe11002_kern`, `emlxs_lpe11002_stub`, and `emlxs_lpe11002_sli1` through `emlxs_lpe11002_sli4` provide firmware entry/version addresses.
- `emlxs_lpe11002_image[]` is emitted only under `EMLXS_FW_IMAGE_DEF`; otherwise the header defines image and size as zero.
- `emlxs_lpe11002_size` is the full array size, not a size for this chunk.

The host driver includes this header through `emlxs_fw.h`, where the image pointer, size, label, and entry/version constants are placed into the firmware table for LPe11002 devices.

## Visible Firmware Control Flow

The chunk starts in the middle of firmware instructions. Early bytes include lower-case hexadecimal formatting data (`0123456789abcdef`, `0x`) immediately after nearby upper-case formatting data in the previous chunk, then continue into output/conversion helpers and byte/word loops. Around offsets `0x06D30` and later, repeated load/store/compare patterns look like low-level string, memory copy, memory compare, or memory set helpers. These are inferred from instruction shape and table/string context; no symbols are present.

Around `0x07B18`, the firmware manipulates table-like state indexed by small counts, often 16 entries. Literal offsets such as `0x04F0`, `0x0530`, `0x0794`, and register/status offsets such as `0x0140` appear in routines that read status words, test masks, update per-slot entries, and call helper routines outside the chunk.

Around `0x09800`, a command/state dispatcher compares a command value against multiple cases and then enters a dense branch table. Nearby routines implement diagnostic output by converting nibbles to ASCII and issuing a software-interrupt-like instruction pattern (`EF 00 00 02`), suggesting firmware console/debug output.

Around `0x09B70` through `0x09D88`, the code enters self-test or error-reporting paths. Embedded strings include `Error bits in ERRCLR cannot be cleared`, `Address`, `Expected`, `Actual`, and `Error bits`. The surrounding code writes or polls apparent hardware control/status registers, captures expected and actual values, and formats failures.

Around `0x0A458`, the chunk handles table-driven tests or commands with stack-resident offset/length bookkeeping, counters, and a larger branch table starting near `0x0A680`. The visible paths call helpers, update a global/control word, and continue into pattern-specific handlers.

Around `0x0AE30` through `0x0B0A0`, the firmware performs pattern generation and verify-style logic. It loops over generated values, writes and reads target locations, and reports mismatches. Embedded diagnostics include `Unknown pattern generation code`, `Error for`, `Expected reset value:`, `Wrote:`, `Read:`, and `Error bits:`.

Around `0x0BFB0` through at least `0x0C8C0`, repeated hardware handshakes are visible. The code toggles a control register at offset `0x3C`, writes command/status bytes such as `0xB0`, `0xD0`, `0x70`, and `0x20`, polls bits including `0x80`, `0x40`, and `0x20`, and uses bounded retry counters such as `0x10` and `0x20`. Several loops branch backward until status changes or retry limits expire.

Near the end of the chunk, from roughly `0x0C9C8` through `0x0CF10`, the firmware shifts into allocator/list management. Routines compare address/length ranges, adjust fields at offsets `0x08`, `0x0C`, `0x10`, `0x14`, `0x18`, `0x1C`, and `0x20`, call free/insert helpers outside the chunk, merge adjacent ranges, and return status or a selected node pointer. The final line ends mid-routine.

## State And Data Dependencies

All C-visible state in this chunk is immutable firmware bytes. Runtime state exists only after the adapter executes the image. Visible firmware state includes:

- Embedded format tables and diagnostic strings.
- Literal pools containing firmware memory/register offsets.
- Apparent per-slot arrays indexed up to 16 entries.
- Hardware status/control bits at offsets such as `0x0140`, `0x03C`, and `0x144`.
- Stack-local bookkeeping for command dispatch, test offsets, expected/actual values, and retry counts.
- Queue/free-list style nodes with range metadata and link/status fields.

The blob depends on exact byte order, 8-byte alignment from the surrounding header, and exact preservation of branch offsets and literal pool placement.

## External Dependencies

The host-side dependency is the `emlxs` firmware loader path: `emlxs_fw.h` includes this header and exposes the full image to the driver firmware table. The chunk itself has no source-level include dependencies beyond being part of the static `uint8_t` initializer.

At runtime, the bytes depend on the LPe11002 adapter CPU, its on-card memory map, SLI/Fibre Channel firmware conventions, and device registers used by the firmware. Many calls and branches target code outside this line range, so the chunk cannot be executed or validated in isolation.

## Risks And Correctness Notes

- Any byte edit can corrupt firmware instructions, branch targets, literal addresses, jump tables, or embedded diagnostics.
- Source-level C tooling cannot reason about this chunk beyond array syntax, alignment, and size.
- The visible polling loops and hardware handshakes could hang or mis-detect device state if surrounding firmware state or register semantics are wrong.
- The self-test paths show explicit checks for un-clearable error bits and expected/read mismatches, but their full recovery behavior crosses chunk boundaries.
- The allocator/range-merging logic at the end is sensitive to field layout and ordering; off-by-one or range corruption would likely affect firmware memory/resource management.
- Version coupling is high. The bytes must match the `LPe11002-S: v2.82a4` metadata and the driver table entries that load this exact firmware.

## Cross-Chunk References

- The chunk begins mid-routine at line 3335; prior lines contain adjacent uppercase hex formatting data and the start of the current formatter/control path.
- Branches and calls throughout this range target helpers before line 3335 and after line 6652.
- The branch table around `0x09870` dispatches to earlier code in this chunk and to routines outside it.
- The larger command/test dispatch table around `0x0A680` continues into handlers later in this chunk and beyond it.
- The final lines at `0x0CF10` end inside another list/range-management routine, which continues in the next chunk.