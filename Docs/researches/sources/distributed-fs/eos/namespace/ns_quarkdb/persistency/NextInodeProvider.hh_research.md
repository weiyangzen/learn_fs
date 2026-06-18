# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/NextInodeProvider.hh

Purpose: Declares the block allocator and QDB-backed provider used to issue unique file/container inode IDs.
Important APIs/types/functions: `InodeBlock` models a contiguous `[start,start+len)` allocation with peek, reserve, empty, and blacklist operations. `NextInodeProvider` exposes `configure(qclient::QHash&, field)`, `getFirstFreeId()`, `reserve()`, and `blacklistBelow()`.
Control flow: users configure a hash field, call `reserve()` for the next ID, and optionally blacklist imported/restored IDs so future allocations skip them.
State/persistence: `InodeBlock` is in-memory only; `NextInodeProvider` persists only the largest reserved ID in QDB through a non-owning `QHash*` and field string. `mMtx` serializes provider operations.
Dependencies/integration: forward-declares `qclient::QHash`, relies on EOS namespace macros, and is composed by `UnifiedInodeProvider`.
Risks: header does not express configured/unconfigured state, so misuse is a runtime/null-pointer concern; comments contain minor spelling errors but not behavioral ambiguity; integer boundary handling is critical because EOS identifiers can exceed 32-bit ranges.
Test signals: standalone `InodeBlock` tests validate empty and negative-length blocks, reserve order, and blacklisting; provider tests validate QDB persistence semantics.
