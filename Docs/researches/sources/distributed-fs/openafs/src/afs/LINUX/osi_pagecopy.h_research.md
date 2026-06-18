# sources/distributed-fs/openafs/src/afs/LINUX/osi_pagecopy.h

## Purpose
This header declares the Linux background pagecopy task API used by AFS VM/readahead code.

## Important APIs, types, and functions
- Forward declaration `struct afs_pagecopy_task`.
- `afs_pagecopy_init_task()`
- `afs_pagecopy_queue_page(task, cachepage, afspage)`
- `afs_pagecopy_put_task(task)`
- `afs_init_pagecopy()`
- `afs_shutdown_pagecopy()`

## Control flow and behavior
The header contains declarations only. Expected caller flow is to initialize global pagecopy support, create a task for a batch of cache-to-AFS page copies, queue page pairs, drop the task reference, and shut down support at module exit.

## State and persistence
No header-owned state exists.

## Dependencies and integration points
The declarations require Linux `struct page` to be visible to users of the header. Implementations live in `osi_pagecopy.c`, and module lifecycle calls are made from `osi_module.c`.

## Risks
The API exposes an opaque task but no explicit cancellation/drain status, so correct lifetime depends on callers following refcount conventions. The header itself does not document allocation failure behavior.

## Test signals
Compile users against the header and run the runtime pagecopy tests described for `osi_pagecopy.c`.
