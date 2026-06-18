# sources/distributed-fs/ceph-client/fs/dlm/util.c

## Purpose
`util.c` converts selected Linux negative errno values to stable architecture-independent DLM wire errno values and back.

## Important APIs, Types, And Functions
Exports are `to_dlm_errno(int err)` and `from_dlm_errno(int err)`. The file defines DLM wire constants for `EDEADLK`, `EBADR`, `EBADSLT`, `EPROTO`, `EOPNOTSUPP`, `ETIMEDOUT`, and `EINPROGRESS`.

## Control Flow
Both functions are switch-based mappings. Unknown errors pass through unchanged.

## State And Persistence
No mutable state. The constants define wire compatibility behavior for DLM messages.

## Dependencies And Integration Points
Lock reply senders call `to_dlm_errno()` before writing result fields to DLM messages. Receivers and requestqueue logging call `from_dlm_errno()` before interpreting or printing results.

## Risks
Only higher errno values known to vary across architectures are mapped. Adding new wire-visible errno values requires stable constant selection and peer compatibility consideration.

## Test Signals
Unit-style tests or compile-time checks can verify round-trip mapping for all listed errors and pass-through behavior for common low-numbered errno values.
