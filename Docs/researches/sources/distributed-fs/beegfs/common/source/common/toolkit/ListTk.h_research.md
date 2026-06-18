<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/ListTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/ListTk.h

Purpose: Provides generic and string-specific list utility functions.

Important APIs/types: `ListTk` exposes `listContains` overloads, `listsEqual`, `removeFromList`, `advance`, and `erase`.

Control flow/state/persistence: Functions iterate and mutate `std::list` values. `advance` moves an iterator up to a count and returns steps advanced; `erase` removes by position.

Dependencies/integration: Used throughout older BeeGFS code built on list aliases.

Risks/test signals: Position and iterator edge cases are main risks. Tests should cover empty lists, duplicate elements, removal with duplicates, erase out of range, and equality order sensitivity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/ListTk.h -->
