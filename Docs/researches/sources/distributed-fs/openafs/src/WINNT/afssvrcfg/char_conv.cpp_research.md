<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/char_conv.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/char_conv.cpp

Purpose: Implements RAII-style wrappers for converting between TCHAR strings and ANSI `char *` strings used by legacy OpenAFS admin APIs.

Important APIs/functions: `S2A::S2A` calls `StringToAnsi`; `S2A::~S2A` frees only in UNICODE builds. `A2S::A2S` calls `AnsiToString`; `A2S::~A2S` similarly frees only when conversion allocation is expected.

Control flow: Instances are typically temporary objects cast implicitly to `char *`, `const char *`, `LPTSTR`, or `LPCTSTR` at call sites.

State and persistence: Per-object pointer ownership only. No durable state.

Dependencies and integration points: Uses app-library conversion and allocation helpers from `WINNT/afsapplib`. Used throughout cfg, partition, salvage, and logging UI paths when bridging Win32 TCHAR controls to AFS C APIs.

Risks: Implicit pointer casts make lifetime easy to misuse if a callee stores the converted pointer beyond the temporary expression. Destructors only free in UNICODE builds, relying on app-library behavior in ANSI builds. Null input handling is delegated to the app-library conversion routines.

Test signals: Compile/test ANSI and UNICODE builds, temporary use inside function calls, null/empty strings, and long fixed-buffer inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/char_conv.cpp -->
