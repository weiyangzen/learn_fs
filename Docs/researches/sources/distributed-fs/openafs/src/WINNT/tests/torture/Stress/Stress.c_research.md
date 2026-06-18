# sources/distributed-fs/openafs/src/WINNT/tests/torture/Stress/Stress.c

Purpose: Windows process fan-out launcher for the torture executable. It starts multiple minimized `wintorture.exe` processes against distinct target directories while preserving most command-line switches.

Important APIs and functions: `main` parses options with an embedded BSD-style `getopt`, finds an unused `LogNNNNN` directory number, validates `-f` target directory and `-d` process count, and launches children with `CreateProcess`. `usage`, `_progname`, and `getopt` provide command-line support.

Control flow: after option parsing, the launcher scans `Log00000` through `Log00099`, then constructs each child command by copying original arguments while rewriting the argument after `-f` to append a zero-padded directory index. It appends `-g <LogID>`, starts `wintorture.exe`, stores the process handle, and sleeps the requested delay between starts.

State and persistence: persistent effects are child processes and whatever `wintorture.exe` writes under the selected log directory and per-process target directories. The local `hArray` stores handles but does not wait for or close them.

Dependencies and integration: depends on the adjacent `wintorture.exe`, Windows process APIs, and the torture command-line contract. It passes through many switches without interpreting them.

Risks and test signals: there is a missing `break` after `case 'd'`, intentionally or accidentally falling through into switch pass-through cases. Command construction is unquoted and fixed-size. Successful fan-out is indicated by minimized child consoles, distinct `-f` target suffixes, and a shared `-g` log ID.
