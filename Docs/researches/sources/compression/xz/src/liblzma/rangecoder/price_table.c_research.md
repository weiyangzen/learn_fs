# sources/compression/xz/src/liblzma/rangecoder/price_table.c

## Purpose
Defines the generated lookup table used by `price.h` to approximate range-coder bit prices quickly.

## Important APIs, Types, And Functions
- `const uint8_t lzma_rc_prices[RC_PRICE_TABLE_SIZE]` is the only exported object, hidden by declaration attributes in `price.h`.

## Control Flow
No runtime control flow beyond table lookup by callers.

## State And Persistence
Immutable process-wide table.

## Dependencies And Integration Points
Includes `range_encoder.h`, which pulls in price and range constants. Used by LZMA encoder optimal parser and length/distance price refreshes.

## Risks
The table must match `price_tablegen.c`, `RC_MOVE_REDUCING_BITS`, and `RC_BIT_PRICE_SHIFT_BITS`. Manual edits can silently degrade compression decisions.

## Test Signals
Regenerate with `price_tablegen.c` and compare byte-for-byte. Compression-ratio tests can catch table corruption indirectly.
