<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/util.pm -->
# sources/distributed-fs/openafs/src/tests/OpenAFS/util.pm

## Purpose
Provides shared AFStools initialization, tracing, global parameters, command-path discovery, and AFS-style option parsing used by the Perl command wrappers and tests.

## Important APIs, Types, And Functions
Exports `AFS_Init`, `AFS_Trace`, and `AFS_SetParm`; optional exports include `%AFS_Parms`, `%AFS_Trace`, `%AFS_Help`, `%AFScmd`, `GetOpts_AFS`, and `GetOpts_AFS_Help`. `_which_opt` handles abbreviated option matching.

## Control Flow
`AFS_Init` sets default auth level, config directory, and local cell, then searches configured command paths for every command in `@CmdList`, caching paths in `%AFScmd`. `GetOpts_AFS` consumes explicit and positional AFS-style options, supports boolean, scalar, and multi-argument options, applies defaults, and dies on missing/extra arguments unless help was requested.

## State And Persistence
Stores global in-process state in `%AFS_Parms`, `%AFS_Trace`, `%AFScmd`, and `%AFS_Help`. It reads local cell configuration through `OpenAFS::afsconf` but writes no persistent state.

## Dependencies And Integration Points
Depends on `OpenAFS::config` and requires `OpenAFS::afsconf` to avoid circular imports. All wrapper modules use `%AFScmd` and `%AFS_Parms`; `wrapper.pm` uses tracing and command paths.

## Risks And Test Signals
Missing any command in `@CmdList` makes `AFS_Init` fail even if a specific test needs only one binary. Abbreviation matching returns the ambiguous input unchanged, which later looks like an unknown option. Test signals are successful initialization and option parser coverage for required, default, multi-argument, abbreviated, and unadorned arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/util.pm -->
