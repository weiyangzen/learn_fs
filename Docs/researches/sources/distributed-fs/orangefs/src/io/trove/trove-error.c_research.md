# sources/distributed-fs/orangefs/src/io/trove/trove-error.c

## Purpose
Maps positive system `errno` values to OrangeFS/TROVE `PVFS_error` constants for DBPF and other TROVE code paths.

## Important APIs, Types, And Functions
Defines `__trove_errno_mapping_t`, static `s_trove_error_map[]`, and `PVFS_error trove_errno_to_trove_error(int errno_value)`. The mapping covers common filesystem, memory, locking, IPC, network, protocol, overflow, restart, cancellation, access, and range errors.

## Control Flow
`trove_errno_to_trove_error` returns non-positive inputs unchanged, linearly scans the mapping table for a matching `errno_value`, returns the mapped TROVE constant, logs an unknown-errno error if no entry matches, and returns sentinel `4242`.

## State And Persistence
No mutable or persistent state. The static mapping table is process constant data.

## Dependencies And Integration Points
Includes `errno.h`, gossip logging, TROVE headers, and is called by DBPF management/open-cache/sync/bstream paths when translating POSIX syscall failures into negative TROVE errors.

## Risks And Test Signals
Risks include platform errno macros that are undefined or aliases, incomplete mapping causing sentinel errors, and callers double-negating values. Tests should verify representative errno conversions, non-positive passthrough, unknown errno logging/sentinel, and build portability across target systems.
