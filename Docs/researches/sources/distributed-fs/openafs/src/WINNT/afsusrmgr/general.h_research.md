## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/general.h

Purpose: shared utility declarations and column-sort type definitions.

Important APIs/types/functions: defines `COLUMNTYPE` (`ctALPHABETIC`, `ctNUMERIC`, `ctDATE`, `ctELAPSED`) and `GetColumnFunction`. Declares date validation, elapsed formatting, ASID name-list creation, local time conversion, server-key formatting/scanning, FastList sort callback, UID appending, edit-text allocation, and machine-account detection.

Control flow: consumed by column modules, delete dialogs, property dialogs, and FastList sorting.

State and persistence behavior: header itself has none; declared functions often read global cell/client and restored view state.

Dependencies and integration points: ties generic display/sort code to OpenAFS `ASID`, Windows `SYSTEMTIME`, and FastList `HLISTITEM` types.

Risks: function signatures expose caller-owned buffers without sizes for several formatting functions, so callers must pass resource-sized buffers.

Test signals: build with all callers after utility signature changes and run UI paths that sort, format names, and parse encryption keys.
