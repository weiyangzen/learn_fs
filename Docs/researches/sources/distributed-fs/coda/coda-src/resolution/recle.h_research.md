<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/recle.h -->
# sources/distributed-fs/coda/coda-src/resolution/recle.h

Purpose: defines the recoverable log-entry wire/storage layout and variable payload structs used by Coda resolution logs.

Important APIs/types: `recle` is the fixed-length recoverable record containing server ID, store ID, opcode, directory vnode/unique, variable-size length, `recvarl *`, volume-log index, and sequence number. It exposes `InitFromsle`, `FreeVarl`, `HasList`, `GetDumpSize`, `DumpToBuf`, and print overloads. Payload classes model ACL/status stores, creates, symlinks, hard links, mkdir, remove, rmdir with child log and child LCP, rename with source/target metadata and target child log, and quota changes.

State/persistence: records and `recvarl` payloads are RVM-managed. Some payloads contain pointers to recoverable child log lists, making logs tree-shaped for directory removal/rename.

Dependencies/integration: uses `rec_dlist`, `recvarl`, vnode/version-vector types, and opcode constants from resolution utilities. `rsle` is the transient source representation.

Risks/test signals: variable-length structs use trailing `char name[1]`, so allocation sizes and string termination are critical. Pointer-bearing payloads complicate dump/purge recursion. Test payload size calculations, alignment, nested-log purge, and compatibility of serialized record stamps across architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/recle.h -->
