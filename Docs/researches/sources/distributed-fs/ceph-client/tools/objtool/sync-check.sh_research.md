# sources/distributed-fs/ceph-client/tools/objtool/sync-check.sh

Purpose: Shell helper that checks objtool source synchronization between kernel copies or generated lists.

Important APIs/types/functions: the file-local declarations and build entries.

Control flow: Runs command-line comparisons and exits nonzero when checked files diverge.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on POSIX shell tools and the kernel tree layout.

Risks: Path assumptions can produce false failures outside the expected build tree.

Test signals: Run from the kernel tree with synced and intentionally modified files.

Source coverage: researched from the complete local file (78 lines, 1376 bytes).
