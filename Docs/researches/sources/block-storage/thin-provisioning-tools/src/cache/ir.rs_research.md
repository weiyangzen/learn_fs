# File Research: sources/block-storage/thin-provisioning-tools/src/cache/ir.rs

Defines the cache metadata intermediate representation and visitor interface used between dump, XML, restore, and synthetic generation.

Types:
- `Superblock`: UUID string, block size, cache block count, policy name, hint width.
- `Map`: cache block, origin block, dirty flag.
- `Hint`: cache block plus arbitrary byte vector.
- `Discard`: begin/end range, although current cache dump/restore paths mostly ignore discards.
- `Visit`: `Continue` or `Stop`.
- `MetadataVisitor`: event-style callbacks for superblock, mappings, hints, discards, and EOF.

This abstraction decouples binary traversal from XML serialization and binary rebuild.
