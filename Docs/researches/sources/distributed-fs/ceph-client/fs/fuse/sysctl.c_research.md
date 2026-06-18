# sources/distributed-fs/ceph-client/fs/fuse/sysctl.c

## Purpose
Registers `/proc/sys/fs/fuse` tunables for global FUSE request sizing and timeout limits.

## Important APIs, Types, And Functions
`fuse_sysctl_table` exposes `max_pages_limit`, `default_request_timeout`, and `max_request_timeout` through `proc_douintvec_minmax`. `fuse_sysctl_register()` registers the table under `fs/fuse`. `fuse_sysctl_unregister()` unregisters it and clears the header pointer.

## Control Flow
Module initialization calls register, which stores the returned `ctl_table_header`; teardown unregisters the same header. Each entry enforces a minimum and a u16-compatible maximum.

## State And Persistence
The file modifies global variables declared elsewhere: `fuse_max_pages_limit`, `fuse_default_req_timeout`, and `fuse_max_req_timeout`. Values live in kernel memory and affect future FUSE connection/request behavior but are not persistent across boot unless managed by userspace sysctl configuration.

## Dependencies And Integration Points
Depends on Linux sysctl infrastructure and FUSE global config variables. Integrates with FUSE initialization/exit code.

## Risks
Too-large limits would exceed protocol field widths, so upper bounds are u16-derived. Runtime tuning can affect memory use and hung-request behavior across all FUSE mounts.

## Test Signals
Verify sysctl registration, unregister cleanup, min/max enforcement, read/write permissions, and that changed limits affect new FUSE request negotiation/timeouts.
