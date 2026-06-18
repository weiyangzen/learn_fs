# sources/distributed-fs/openafs/src/afs/LINUX/osi_pagecopy.c

## Purpose
This file implements asynchronous background copying from disk-cache pages to AFS pages for Linux readahead/readpage paths. It lets readpages queue copies that wait for backing cache pages to unlock, then uses workqueue jobs to copy page data without blocking the original readahead caller.

## Important APIs, types, and functions
- `struct afs_pagecopy_page` links one cache page to one target AFS page.
- `struct afs_pagecopy_task` groups pages for one higher-level read/readahead task and owns workqueue state, page lists, refcount, and a spinlock.
- `afs_pagecopy_init_task` allocates and initializes a task.
- `afs_pagecopy_queue_page` references pages, queues them on the task, adds the task to the global check queue, and wakes the monitor thread.
- `afs_pagecopy_put_task` drops task references and frees on zero.
- `afs_pagecopy_checkworkload` moves unlocked cache pages to copy-ready lists and schedules work.
- `afs_pagecopy_worker` copies page contents, marks target page state, unlocks target pages, drops references, and frees page records.
- `afs_pagecopy_thread` monitors queued tasks, waits for locked cache pages, and sleeps on a waitqueue.
- `afs_init_pagecopy` and `afs_shutdown_pagecopy` start/stop the background thread.

## Control flow and behavior
Callers create a task, queue page pairs, and eventually drop their task reference. Queueing increments page references and, if the task is not already on the global workload list, adds it with an extra task reference. The monitor thread repeatedly scans all tasks. For each queued page whose cache page is unlocked, it moves the page to `copypages`, increments the task reference, and schedules the task work item. If a page remains locked, it records one cache page to wait on. Tasks with no more check pages are removed from the global queue and their queue reference is released.

Workers drain `copypages` under the task lock. For each page, if the cache page is uptodate, they call `copy_highpage`, flush target dcache, clear target error, and mark target uptodate. They always unlock the target AFS page, release both page references, free the page record, and finally drop the work reference. The monitor waits on a locked cache page with `afs_page_wait_locked`/`afs_put_page`, then sleeps until work is queued or the thread is stopped.

## State and persistence
Runtime state includes global waitqueue `afs_pagecopy_wq`, spinlock `afs_pagecopy_lock`, list `afs_pagecopy_tasks`, monitor thread pointer, task lists/refcounts, and page references. It mutates page uptodate/error/locked/cache coherency state. No disk state is written directly.

## Dependencies and integration points
The code depends on Linux pages, kthreads, waitqueues, workqueues, spinlocks, and compatibility helpers for folio/page waiting and `ClearPageError`. It integrates with Linux AFS VM/readahead code through prototypes in `osi_pagecopy.h` and is initialized/shutdown by `osi_module.c`.

## Risks
`afs_pagecopy_init_task` does not check `kzalloc` failure before dereferencing. `afs_pagecopy_queue_page` also assumes page record allocation succeeds. Shutdown stops the monitor thread but does not explicitly flush queued work items or drain tasks in this file, so callers/module unload ordering must guarantee no live tasks. Refcount/list locking is subtle: scheduling failure drops a reference, and task removal drops the global queue reference. Target pages are unlocked even if the cache page is not uptodate, leaving error/uptodate state dependent on prior initialization.

## Test signals
Test readahead with locked and already-unlocked cache pages, cache-page error/not-uptodate cases, multi-page tasks, concurrent queueing, module unload with outstanding pagecopy work, allocation failure injection, and lockdep/KASAN/refcount checks.
