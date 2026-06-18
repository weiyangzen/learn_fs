# sources/distributed-fs/ipfs-kubo/test/cli/testutils/floats.go

Purpose: numeric helper for truncating floating-point values to a fixed number of decimal places in tests.

Important API: `FloatTruncate(value float64, decimalPlaces int) float64` computes `10^decimalPlaces`, multiplies the value, casts to `int`, then divides back.

Control flow: a simple loop multiplies `pow` by 10 for each decimal place. Truncation is toward zero because of the `int` conversion.

State and persistence: no state.

Dependencies and integration points: no imports. Useful for tests that need deterministic formatting or approximate numeric comparisons without rounding.

Risks and test signals: negative values truncate toward zero, not toward negative infinity. Large values or high decimal places may lose precision or overflow `int`. Callers should avoid using this for production numeric correctness.
