# sources/distributed-fs/ceph-client/include/linux/sched/jobctl.h

Purpose: defines `task_struct.jobctl` flags and helper prototypes for job control stops, ptrace traps, and freezer-related stop states.

Important APIs and types: `JOBCTL_*` bit definitions, stop/trap/pending masks, `task_set_jobctl_pending()`, `task_clear_jobctl_trapping()`, and `task_clear_jobctl_pending()` are the key exports.

Control flow: signal and ptrace code sets pending stop/trap bits under signal locks, tasks consume them while entering stopped/traced states, and wakeup paths inspect `JOBCTL_STOPPED`/`JOBCTL_TRACED`.

State and persistence: state is the per-task `jobctl` bitfield, protected primarily by `sighand->siglock`. It lasts across signal-stop/ptrace/freezer transitions.

Dependencies and integration points: integrates signal delivery, ptrace, cgroup freezer, task state reporting, and scheduler wakeups.

Risks and test signals: risks include bit overlap with stop signal mask, missed clearing of trapping state, and stop/ptrace/freezer race regressions. Test job-control stop/continue, ptrace attach/detach/listen, freezer interactions, and signal wakeups.
