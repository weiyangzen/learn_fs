# sources/distributed-fs/openafs/src/bucoord/main.c

## Purpose
Defines the `backup` program entrypoint. It initializes error tables, RX/LWP, VLDB and BUDB clients, backup configuration, and status monitoring; registers all command syntaxes; dispatches one-shot, interactive, and load-file commands; and waits for background jobs before non-interactive exit.

## Important APIs, Types, And Functions
Important functions are `InitErrTabs`, `bc_HandleMisc`, `bc_InitTextConfig`, `backupInit`, `MyBeforeProc`, `doDispatch`, `bc_interactCmd`, `add_std_args`, and `main`. Global process state includes `localauth`, `interact`, `nobutcauth`, `tcell`, `tokenExpires`, `whoami`, `bcInit`, `DefaultConfDir`, `dispatchLock`, and `lineBuffer`.

## Control Flow
`main` initializes locks and error tables, decides whether to enter interactive mode, registers a `cmd` before-proc, then builds syntaxes for dump, restore, configuration, tape, database, and status commands. `MyBeforeProc` lazily performs full initialization on the first real command, capturing standard auth arguments from command parameter slots. `backupInit` creates `bc_globalConfig`, initializes LWP and RX, sets RX dead time, initializes VLDB and BUDB clients, initializes status locks/queue, and starts the status watcher LWP. `doDispatch` serializes `cmd_Dispatch` with `dispatchLock`, handles `dump -file` by opening the requested command file, echoes lines, skips blanks/comments, parses lines, and recursively dispatches them up to `MAXRECURSION`. Non-interactive mode waits for jobs through `bc_WaitForNoJobs`; interactive mode reads lines with `LWP_GetLine` until EOF.

## State And Persistence
Most state is process-global and transient. `bc_InitTextConfig` initializes BUDB text handles for tape hosts, volume sets, and dump schedules with version `-1` and temp file name slots; actual text content is fetched lazily by update functions. Persistent changes are made by command handlers through BUDB and butc, not by `main.c` directly.

## Dependencies And Integration Points
Depends on OpenAFS `cmd`, RX, LWP, auth/cell config, VLDB, BUDB, butm/butc/butx error tables, status watcher from `bc_status.c`, model/config functions, and every command handler declared in `bucoord_internal.h`. The command parameter indexes used by `add_std_args` and `MyBeforeProc` must remain aligned.

## Risks And Test Signals
Command registration relies on hard-coded parameter indexes for common auth flags, which can break if syntaxes shift. `doDispatch` uses global `loadFile`/`dontExecute` for recursive load-file handling and serializes all dispatches to avoid parser corruption. Interactive startup can defer initialization until after help/apropos-like commands. Test signals include `backup -help` without full init, non-interactive standard auth parsing, interactive prompt dispatch, load-file recursion cutoff, blank/comment handling, command-line-too-long handling, job wait exit status, and status watcher startup failure.
