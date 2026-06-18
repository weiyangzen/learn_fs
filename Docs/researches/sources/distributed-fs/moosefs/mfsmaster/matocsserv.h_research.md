## sources/distributed-fs/moosefs/mfsmaster/matocsserv.h

Purpose: declares the public contract for the master-to-chunkserver service and exposes reason enums shared with chunk scheduling, logging, and operation accounting. It intentionally hides `matocsserventry`; callers pass opaque `void *` server handles obtained from chunkserver database/chunk structures.

Important APIs and types: `REPL_*` reasons classify copy, erasure-coded replication, local split, join, and recover operations; `OP_*` reasons classify generic/delete-invalid/delete-not-used/delete-overgoal operations. `REPL_REASONS_STRINGS` and `OP_REASONS_STRINGS` keep human-readable order coupled to the enums. Exported APIs cover label matching, server counts, replication-capable server lists, weighted random creation server selection, replication-limit grouping, global space access, per-server data access, per-server counters, command senders, chunk status broadcast, validity/disconnection notification, shutdown/drain helpers, and initialization.

Control flow and integration: `chunks.c` is the primary consumer. It asks this module for candidate servers, opaque server properties, and rate counters, then invokes senders to enqueue protocol commands. `metadata.c` uses `matocsserv_close_lsock`, `matocsserv_no_more_pending_jobs`, and shutdown-related functions. `storageclass` integration enters through `storagemode` recounting and label expression matching.

State and persistence behavior: the header itself owns no state, but its APIs expose runtime scheduling state and bridge chunkserver state into durable metadata subsystems. Reason enum order is effectively part of diagnostic output and counter interpretation.

Dependencies: includes `chunks.h` for `MAXCSCOUNT` and `storageclass.h` for `storagemode`; also uses fixed-width integer types and `SCLASS_EXPR_MAX_SIZE` via the storage class header.

Risks: because server handles are opaque `void *`, type safety depends on callers only passing live `matocsserventry` pointers. Enum/string list drift would corrupt diagnostics and reason counters. Adding a new command sender requires updating both this header and the protocol dispatch/status handling in the implementation.

Test signals: compile coverage from `chunks.c` and metadata shutdown paths is necessary. Behavioral tests should validate that each exported sender queues a protocol command and that each reason enum maps to the intended log label.
