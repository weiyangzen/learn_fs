# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/enum.h

## Purpose
Declares small utilities for mapping numeric values/bitfields to printable names.

## Important APIs, Types, And Functions
Defines `struct nvkm_enum`, `nvkm_enum_find`, `struct nvkm_bitfield`, and `nvkm_snprintbf`.

## Control Flow
`nvkm_enum_find` searches a sentinel-terminated enum table. `nvkm_snprintbf` formats names for set bits from a bitfield table.

## State And Persistence
No persistent state; table data is caller-owned static data.

## Dependencies And Integration Points
Depends on core OS helpers and is used in debug logging, register decoding, and status reporting.

## Risks
Tables must be correctly terminated and masks non-overlapping when expected. Buffer sizing matters for formatted bitfields.

## Test Signals
Register decode logs, enum lookup tests, and truncation-safe formatted output validate behavior.
