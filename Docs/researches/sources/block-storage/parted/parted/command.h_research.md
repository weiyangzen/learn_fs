# File Research: sources/block-storage/parted/parted/command.h

## Purpose

`command.h` declares the `Command` structure and command helper functions for the `parted` frontend.

## Contents

- `Command` fields:
  - `names`,
  - `method`,
  - `summary`,
  - `help`,
  - one-bit `non_interactive` flag.
- Function declarations for create, destroy, register, lookup, name aggregation, summary/help printing, and command execution.

## Dependencies and Role

Includes `<parted/parted.h>` for `PedDevice` and `PedDisk`, and `strlist.h` for command names and documentation text. This header is the frontend’s command-dispatch contract.
