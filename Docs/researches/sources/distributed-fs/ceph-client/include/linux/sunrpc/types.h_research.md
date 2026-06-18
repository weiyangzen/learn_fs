# sources/distributed-fs/ceph-client/include/linux/sunrpc/types.h

Purpose: provides generic SUNRPC includes and a small signal-pending shorthand used by older SUNRPC code.

Important APIs and types: `signalled()` expands to `signal_pending(current)`.

Control flow: callers use `signalled()` to decide whether an RPC operation should abort or return restart/interruption status.

State and persistence: no state is owned here.

Dependencies and integration points: includes timers, signal-aware scheduler state, workqueues, SUNRPC debug support, and lists. It is a common foundational include for other SUNRPC headers.

Risks and test signals: risks are macro opacity around `current` and accidental use in contexts where signal state is irrelevant. Test via signal-interrupted RPC waits and compile coverage of SUNRPC headers.
