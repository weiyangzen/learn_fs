# File Research: sources/block-storage/stratisd/src/bin/tools/legacy_pool.rs

Testing-only v1 pool creation helper.

Key behavior:
- Parses pool name, block devices, optional key description, and optional Clevis binding.
- Supports Clevis `nbde`/`tang` with Tang URL plus thumbprint or trust URL, and `tpm2` with empty JSON config.
- Warns interactively that generated v1 pools are only for testing and exits unless the user confirms.
- Converts block-device paths through `ProcessedPathInfos`.
- Builds legacy encryption info with `InputEncryptionInfo::new_legacy`.
- Registers Clevis token support, then calls `StratPool::initialize`.

Filesystem relevance:
- Creates old-format pools for compatibility testing against current Stratis code.
