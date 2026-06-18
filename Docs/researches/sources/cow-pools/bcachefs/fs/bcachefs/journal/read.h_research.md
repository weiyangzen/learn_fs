# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/read.h

## Role

Public interface and iteration helpers for journal reading and replay-entry traversal.

## Contents

- Declares member-info journal position helpers.
- Defines `journal_replay_ignore()`.
- Provides typed jset-entry iteration helpers and key iteration macros.
- Defines `jset_datetime()` and `journal_nonce()`.
- Declares journal pointer formatting, missing-range detection, datetime formatting, rewind reread, and journal read.

## Notable Details

`journal_nonce()` derives the journal encryption/checksum nonce from the journal sequence and `BCH_NONCE_JOURNAL`.
