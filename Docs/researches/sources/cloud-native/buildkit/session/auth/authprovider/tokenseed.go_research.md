<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/authprovider/tokenseed.go -->
# sources/cloud-native/buildkit/session/auth/authprovider/tokenseed.go

Purpose: persists per-registry random client token seeds used to derive token authority keys.

Important APIs, types, and functions: `tokenSeeds` stores a mutex, directory, and in-memory host-to-seed map. `seed` wraps seed bytes. `(*tokenSeeds).getSeed(host)` creates the config dir, locks `.token_seed.lock` when possible, reads `.token_seed`, unmarshals seeds, creates a new seed if missing, writes the map with mode 0600, and returns the host seed. `newSeed` returns 16 random bytes.

Control flow and state: state is both in memory and persisted as JSON under Docker config dir. File locking is best-effort: read-only or permission failures are tolerated for lock/write but most other errors fail.

Dependencies and integration: uses `gofrs/flock`, `crypto/rand`, JSON, and Docker config dir from auth provider. `authprovider.getAuthorityKey` consumes seeds for HMAC key derivation.

Risks and test signals: `rand.Read` error is ignored in `newSeed`. If write fails due to read-only or permission issues, new seeds are returned but may not persist, changing token authority across runs. Tests should cover lock failure tolerance, corrupt JSON recovery, permissions, and seed stability.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/authprovider/tokenseed.go -->
