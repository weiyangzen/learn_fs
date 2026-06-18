# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_ids.c

## Purpose
`nand_ids.c` is the raw NAND static identification database. It contains legacy, extended-ID, and selected full-ID NAND descriptors plus the manufacturer-ID table that connects manufacturer IDs to optional manufacturer operations.

## Important APIs, types, and functions
- `nand_flash_ids[]` is the exported chip table consumed by `nand_detect()` when no controller-specific table is supplied.
- Full-ID entries describe devices whose shared device IDs are not sufficient; they include exact ID byte arrays, geometry, options, ID length, OOB size, and ECC requirements.
- `LEGACY_ID_NAND()` and `EXTENDED_ID_NAND()` entries cover older small-page devices and density-coded large-page devices where geometry is decoded from ID bytes.
- `nand_manufacturer_descs[]` maps manufacturer constants such as AMD/Spansion, ESMT, Hynix, Macronix, Micron, Samsung, SanDisk, Toshiba, and others to names and optional `nand_manufacturer_ops`.
- `nand_get_manufacturer_desc(u8 id)` linearly searches the descriptor table and returns a matching manufacturer descriptor or `NULL`.

## Control flow
During `nand_detect()`, the raw NAND core reads ID bytes, stores the manufacturer descriptor from `nand_get_manufacturer_desc()`, and walks `nand_flash_ids[]`. Full-ID entries are tried first, which lets the core match specific incompatible devices before falling back to generic device-ID entries. If no fixed-size table entry fully identifies the chip, the core tries ONFI, JEDEC, and manufacturer-specific extended-ID decoding.

## State and persistence behavior
This file is static data plus one lookup function. It does not allocate memory, mutate runtime state directly, or persist anything. Its descriptors indirectly determine runtime geometry, ECC requirements, options such as bus width or scrambling, and manufacturer hook selection during scan.

## Dependencies and integration points
It depends on `internals.h` for NAND descriptor macros, constants, and manufacturer ops declarations. It integrates with `nand_base.c` identification, ONFI/JEDEC fallback logic, and manufacturer-specific files such as ESMT and Hynix. The descriptor order is part of behavior: full-ID devices must precede generic shared-ID entries.

## Risks and edge cases
- Incorrect geometry, OOB size, or ECC requirement data in a table entry can cause destructive misaddressing or insufficient ECC.
- Adding a generic entry before a more specific full-ID entry could prevent the specific match.
- Manufacturer descriptors without ops still provide names but leave decoding to generic mechanisms.
- Full-ID entries using `NAND_NEED_SCRAMBLING` or high ECC requirements are board-critical; omitting these options can produce unreliable reads.

## Test signals
Tests should verify full-ID precedence, fallback to legacy/extended-ID entries, manufacturer descriptor lookup for known and unknown IDs, detection with a controller-provided alternate table, and probe logs/geometry for the listed special devices. Static build coverage should catch missing manufacturer ops declarations when descriptors reference vendor hooks.
