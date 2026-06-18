<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/repair/repair.h -->
# sources/distributed-fs/coda/coda-src/repair/repair.h

Purpose: client-only repair tool interface. It defines repair session states, declares shared globals, declares parser command handlers, and provides the initial help text shown by the repair executable.

Important APIs/types: `NOT_IN_SESSION`, `FILE_SESSION`, and `DIRECTORY_SESSION` encode the active repair mode. `ConflictObj` is the active `struct conflict *` returned by `BeginRepair`; `allowclear`, `interactive`, `repair_DebugFlag`, and `session` are shared process flags. The declared command handlers are `rep_BeginRepair`, `rep_ClearInc`, `rep_CompareDirs`, `rep_DoRepair`, `rep_EndRepair`, `rep_Exit`, `rep_Help`, `rep_RemoveInc`, and `rep_ReplaceInc`.

Control flow/integration: included by `repair.cc`, and transitively exposes declarations from `repcmds.h`. It is a thin adapter header between the command parser and Coda repair library.

State/persistence: no storage is defined here, but declarations describe singleton process state used by the repair CLI. Persistence is delegated to the lower repair library and Venus kernel/user interfaces.

Dependencies: `repcmds.h` supplies `struct conflict` and repair command APIs. The signal handler declaration references `struct sigcontext`, making this header tied to legacy platform signal ABI assumptions.

Risks/test signals: the `getcompareargs` prototype accepts many `char **` parameters, but `repair.cc` implements `getcompareargs(int,char **,char **,struct repinfo *)`; this mismatch is a compile-time/API drift risk. `interactive` is declared but not defined in `repair.cc`, so its owner must be elsewhere or dead. Compile the repair tool with warnings enabled and exercise all parser command declarations against the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/repair/repair.h -->
