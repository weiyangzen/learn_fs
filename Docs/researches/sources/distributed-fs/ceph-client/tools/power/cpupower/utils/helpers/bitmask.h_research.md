# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/bitmask.h

## Purpose
Declares the local bitmask type and operations used throughout cpupower for CPU lists.

## Important APIs, Types, and Functions
Defines `struct bitmask` with a bit count and unsigned-long storage pointer, plus allocation, free, mutation, query, parsing, and display prototypes.

## Control Flow, State, and Persistence
The header has no runtime flow. It exposes ownership rules implicitly: callers allocate masks, pass them to helpers, and must free them. Parser/display semantics are defined by `bitmask.c`.

## Dependencies and Integration Points
Included by the top-level dispatcher and most CPU-selection-aware subcommands. It avoids depending on external libbitmask availability.

## Risks and Test Signals
Because the struct is public, callers could mutate internals directly. Tests should build all users and cover ABI expectations for parser and display formatting.
