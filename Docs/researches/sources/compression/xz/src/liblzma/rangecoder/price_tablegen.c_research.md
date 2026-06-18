# sources/compression/xz/src/liblzma/rangecoder/price_tablegen.c

## Purpose
Standalone C generator for `price_table.c`.

## Important APIs, Types, And Functions
- `init_price_table()` computes prices for each reduced probability bucket.
- `print_price_table()` emits the C source containing `lzma_rc_prices`.
- `main()` initializes and prints the table.

## Control Flow
The generator defines `BUILDING_PRICE_TABLEGEN` to avoid normal liblzma dependencies, includes `range_common.h` and `price.h`, computes the table with repeated squaring/bit counting, and prints formatted C source with a split SPDX string.

## State And Persistence
Uses a local static `rc_prices` array during generation. Output is persisted by redirecting stdout when regenerating the committed table.

## Dependencies And Integration Points
Depends only on standard `<inttypes.h>`, `<stdio.h>`, and range/price constants. Listed in `EXTRA_DIST`.

## Risks
Generator and committed table can drift. The generator relies on constants from headers; changing price constants requires regenerating and reviewing output. Since it includes `price.h`, declaration of `lzma_rc_prices` is made harmless by stub visibility macros.

## Test Signals
Build and run generator, compare output against `price_table.c`, and compile generated output. Dist checks should include this source.
