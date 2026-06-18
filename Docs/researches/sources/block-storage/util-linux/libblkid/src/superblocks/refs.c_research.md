# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/refs.c

## Scope

Declares static libblkid detection metadata for Microsoft ReFS.

## Behavior

- Registers filesystem name `ReFS`.
- Uses an 8-byte magic containing leading NULs and `ReFS`.

## Dependencies And Risks

- No probefunc exists, so detection depends entirely on the magic table.
- It exports only type/usage/magic-level information, not label, UUID, size, or block size.
