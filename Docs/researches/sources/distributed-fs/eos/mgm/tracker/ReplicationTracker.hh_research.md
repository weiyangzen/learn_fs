# sources/distributed-fs/eos/mgm/tracker/ReplicationTracker.hh

## Purpose
Declares the replication tracker interface and its background-thread state.

## Important APIs, types, and functions
`OperationMode` distinguishes injection, creation, and access conversion policies. `Options` carries enablement, atomic cleanup age, and scan interval. Public methods include `Create()`, `Access()`, `ConversionPolicy()`, `ConversionSizePolicy()`, `Commit()`, `Validate()`, `Scan()`, `Prefix()`, `enabled()/enable()/disable()`, conversion enable/disable helpers, and `getOptions()`.

## Control flow
External MGM operations call `Create`, `Commit`, or `Access`; the tracker thread calls `getOptions()` and `Scan()`. The static `Create()` factory returns a heap-allocated tracker for legacy construction sites.

## State and persistence behavior
The header owns process-local state: an `AssistedThread`, atomic enable flags, an error object, root virtual identity, and the tracker root path. Durable tracker state is implied by namespace files under `mPath`.

## Dependencies and integration points
Depends on `AssistedThread`, `VirtualIdentity`, `IFileMD`, XRootD strings/errors, and MGM namespace macros. It is integrated with global MGM services in the implementation.

## Risks and test signals
`Validate()` is declared but empty in the implementation. Enable flags are atomics, but broader namespace work relies on external locks. Tests should exercise enable/disable idempotence, conversion flag toggling, background thread shutdown, and scan reporting via the optional output string.
