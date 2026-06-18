# sources/distributed-fs/openafs/src/WINNT/tests/torture/DumpAfsLog/DumpAfsLog.c

## Purpose

`DumpAfsLog.c` is a Windows console utility that repeatedly dumps OpenAFS client trace logs, optionally captures minidumps, and archives the generated files into a timestamp-like sequence under `DumpAfsLogDir`. It is intended for long-running diagnostic capture during stress or deadlock reproduction.

## Important APIs, Types, and Functions

- Uses OpenAFS/roken headers plus Win32 console, environment, sleep, and process APIs.
- `main()` parses options, enables and resets `fs trace`, creates a logging directory, loops until runtime expires or the user presses Q, and disables tracing at exit.
- Options include `-d <drive>`, `-e` for `fs minidump`, `-h <host>` parsed but not used in the shown flow, `-m <minutes>`, `-s <seconds>`, and help.
- `usage()` prints supported options.
- `GetConsoleInput()` peeks/reads console input and exits immediately on `q` or `Q`.

## Control Flow

Startup defaults to 15 seconds between dumps and 30 minutes total runtime. The program runs `fs trace -on` and `fs trace -reset`, builds a working directory on the requested logging drive, removes and recreates `DumpAfsLogDir`, then enters a loop. Each iteration optionally runs `fs minidump`, copies `%windir%\TEMP\afsd.dmp` into the log directory, renames it to `afsd_#####.dmp`, runs `fs trace -dump`, copies `%windir%\TEMP\afsd.log`, and renames it to `afsd_#####.log`. Between iterations it polls console input every 500 ms until the delay expires. On normal timeout it runs `fs trace -off`.

## State and Persistence

Persistent output is the `DumpAfsLogDir` directory in the current/logging-drive-adjusted working directory, containing numbered `afsd_*.log` and optionally `afsd_*.dmp` files. The utility mutates OpenAFS client tracing state by turning trace on, resetting it, dumping it, and turning it off.

## Dependencies and Integration Points

The utility depends on `fs.exe` commands (`trace -on`, `trace -reset`, `trace -dump`, `trace -off`, `minidump`), `%windir%\TEMP\afsd.log`, `%windir%\TEMP\afsd.dmp`, and Windows shell commands `rmdir`, `mkdir`, `copy`, and `rename`. It uses roken `strlcpy`/`strlcat` for safer string construction.

## Risks and Edge Cases

- Many operations are shell-command based and depend on paths without full quoting, so spaces in directories can break commands.
- `HostName`, `NewSessionDeadlock`, and related variables are parsed or declared but unused in the active flow.
- `GetConsoleInput()` exits the process directly on Q, bypassing the final `fs trace -off`.
- `system()` return codes are assigned but largely ignored.
- The directory is removed recursively at startup, so an incorrect working directory or logging drive can destroy prior capture data.

## Test Signals

Signals are visible console commands, numbered copied logs/dumps, and successful trace-off on timeout. During testing, verify that `%windir%\TEMP` artifacts are copied and renamed each cycle, Q stops the loop, and `fs trace -dump` produces fresh logs.
