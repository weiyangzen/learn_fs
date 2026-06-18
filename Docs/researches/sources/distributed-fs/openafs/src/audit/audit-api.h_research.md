# sources/distributed-fs/openafs/src/audit/audit-api.h

## Purpose
`audit-api.h` defines the private plugin interface used by audit output backends.

## Important APIs, types, and functions
It defines `OSI_AUDIT_MAXMSG` as 2048 and `struct osi_audit_ops`. Required callbacks are `send_msg`, `open_file`, `print_interface_stats`, `create_interface`, and `close_interface`. Optional callbacks are `set_option` and `open_interface`.

## Control flow
No runtime control flow is present. `audit.c` invokes callbacks in a documented sequence: create/open during option processing, optional open after daemon thread setup, send during events, stats on request, and close at shutdown.

## State and persistence
The interface is explicitly context-based: each backend returns a `rock` from `create_interface`, persists backend-specific state there, and releases it through `close_interface`.

## Dependencies and integration points
Implemented by `audit-file.c` and `audit-sysvmq.c`; consumed by `audit.c`. Backends are selected by name from `audit_interfaces`.

## Risks
Callback contracts rely on discipline rather than type-enforced ownership. `send_msg` receives a truncation flag and a length, so backends must not assume NUL-termination unless they add it. Optional `set_option` must be checked before parsing options.

## Test signals
Backend contract tests should verify create/open/send/stats/close ordering, option parsing only when `set_option` exists, max message handling, and cleanup after partial open failures.
