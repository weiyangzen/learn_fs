# File Research: sources/block-storage/util-linux/libblkid/src/tag.c

## Scope

Implements libblkid cache/device tag allocation, mutation, parsing, iteration, and lookup by tag.

## Behavior

- Tags are linked both on the owning device (`bit_tags`) and under a cache-level head for the tag name (`bit_names`).
- `blkid_set_tag()` adds, updates, or deletes tags, keeps common direct device fields (`TYPE`, `LABEL`, `UUID`) synchronized, and marks the cache changed.
- `blkid_parse_tag_string()` parses `NAME=value` tokens with simple quote stripping.
- Public tag iteration wraps internal list traversal behind `blkid_tag_iterate_*`.
- `blkid_find_dev_with_tag()` searches the cache by type/value, prefers highest device priority, verifies stale entries, and triggers new/all probing if needed.

## Dependencies And Risks

- List membership is central; freeing a tag removes both list links.
- Direct device fields point at tag value allocations, so update/delete lifetime must stay coordinated.
- Lookup may mutate cache state through verification and probing retries.
