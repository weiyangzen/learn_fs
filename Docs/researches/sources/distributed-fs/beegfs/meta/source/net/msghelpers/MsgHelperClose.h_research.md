<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperClose.h -->
# sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperClose.h

## Purpose
Declares static close helpers used by metadata close and cleanup messages.

## Important APIs, Types, and Functions
Public methods are `closeFile()`, `closeSessionFile()`, `closeChunkFile()`, and `unlinkDisposableFile()`. Private methods are `closeChunkFileSequential()` and `closeChunkFileParallel()`. The class is non-instantiable through a private constructor.

## Control Flow, State, and Persistence
The signatures expose caller-owned outputs for disposal unlink, hardlink count, last-writer state, dynamic attributes, and mirrored timestamps. Persistent effects are delegated to implementation helpers and `MetaStore`.

## Dependencies and Integration Points
Includes common types and `MetaStore`. Integrates with session/opening messages and storage target close work.

## Risks and Test Signals
Callers must pass valid output pointers for required values. Tests should verify all optional outputs are filled only when expected and default/null dynamic attribute pointers are safe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperClose.h -->
