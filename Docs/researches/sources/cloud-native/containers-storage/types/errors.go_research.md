# sources/cloud-native/containers-storage/types/errors.go

Purpose: central sentinel error definitions for storage-layer, image, container, metadata, read-only, user namespace, and integrity-check failure modes.

Important APIs and control flow: exports package variables such as `ErrContainerUnknown`, `ErrDuplicateID`, `ErrIncompleteOptions`, `ErrStoreIsReadOnly`, `ErrInvalidMappings`, `ErrNoAvailableIDs`, and many layer/image/container integrity errors. There is no control flow; callers compare or wrap these values with `errors.Is` semantics.

State and persistence: no mutable state. The values are process-wide sentinels created with `errors.New`.

Dependencies and integration: used across the storage library as stable error contracts between stores, drivers, repair/check flows, and callers. Integrity errors are especially important for health-check or repair code that needs distinguishable failure classes.

Risks: because exported variables are mutable package variables, external code could technically reassign them, though Go convention treats them as constants. Message text becomes part of operator-facing diagnostics, so changing text may affect tests or integrations that match strings.

Test signals: direct tests are not in this file; coverage is indirect through storage operations, delete paths, lookup failures, read-only stores, and consistency checks.
