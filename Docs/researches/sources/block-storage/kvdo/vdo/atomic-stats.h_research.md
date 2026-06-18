# File Research: sources/block-storage/kvdo/vdo/atomic-stats.h

## Purpose

Defines atomic statistics counters for VDO bio and metadata I/O accounting.

## Contents

- `struct atomic_bio_stats`
  - read,
  - write,
  - discard,
  - flush,
  - empty flush,
  - FUA.
- `struct atomic_statistics`
  - submitted/completed bio counts,
  - flush output,
  - invalid advice,
  - no-space errors,
  - read-only errors,
  - categorized atomic bio stat groups for incoming, outgoing, metadata, journal, and page-cache I/O.

## Dependencies and Role

Uses Linux `atomic64_t` because updates may come from arbitrary concurrent threads.
