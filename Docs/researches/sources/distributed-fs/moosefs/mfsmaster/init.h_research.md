# sources/distributed-fs/moosefs/mfsmaster/init.h

## Purpose
`init.h` defines master-process module startup wiring and command-line option macros for `mfsmaster`. It centralizes the ordered initialization tables for normal startup and metadata restore mode.

## Important APIs, Types, And Macros
`MODULE_OPTIONS_GETOPT` declares short options `i`, `a`, and `x`. `MODULE_OPTIONS_SWITCH` maps those flags to metadata-manager behavior: `-i` calls `meta_setignoreflag`, `-a` calls `meta_allowautorestore`, and `-x` calls `meta_incverboselevel`. `MODULE_OPTIONS_SYNOPSIS` and `MODULE_OPTIONS_DESC` provide user-facing usage text.

The local `runfn` typedef describes module init functions returning `int`. `RunTab`, `LateRunTab`, and `RestoreRunTab` are sentinel-terminated arrays of `{fn, name}` pairs. The sentinel uses a null function pointer and `"****"`.

`RunTab` normal startup order is: random generator, background saver, glob cache, multilan map, changelog, missing log, data cache manager, exports, topology, metadata, charts, metalogger service, chunkserver service, and client service. Inline comments note important ordering: missing log and data cache manager must be before filesystem/client initialization.

`LateRunTab` is currently empty except for the sentinel. `RestoreRunTab` initializes the data cache manager and then runs `meta_restore`.

## Control Flow
The main master program is expected to include this header and iterate `RunTab` during normal startup, `LateRunTab` for any late initialization phase, and `RestoreRunTab` when restoring metadata. Command-line parsing is expected to splice the macro switch into a larger option handler.

This style makes module ordering compile-time static. Adding a module requires editing the table and selecting the correct position relative to dependencies.

## State And Persistence Behavior
The header does not own state directly, but its option macros mutate metadata restore/load state before initialization. `-i` enables ignoring some metadata structure errors, `-a` enables automatic changelog restore, and `-x` increases restore/load verbosity.

Persistence integration is indirect but critical: `meta_init` and `meta_restore` are the gates for loading metadata, replaying logs, and building filesystem state. `bgsaver_init`, `changelog_init`, and `missing_log_init` also participate in durable master behavior.

## Dependencies And Integration Points
The header includes each module whose init function appears in the tables: topology, exports, data cache manager, master-to-metalogger service, master-to-chunkserver service, master-to-client service, metadata, random, changelog, charts, missing log, glob engine, background saver, and multilan.

It integrates with the master executable's option parsing and generic run-table executor. The restore table integrates with metadata recovery tools/paths rather than normal network service startup.

## Risks
Initialization order is the main risk. The ordering comments are sparse, and dependency constraints are encoded only by array position. Moving `missing_log_init`, `dcm_init`, or `meta_init` can create startup bugs that compile cleanly.

The `-i` option is intentionally dangerous because it can ignore metadata structural errors. The description text says not to use it unless restoration alternatives are exhausted, so tests and operational docs should treat it as emergency-only.

The usage description contains a typo (`absoluttely`), which is harmless but user-visible.

## Test Signals
Useful tests include normal startup run-table execution order, restore-mode execution order, command-line option parsing for `-i`, `-a`, `-x`, and `-xx`, and failure injection where an init function returns an error. Startup smoke tests should verify that metadata loads after its prerequisites and network services start only after metadata-dependent modules initialize.
