# sources/distributed-fs/openafs/src/WINNT/tests/torture/Source/nbio.c

Purpose: Windows torture-test I/O engine derived from Samba nbio code, adapted to exercise OpenAFS/Windows filesystem behavior through Win32 APIs and shell utilities. It implements scriptable operations such as create, read, write, close, unlink, rename, directory tree cleanup, locker attach/detach, copy/move, path/file queries, and filesystem free-space queries.

Important APIs and functions: `FindHandle` resolves logical script handles in thread-local `ftable`; `nb_createx`, `nb_writex`, `nb_readx`, `nb_close`, `nb_unlink`, `nb_rmdir`, `nb_rename`, `nb_qpathinfo`, `nb_qfileinfo`, `nb_qfsinfo`, `nb_findfirst`, `nb_deltree`, and `nb_cleanup` implement the command surface declared in `proto.h`. `CreateObject`, `GetFileList`, `WinFindFirstFile`, `WinFindNextFile`, `GetPathInfo`, `GetFileInfo`, `nb_read`, and `nb_write` are local Win32 shims.

Control flow: each command prepends `AfsLocker` where appropriate, starts timing with `StartFirstTimer`, performs a Win32 or `system` operation, then records success/error timing with `EndFirstTimer`. Failures call `LeaveThread`, which increments command error counts, formats the last error, writes per-thread logs, optionally dumps AFS trace data, and clears `*pThreadStatus`.

State and persistence: most operational state is thread-local: process number, command counters, open-file table, I/O buffer, active locker path, host name, exit status, and timing ticks. Persistent effects are real filesystem mutations under the locker path plus log files under `logNNNNN/<host>/Thread_XXXXX.log`.

Dependencies and integration: depends on `common.h` command IDs/types, `includes.h` Win32 definitions, `output.c` logging, the torture script runner that dispatches `nb_*` functions, and external MIT `attach`/`detach`, DOS `copy`, `xcopy`, `move`, `del`, `mkdir`, and `rmdir` tools.

Risks and test signals: fixed-size buffers and unquoted shell command construction are fragile for long paths and spaces. `nb_qpathinfo` has compatibility flags encoded as magic `Type` values. `GetFileInfo` appears to set `rc = 0` when optional `size` or `mode` outputs are requested, so callers with those arguments must be checked carefully. Positive test signals are command counters, per-command latency/error statistics, Win32 `GetLastError` logs, and optional AFS trace dumps.
