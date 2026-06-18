# sources/cloud-native/containerd/core/diff/apply/apply.go

Purpose: filesystem diff applier that reads layer content from a content provider, runs stream processors, applies the resulting tar stream to mounts, and returns the uncompressed applied-layer descriptor.

Important APIs/types: `NewFileSystemApplier`, `NewFileSystemApplierWithMountManager`, `fsApplier.Apply`, `readCounter`, `progressReader`, and read closer adapters.

Control flow and state: `Apply` gathers `diff.ApplyConfig`, opens content `ReaderAt`, wraps progress if requested, builds a processor chain using the descriptor media type, repeatedly resolves processors until it reaches `ocispec.MediaTypeImageLayer`, tees processed bytes into a canonical digester, optionally activates a mount manager for multi-mount setups, calls platform-specific `apply`, drains trailing data, checks processor `Err()` hooks, and returns descriptor with uncompressed size/digest/media type.

Dependencies and integration: core content, core diff processors, mount manager, archive application via platform files, go-digest, OCI descriptors, errdefs, logging.

Risks: processor chain must eventually produce OCI layer media type or fail. Progress reports bytes read before each read plus final close. Mount manager activation uses random-ish IDs and is skipped for single mounts. Draining trailing data is important for processor error propagation.

Test signals: platform-specific helper has a small Linux test; full `Apply` behavior requires integration tests with content stores and mounts.
