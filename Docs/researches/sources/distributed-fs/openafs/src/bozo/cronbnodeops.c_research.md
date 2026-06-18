# sources/distributed-fs/openafs/src/bozo/cronbnodeops.c

`cronbnodeops.c` implements the `cron` bnode type: a bosserver-supervised command that runs once or periodically according to a `ktime` schedule. It is used for administrative scheduled jobs and by `bos salvage` for temporary one-shot salvager execution.

Important APIs are the `cronbnode_ops` vtable, `cron_create`, `ScheduleCronBnode`, `cron_timeout`, `cron_setstat`, `cron_procexit`, `cron_getstat`, `cron_getstring`, and `cron_getparm`. `struct cronbnode` stores the command, original schedule string, parsed `ktime`, next run time, process pointer, last start time, and shutdown/running flags.

Control flow parses the schedule at creation, translates the command from canonical bin path to local path, and computes `when`. For one-shot jobs (`when == 0`), `ScheduleCronBnode` starts the process immediately and deletes the bnode after it has run. For periodic jobs, it sets bnode timeouts until the next run. Shutdown sends SIGTERM and schedules a SIGKILL after `SDTIME`; process exit logs signal/nonzero status, clears state, recomputes the next run, and reschedules.

State is mostly in memory; persistence occurs indirectly because bosserver writes bnode type, command, and schedule string to `BosConfig`. Dependencies are bnode process APIs, `ktime`, path translation, LWP/procmgmt, and logging. Risks include schedule parser edge cases, one-shot self-deletion while active, fixed 60-second shutdown grace, command path translation constraints, and no binary-change restart support (`cron_restartp` returns 0). Test signals include one-shot lifecycle, periodic timeout computation, shutdown/kill behavior, status strings, and salvage-tmp compatibility.
