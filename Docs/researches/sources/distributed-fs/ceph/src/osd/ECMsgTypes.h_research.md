# sources/distributed-fs/ceph/src/osd/ECMsgTypes.h

Purpose: `ECMsgTypes.h` defines the EC suboperation payload types exchanged between OSD shards during EC reads and writes. It is the wire-contract header for EC subwrite/subread request and reply structures.

Important APIs and types: `ECSubWrite` carries source shard, transaction id, client request id, object id, stats, `ObjectStore::Transaction`, versioning, log entries, temp objects, hit-set history, and async recovery flags. `ECSubWriteReply` reports commit/apply status and last complete version. `ECSubRead` carries extents, attrs, subchunk requests, OMAP header requests, and OMAP iteration start/max bytes. `ECSubReadReply` returns buffers, attrs, errors, OMAP headers, OMAP entries, and completion bits.

Control flow: declarations support both single-buffer and split payload/data-buffer encode/decode forms. `claim` on `ECSubWrite` moves expensive members out of another write payload without public copying. Formatter and ostream overloads support debug and admin reporting.

State and persistence: the structures are transient but transport persistent operations. `ECSubWrite` embeds the exact object-store transaction and PG log state that replicas apply; `ECSubReadReply` may return authoritative OMAP fragments used by the primary.

Dependencies and integration: includes Ceph object, encoding, buffer, and transaction types. Formatter specializations allow `fmt` to stream these messages. Message classes and EC backend code depend on this header for subop payload layout.

Risks: copying is deliberately restricted for `ECSubWrite`, so call sites must use `claim` or references correctly. Wire compatibility depends on implementations in the `.cc`; adding members here without versioned encode/decode support would break mixed-version clusters.

Test signals: generated test instances should be included in Ceph encoding tests. Integration coverage should verify EC subwrites with temp objects, backfill/async recovery, OMAP reads, and old-feature decode paths.
