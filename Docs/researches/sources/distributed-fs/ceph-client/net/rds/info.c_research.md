# sources/distributed-fs/ceph-client/net/rds/info.c

## Purpose
`info.c` implements the RDS getsockopt information snapshot framework. It lets RDS subsystems register fixed-record info providers and copies their snapshots into user buffers through pinned user pages.

## Important APIs, Types, and Functions
The local `struct rds_info_iterator` tracks pinned pages, current mapped address, and page offset. Public functions are `rds_info_register_func()`, `rds_info_deregister_func()`, `rds_info_iter_unmap()`, `rds_info_copy()`, and `rds_info_getsockopt()`. Registered provider callbacks use `struct rds_info_lengths` to report record count and size.

## Control Flow
Providers register by option number in `rds_info_funcs[]` under `rds_info_lock`. `rds_info_getsockopt()` reads the user-supplied buffer length, validates wrapping and negative lengths, pins the user pages if length is nonzero, looks up the provider, initializes an iterator at the user's page offset, calls the provider, unmaps any active kmap, compares required total bytes with supplied length, writes the required length back to `optlen`, and returns either element size or `-ENOSPC`.

`rds_info_copy()` is the provider-side copy helper. It keeps an atomic kmap active across consecutive copies to avoid repeated mapping overhead, copies across page boundaries, and advances the iterator.

## State and Persistence
The only persistent state is the registered callback table. Pinned pages and kmap state are request-local and released before return. No data is stored on disk or retained after the query beyond provider registration.

## Dependencies and Integration Points
Transport and core RDS modules register callbacks for stats, connections, messages, and RDMA state. The copy mechanism depends on `pin_user_pages_fast()`, `kmap_atomic()`, and fixed-size snapshot contracts. `info.h` exposes the provider API.

## Risks
Providers must set `lens->each` and `lens->nr` correctly; `BUG_ON(lens.each == 0)` turns provider bugs into kernel failures. The framework pins the full user buffer before invoking providers; very large lengths can create memory pressure, though length validation prevents overflow. Providers must call `rds_info_iter_unmap()` before sleeping if they perform blocking work while using the iterator.

## Test Signals
Test zero-length size probes, too-small buffers returning `-ENOSPC` and updated length, invalid option numbers, callback register/deregister ordering, page-boundary copies, and providers that produce snapshots larger than one page.
