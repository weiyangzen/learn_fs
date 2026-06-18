<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrDebug.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrDebug.cpp

Purpose: implements simple synchronized console logging for the Windows admin server.

Important APIs/types/functions: static `PrintDetailLevel` initializes to `dlDEFAULT`. `vPrint()` lazily creates a `CRITICAL_SECTION`, filters by level, formats with `wvsprintf()`, writes an `AdmSvr:` prefix, optional alert marker, and indentation spaces. Two `Print()` overloads dispatch to `vPrint()`. `GetPrintDetailLevel()` and `SetPrintDetailLevel()` expose the filter mask.

Control flow: callers use `Print(level, format, ...)` or `Print(format, ...)`. Messages with a zero level always print; otherwise the configured bitmask controls output.

State and persistence: only process-local static logging level and lazily allocated critical section. No log file or registry persistence.

Dependencies/integration: included through `TaAfsAdmSvrInternal.h`; uses Windows critical sections, C varargs, `wvsprintf`, and stdout `printf`.

Risks and test signals: lazy critical-section creation is not itself synchronized, so two threads could race during first log. `wvsprintf()` and a fixed 1024-character buffer risk truncation/overflow on long formatted output. Tests should cover level masks, indentation bits, concurrent logging, and debug/non-debug default masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrDebug.cpp -->
