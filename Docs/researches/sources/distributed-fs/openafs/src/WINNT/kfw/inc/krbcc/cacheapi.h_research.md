## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krbcc/cacheapi.h

Purpose: Public Kerberos Common Cache DLL API for managing named credential caches containing Kerberos V and legacy Kerberos IV credentials.

Important APIs/types/functions: Defines `cc_int32`, `cc_uint32`, `cc_time_t`, API versions, `CCACHE_API`, error codes, opaque handles `apiCB`, `ccache_p`, `ccache_cit`, `cc_data`, V5 `cc_creds`, V4 `V4Cred_type`, `cred_union`, `infoNC`, cache version constants, and lock constants. APIs include `cc_initialize`, `cc_shutdown`, `cc_get_change_time`, named-cache create/open/close/destroy/iterate/info/principal/version/lock, credential store/remove/iterate, and DLL-owned free functions.

Control flow: Clients initialize an API control block, open or create named caches, set principals, store or fetch V4/V5 credentials through iterators, optionally lock caches, free returned allocations with cache API free calls, then shut down.

State and persistence: The DLL owns main cache state and named caches; credential data can persist in the common cache backend. `cc_get_change_time` reports global mutation time. Handles and iterators are opaque DLL state.

Dependencies and integration points: Includes `windows.h`, exports via `__declspec(dllexport)`, and bridges KfW credential cache operations used by Kerberos and OpenAFS token acquisition.

Risks: The header always defines `CCACHE_API` as export, which is awkward for import-side consumers unless build flags compensate. Cross-DLL allocation ownership is strict. V4 fixed buffers and V5 pointer graphs require deep-copy/free correctness. Lock semantics are cooperative and easy to misuse.

Test signals: Initialize/shutdown version negotiation, create/open/destroy caches, store/fetch V4 and V5 credentials, iterator begin/next/end edge cases, lock/no-block behavior, change-time updates, and correct nulling/freeing of returned pointers.
