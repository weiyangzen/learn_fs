<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrInternal.h -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrInternal.h

Purpose: umbrella internal header for the Windows AFS admin server implementation.

Important APIs/types/functions: includes RPC headers, AfsClass, public `TaAfsAdmSvr.h`, and internal modules for debug, search, properties, general server helpers, and callbacks. It also includes C admin-library headers for KAS, PTS, VOS, BOS, client, and utility admin APIs.

Control flow: implementation files include this header to get the full internal server surface and backend admin-library dependencies.

State and persistence: no state. It organizes dependencies and compile visibility only.

Dependencies/integration: bridges C++ AfsClass/Windows code with C OpenAFS admin APIs inside an `extern "C"` block.

Risks and test signals: as an umbrella header it can hide excess coupling and slow or complicate builds. Compile tests should ensure C/C++ linkage remains correct and include ordering does not break Windows/RPC definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrInternal.h -->
