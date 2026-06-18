# sources/cloud-native/overlaybd/src/overlaybd/lsmt/test/test.cpp

## Purpose
Implements LSMT index and file tests. It validates low-level mapping operations and high-level OverlayBD layer workflows under randomized writes and layered reads.

## Important APIs and Types
Tests cover `Index`, `LevelIndex`, `Index0`, `ComboIndex`, `merge_memory_indexes`, `compress_raw_index`, `compress_raw_index_predict`, `create_level_index`, LSMT RW/RO file APIs, `stack_files`, `merge_files_ro`, `flatten`, `seek_data`, `restack`, zfile commits, and warp-file remote data.

## Control Flow
The file starts with deterministic random seed setup, Photon initialization, gtest/gflags parsing, and `RUN_ALL_TESTS`. Individual tests construct mapping arrays for exact expected output, use randomized sector writes, commit layers to RO files, reopen them, stack lower and upper files, flatten to new layers, and compare all reads to the verification file.

## State and Persistence
Tests persist temporary data/index/layer files under `/tmp`, use global flags for virtual size, layer count, write count, IO engine, and verification, and track global mapping state for performance tests.

## Dependencies and Integration Points
Depends on fixtures in `lsmt-filetest.h`, Photon localfs/thread runtime, zfile/gzip integration, and LSMT implementation internals. It provides regression coverage for the file/index contracts used by registry, tar import, and image tooling.

## Risks
Performance tests insert one million mappings and can be slow or memory-heavy. The fixed seed improves repeatability but does not cover broad random distributions. Some assertions rely on internal casts to concrete implementation classes.

## Test Signals
Exact mapping equality, allocation block count checks, full-image read verification, compressed commit reopen, sparse-file behavior, checksum zfile paths, restack correctness, warp UUID semantics, and multithreaded reads are the main acceptance signals.
