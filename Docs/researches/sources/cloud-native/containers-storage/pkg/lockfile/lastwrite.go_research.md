# sources/cloud-native/containers-storage/pkg/lockfile/lastwrite.go

Purpose: defines the opaque `LastWrite` token stored in lock files to detect changes to protected state across goroutines and processes.

Important APIs, types, and functions: `LastWrite`, `newLastWrite`, `serialize`, `equals`, `newLastWriteFromData`, `lastWriterIDCounter`, and `lastWriterIDSize`.

Control flow: `newLastWrite` builds a 64-byte token from current time, an atomic per-process counter, PID, and random bytes. `serialize` and `equals` panic on uninitialized values to enforce opaque value semantics. `newLastWriteFromData` wraps bytes read from a lock file.

State and persistence: tokens are persisted as raw lock-file contents by OS-specific `RecordWrite`. In-process state includes the atomic counter used to reduce collision risk.

Dependencies and integration points: depends on `bytes`, `crypto/rand`, `encoding/binary`, `os`, `sync/atomic`, and `time`. It integrates with `LockFile.GetLastWrite`, `RecordWrite`, and `ModifiedSince`.

Risks and edge cases: random failure panics. `newLastWriteFromData` does not copy the slice, so callers should not mutate the source bytes. Equality ignores semantic structure and compares raw bytes.

Test signals: lockfile tests exercise `RecordWrite`, `GetLastWrite`, `Modified`, and `ModifiedSince`, indirectly validating token uniqueness and comparison.
