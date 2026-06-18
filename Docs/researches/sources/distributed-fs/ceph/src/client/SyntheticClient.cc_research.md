# sources/distributed-fs/ceph/src/client/SyntheticClient.cc

## Purpose
`SyntheticClient.cc` implements a CephFS synthetic workload driver for `StandaloneClient`. It parses `--syn` command sequences into global mode/argument queues, mounts a client, executes metadata, data, trace-replay, object, snapshot, and stress workloads, then unmounts and shuts down.

## Important APIs, Types, and Functions
The file defines `parse_syn_options()`, global workload queues (`syn_modes`, `syn_iargs`, `syn_sargs`), `synthetic_client_thread_entry()`, and the full `SyntheticClient` method set declared in the header. `run()` is the central dispatcher from `SYNCLIENT_MODE_*` values to helpers. Trace replay uses `play_trace(Trace&, string&, bool)`. File tests use `write_file()`, `read_file()`, `read_random()`, `read_random_ex()`, and `chunk_file()`. Metadata tests use `make_dirs()`, `stat_dirs()`, `read_dirs()`, `make_files()`, `full_walk()`, `random_walk()`, `thrash_links()`, `import_find()`, lookup helpers, and snapshot helpers. Objecter-level tests use `create_objects()` and `object_rw()`.

## Control Flow
`parse_syn_options()` removes recognized synthetic options from argv and appends modes plus typed arguments. `run()` picks user permissions, initializes and mounts the client, iterates modes, consumes the matching arguments, applies `run_only`/`exclude`/duration gates, and invokes the workload helper. `play_trace()` reads tokenized operations from `Trace`, maps trace-local ids to open file handles, low-level inode handles, directories, and object ids, then dispatches high-level POSIX calls, `ll_*` calls, and Objecter read/write/zero/stat calls.

## State and Persistence Behavior
The code mutates the mounted CephFS namespace and RADOS objects used by file layouts. It also maintains in-memory workload state: current working `filepath`, cached directory contents/subdirs, open file sets, trace handle maps, and async counters guarded by Ceph mutex/condition variables. Data-writing helpers stamp each 16-byte record with offset and client id; read helpers validate those fingerprints. Snapshot helpers create `.snap` entries and rewrite data after a snapshot.

## Dependencies and Integration Points
It depends on `Client`, `StandaloneClient`, `Trace`, `UserPerm`, `Objecter`, `Filer`, Ceph layout/object types, `C_SafeCond`, perf/debug infrastructure, and POSIX headers. It integrates with both path-based libcephfs APIs and low-level inode/Fh APIs, plus direct Objecter and Filer operations.

## Risks
This is test/stress code with intentional rough edges: many operations ignore return values, `foo()` contains infinite/debug scenarios behind constant branches, `random_walk()` aborts in its readdir population block, `overload_osd_0()` has a `while (left < 0)` condition that prevents normal positive workloads, and trace replay aborts on unknown symbols. Several helpers reseed randomness repeatedly, allocate variable-size buffers from user arguments, and use fixed path buffers.

## Test Signals
Useful test signals are successful mode parsing, clean mount/unmount, expected throughput logs, fingerprint mismatch warnings in reads, `full_walk()` nlink/frag count discrepancies, trace replay line progress, and completion of async object counters without leaked in-flight references.
