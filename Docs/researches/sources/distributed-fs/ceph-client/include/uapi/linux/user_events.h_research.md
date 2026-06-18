# sources/distributed-fs/ceph-client/include/uapi/linux/user_events.h

Purpose: Defines the user_events tracing ABI for registering, unregistering, and writing user-defined trace events.

Important APIs/types/functions: System names are `user_events` and `user_events_multi`, with prefix `u:`. `DYN_LOC(offset, size)` encodes dynamic field locations. Registration flags include persistence, multi-format, and other user-event behavior flags. `struct user_reg` carries size, enable bit location, flags, event name/format, write index, and enable address/bit metadata. `struct user_unreg` carries size and disable metadata. Ioctls `DIAG_IOCSREG`, `DIAG_IOCSDEL`, and `DIAG_IOCSUNREG` register, delete, and unregister events through the tracing diagnostics interface.

Control flow: Userspace registers an event format, receives an enable bit/index, checks whether tracing is enabled, then writes event payloads to the user_events data path. Unregister/delete ioctls remove per-process or named event registrations.

State and persistence behavior: Registration creates tracing metadata in kernel tracefs/user_events state. Enable bits are shared with userspace so tracing can be skipped cheaply. Persistent events may outlive the registering process depending on flags and kernel policy.

Dependencies and integration points: Includes `linux/types.h` and `linux/ioctl.h`; integrates with ftrace/tracefs, perf/BPF consumers, dynamic event format parsing, and observability agents.

Risks: User-provided format strings and dynamic locations require strict validation. Enable address handling crosses user/kernel memory boundaries. Event deletion must not race active writers/readers.

Test signals: Register simple and dynamic events, verify enable bit toggling through tracefs, write payloads and read trace output, unregister/delete, test duplicate formats, invalid flags/addresses, and multi-process persistence behavior.
