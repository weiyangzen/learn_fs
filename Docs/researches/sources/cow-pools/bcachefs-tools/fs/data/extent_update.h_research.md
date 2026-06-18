# File Research: sources/cow-pools/bcachefs-tools/fs/data/extent_update.h

Declares atomic extent trimming API.

Key responsibilities:
- Exposes `bch2_extent_trim_atomic()` for btree transaction update code.

Important interactions:
- Used where extent insert/update operations need to stay within transaction iterator limits.
