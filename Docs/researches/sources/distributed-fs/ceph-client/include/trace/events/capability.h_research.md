# sources/distributed-fs/ceph-client/include/trace/events/capability.h

## Purpose
`capability.h` traces Linux capability checks after the kernel determines whether credentials are capable in a target user namespace.

## Important APIs, types, and functions
The single event is `cap_capable`. It records `const struct cred *`, target user namespace, capable namespace, capability number, and return code.

## Control flow
The common capability code emits the event after a check. The assignment stores `capable_ns` only on success (`ret == 0`); failures record it as `NULL`, making successful namespace derivation explicit.

## State and persistence behavior
The header stores no state. Event records contain pointer identities, capability id, and success/failure code.

## Dependencies and integration points
It depends on credential and user-namespace headers plus tracepoints. It integrates with security debugging, audit-adjacent observability, and BPF tools that inspect capability decisions.

## Risks and test signals
Risks include sensitive pointer/context exposure, pointer identity being boot-local, and high event volume on systems tracing all capability checks. Test signals are namespace capability tests for root/user namespaces, success and denial paths, and verification that failed checks show a null capable namespace.
