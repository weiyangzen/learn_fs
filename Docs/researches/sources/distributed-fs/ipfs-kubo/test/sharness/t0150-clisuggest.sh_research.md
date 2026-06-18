## sources/distributed-fs/ipfs-kubo/test/sharness/t0150-clisuggest.sh

Purpose: tests CLI typo suggestions for unknown commands both offline and through a daemon.

Important APIs and helpers: defines `test_suggest`, uses `test_must_fail ipfs kog`, `test_must_fail ipfs li`, `grep`, `test_fsh`, and daemon lifecycle helpers.

Control flow and state: initializes a repo, runs typo cases offline, starts the daemon, repeats the cases online, and kills the daemon. The command state is transient; no persistent config is modified beyond repo initialization.

Dependencies and integration points: covers command parser suggestion logic, CLI error output, and daemon command dispatch consistency.

Risks and test signals: catches missing or misleading suggestions and offline/online divergence. Passing requires singular "Did you mean this?" with `log` and plural "Did you mean any of these?" with both `ls` and `log`.
