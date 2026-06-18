# File Research: sources/block-storage/lvm2/lib/id/id.h

## Summary
Declares LVM ID and logical-volume ID structures and helper APIs.

## Main Contents
Defines `ID_LEN` as 32, `struct id` as a 32-byte UUID-like printable identifier, and `union lvid` as two IDs plus string padding for historical format compatibility.

## API Surface
Declares LVID creation, ID creation, validation, equality, formatted write/read, quiet parse try, and pool-backed format-and-copy.

## Risks And Invariants
`union lvid` layout preserves older format expectations. Consumers should use helper functions rather than assuming C-string semantics for raw `struct id`.
