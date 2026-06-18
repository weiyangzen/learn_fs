# sources/distributed-fs/openafs/src/bozo/ezbnodeops.c

`ezbnodeops.c` implements the `simple` bnode type: supervision for a single long-running command. It starts, stops, restarts after exits when the bnode goal is normal, detects core files, supports pid files, and reports simple status.

Important APIs are `ezbnode_ops`, `ez_create`, `ez_setstat`, `ez_timeout`, `ez_procexit`, `ez_restartp`, `ez_getstat`, `ez_getparm`, and pid-file hooks in `ez_procstarted`. The implementation uses `struct ezbnode` from bnode internals, with fields such as command, proc, running/shutdown flags, last start, and inherited bnode error state.

Control flow translates the canonical command path during creation, starts the process on `BSTAT_NORMAL`, sends SIGTERM and arms a 60-second timeout on shutdown, sends SIGKILL in `ez_timeout` if needed, and restarts automatically from `ez_procexit` if the desired goal remains normal. Error-stop retry uses `bnode_IsErrorRetrying` and `errorStopDelay`.

State is in-memory except for `BosConfig` persistence of the command and optional pid files under the configured pid directory. Dependencies are bnode APIs, path translation, procmgmt signals, pid-file helpers, and file stat checks for binary-change restarts. Risks include command parsing in `ez_restartp`, fixed shutdown grace, sparse auxiliary status text, and pid-file cleanup consistency on unusual exits. Test signals include start/stop/restart, ignored SIGTERM leading to SIGKILL, binary ctime restart detection, pid-file creation/removal, and error retry delay.
