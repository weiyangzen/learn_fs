# sources/cloud-native/containers-storage/pkg/stringid/stringid.go

Purpose: generates, truncates, and validates 64-character hex identifiers used for images and storage objects.

Important APIs, types, and functions: `IsShortID`, `TruncateID`, `GenerateRandomID`, `GenerateNonCryptoID`, `ValidateID`, private `generateID`, `readerFunc`, regex globals, and private pseudo-random generator state.

Control flow: `generateID` reads 32 bytes from a reader, hex-encodes them, rejects IDs whose 12-character truncation parses as a decimal integer, and retries. Crypto generation uses `crypto/rand.Reader`; non-crypto generation uses a locked private `math/rand.Rand` seeded with crypto randomness or time. `TruncateID` strips a prefix before `:` and returns at most 12 characters.

State and persistence: no persistence. Global `rng` and `rngLock` maintain non-crypto random sequence state.

Dependencies and integration points: depends on crypto, encoding, math/rand, strings, sync, time, and delayed regex wrapper. Used by storage object ID generation and validation.

Risks and edge cases: `GenerateNonCryptoID` is not cryptographically secure despite crypto seeding. `generateID` panics on reader failure. Validation only accepts lowercase 64-hex strings. Short ID collisions remain possible.

Test signals: `stringid_test.go` covers generated lengths, truncation of raw and `sha256:` IDs, empty/short truncation, and short-ID validation negatives.
