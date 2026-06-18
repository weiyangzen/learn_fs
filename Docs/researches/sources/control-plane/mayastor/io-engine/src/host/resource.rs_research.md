# sources/control-plane/mayastor/io-engine/src/host/resource.rs

## Purpose
This file implements the host resource-usage query used by the gRPC host API. It is a small async wrapper around `getrusage(2)` for the current io-engine process.

## Important APIs, types, and functions
`Usage(pub libc::rusage)` is a transparent result wrapper so upper layers can serialize or map the raw libc structure. `get_resource_usage()` is the public async entry point and returns `RUSAGE_SELF`. The private `getrusage(who)` function owns the unsafe syscall boundary by allocating `MaybeUninit<libc::rusage>`, calling `libc::getrusage`, returning `Error::last_os_error()` on negative return, and `assume_init` only after success.

## Control flow
The call path is linear: public async method, syscall helper, raw `rusage` wrap. There is no reactor handoff or blocking work beyond the syscall itself.

## State and persistence behavior
No state is persisted or cached. The returned `rusage` is a point-in-time kernel snapshot of process CPU, memory, page fault, context switch, and I/O counters.

## Dependencies and integration points
The module depends on `libc` and standard `std::io::Error`. It integrates through `host` and gRPC code that exposes process diagnostics to the control plane.

## Risks and test signals
The unsafe block is narrow and guarded by the syscall return value. The code assumes the platform has libc `getrusage` and that `libc::rusage` layout matches the kernel ABI. Tests are likely integration-level host RPC tests; this file has no local unit tests.
