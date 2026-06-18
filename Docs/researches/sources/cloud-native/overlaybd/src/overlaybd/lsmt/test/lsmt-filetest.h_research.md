# sources/cloud-native/overlaybd/src/overlaybd/lsmt/test/lsmt-filetest.h

## Purpose
Provides GoogleTest fixtures and helpers for exercising LSMT file behavior across writable layers, read-only layers, sparse writes, compressed commits, stacked files, warp files, and Photon threading.

## Important APIs and Types
Defines `FileTest`, `FileTest2`, `FileTest3`, and `WarpFileTest`. Helpers create/open RW and RO layers, generate randomized sector-aligned writes, maintain a verify image, compare file contents, create committed layers, load stacked images, and build warp-file layers with remote mapping operations.

## Control Flow
Fixtures initialize a Photon local filesystem rooted at `/tmp`, generate deterministic layer filenames, create LSMT files with `LayerInfo`/`WarpFileArgs`, perform randomized `pwritev` or discard operations, and verify full virtual-size reads against the local verification file. Cleanup removes generated layer, data, index, merged, and verify files where enabled.

## State and Persistence
Fixture state tracks layer filenames, current/next layer IDs, parent UUIDs, virtual size, opened `IFile` handles, and compressed-layer sizes. Test persistence is temporary local files representing LSMT data/index/committed layers.

## Dependencies and Integration Points
Includes `index.cpp` and `file.cpp` directly, plus zfile, Photon localfs/thread/uuid utilities, gtest, gflags, and syscalls. It is the main behavioral harness for the LSMT file and index implementation.

## Risks
Randomized tests use a fixed seed in `test.cpp` but still depend on `/tmp` capacity and selected IO engine. Some teardown paths return early, leaving files for inspection but increasing local state leakage. Direct implementation inclusion may diverge from production build linkage.

## Test Signals
Strong signals are byte-for-byte verification against the check file after create/open/commit/stack/flatten/repack/restack, plus UUID preservation checks and multi-thread Photon verification.
