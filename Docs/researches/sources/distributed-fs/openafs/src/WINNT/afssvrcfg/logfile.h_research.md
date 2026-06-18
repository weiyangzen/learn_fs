<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/logfile.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/logfile.h

Purpose: Declares `LOGFILE`, the small logging wrapper used across the server configuration application.

Important APIs/types: `LOGFILE_TIMESTAMP_MODE`, `LOGFILE_OPEN_MODE`, and methods `Open`, `Close`, `GetPath`, `Write`, `WriteError`, `WriteMultistring`, `WriteTimeStamp`, and `WriteBoolResult`.

Control flow: No implementation logic in the header; callers open once and then write diagnostics through the global `g_LogFile`.

State and persistence: Instances own a `FILE *`, path buffer, and timestamp mode; writes persist to the configured log path.

Dependencies and integration points: Includes Windows and stdio headers. Used by nearly every configuration, discovery, partition, and salvage path.

Risks: No copy-control declarations; accidental copying would duplicate a raw `FILE *`. Variadic methods provide no compile-time format checking.

Test signals: Compile with warnings for copy/use, verify global lifecycle in `WinMain`, and test destructor close behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/logfile.h -->
