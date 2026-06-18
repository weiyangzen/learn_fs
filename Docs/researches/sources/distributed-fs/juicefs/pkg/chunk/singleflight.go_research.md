## sources/distributed-fs/juicefs/pkg/chunk/singleflight.go

Purpose: custom singleflight controller for coalescing concurrent full-block loads while preserving `Page` reference counts.

Important APIs/types/functions: `request` holds a waitgroup, resulting `*Page`, duplicate count, and error. `Controller` maps keys to active requests. `Execute` waits on existing requests or registers a new one, runs `fn`, acquires the returned page once for every duplicate waiter, deletes the request, and releases waiters. `TryPiggyback` waits only if a request already exists, otherwise returns nil.

State and persistence: in-memory active-request map only.

Dependencies and integration points: used in `cachedStore.ReadAt`, `loadRange`, and prefetch to deduplicate object-store reads and let range reads piggyback on full reads.

Risks and test signals: assumes `fn` returns a non-nil page even on errors before duplicate acquisition; nil pages with duplicates could panic. Correct page refcounts are critical because all waiters release returned pages. Tests exercise concurrent Execute and piggyback semantics.
