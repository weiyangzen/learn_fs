# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/entryid.go

Purpose: provides compact parsing and a fixed-capacity thread-safe set/map for BeeGFS entry IDs.

Important APIs/types/functions: `packedEntryID`; `newPackedEntryID`; `parseHexToUint32`; `packedEntryMap`; `newPackedEntryMap`; `Add`; `Contains`.

Control flow: entry IDs are split into exactly three hyphen-separated hex sections, each one to eight chars, and parsed without heap allocation into uint32 fields. The map stores packed IDs in a ring buffer and an index map. `Add` returns false for duplicates, evicts the oldest ID when capacity is full, inserts the new ID, and advances the ring position. `Contains` parses and checks under read lock.

State and persistence: in-memory only. `packedEntryMap` is guarded by an RW mutex and bounded by capacity.

Dependencies and integration points: likely used by entry traversal/migration workflows that need duplicate suppression without retaining unbounded strings.

Risks: special IDs such as root/disposal/mdisposal are intentionally unsupported. Capacity <= 0 silently becomes 1. FIFO eviction is by insertion position, not access recency. Parsing accepts uppercase and lowercase hex but rejects any section longer than 8 chars.

Test signals: `entryid_test.go` covers valid/invalid packing, hex parsing, duplicate detection, eviction behavior, ring/index internals, invalid contains input, and zero-capacity normalization.
