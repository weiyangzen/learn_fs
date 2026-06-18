# sources/distributed-fs/ceph/src/osd/scrubber/osd_scrub.h

## Purpose
Declares `OsdScrub`, the OSDService component responsible for OSD-wide scrub initiation, queue forwarding, resource accounting, environmental checks, and scrub perf counters.

## APIs and Control Flow
Public methods include `initiate_scrub()`, `dump_scrubs()`, `dump_scrub_reservations()`, `on_config_change()`, queue manipulation, local resource inc/dec, blocked-PG accounting, `scrub_sleep_time()`, `scrub_time_permit()`, `update_load_average()`, and `get_perf_counters()`. Private helpers compute restrictions and start one PG scrub.

## State, Dependencies, and Integration
Owns `ScrubResources`, `ScrubQueue`, perf-counter map, CPU count cache, and service/config references. It depends on `osd_scrub_sched.h`, `scrub_resources.h`, scrub common types, and OSD perf counters. PG scrubbers use it to register jobs and reserve resources.

## Risks and Test Signals
The class itself has no single lock; protected queue state lives in `ScrubQueue`. Perf counters require explicit destruction. Tests should validate resource forwarding, queue forwarding, time/load decisions, and perf-counter indexing for replicated/EC shallow/deep scrubs.
