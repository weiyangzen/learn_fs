# sources/distributed-fs/openafs/src/bozo/test/testproc.c

`testproc.c` is a small controllable process for exercising bosserver bnode supervision. It can sleep, ignore termination, reload behavior from a file, return normally, exit with error, or intentionally crash.

Important APIs are `main`, `readfile`, `trim`, `sigproc`, and `sigreload`. Options are `-ignore`, `-sleep <n>`, and `-file <file>`. A control file can contain `sleep N`, `run`, `return`, `exit`, or `crash`; SIGHUP reloads it, while SIGTERM/SIGQUIT either exit or are ignored depending on `-ignore`.

Control flow parses options, installs signal handlers, and loops while `run` is true, optionally reading the control file and sleeping. State is process-local globals (`ignore`, `sleepTime`, `run`, `file`) plus the external control file. Dependencies are standard C/POSIX signal, sleep, stdio, and AIX full-core handling.

Risks are intentional because this is a test helper: `crash` dereferences NULL, file parsing only reads one line, and invalid control files can terminate the process. Test signals are exactly its behaviors under bnode supervision: normal return, ignored SIGTERM leading to SIGKILL, SIGHUP reconfiguration, nonzero exit, and core generation.
