<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrDebug.h -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrDebug.h

Purpose: defines admin-server logging levels and declares logging helpers.

Important APIs/types/functions: level bits include `dlSTANDARD`, `dlWARNING`, `dlERROR`, `dlCONNECTION`, `dlOPERATION`, `dlDETAIL`, `dlDETAIL2`, `dlALL`, and indentation bits `dlINDENT1` through `dlINDENT3`. `dlDEFAULT` is broader under `DEBUG`. Declares `Print()` overloads and detail-level getters/setters.

Control flow: server code annotates log calls with detail bits; runtime code can alter the active mask via `SetPrintDetailLevel()`.

State and persistence: no state in the header; implementation stores a process-local mask.

Dependencies/integration: includes `WINNT/TaAfsAdmSvr.h` for base admin types and is pulled into the internal server header.

Risks and test signals: `GetPrintDetailLevel` is declared with a `DWORD dwLevel` parameter but implemented with no parameter, so strict prototype checking would flag a mismatch. Compile tests should cover callers and the declaration/definition consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrDebug.h -->
