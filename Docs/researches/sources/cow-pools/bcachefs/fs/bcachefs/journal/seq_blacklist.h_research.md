# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/seq_blacklist.h

## Role

Public interface for journal sequence blacklist operations.

## Contents

- Defines `blacklist_nr_entries()` for variable-size superblock fields.
- Declares next-blacklisted, next-nonblacklisted, membership, last-blacklisted, add, initialize, field ops, and GC helpers.

## Notable Details

Membership checks support a `dirty` parameter, letting callers mark blacklist ranges still actively needed by observed btree state.
