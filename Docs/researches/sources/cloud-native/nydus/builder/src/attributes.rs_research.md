# sources/cloud-native/nydus/builder/src/attributes.rs

Purpose: parses Nydus-specific attributes files using git-attributes syntax and exposes lookups for build behavior such as external paths and CRC lists.

Important APIs/types/functions: `Attributes::from(path)` reads and parses a file with `gix_attributes::parse`. `Attributes` stores `items: HashMap<PathBuf, HashMap<String, String>>` and `crcs: HashMap<PathBuf, Vec<u32>>`. Lookup helpers include `is_external`, `is_prefix_external`, `get_value`, `get_values`, and `get_crcs`. Attribute keys currently recognized specially are `type` and `crcs`; `type=external` drives external handling.

Control flow: parser iterates parsed pattern entries, normalizes relative patterns to absolute paths by joining with `/`, records every parsed attribute as a string, parses comma-separated CRC values as hex with optional `0x`, stores CRC vectors, then walks parent directories and inserts missing parents as `type=external`.

State and persistence: state is entirely in the returned `Attributes` object. The source attribute file is read but not modified.

Dependencies and integration points: consumed by `BuildContext` and builder logic that needs path-scoped policy. Depends on `gix-attributes` for syntax parsing and `anyhow` for parse errors.

Risks: only pattern entries are processed; macro or unsupported gitattributes constructs may be ignored depending on parser output. Parent insertion can mark broad directories external, so a single deep external file affects ancestor lookup. Invalid CRC tokens fail the whole parse. `is_prefix_external` checks stored item paths starting with the target, which is useful for subtree detection but can surprise callers expecting target-starts-with-item semantics.

Test signals: tests cover parsing, relative-path normalization, parent injection, external checks, value lookups, CRC parsing with and without `0x`, whitespace, defaults, and non-external types.
