## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/general.cpp

Purpose: shared formatting, parsing, sort, list-name, and utility functions for account manager dialogs and FastList controls.

Important APIs/types/functions: `fIsValidDate`, `FormatElapsedSeconds`, `CreateNameList`, `GetLocalSystemTime`, `FormatServerKey`, `ScanServerKey`, `General_ListSortFunction`, `AppendUID`, `GetEditText`, and overloaded `fIsMachineAccount`.

Control flow: `FormatElapsedSeconds` appends localized weeks/days/hours/minutes/seconds parts. `CreateNameList` resolves each ASID name, optionally appends UID from object properties, and joins using the locale list separator. `General_ListSortFunction` uses static cached sort context initialized by FastList sentinel calls, dispatches to `User_GetColumn` or `Group_GetColumn`, and compares by column type. Server-key routines encode/decode `ENCRYPTIONKEYLENGTH` bytes using backslash triples.

State and persistence behavior: uses a static cached locale separator and static sort context within the sort callback. No disk persistence, but it reads global `g.idClient`, `g.idCell`, and restored `gr.view*` sort definitions.

Dependencies and integration points: depends on localized resource strings, `usr_col`/`grp_col`, FastList sort API, OpenAFS object property cache, and Windows time conversion APIs.

Risks: `ScanServerKey` relies on `_istdigit`/`isdigit` style digit checks and fixed triple parsing; malformed input can fail late. `General_ListSortFunction` returns numeric differences directly, which can overflow for large values. Static cached sort context is not reentrant.

Test signals: sort all column types, create name lists with missing objects and locale-specific separators, round-trip server keys including all-zero hidden keys, and classify machine-account names composed only of dots/digits.
