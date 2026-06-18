# sources/cloud-native/containers-storage/pkg/stringid/stringid_test.go

Purpose: tests identifier generation, truncation, and short-ID recognition.

Important APIs, types, and functions: `TestGenerateRandomID`, `TestGenerateNonCryptoID`, `TestShortenId`, `TestShortenSha256Id`, `TestShortenIdEmpty`, `TestShortenIdInvalid`, `TestIsShortIDNonHex`, and `TestIsShortIDNotCorrectSize`.

Control flow: tests call generators and check 64-character length, call `TruncateID` with full, prefixed, empty, and already-short strings, and verify invalid short-ID cases.

State and persistence: no persistence. Generator tests consume randomness and the global non-crypto RNG.

Dependencies and integration points: depends on `strings` and `testing`. It validates behavior for storage ID display and validation helpers.

Risks and edge cases: tests do not validate `ValidateID`, all-numeric truncated rejection, uniqueness, uppercase rejection, or collision behavior.

Test signals: confirms core display truncation and basic generated ID shape.
