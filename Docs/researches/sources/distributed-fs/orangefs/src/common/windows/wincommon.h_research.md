<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/windows/wincommon.h -->
## sources/distributed-fs/orangefs/src/common/windows/wincommon.h

Purpose: Provides a small Windows portability shim for OrangeFS/PVFS code that otherwise assumes POSIX/GNU C names. It includes `Windows.h` and `<sys/timeb.h>`, remaps common C/POSIX identifiers to MSVC spellings, suppresses GCC `__attribute__`, and supplies `gettimeofday()`.

Important APIs, types, and functions: The file defines `__inline__`, `inline`, and `__func__` compatibility macros, maps `index`, `strdup`, `strcasecmp`, `strncasecmp`, `strtoll`, and `strtok_r`, and implements `static int gettimeofday(struct timeval *tv, struct timezone *tz)` using `_ftime_s`. `tz` is ignored, matching the common portability usage of `gettimeofday`.

Control flow and state: The only runtime path zeroes a `_timeb`, calls `_ftime_s`, and on success fills seconds and microseconds. There is no persistent state.

Dependencies and integration points: Included from Windows-only BMI code such as `bmi.c` when `WIN32` is set. It depends on MSVC CRT functions and a visible `struct timeval` definition from the including environment.

Risks and test signals: `strtoll(str,end,base)` ignores `end` and `base`, which can silently change parsing semantics. `snprintf` is commented out, so callers still need a compatible declaration. Build tests should compile Windows BMI paths and exercise timestamp conversion and string parsing callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/windows/wincommon.h -->
