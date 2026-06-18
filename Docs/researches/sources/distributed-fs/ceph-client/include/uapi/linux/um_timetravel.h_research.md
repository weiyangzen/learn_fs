# sources/distributed-fs/ceph-client/include/uapi/linux/um_timetravel.h

Purpose: Defines the User-Mode Linux time-travel protocol for coordinating simulated time with an external calendar/controller.

Important APIs/types/functions: `struct um_timetravel_msg` carries operation, sequence, and nanosecond time. Operations include ACK, START, REQUEST, WAIT, GET, UPDATE, RUN, FREE_UNTIL, GET_TOD, and BROADCAST. Shared-memory support defines max fd count, fd indices, start ACK ID mask, version 2, capability/flag enums, `union um_timetravel_schedshm_client`, and `struct um_timetravel_schedshm` containing version, length, free-until, current time, running client ID, max clients, and per-client request records.

Control flow: A UML instance sends START, negotiates optional shared-memory fds, requests a run time, waits, and resumes when the controller sends RUN or permits FREE_UNTIL. Shared-memory-capable clients publish requests and current time in shared memory to avoid messages for common operations.

State and persistence behavior: Protocol state is live simulation state: sequence numbers, requested run times, current time, free-until horizon, running client, and per-client capabilities. It is not persistent beyond the controller/UML session.

Dependencies and integration points: Includes `linux/types.h`; integrates with UML, simulation controllers, Unix sockets with fd passing, shared memory mappings, and coordinated virtual time tests.

Risks: Shared memory has explicit writer ownership rules; violating them can corrupt scheduling. Sequence mismatches, stale `free_until`, incorrect controller time-domain conversion, and missing ACK expectations can deadlock simulations.

Test signals: Simulate START/REQUEST/WAIT/RUN cycles, sequence mismatch handling, shared-memory version fallback, multi-client request ordering, FREE_UNTIL behavior, broadcast delivery, fd passing, and log-fd flushing.
