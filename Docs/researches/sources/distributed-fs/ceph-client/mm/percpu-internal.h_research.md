# sources/distributed-fs/ceph-client/mm/percpu-internal.h

## Purpose
`percpu-internal.h` defines the private data structures and helper interfaces shared by the generic per-CPU allocator and its VM/KM backends. It describes chunk metadata, allocation bitmaps, optional object accounting extensions, global allocator state, and debug statistics helpers.

## Important APIs, Types, And Functions
- `struct pcpu_block_md` stores scan and contiguous-free hints for bitmap blocks.
- `struct pcpuobj_ext` stores optional memcg object cgroup and allocation profiling codetag state.
- `struct pcpu_chunk` is the central allocator chunk with lists, free bytes, bitmap maps, metadata blocks, base address, population counters, object extensions, and populated bitmap.
- `need_pcpuobj_ext()` decides whether object extension storage is needed.
- `pcpu_chunk_nr_blocks()`, `pcpu_nr_pages_to_map_bits()`, `pcpu_chunk_map_bits()`, and `pcpu_obj_full_size()` convert between pages, bitmap bits, and accounting sizes.
- `struct percpu_stats` and inline `pcpu_stats_*()` helpers track allocation and chunk statistics under `CONFIG_PERCPU_STATS`.

## Control Flow
The header is mostly declarative. Allocator code updates chunk maps and metadata under `pcpu_lock`; stats helpers assert or take that lock depending on whether they update allocation or chunk-wide counters. Object extension sizing adds per-object overhead for memcg when kmem accounting is active. In non-stats builds, all stats helpers compile to empty inline functions.

## State And Persistence Behavior
State is volatile allocator metadata: global chunk lists, slots, reserved/first chunks, bitmap maps, populated-page bits, per-chunk counters, optional object extension arrays, and stats. Nothing is persisted outside memory. `pcpu_chunk::immutable` prevents depopulation for pre-mapped chunks, while `isolated` tracks reclaim-list membership.

## Dependencies And Integration Points
The header depends on `linux/percpu.h`, memcg, optional memory allocation profiling, spinlocks, and constants such as `PCPU_BITMAP_BLOCK_SIZE` and `PCPU_MIN_ALLOC_SIZE`. It is consumed by core percpu allocation code and backend files `percpu-vm.c`, `percpu-km.c`, and `percpu-stats.c`.

## Risks
- Bitmap and metadata unit conversions must stay aligned with `PCPU_MIN_ALLOC_SIZE`, page size, and unit sizing.
- `pcpu_block_md` hint invariants are relied on for allocation scanning efficiency and correctness.
- Optional object extension sizing affects accounting and allocation size; miscalculations can undercharge or overrun metadata.
- Stats helpers assume correct locking and can become misleading if chunk paths bypass them.

## Test Signals
- Percpu allocation/free stress with varying sizes and alignments.
- Config matrix with `CONFIG_PERCPU_STATS`, memcg kmem enabled/disabled, and memory allocation profiling.
- Validate chunk metadata with debug checks after fragmentation and reclaim.
