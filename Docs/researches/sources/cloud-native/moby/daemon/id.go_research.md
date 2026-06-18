<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/id.go -->
# sources/cloud-native/moby/daemon/id.go

Purpose: owns the daemon engine ID file lifecycle.

Important APIs and control flow: `LoadOrCreateID(root)` reads `<root>/engine-id`; if missing, it generates a UUID and writes it with `atomicwriter.WriteFile` mode `0600`; otherwise it returns the file contents. Errors are wrapped with path or save context.

State and persistence: persists the engine ID as a root-owned file under the daemon root. The function assumes the daemon root already exists with correct permissions.

Dependencies and integration: uses `github.com/google/uuid` for ID generation and `moby/sys/atomicwriter` for safe file replacement. The daemon uses the returned ID in system info and BuildKit identity wiring.

Risks: existing file contents are trusted verbatim; there is no UUID validation or whitespace trimming. Concurrent first-start callers could race through UUID generation, although atomic file writes limit partial-file exposure.

Test signals: no direct tests in this subset; coverage is usually daemon startup and persistence behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/id.go -->
