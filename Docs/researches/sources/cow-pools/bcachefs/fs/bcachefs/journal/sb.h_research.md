# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/sb.h

## Role

Header for journal superblock field helpers.

## Contents

- Inline count helper for legacy journal bucket arrays.
- Inline count helper for `journal_v2` range entries.
- Declares superblock field ops for both formats.
- Declares conversion-to-superblock and sorting helpers.

## Notable Details

Both count helpers derive element counts from variable-structure boundaries using `vstruct_end()`.
