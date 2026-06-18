# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/reiserfs.c

## Scope

Implements ReiserFS v3 and Reiser4 filesystem probing.

## Behavior

- ReiserFS validates minimum block size and rejects superblocks that appear inside the journal.
- Exports label/UUID only for newer v3.6/JR signatures, and sets version `3.5`, `3.6`, or `JR`.
- Reiser4 reads its own layout, derives block size from a 256-byte multiplier, validates minimum 512 bytes, and exports label, UUID, and version `4`.
- Both set filesystem block size and block size.

## Dependencies And Risks

- Multiple ReiserFS magic offsets cover legacy layouts.
- Journal-position validation prevents accidental matches on journal copies.
- Reiser4’s compact block-size encoding is trusted after the minimum guard.
