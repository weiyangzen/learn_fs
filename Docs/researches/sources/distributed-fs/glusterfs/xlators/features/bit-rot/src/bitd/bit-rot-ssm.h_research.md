<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-ssm.h -->
# sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-ssm.h

## Purpose
Defines scrub states, scrub events, and the state-machine entry point for bit-rot scrubbing.

## APIs, Types, and Functions
Defines `br_scrub_state_t` values `INACTIVE`, `PENDING`, `ACTIVE`, `PAUSED`, `IPAUSED`, `STALLED`, and `BR_SCRUB_MAXSTATES`; defines `br_scrub_event_t` values `SCHEDULE`, `PAUSE`, `ONDEMAND`, and `BR_SCRUB_MAXEVENTS`; forward-declares `struct br_monitor`; declares `br_scrub_state_machine(xlator_t *, gf_boolean_t)`.

## Control Flow, State, and Persistence
No direct control flow. The enum numeric order is part of the table contract in `bit-rot-ssm.c`, and current state is stored in `struct br_monitor` from `bit-rot.h`.

## Dependencies and Integration
Includes `glusterfs/defaults.h` for xlator and boolean-related defaults. Used by `bit-rot.h`, `bit-rot-scrub.c`, and `bit-rot-ssm.c`.

## Risks and Test Signals
Risks are enum reordering without updating the state table and adding states/events without table coverage. Build coverage plus transition tests for every enum value are the test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-ssm.h -->
