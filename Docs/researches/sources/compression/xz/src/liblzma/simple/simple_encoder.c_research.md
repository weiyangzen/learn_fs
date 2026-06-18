# sources/compression/xz/src/liblzma/simple/simple_encoder.c

## Purpose
Encodes serialized BCJ/simple filter properties and reports their encoded size.

## Important APIs, Types, And Functions
- `lzma_simple_props_size()` returns 0 for default/no options or 4 for nonzero start offset.
- `lzma_simple_props_encode()` writes little-endian start offset when nonzero.

## Control Flow
Both functions inspect `options` as `lzma_options_bcj`. Default NULL or zero offset produces no property bytes. Nonzero offset writes four bytes.

## State And Persistence
No persistent state. Writes caller-provided output buffer.

## Dependencies And Integration Points
Includes `simple_encoder.h`, uses `write32le()`. Used by filter property serialization.

## Risks
Callers must provide a large enough `out` buffer when size is 4. Start offset alignment is validated later by `lzma_simple_coder_init()`, not here.

## Test Signals
Property size/encode tests for NULL, zero, and nonzero offsets; decode symmetry with `simple_decoder.c`.
