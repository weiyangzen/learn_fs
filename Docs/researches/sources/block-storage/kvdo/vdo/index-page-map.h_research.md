# File Research: sources/block-storage/kvdo/vdo/index-page-map.h

Header defining the index-page-map structure and persistence/search API.

Key responsibilities:
- Defines `struct index_page_map` with geometry pointer, `last_update`, per-chapter entry count, and `uint16_t` entries array.
- Declares allocation/free, read/write, update, lookup, bounds query, and serialized-size computation functions.

Dependencies:
- Includes buffered reader/writer, common types, and geometry.

Notable risks:
- The map keeps a raw pointer to `const struct geometry`; the geometry must outlive the map.
- Entry storage is implementation-owned but directly visible through the struct definition, so external code could mutate it without validation.
