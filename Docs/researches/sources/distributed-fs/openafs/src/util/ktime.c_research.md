# sources/distributed-fs/openafs/src/util/ktime.c

Purpose: Implements absolute and periodic time parsing, display, and conversion routines for OpenAFS command and scheduling code.

Important APIs: `ktime_SetTestTime()` sets a test clock override. `ktime_DateOf()` formats an `afs_int32` epoch value. `ktime_Str2int32()` parses `hh[:mm[:ss]]`. `ktime_ParsePeriodic()` parses `now`, `never`, `at`, `every`, weekdays, times, and am/pm. `ktime_DisplayString()` formats periodic times. `ktime_next()` computes the next matching event after an offset from now. `ktime_DateToInt32()`, `ktime_GetDateUsage()`, and `ktime_InterpretDate()` handle absolute dates.

Control flow and state: A static token list parser splits periodic strings. `ktime_ParsePeriodic()` applies tokens in sequence, setting mask bits and adjusting am/pm. `ktime_next()` iterates local days by 23 hours to avoid skipping spring DST days, patches desired time fields into a `ktime_date`, then converts to epoch. `ktime_InterpretDate()` binary-searches signed 31-bit time space using `localtime()` and `KDateCmp()`.

Dependencies and integration: Uses `ktime.h`, `afsutil.h`, roken, ctype, localtime/ctime. Relative time code in `kreltime.c` depends on its date interpretation.

Risks and test signals: `ktime_ParsePeriodic()` frees only from the current token pointer at exit, so on successful full iteration it can leak the earlier token list. `LocalParseLine()` can return after allocating partial tokens without freeing on token-too-long. Static buffers in `ktime_DateOf()` are not reentrant. `ktime_SetTestTime()` is process-global. Date tests should cover DST, `never`/`now`, ISO and legacy mm/dd/yy formats.
