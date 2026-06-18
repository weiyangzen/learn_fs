# sources/distributed-fs/ceph-client/net/vmw_vsock/vsock_addr.c

## Purpose
This file provides small exported helpers for initializing, validating, comparing, binding, unbinding, and casting AF_VSOCK socket addresses.

## Important APIs, types, and functions
`vsock_addr_init()` clears a `struct sockaddr_vm` and sets family, CID, and port. `vsock_addr_validate()` rejects null pointers, non-`AF_VSOCK` families, and unsupported `svm_flags` values, currently allowing only `VMADDR_FLAG_TO_HOST`. `vsock_addr_bound()` tests whether the port is not `VMADDR_PORT_ANY`; `vsock_addr_unbind()` resets to `VMADDR_CID_ANY` and `VMADDR_PORT_ANY`. `vsock_addr_equals_addr()` compares CID and port. `vsock_addr_cast()` validates a generic `sockaddr_unsized` buffer length, casts it to `sockaddr_vm`, and validates the result.

## Control flow
The helpers are direct and side-effect-free except for address initialization/reset. Cast validation first checks the user-provided length to avoid short-address access, then delegates to `vsock_addr_validate()`.

## State and persistence
No global state is stored. The only mutations are to caller-provided `sockaddr_vm` objects.

## Dependencies and integration points
The functions are exported with `EXPORT_SYMBOL_GPL` and used by AF_VSOCK core and transports for bind, connect, address comparison, and userspace address parsing. They depend on `net/vsock_addr.h`, VMADDR constants, and Linux socket address conventions.

## Risks
Flag validation must remain aligned with the AF_VSOCK ABI; accepting unknown flags can alter routing semantics, while rejecting newly valid flags without updating this helper can block new features. The cast helper relies on callers passing the true userspace sockaddr length.

## Test signals
Unit tests or syscall-level tests should cover null input, wrong family, unsupported flags, short lengths, wildcard unbind state, equality behavior, and valid `VMADDR_FLAG_TO_HOST` addresses.
