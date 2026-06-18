<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/EntryIdTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/EntryIdTk.h

Purpose: Declares entry ID validation helpers.

Important APIs/types: Namespace `EntryIdTk` exposes `isValidEntryIdFormat` and `isValidHexToken`.

Control flow/state/persistence: Stateless declarations for pure validation functions.

Dependencies/integration: Includes `<string>`. Used in metadata-facing tooling and consistency checks.

Risks/test signals: Tests should pin accepted format examples to prevent accidental loosening/tightening.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/EntryIdTk.h -->
