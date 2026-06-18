# sources/distributed-fs/ceph/src/osd/ECTransactionL.cc

Purpose: `ECTransactionL.cc` implements legacy EC transaction generation using full-stripe logical buffers and legacy `HashInfo` metadata. It predates optimized shard extent maps and explicitly does not support OMAP updates.

Important APIs and functions: internal `encode_and_write` encodes a logical full-stripe-aligned buffer into shard buffers, updates `HashInfo`, records written logical extents, and appends writes to per-shard transactions. `ECTransactionL::generate_transactions` translates each `PGTransaction::ObjectOperation` into legacy shard transactions, rollback metadata, hinfo attr updates, and temp object tracking.

Control flow: for each object operation, it loads the planned `HashInfo`, handles zero-truncate-to-delete, delete-first, create/clone/rename init, attrs, alloc hints, partial read extents, truncates, buffer updates, append-extension zeros, overwrite rollback clone ranges, full-stripe encode/write, and hinfo persistence. Overwrites before `append_after` create rollback extents; appends update mod_desc append state.

State and persistence: legacy EC persists `hinfo_key` attrs containing total chunk size and optional cumulative shard hashes. Rollback state is stored in PG log mod_desc and clone objects. Per-shard `ObjectStore::Transaction`s write encoded chunks and attrs. In-memory `HashInfo` projected size coordinates in-flight operations.

Dependencies and integration: depends on `ECTransactionL.h`, `ECUtilL`, `ObjectStore`, `PGTransaction`, erasure-code deprecated encode/decode APIs, and Ceph release gates for create versus touch behavior.

Risks: all writes must be stripe-aligned by the time encoding happens; assertions enforce this. OMAP is asserted unsupported. Hinfo correctness is critical for object size and scrub behavior. Rollback extent calculations are chunk-space, so logical/chunk conversion mistakes are high impact.

Test signals: legacy EC tests should cover hinfo encode/decode, append hash updates, partial overwrite rollback, truncate down/up, clone/rename hinfo copying, temp objects, old-release create behavior, and assertion that OMAP updates are rejected.
