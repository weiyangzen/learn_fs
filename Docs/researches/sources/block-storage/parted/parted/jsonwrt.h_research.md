# File Research: sources/block-storage/parted/parted/jsonwrt.h

## Purpose

`jsonwrt.h` declares the small JSON writer API used by the `parted` frontend.

## Contents

- JSON node type enum:
  - `UL_JSON_OBJECT`,
  - `UL_JSON_ARRAY`,
  - `UL_JSON_VALUE`.
- `struct ul_jsonwrt` with output stream, indentation level, and `after_close` state.
- Core functions:
  - initialize,
  - indent,
  - open,
  - close.
- Convenience macros for root/object/array/value open and close operations.
- Value writer declarations for raw, string, u64, boolean, and null values.

## Dependencies and Role

The header assumes `FILE` and `uint64_t` are available through includers or previous includes. It is a frontend-local formatting API rather than a general libparted API.
