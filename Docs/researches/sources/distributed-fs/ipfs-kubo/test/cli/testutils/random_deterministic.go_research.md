# sources/distributed-fs/ipfs-kubo/test/cli/testutils/random_deterministic.go

Purpose: creates deterministic pseudo-random byte streams for tests that need large or exact-size data without storing fixtures.

Important APIs and types: `randomReader` holds a ChaCha20 cipher and remaining byte count. `DeterministicRandomReader(sizeStr, seed string)` parses human-readable sizes with `go-humanize`. `DeterministicRandomReaderBytes(size int64, seed string)` hashes the seed to a 32-byte key and returns a reader producing exactly `size` bytes.

Control flow: `randomReader.Read` returns EOF when no bytes remain, otherwise XORs a zero buffer through ChaCha20 into the requested slice, decreases `remaining`, and returns the number of bytes filled.

State and persistence: state is per-reader: cipher stream position and remaining bytes. No external persistence.

Dependencies and integration points: uses SHA-256 for seed-to-key derivation, `x/crypto/chacha20` for deterministic stream generation, and `go-humanize` for size strings.

Risks and test signals: zero nonce is acceptable for deterministic test data but not cryptographic use. Each reader is not concurrency-safe. Exact byte count behavior is the key signal; parse errors surface from humanize size parsing.
