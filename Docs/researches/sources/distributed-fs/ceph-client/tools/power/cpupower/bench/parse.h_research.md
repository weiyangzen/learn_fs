<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bench/parse.h -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/bench/parse.h

## Purpose
Defines cpufreq-bench runtime configuration and parser API. `struct config` stores sleep/load timings, steps, cycle/round counts, target CPU, governor name, scheduler priority enum, verbosity, output handle, and an optional output filename pointer.

## Important APIs, Types, And Functions
State is owned by callers that allocate through `prepare_default_config()` and eventually free the struct and close output if needed. Dependencies are `FILE` being declared by including stdio before this header in users, and parser implementations in `parse.c`. Risks include missing include guards, a fixed 15-byte governor buffer, comments promising `output_filename` ownership while implementation does not consistently set it, and header reliance on include order for `FILE`. Test signals are compiler warnings with strict include ordering, long governor names, and config lifetime checks.

## Control Flow
State is owned by callers that allocate through `prepare_default_config()` and eventually free the struct and close output if needed. Dependencies are `FILE` being declared by including stdio before this header in users, and parser implementations in `parse.c`. Risks include missing include guards, a fixed 15-byte governor buffer, comments promising `output_filename` ownership while implementation does not consistently set it, and header reliance on include order for `FILE`. Test signals are compiler warnings with strict include ordering, long governor names, and config lifetime checks.

## State And Persistence
State is owned by callers that allocate through `prepare_default_config()` and eventually free the struct and close output if needed. Dependencies are `FILE` being declared by including stdio before this header in users, and parser implementations in `parse.c`. Risks include missing include guards, a fixed 15-byte governor buffer, comments promising `output_filename` ownership while implementation does not consistently set it, and header reliance on include order for `FILE`. Test signals are compiler warnings with strict include ordering, long governor names, and config lifetime checks.

## Dependencies And Integration Points
State is owned by callers that allocate through `prepare_default_config()` and eventually free the struct and close output if needed. Dependencies are `FILE` being declared by including stdio before this header in users, and parser implementations in `parse.c`. Risks include missing include guards, a fixed 15-byte governor buffer, comments promising `output_filename` ownership while implementation does not consistently set it, and header reliance on include order for `FILE`. Test signals are compiler warnings with strict include ordering, long governor names, and config lifetime checks.

## Risks And Edge Cases
State is owned by callers that allocate through `prepare_default_config()` and eventually free the struct and close output if needed. Dependencies are `FILE` being declared by including stdio before this header in users, and parser implementations in `parse.c`. Risks include missing include guards, a fixed 15-byte governor buffer, comments promising `output_filename` ownership while implementation does not consistently set it, and header reliance on include order for `FILE`. Test signals are compiler warnings with strict include ordering, long governor names, and config lifetime checks.

## Test Signals
State is owned by callers that allocate through `prepare_default_config()` and eventually free the struct and close output if needed. Dependencies are `FILE` being declared by including stdio before this header in users, and parser implementations in `parse.c`. Risks include missing include guards, a fixed 15-byte governor buffer, comments promising `output_filename` ownership while implementation does not consistently set it, and header reliance on include order for `FILE`. Test signals are compiler warnings with strict include ordering, long governor names, and config lifetime checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/bench/parse.h -->
