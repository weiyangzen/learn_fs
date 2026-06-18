<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/auth.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/util/auth.go

Purpose: derives the 64-bit BeeMsg authentication secret from arbitrary input bytes.

Important APIs/types/functions: `GenerateAuthSecret` hashes input with SHA-256 and returns the first eight hash bytes interpreted as little-endian `uint64`.

Control flow: single-pass hash and byte conversion.

State and persistence: no state; deterministic pure function.

Dependencies and integration points: depends on `crypto/sha256` and `encoding/binary`. `ConnectTCP` uses an already-derived secret to send `AuthenticateChannel`; this helper likely feeds configuration parsing or secret setup elsewhere.

Risks: compatibility depends on matching other BeeGFS implementations' little-endian truncation. No salt/stretching is performed; this is protocol derivation, not password storage.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/auth.go -->
