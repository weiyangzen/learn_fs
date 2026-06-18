# sources/cloud-native/moby/internal/namesgenerator/names-generator_test.go

## Purpose
Tests and benchmarks random name formatting behavior.

## Important APIs, Types, And Functions
- `TestNameFormat` calls `GetRandomName(0)` and checks underscore plus no digits.
- `TestNameRetries` calls `GetRandomName(1)` and checks underscore plus a digit.
- `BenchmarkGetRandomName` repeatedly calls `GetRandomName(5)` and reports allocations.

## Control Flow
The tests perform a single random generation each and assert string properties with `strings.Contains`/`ContainsAny`. The benchmark stores the last result to keep the call observable.

## State And Persistence
No persistent state beyond global random source advancement during tests.

## Dependencies And Integration Points
Uses standard `strings` and `testing`. Covers `internal/namesgenerator` public function.

## Risks And Edge Cases
Because generation is random, the tests verify format properties rather than exact values. They do not explicitly test the disallowed `boring_wozniak` combination or collision rates.

## Test Signals
Passing confirms generated names contain an underscore, retry-zero names do not include digits, retry-positive names include a digit, and the benchmark can run without allocations surprises being hidden.
