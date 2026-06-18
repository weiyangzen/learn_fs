<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/al/al.h -->
# sources/distributed-fs/coda/coda-src/al/al.h

Purpose: Declares Coda access-list data structures and the access-list/protection-set API used by VICE/server code.

Important APIs, types, and functions: Defines `AL_VERSION`, `AL_AccessEntry` with internal id and rights mask, `AL_AccessList` with serialized size/version/counts and flexible `ActualEntries`, `AL_MAXEXTENTRIES`, `AL_ExternalAccessList`, global `AL_MaxExtEntries`, and `AL_DebugLevel`. Public functions allocate/free and byte-swap access lists and CPS objects, externalize/internalize ACLs, check rights against a CPS, initialize the library, map names to ids and ids to names, fetch internal/external CPS, test membership, print ACLs, enable/disable groups, and compare plus/minus entries.

Control flow: Callers initialize the AL library, convert external text ACLs to internal `AL_AccessList`, convert host/network byte order for storage, obtain CPS membership for users/groups, and call `AL_CheckRights()` to compute effective rights. Plus entries grant rights and minus entries remove rights according to comparator/order semantics implemented elsewhere.

State and persistence: `AL_AccessList` is the on-secondary-storage format for VICE ACLs. `AL_ExternalAccessList` is a textual format with plus/minus counts and name/right lines. Global limits and debug level influence parsing/allocation behavior.

Dependencies and integration points: Depends on `PRS_InternalCPS` and `PRS_ExternalCPS` from `prs.h` included by users of this header or related code. Integrates with Coda protection database name/id lookup and VICE ACL enforcement.

Risks and test signals: The one-element trailing array requires careful allocation by `AL_NewAlist()`. External ACL parsing depends on `AL_MaxExtEntries` and exact text format. Byte-order conversion is required before/after storage. Tests should cover ACL allocation sizes, external/internal round trips, network byte order conversion, rights computation with plus and minus entries, group enable/disable membership, and name/id lookup failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/al/al.h -->
