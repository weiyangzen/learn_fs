<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-ssm.c -->
# sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-ssm.c

## Purpose
Scrub state machine implementation for bit-rot. It maps current scrub monitor state and requested event to scheduling, pausing, resuming, or on-demand actions.

## APIs, Types, and Functions
Implements action functions `br_scrub_ssm_noop()`, `br_scrub_ssm_state_pause()`, `br_scrub_ssm_state_ipause()`, `br_scrub_ssm_state_active()`, and `br_scrub_ssm_state_stall()`, plus `br_scrub_state_machine()`. The static `br_scrub_ssm[BR_SCRUB_MAXSTATES][BR_SCRUB_MAXEVENTS]` table maps inactive/pending/active/paused/ipaused/stalled states against schedule/pause/ondemand events.

## Control Flow, State, and Persistence
`br_scrub_state_machine()` reads `priv->scrub_monitor.state`, derives the event from the on-demand flag or `_br_child_get_scrub_event()`, then invokes the table entry. Actions call scheduler functions in `bit-rot-scrub.c` or update `scrub_monitor->state` directly. State is volatile monitor state; no disk persistence occurs here.

## Dependencies and Integration
Depends on `bit-rot-ssm.h`, `bit-rot-scrub.h`, message IDs, and `br_private_t` definitions from `bit-rot.h`. Called by monitor startup, reconfigure, and on-demand control paths in the main bit-rot translator.

## Risks and Test Signals
Risks include invalid state/event indexes if enums drift, no null validation on `this->private`, subtle differences between paused and initially paused states, and on-demand no-op behavior in several states. Test signals are transition tests for schedule, pause, resume, stalled active scrub, and on-demand requests from pending versus non-pending states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-ssm.c -->
