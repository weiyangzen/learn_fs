# File Research: sources/block-storage/lvm2/lib/id/id.c

## Summary
Implements LVM ID generation, validation, comparison, formatting, parsing, and pool-backed formatted copies.

## Main Responsibilities
- Generates 32-byte IDs from `/dev/urandom`, mapping bytes into LVM’s printable character alphabet while avoiding the final two characters for LVM1 compatibility.
- Creates LVIDs by combining a VG ID with a newly generated LV ID.
- Validates IDs by checking each character against the allowed alphabet.
- Formats IDs into the standard dashed 6-4-4-4-4-4-6 grouping.
- Parses formatted IDs by stripping dashes, enforcing exact length, and validating characters.

## Important Behavior
IDs beginning with `#` are copied as-is in `id_write_format()`, which preserves a special legacy/internal representation path.

## Risks And Invariants
The ID validity check has no checksum, so corruption that preserves allowed characters is not detected. Formatting assumes `ID_LEN == 32` and requires at least 39 bytes including the terminator.
