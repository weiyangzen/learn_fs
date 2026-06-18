# File Research: sources/block-storage/thin-provisioning-tools/src/thin/ir.rs

This file defines the thin metadata intermediate representation and visitor interface.

Key elements:
- `Superblock` IR includes uuid, time, transaction, optional flags/version, data block size, number of data blocks, and optional metadata snapshot.
- `Device` IR includes device ID, mapped blocks, transaction, creation time, and snapshot time.
- `Map` IR describes a logical thin range mapped to a data range with time and length.
- `Visit` is `Continue` or `Stop`.
- `MetadataVisitor` defines callbacks for:
  - superblock begin/end
  - shared definition begin/end
  - device begin/end
  - map
  - shared reference
  - EOF

Interactions:
- Used as the common exchange layer between dump, restore, XML, human-readable formatting, metadata generation, and delta output.
- Visitors mostly return `Visit::Continue`; stop propagation is supported by the trait but not broadly used in these files.

Risks and notes:
- This IR is intentionally minimal and trusts producers for ordering and validity constraints.
