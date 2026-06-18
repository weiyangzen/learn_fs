# File Research: sources/block-storage/kvdo/vdo/buffer.h

## Purpose

Declares the rolling buffer structure and marshalling helper API.

## Contents

- `struct buffer`
  - `start`,
  - `end`,
  - `length`,
  - `data`,
  - `wrapped`.
- Construction/destruction APIs.
- Space/content query APIs.
- Position manipulation APIs.
- Byte and buffer copy APIs.
- Boolean and little-endian integer get/put APIs.

## Role

Used by metadata format encoders/decoders such as block map state serialization.
