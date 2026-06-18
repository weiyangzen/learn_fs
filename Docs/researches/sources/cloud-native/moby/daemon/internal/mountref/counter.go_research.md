<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/mountref/counter.go -->
# sources/cloud-native/moby/daemon/internal/mountref/counter.go

Purpose: maintains reference counts for graphdriver mount paths while accounting for paths that may already be mounted before the counter sees them.

Important APIs and types: `Counter`, `Checker`, `NewCounter`, `Increment`, `Decrement`, and internal `minfo`.

Control flow: `Increment`/`Decrement` call `incdec`, which initializes per-path state, checks `isMounted` only on first access, seeds the count if already mounted, applies the increment/decrement operation, deletes state at zero or below, and returns the current count.

State and persistence: in-memory map keyed by path; protected by mutex. Existing kernel mount state is sampled once per map entry.

Dependencies and integration: used by graphdriver Get/Put-style mount management and supplied with a mount checker.

Risks: if actual mount state changes outside the counter after first access, the counter does not recheck until state is deleted and recreated. Decrement can delete entries at zero or negative, masking extra decrements.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/mountref/counter.go -->
