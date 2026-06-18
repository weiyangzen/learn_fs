# File Research: sources/block-storage/thin-provisioning-tools/src/thin/metadata_generator.rs

This devtools file sketches metadata generation and simple metadata mutation operations.

Key elements:
- `MetadataGenerator` trait emits metadata into a `MetadataVisitor`.
- `ThinGenerator` currently implements `generate_metadata()` as a TODO stub returning `Ok(())`.
- `format()` creates a core metadata space map, write batcher, and quiet `Restorer`, then asks `ThinGenerator` to generate metadata.
- `set_needs_check()` reads the superblock, toggles `needs_check`, and writes it back.
- `ThinFormatOpts` carries desired data block size and number of data blocks, but is not yet used.
- `MetadataOp` supports `Format(ThinFormatOpts)` and `SetNeedsCheck(bool)`.
- `generate_metadata()` opens the output writable and dispatches by operation.

Interactions:
- Uses `Restorer` as the write path for generated metadata.
- Exposed only under the `devtools` feature.

Risks and notes:
- Formatting is not functionally implemented because `ThinGenerator` emits no superblock/devices/EOF.
- `ThinFormatOpts` is currently ignored.
- The useful implemented operation is setting/clearing `needs_check`.
