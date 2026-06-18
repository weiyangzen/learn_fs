# sources/compression/xz/src/liblzma/rangecoder/price.h

## Purpose
Provides inline probability price calculations used by LZMA optimal parsing and price-table refresh logic.

## Important APIs, Types, And Functions
- Constants: `RC_MOVE_REDUCING_BITS`, `RC_BIT_PRICE_SHIFT_BITS`, `RC_PRICE_TABLE_SIZE`, and `RC_INFINITY_PRICE`.
- External table `lzma_rc_prices`.
- `rc_bit_price()`, `rc_bit_0_price()`, and `rc_bit_1_price()` map probabilities/bits to fixed-point prices.
- `rc_bittree_price()` and `rc_bittree_reverse_price()` compute prices for normal and reverse bit trees.
- `rc_direct_price()` prices unmodeled direct bits.

## Control Flow
All functions are inline arithmetic over probability tables. Bit-tree price functions walk from symbol to root or from root to leaves, summing individual bit prices.

## State And Persistence
No mutable state. Uses the generated immutable `lzma_rc_prices` table.

## Dependencies And Integration Points
Requires range-coder constants and `probability` from `range_common.h`; included by `range_encoder.h` and optimal parser code.

## Risks
Price scale constants must match `price_table.c` generation and parser assumptions. Incorrect indexing can bias optimal parsing. `RC_INFINITY_PRICE` must be safely above realistic path costs without overflowing additions.

## Test Signals
Price-table generation comparison, parser round trips, compression-ratio benchmarks, and unit checks for bit-tree price symmetry are useful.
