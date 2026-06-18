<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/repair/repair.cc -->
# sources/distributed-fs/coda/coda-src/repair/repair.cc

Purpose: command-line and interactive front end for Coda conflict repair. It owns global repair session state (`allowclear`, `session`, `repair_DebugFlag`, `ConflictObj`, `cfix`) and maps parser commands to library routines from `repcmds.h`/repair I/O.

Important APIs and flow: `main` initializes Coda configuration, installs the interrupt handler, handles the special `-remove <pathname>` path, supports a batch path for object/fixfile repair, and otherwise enters `Parser_commands`. `rep_BeginRepair` calls `BeginRepair`, classifies the conflict as directory or file, and exposes only relevant commands. `rep_CompareDirs` parses fix-file, ACL, owner, and mode options into `repinfo` and calls `CompareDirs`. `rep_DoRepair` calls `DoRepair`; `rep_RemoveInc` calls `RemoveInc`, ends the session, then removes the local object with `rmdir`/`unlink`; `rep_ReplaceInc` validates a replacement regular file and calls `dorep` after ending the repair session.

State/persistence: user-visible state is process-global and single-session only. Persistent changes happen through Venus/repair library calls and filesystem removal/replacement, not directly in this file.

Dependencies/integration: depends on Coda config (`venus.conf` mountpoint), parser library, token helpers, `BeginRepair`/`EndRepair`, `repair_getfid`, `CompareDirs`, `DoRepair`, `dorep`, and POSIX file operations.

Risks/test signals: header prototype for `getcompareargs` in `repair.h` is stale relative to this implementation. Several `strncpy` calls do not guarantee termination on max-length inputs. `rep_RemoveInc`/`rep_ReplaceInc` exit with `EXIT_FAILURE` even on successful repair, which may be historical but is surprising for scripts. Test with interactive begin/end, directory compare, file replace, invalid fixfile under `/coda`, SIGINT cleanup, and `-remove` on both file and directory conflicts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/repair/repair.cc -->
