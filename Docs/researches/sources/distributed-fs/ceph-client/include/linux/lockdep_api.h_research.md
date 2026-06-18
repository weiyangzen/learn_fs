<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lockdep_api.h -->
# sources/distributed-fs/ceph-client/include/linux/lockdep_api.h

## Purpose
This compatibility header re-exports the lockdep API by including `linux/lockdep.h`.

## Important APIs, Types, and Functions
All APIs come from `lockdep.h`, including lock class keys, lockdep maps, acquire/release annotations, assertions, and disabled-config stubs.

## Control Flow
There is no independent control flow. Include processing redirects users to the main lockdep header.

## State and Persistence Behavior
No state is declared here; runtime state is the lockdep state declared and implemented through `lockdep.h` and related files.

## Dependencies and Integration Points
Its only dependency is `linux/lockdep.h`. It supports users that include the historical or narrower API name.

## Risks and Test Signals
Risks are limited to duplicate include expectations and stale compatibility includes. Build coverage and lockdep tests for the underlying API are sufficient signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lockdep_api.h -->
