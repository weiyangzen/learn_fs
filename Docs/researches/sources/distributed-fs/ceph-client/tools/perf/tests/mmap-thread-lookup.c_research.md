# sources/distributed-fs/ceph-client/tools/perf/tests/mmap-thread-lookup.c

## Purpose
Tests that synthesized thread mmap events populate machine/thread maps sufficiently for `thread__find_map()` to locate per-thread anonymous executable mappings.

## Important APIs, Types, and Functions
- `struct thread_data` stores pthread id, Linux tid, mmap address, and a readiness pipe.
- `thread_init()` mmaps one page with read/write/exec permissions and records the thread tid.
- `thread_fn()` initializes a worker thread, signals readiness, waits for `go_away`, then unmaps.
- `threads_create()` initializes main thread data and creates worker threads.
- `synth_all()` uses `perf_event__synthesize_threads()`.
- `synth_process()` uses `thread_map__new_by_pid()` and `perf_event__synthesize_thread_map()`.
- `mmap_events()` creates threads, synthesizes events into a host machine, then verifies each thread's map can be resolved.

## Control Flow
The suite runs `mmap_events()` twice: once synthesizing all threads globally, once synthesizing a process thread map. For each run, it creates four total thread entries including main, initializes a host machine, invokes the synthesizer, destroys threads, then for each `thread_data` finds or creates the machine thread and calls `thread__find_map()` on `td->map + 1`. Each lookup must return a map.

## State and Persistence
The test creates pthreads, anonymous mmaps, readiness pipes, and in-memory machine state. `go_away` controls worker lifetime. All mmaps and threads are cleaned up; no persistent files are used.

## Dependencies and Integration Points
Exercises synthetic event generation, machine event processing, thread maps, map lookup, perf environment initialization, and pthread/syscall APIs. Registered as `DEFINE_SUITE("Lookup mmap thread", mmap_thread_lookup)`.

## Risks and Edge Cases
- Requires thread synchronization to ensure mappings exist before synthesis; readiness pipes handle worker initialization.
- Main thread mapping is initialized without a pthread and cleaned separately.
- `go_away` is a plain static int shared across threads; sufficient for this short test but not a robust synchronization primitive.

## Test Signals
Passing confirms both global and process-scoped synthesis paths allow every thread object to find its synthetic mmap.
