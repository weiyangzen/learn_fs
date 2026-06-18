# sources/cloud-native/moby/daemon/internal/stringid/stringid.go

## Purpose
Provides helpers for Docker-style hexadecimal IDs: generating random full IDs and presenting short prefixes.

## Important APIs, Types, And Functions
`TruncateID` removes any algorithm prefix before `:` and returns at most 12 characters. `GenerateRandomID` reads 32 random bytes, hex-encodes them into a 64-character ID, and retries if the first 12 characters are numeric-only. `allNum` checks whether a byte string contains only ASCII digits.

## Control Flow
Random ID generation loops until the shortened hostname-safe prefix contains at least one non-digit. `rand.Read` errors panic because cryptographic randomness is expected to be available.

## State And Persistence
No state is stored. Generated IDs are returned to callers for persistence elsewhere.

## Dependencies And Integration Points
Used throughout daemon object creation and display. The numeric-prefix guard exists because truncated container IDs can become default hostnames, and all-numeric hostnames are problematic.

## Risks And Test Signals
The short length is fixed at 12 but documented as not a stable external contract. `TruncateID` does not validate hex content or uniqueness. Tests cover length, digest-prefix truncation, invalid short input, and numeric-only detection.
