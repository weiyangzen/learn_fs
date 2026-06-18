# sources/distributed-fs/ceph-client/drivers/misc/ibmasm/ibmasm.h

## Purpose
`ibmasm.h` is the central private header for the IBM ASM service processor driver. It defines driver metadata, protocol constants, core state structures, debug helpers, and cross-module function prototypes.

## Important APIs, Types, and Functions
Important structures include `struct command`, `struct ibmasm_event`, `struct event_buffer`, `struct event_reader`, `struct reverse_heartbeat`, `struct ibmasm_remote`, and `struct service_processor`. Inline helpers include `get_timestamp()`, `command_put()`, and `command_get()`. The header declares command, event, heartbeat, reverse heartbeat, dot-command, low-level, remote input, filesystem, and optional UART APIs.

## Control Flow
The header defines how modules coordinate through `struct service_processor`: module probe initializes it, low-level interrupts dispatch messages, command/event/heartbeat code uses `sp->lock`, ibmasmfs exposes files, remote input registers input devices, and UART support optionally binds an 8250 port.

## State and Persistence
All driver runtime state is memory-resident under `service_processor` plus per-command/readers. Driver VPD strings and system-state constants are protocol payloads sent to the service processor.

## Dependencies and Integration Points
It includes kernel list, wait, spinlock, kref, device, input, interrupt, and time facilities. It is included by every ibmasm C file.

## Risks and Edge Cases
The global debug macro depends on `ibmasm_debug`. `command_put()` takes the command's service-processor lock around `kref_put()`, so kref callbacks must be lock-compatible. Structure layouts are private but tightly coupled across modules.

## Test Signals
Build all ibmasm configurations, validate command kref lifecycle, multi-service-processor initialization, debug logging, and stubbed UART behavior when serial 8250 is disabled.
