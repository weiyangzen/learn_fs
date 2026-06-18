# File Research: sources/block-storage/thin-provisioning-tools/src/cache/xml.rs

Serializes and parses cache metadata XML using the cache IR visitor interface.

Writer behavior:
- `XmlWriter<W>` emits indented XML.
- Writes `<superblock>` with `uuid`, `block_size`, `nr_cache_blocks`, `policy`, `hint_width`.
- Writes `<mappings>` and empty `<mapping cache_block=... origin_block=... dirty=.../>` entries.
- Writes `<hints>` and empty `<hint cache_block=... data=.../>` entries, base64-encoding hint data.
- Includes discard writer methods for `<discards>` and `<discard>`, though the current dump path does not call them.
- Flushes on EOF.

Parser behavior:
- Parses superblock, mapping, and hint elements.
- Validates required attributes and rejects unknown attributes/tags.
- Decodes hint data from base64.
- Ignores text and comments.
- Calls visitor EOF on XML EOF and stops when visitor returns `Visit::Stop`.

Notable details:
- Parser does not handle discard XML tags despite writer methods existing for discards.
- Attribute iteration uses `unwrap()` on XML attributes, so malformed attributes can panic.
