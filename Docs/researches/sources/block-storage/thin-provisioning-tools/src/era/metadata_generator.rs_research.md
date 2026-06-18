# File Research: sources/block-storage/thin-provisioning-tools/src/era/metadata_generator.rs

This devtools-gated file generates synthetic era metadata.

`MetadataGenerator` emits metadata through the same `MetadataVisitor` interface used by dump/restore. `CleanShutdownMeta` generates a clean-shutdown superblock, a sequence of random writesets, and a random era array.

Important behavior:
- `IndependentSequence` creates random contiguous marked ranges with independent per-block probability.
- `CleanShutdownMeta` validates `current_era > 0` and `nr_writesets <= current_era`.
- Generated writesets cover eras from `current_era - nr_writesets + 1` through `current_era`.
- `format()` feeds generated metadata into `Restorer` through `WriteBatcher`.

Public entry point:
- `generate_metadata(EraGenerateOpts)`

Integration points:
- Uses `Restorer` to materialize generated visitor events into real on-disk metadata.
- Uses `EngineBuilder` and metadata space-map allocation.

Risks and notes:
- Random generation makes exact output nondeterministic.
- Feature-gated under `devtools`.
