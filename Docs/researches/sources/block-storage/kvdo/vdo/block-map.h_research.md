# File Research: sources/block-storage/kvdo/vdo/block-map.h

## Purpose

Defines the runtime block map structures and top-level block map API.

## Contents

- `struct block_map_tree_zone`
  - dirty lists,
  - active lookup count,
  - loading page lock map,
  - VIO pool,
  - flusher and flush waiters,
  - generation tracking.
- `struct block_map_zone`
  - zone/thread identity,
  - owning block map,
  - read-only notifier,
  - leaf page cache,
  - tree zone,
  - admin state.
- `struct block_map`
  - action manager,
  - root origin/count,
  - era points,
  - entry count,
  - nonce,
  - recovery journal,
  - current and next forests,
  - zone count and flexible zone array.
- Declares decode, drain, resume, grow, record, initialize, lookup, update, read/write mapping, and stats APIs.

## Role

This header is the central block-map contract for data VIO processing, recovery, layout metadata, and administrative control.
