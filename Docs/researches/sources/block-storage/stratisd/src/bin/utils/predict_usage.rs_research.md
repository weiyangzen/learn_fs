# File Research: sources/block-storage/stratisd/src/bin/utils/predict_usage.rs

Implements JSON space-usage prediction for Stratis pool/filesystem creation.

Key behavior:
- Filesystem logical size must be at least 512 MiB, less than 32 PiB, and sector-aligned.
- Overprovisioned filesystem usage uses `FSSizeLookup`, a recorded usage table indexed by rounded-up log2 size.
- Non-overprovisioned filesystem usage sums logical sectors directly.
- Pool prediction subtracts:
  - Stratis BDA/metadata allocation.
  - dm-integrity metadata space from `integrity_meta_space`.
  - crypt metadata offset `DEFAULT_CRYPT_DATA_OFFSET_V2`.
  - thin-pool metadata and MDV sizes from `ThinPoolSizeParams`.
  - optional predicted filesystem usage.
- Emits JSON strings for byte counts:
  - Filesystem: `{"used": "..."}`
  - Pool: `{"total","used","free","stratis-admin-space","stratis-metadata-space"}`.

Filesystem relevance:
- Encodes practical capacity planning rules for Stratis layered storage: block device metadata, integrity metadata, crypt offset, thin metadata, and filesystem provisioning.
