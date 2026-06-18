# sources/distributed-fs/openafs/src/WINNT/bosctlsvc/bosctlsvc.c

Purpose: implements the Windows SCM service wrapper that controls the AFS `bosserver`, including start, stop, and restart handling.

Important APIs and control flow: `main` registers `BosCtlMain` with `StartServiceCtrlDispatcher`. `BosCtlMain` initializes `SERVICE_STATUS`, creates stop/exit events, registers `BosCtlHandler`, opens firewall ports, initializes AFS server dir paths, installs a `SIGCHLD` handler, and calls `BosserverRun`. `BosserverRun` builds a `spawnprocve` argument vector for `AFSDIR_SERVER_BOSVR_FILEPATH`, marks process management as detached, starts/restarts the child, reports `SERVICE_RUNNING`, and waits for stop or child-exit events. `BosserverDoStopEvent` sends `SIGQUIT`, waits bounded time for child exit while updating SCM checkpoints, and reports timeout/failure. `BosserverDoExitEvent` distinguishes spurious SIGCHLD, restart exit codes via `BOSEXIT_DORESTART`, and terminal child exits.

State and dependencies: service status is protected by `bosCtlStatusLock`; `bosCtlEvent` handles coordinate SCM controls and signal events. Dependencies include Windows services/events, OpenAFS event logging, registry service name constants, process management, dirpath, bnode restart-code macros, and firewall configuration.

Risks and test signals: stop timeout behavior, child restart loops, SCM checkpoint reporting, and signal/event races are central risks. There is a potential uninitialized `status` path if the first event creation succeeds and the second fails before reporting resources. Tests should simulate SCM stop, bosserver clean exit, restart exit, spawn failure, event creation failure, SIGCHLD without wait status, and stop timeout.
