# sources/compression/xz/src/liblzma/simple/simple_decoder.c

## Purpose
Decodes serialized BCJ/simple filter properties into `lzma_options_bcj`.

## Important APIs, Types, And Functions
- `lzma_simple_props_decode()` parses zero-byte or four-byte properties.

## Control Flow
If `props_size` is zero, defaults are used and it returns OK. If size is not four, it returns `LZMA_OPTIONS_ERROR`. For four bytes it allocates `lzma_options_bcj`, reads little-endian `start_offset`, frees the allocation if the offset is zero, otherwise stores it through `options`.

## State And Persistence
Allocates an options struct only for non-default start offsets. Caller owns the resulting options through liblzma allocator conventions.

## Dependencies And Integration Points
Includes `simple_decoder.h`, uses `read32le()` and allocator helpers. Used by raw/container filter property decoding for BCJ filters.

## Risks
The function assumes `*options` already represents default NULL when props are empty or offset zero; callers must initialize it appropriately. Allocation failure returns `LZMA_MEM_ERROR`.

## Test Signals
Decode empty props, four zero bytes, nonzero start offset, invalid prop lengths, and allocation-failure paths.
