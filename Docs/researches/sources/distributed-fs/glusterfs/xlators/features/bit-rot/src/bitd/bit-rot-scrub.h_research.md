<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-scrub.h -->
# sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-scrub.h

## Purpose
Public internal interface for bit-rot scrub scheduling, initialization, option handling, scanner entry point, and bad-object collection.

## APIs, Types, and Functions
Declares `br_fsscanner()`, schedule/reschedule/activate/deactivate/ondemand functions, `br_scrubber_handle_options()`, `br_scrubber_monitor_init()`, `br_scrubber_init()`, `br_collect_bad_objects_from_children()`, and `br_child_set_scrub_state()`.

## Control Flow, State, and Persistence
No direct control flow. The declarations expose the scrub subsystem to `bit-rot.c` and the state machine, allowing lifecycle code to start scanner threads, configure scrub behavior, and ask children for bad-object inventories.

## Dependencies and Integration
Includes `bit-rot.h`, so callers share `br_private_t`, `br_child_t`, xlator, dict, and scrub state definitions.

## Risks and Test Signals
Risks are contract drift between this header and `bit-rot-scrub.c`, especially for functions used by `bit-rot-ssm.c`. Build coverage and runtime calls from init/reconfigure/CLI status paths are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-scrub.h -->
