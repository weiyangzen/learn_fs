# sources/control-plane/mayastor/io-engine/tests/lvs_grow.rs

Purpose: validates LVS pool growth after backing-device expansion through both internal Mayastor APIs and gRPC API, for malloc and AIO-backed devices.

Important APIs/types/functions: `TestPoolStats` normalizes capacity, disk capacity, and max expandable size from `Lvs` or gRPC `Pool`. `GrowTest` trait abstracts pool creation, stats, grow operation, device size, and device grow. `test_grow` encodes shared assertions. Concrete tests are `lvs_grow_ms_malloc`, `lvs_grow_api_malloc`, and `lvs_grow_api_aio`.

Control flow: shared test creates pool, checks initial capacity is near disk capacity, grows the underlying device, verifies pool capacity has not changed while disk capacity reflects growth, calls pool grow, then verifies capacity increases and remains below/near disk capacity. Malloc internal path uses `resize_malloc_disk`; gRPC malloc path recreates malloc bdev with `resize`; AIO path expands a tempfs file by `max_expandable_size - disk_capacity`.

State and persistence: malloc tests use in-memory bdevs; AIO test uses `/tmp/disk1.img` bind-mounted into a compose container. LVS metadata persists on the backing bdev within the test lifetime.

Dependencies and integration points: LVS pool APIs, gRPC v1 pool API, compose builders, `PoolBuilder`, bdev lookup/create helpers, SPDK malloc resize, and filesystem expansion helper.

Risks and edge cases: capacity comparison allows 10 percent tolerance to account for metadata. AIO disk capacity may lag new file size until pool/bdev refresh, which the test explicitly accounts for. Compose/network startup required for API paths.

Test signals: covers internal and external API growth behavior and protects against accidental capacity changes before explicit grow.
