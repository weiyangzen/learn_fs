<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/logfile.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/logfile.cpp

Purpose: Implements the `LOGFILE` class used by the configuration program to write timestamped diagnostics and translated AFS error details.

Important APIs/functions: Constructor/destructor manage `FILE *`. `Open` chooses overwrite/append mode, stores path, writes initial timestamp/open message. `Close` writes closing message. `Write` formats varargs entries and optionally timestamps each new line. `WriteError` formats caller text and translates an admin error code via `util_AdminErrorCodeTranslate`. `WriteMultistring` logs NUL-separated strings. `WriteBoolResult` logs Yes/No.

Control flow: Most operations early-return false when no file is open. `Write` maintains a static `bTimestampNextLine` so multiline entries are timestamped only at line starts.

State and persistence: Maintains the open file pointer, path, timestamp mode, and writes durable log text to disk. `Write`'s static timestamp flag is shared across all `LOGFILE` instances.

Dependencies and integration points: Uses C stdio/time helpers, Win32 types, OpenAFS utility error translation, `TaLocale_GetLanguage`, and is held globally as `g_LogFile`.

Risks: `strcpy(m_szPath, pszLogFilePath)` can overflow `MAX_PATH`. `Write` indexes `pszEntry[strlen(pszEntry)-1]`, which is invalid for an empty format string. The static timestamp flag is not per instance or thread-safe. `WriteMultistring` increments by `strlen(p)` instead of `strlen(p)+1`, causing the next loop to land on the NUL terminator and stop after the first string. Logging from worker/UI threads is unsynchronized.

Test signals: Test open/append/overwrite modes, long paths, empty writes, multiline timestamping, multiple instances, translated/untranslated errors, multistring with multiple hosts, and concurrent writes from config/salvage threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/logfile.cpp -->
