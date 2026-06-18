<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/EntryIdTk.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/EntryIdTk.cpp

Purpose: Implements validation helpers for BeeGFS entry IDs and hexadecimal tokens.

Important APIs/functions: `EntryIdTk::isValidEntryIdFormat` checks the expected tokenized entry-id shape. `EntryIdTk::isValidHexToken` verifies uppercase hex-token characters.

Control flow/state/persistence: Pure string validation; no state.

Dependencies/integration: Used by metadata/fsck/tools before accepting entry IDs.

Risks/test signals: Format strictness can reject older or externally generated IDs. Tests should cover valid IDs, lowercase hex, missing tokens, extra separators, empty tokens, and non-hex characters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/EntryIdTk.cpp -->
