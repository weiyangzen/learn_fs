# File Research: sources/block-storage/stratisd/src/engine/strat_engine/metadata/static_header.rs

## Purpose

`static_header.rs` implements Stratis static signature-block metadata. It reads, writes, repairs, parses, and wipes the two redundant static headers at the start of each Stratis member device.

## Main Responsibilities

- Encode and decode the Stratis signature block.
- Store pool UUID, device UUID, block device size, sigblock version, MDA size, reserved size, and initialization time.
- Read both redundant signature blocks independently.
- Repair missing, stale, unreadable, or corrupted copies when a valid peer exists.
- Distinguish non-Stratis devices from corrupted Stratis devices.
- Wipe Stratis identifying information from the static-header region.

## Key Constants

- `RESERVED_SECTORS`: 3 MiB of reserved space.
- `STRAT_MAGIC`: Stratis magic bytes.
- CRC algorithm: CRC-32C iSCSI/Castagnoli.
- Static header layout constants come from `sizes::static_header_size`.

## Key Types

- `StaticHeaderResult`
  - Holds read bytes or read error plus optional parsed header result.
  - Invariant: read error means no parsed header.
- `MetadataLocation`
  - `Both`, `First`, `Second`.
- `StratisIdentifiers`
  - Pool UUID and device UUID.
- `StaticHeader`
  - block device size, sigblock version, identifiers, MDA size, reserved size, flags, initialization time.

## Public Functions

- `device_identifiers()` reads and repairs sigblocks, then returns identifiers.
- `static_header()` reads and repairs sigblocks, then returns the full header.
- `disown_device()` wipes the static header region.

## Important Methods

- `StaticHeader::new()` builds a header and truncates initialization time to whole seconds.
- `read()` reads both sigblock sectors separately.
- `write()` writes one or both static-header regions, including zeroed padding and `sync_all()`.
- `bda_extended_size()` returns BDA plus reserved space.
- `read_sigblocks()` returns bytes plus parse results for both locations.
- `write_header()` is the repair callback that writes a header.
- `do_nothing()` is a repair callback for read-only validation behavior.
- `repair_sigblocks()` reconciles the two sigblock reads.
- `sigblock_to_buf()` serializes the signature block and writes its CRC.
- `sigblock_from_buf()` validates magic, CRC, version, UUIDs, sizes, and timestamp.
- `wipe()` zeroes the full static-header region.

## Repair Semantics

If both sigblocks parse successfully:

- Equal headers are accepted.
- Different initialization times choose the newer header and rewrite the older location.
- Same initialization time with differing contents is an error.

If one sigblock is valid and the other is missing, invalid, or unreadable:

- The valid sigblock is returned.
- The other location is repaired when the provided callback writes.

If both locations lack Stratis magic:

- Returns `Ok(None)`.

If metadata looks like Stratis but neither sigblock validates:

- Returns an error.

If neither sigblock location can be read:

- Returns an error.

## Tests

The tests verify:

- Ownership detection before write, after write, and after wipe.
- One-corrupt-copy repair.
- Both-copy corruption behavior, including magic-byte corruption treated as non-Stratis when both magic values are gone.
- Serialization round-trip of header fields.
- Rewriting older sigblocks from newer sigblocks.

## Notable Edge Cases

- The `flags` field is carried in memory but not meaningfully parsed from disk here; parsed headers set it to `0`.
- Timestamp parsing uses unsigned seconds with zero nanoseconds.
- Repair behavior is parameterized by callback, allowing no-write scans.
- Static header writes sync after each region write.
