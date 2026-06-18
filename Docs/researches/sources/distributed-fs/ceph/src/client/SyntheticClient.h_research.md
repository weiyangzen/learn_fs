# sources/distributed-fs/ceph/src/client/SyntheticClient.h

## Purpose
`SyntheticClient.h` declares the synthetic workload driver used by CephFS client test tools. It exposes mode constants, global option parsing, and the `SyntheticClient` class interface.

## Important APIs, Types, and Functions
The header defines many `SYNCLIENT_MODE_*` integer constants for random walks, trace replay, directory/file creation, read/write tests, object tests, lookup tests, snapshots, and timing/client-selection controls. `parse_syn_options(std::vector<const char*>&)` fills shared mode queues. `SyntheticClient` stores a `StandaloneClient*`, thread id, operation distribution, current path state, directory caches, open file set, run filters, and mode argument queues. Public methods include thread lifecycle, `run()`, argument accessors, stop checks, path composition, all workload helpers, trace replay, object operations, lookup helpers, chunking, and snapshot helpers.

## Control Flow
Instances copy global parse results into per-client queues. `start_thread()` launches `run()` through a pthread entrypoint; `join_thread()` waits. `run_me()`, `did_run_me()`, and `time_to_stop()` gate mode execution by client id and time.

## State and Persistence Behavior
Header state is entirely in-memory, but it drives persistent CephFS/RADOS mutations through the implementation. Directory-selection helpers use cached `contents` and `subdirs`; `clear_dir()` resets that cache after navigation or error recovery.

## Dependencies and Integration Points
It depends on `Client.h`, `Distribution`, `Trace`, `filepath`, `UserPerm`, and Ceph time/client id types. It is tightly coupled to `StandaloneClient` and CephFS low-level handles declared elsewhere.

## Risks
The mode interface is macro-based and positional: parser and dispatcher must consume exactly matching argument counts. Helper methods expose raw sizes, paths, and counts, so invalid command input can produce oversized allocations or unexpected namespace mutations.

## Test Signals
Compile coverage should confirm every declared helper has a matching implementation. Runtime tests should verify mode argument consumption order and multi-client `only`/`onlyrange` behavior.
