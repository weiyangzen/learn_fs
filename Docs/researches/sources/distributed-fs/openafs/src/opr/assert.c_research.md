# sources/distributed-fs/openafs/src/opr/assert.c

Purpose: assertion failure implementation for OPR.

Important APIs/types/functions: `opr_AssertionFailed(file, line)` formats current local time, prints an assertion failure message to stderr, flushes, and calls `opr_abort`. On NT, `opr_NTAbort` triggers `DebugBreak`.

Control flow: assertion macros in `opr.h` call this function when expressions fail. It does not return.

State and persistence: no persistent state; writes diagnostic output to stderr.

Dependencies/integration: depends on `opr.h`, time functions, stderr, and platform abort handling. Used by `opr_Assert` and `opr_Verify` across OPR and other OpenAFS code.

Risks and test signals: `localtime_r` and `strftime` are used during failure handling; if unavailable or broken, diagnostics may fail. Tests are normally assertion-trigger smoke tests or indirect failure output checks.
