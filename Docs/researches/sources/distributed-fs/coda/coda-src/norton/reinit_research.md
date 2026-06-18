# sources/distributed-fs/coda/coda-src/norton/reinit

Purpose: Bourne shell orchestration script for server RVM reinitialization using `norton-reinit`, `rvmutl`, and `rdsinit`.

Flow/state: prompts for confirmation, ensures backup volumes are purged or acknowledged, blocks server startup by writing `/vice/srv/pid`, gathers skip-volume and RVM geometry parameters, dumps state to a user-provided file, asks at point of no return, reinitializes the RVM log/data heap, reloads the dump, removes the pid blocker, and leaves dump cleanup to the operator.

Dependencies and risks: assumes `/vice`, `VolumeList`, optional `skipsalvage`, and required tools in `PATH`. It is intentionally interactive and destructive. Risks include manual input mistakes, pid-file based server exclusion, no shell quoting around many variables, and partial failure requiring manual cleanup. Test signal is full operator rehearsal in a disposable server environment.
