# File Research: sources/block-storage/lvm2/tools/pvmove_poll.h

## Purpose

`pvmove_poll.h` declares the pvmove-specific polling callbacks used by `pvmove.c` and implemented in `pvmove_poll.c`.

## Contents

- Include guard: `LVM_PVMOVE_POLL_H`.
- Forward declarations for:
  - `struct cmd_context`
  - `struct dm_list`
  - `struct logical_volume`
  - `struct volume_group`
- Function declarations:
  - `pvmove_update_metadata()`
  - `pvmove_finish()`

## Role in the Module

This header is the narrow interface between pvmove setup/orchestration and pvmove poll completion logic. It avoids exposing implementation details from `pvmove_poll.c`.
