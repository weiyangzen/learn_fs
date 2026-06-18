# sources/distributed-fs/openafs/src/ptserver/readgroup.c research

## Purpose
`readgroup.c` is an import utility that reads a textual group file, creates protection groups, and adds listed users or expanded members from referenced groups. It is intended for bulk population or migration of PT group membership data.

## Important APIs, types, and functions
`main` parses `[-v] [-c cellname] groupfile`, initializes libprot with `pr_Initialize(2, AFSDIR_CLIENT_ETC_DIRPATH, cellname)`, opens the input file, parses group headers and continuation member lines, calls `pr_CreateGroup`, `pr_AddToGroup`, and `pr_ListMembers`, and reports errors with `report_error`. `skip` advances over whitespace-delimited tokens. A local `osi_audit` stub satisfies auth-library linkage in a non-server program.

## Control flow, state, and persistence
The input format treats a non-indented line as a new group declaration: group name, numeric id, then optional members on the same line. Leading space or tab means additional members for the current group. The utility lowercases group names, derives an owner prefix from the group name before `:`, maps owner `system` to `system:administrators`, and attempts to create the group with the parsed id. If the group already exists, membership import may continue; if creation fails for other reasons, later member lines are skipped until the next group. Members without `:` are added directly. Tokens containing `:` are treated as groups, expanded with `pr_ListMembers`, and each returned member is added to the target group.

Persistent state changes are remote ptserver group creation and membership additions through `ptuser.c`.

## Dependencies and integration points
The file depends on `ptuser.h`, generated client types, `pterror.h`, `ptprototypes.h`, AFS config paths, Rx/XDR, and `pr_ErrorMsg`. It is a batch client of the same RPCs exposed through `pts`.

## Risks and test signals
Parsing is simple and fragile: it uses fixed buffers, assumes `:` exists in group names before deriving the owner, and treats any token containing `:` as a group reference. It should be tested with missing colons, long lines, empty lines, existing groups, nonexistent referenced groups, duplicate members, verbose mode, and explicit cell selection. Because it expands referenced groups by current server state, import results can depend on ordering and preexisting memberships.
