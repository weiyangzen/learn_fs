# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/rtla.c

## Purpose
`rtla.c` is the top-level command dispatcher for the RTLA executable. It supports both direct aliases (`osnoise`, `hwnoise`, `timerlat`) and the normal `rtla COMMAND ...` form.

## Important APIs, Types, and Functions
`rtla_usage()` prints version, usage, and command list. `run_command()` checks an argument position and dispatches to `osnoise_main()`, `hwnoise_main()`, or `timerlat_main()`. `main()` handles alias mode, help flags, command dispatch, and usage failure.

## Control Flow
`main()` first tries `run_command(argc, argv, 0)` so an executable invoked as `osnoise` or `timerlat` can dispatch by `argv[0]`. If not an alias, it requires at least one command argument, handles `-h`/`--help`, then calls `run_command()` at position 1. Command mains generally exit directly.

## State and Persistence
This file owns no persistent state; it delegates all tracefs and runtime effects to command modules.

## Dependencies and Integration Points
It includes `osnoise.h` and `timerlat.h` and depends on those modules' command entry points. It uses the compile-time `VERSION` macro.

## Risks and Edge Cases
Alias dispatch compares the full `argv[0]` string, so invocation through a path like `/usr/bin/timerlat` may not match unless the executable name is stripped elsewhere by the environment. Unknown commands fall through to usage with exit status 1.

## Test Signals
Run `rtla -h`, `rtla --help`, `rtla osnoise -h`, `rtla timerlat -h`, unknown commands, and symlink/alias invocations to verify dispatch behavior.
