# sources/distributed-fs/ceph-client/include/linux/apm-emulation.h

## Purpose
Defines architecture-neutral APM emulation status data and event injection hooks for systems that emulate APM behavior without a PC BIOS implementation.

## Important APIs, Types, And Functions
`struct apm_power_info` contains AC line state, battery state/flags, battery life, remaining time, and time units. It declares the function pointer `apm_get_power_status` for machine-specific population and `apm_queue_event(apm_event_t event)` for queuing suspend-related APM events.

## Control Flow, State, And Persistence
Consumers call `apm_get_power_status()` through the global function pointer to fill status with safe defaults for unspecified fields. `apm_queue_event()` feeds the APM event stream. Persistent battery state is not stored here; it is sampled from architecture/platform code.

## Dependencies And Integration Points
Includes `linux/apm_bios.h` for APM event types and BIOS constants. Integrates handheld/ARM APM emulation, userspace APM interfaces, and suspend event reporting.

## Risks And Test Signals
Risks include uninitialized status fields, wrong units, and event ordering differences from BIOS-backed APM. Tests should inspect `/proc/apm` style output where available, verify suspend event delivery, handle unknown battery values, and build architectures that set or omit `apm_get_power_status`.
