# sources/cloud-native/containers-storage/utils.go

Purpose: top-level storage package utility wrappers and small validation/name-list helpers.

Important APIs and control flow: `ParseIDMapping` delegates to `types.ParseIDMapping`, preserving the public package API. `DefaultStoreOptions` delegates to `types.DefaultStoreOptions`. `validateMountOptions` rejects unsupported image mount options, currently `rw`. `applyNameOperation` implements `setNames`, `removeNames`, and `addNames`, then deduplicates results; unknown operations return `errInvalidUpdateNameOperation`.

State and persistence: no persistent state. Name operations return new slices and do not mutate the old list in place.

Dependencies and integration: bridges callers of the root `storage` package to the `types` package. `applyNameOperation` integrates with name update flows elsewhere in the package and depends on operation constants plus `dedupeStrings`.

Risks: `addNames` prepends new names before old names, so ordering is semantically significant. `validateMountOptions` matches exact strings only; option variants or comma-composed values must be normalized before calling.

Test signals: indirect tests should cover name update operations and mount option rejection; no direct tests are in this subset.
