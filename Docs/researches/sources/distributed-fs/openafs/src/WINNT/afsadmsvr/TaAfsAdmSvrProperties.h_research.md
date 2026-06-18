<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrProperties.h -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrProperties.h

Purpose: declares property-cache, AfsClass notification, and cell auto-refresh helpers for the admin server.

Important APIs/types/functions: declarations include `AfsAdmSvr_NotifyCallback()`, rudimentary/full property collection, current-property lookup, property invalidation, change testing, refresh-rate setup, refresh-thread stop, and refresh-thread timestamp marking.

Control flow: AfsClass initialization registers the callback; RPC handlers and search code call property helpers to obtain or refresh `ASOBJPROP` data.

State and persistence: no state is exposed. Implementation stores refresh-thread state privately and attaches property state to `IDENT` objects.

Dependencies/integration: includes public `WINNT/TaAfsAdmSvr.h` for `ASOBJPROP`, `ASID`, and related types.

Risks and test signals: callers receive raw `LPASOBJPROP` pointers into cache state, so tests should ensure callers do not free or retain stale pointers across object destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrProperties.h -->
