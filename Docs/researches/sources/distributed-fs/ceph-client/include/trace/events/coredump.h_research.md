# sources/distributed-fs/ceph-client/include/trace/events/coredump.h

## Purpose
`coredump.h` defines a stable tracepoint emitted when a coredump attempt starts.

## Important APIs, types, and functions
The single event is `coredump`. It records the triggering signal number and current task command name.

## Control flow
Coredump code emits this event at the beginning of a dump attempt, before the rest of dump generation succeeds or fails.

## State and persistence behavior
No state is stored by the header. Records snapshot `sig` and `current->comm`; success, file path, and dump size are not recorded here.

## Dependencies and integration points
It depends on scheduler task state and tracepoints. It integrates with observability tools that monitor process crashes without parsing kernel logs.

## Risks and test signals
Risks include assuming the event means a core file was written and relying on `comm` rather than pid/exe path. Test signals are crash tests that trigger core-dumping signals and verify the event appears before dump completion.
