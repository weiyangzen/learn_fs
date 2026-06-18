<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/identity/randomid.go -->
# sources/cloud-native/buildkit/identity/randomid.go

Purpose: generates opaque random identifiers with low collision probability for BuildKit components.

Important APIs, types, and functions: `idReader` defaults to `crypto/rand.Reader` and is replaceable for tests. Constants define 17 bytes of entropy, base36 encoding, and fixed output length 25. `NewID()` reads random bytes, sets the high bit, converts to base36, and slices to 25 characters after dropping the leading extra-entropy character.

Control flow and state: no persistence. The only mutable package state is `idReader` for test injection. `NewID` panics if random bytes cannot be read.

Dependencies and integration: uses `crypto/rand`, `io.ReadFull`, and `math/big`. Callers should treat returned identifiers as opaque strings.

Risks and test signals: panic on entropy failure is deliberate but can crash callers in constrained environments. The string slicing depends on high-bit and entropy sizing invariants. Tests should inject deterministic readers and assert length/base36 properties.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/identity/randomid.go -->
