# sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/afsrm.c

Purpose: command-line utility to forcibly remove legacy AFS software without InstallShield.

Important APIs/types/functions: `DoClient34()` calls `Client34Eradicate(FALSE)` and prints success/failure. `SetupCmd()` registers the `client34` command through the OpenAFS command package. `main()` initializes command errors, registers syntax, and dispatches arguments.

Control flow: command execution is delegated to `cmd_Dispatch()`. The only supported subcommand removes an AFS 3.4a client and does not preserve config because it passes `FALSE`.

State/persistence: no internal persistent state. The called removal routine can delete services, files, registry keys, PATH/provider entries, and start-menu entries.

Dependencies/integration: depends on OpenAFS `cmd` library, Windows APIs, and `forceremove.h`.

Risks/test signals: a mistaken invocation can destructively remove legacy client artifacts. Tests should mock or sandbox `Client34Eradicate()`, verify command registration, return-code propagation, and printed status for success/failure.
