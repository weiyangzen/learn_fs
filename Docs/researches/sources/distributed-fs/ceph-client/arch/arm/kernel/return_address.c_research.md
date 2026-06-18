# sources/distributed-fs/ceph-client/arch/arm/kernel/return_address.c

Purpose: implements `return_address()` support for callers needing an ancestor return PC, using ARM stack unwinding.

Important APIs/types/functions: `return_address` seeds a `stackframe` from current frame pointer/SP/LR/label PC and walks frames until the requested level is reached.

Control flow: level zero returns the compiler return address directly; higher levels invoke `walk_stackframe` with a callback that counts frames and captures the requested PC.

State and persistence: stateless.

Dependencies and integration: used by tracing/debug facilities; depends on frame pointer or unwind support and stacktrace helpers.

Risks: unreliable when unwind metadata/frame pointers are unavailable or optimized; must avoid exposing invalid PCs. Test signals include ftrace/lockdep callers using return addresses and stacktrace selftests.
