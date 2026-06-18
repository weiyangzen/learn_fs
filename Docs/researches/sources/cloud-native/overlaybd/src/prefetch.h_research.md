## sources/cloud-native/overlaybd/src/prefetch.h

Purpose: public interface and lifecycle documentation for OverlayBD prefetch support.

Important APIs/types: `Prefetcher` derives from Photon `Object`, defines `Mode { Disabled, Record, Replay }` and `TraceOp { READ, WRITE }`, and declares `record`, `replay`, `new_prefetch_file`, `detect_mode`, and `get_mode`. Factories create trace-based or dynamic prefetchers.

Control flow contract: static mode is driven by trace-file existence and size; recording stops when the lock file is removed or the prefetcher is destroyed; replay uses a non-empty trace. Dynamic mode reads a file list specified via `recordTracePath` and prefetches listed files/directories.

State/persistence: header documents persistent trace, lock, and OK files but does not define binary layout. Dependencies are C++ string/cstdint and Photon filesystem.

Integration points: consumers wrap layer/source files with `new_prefetch_file` so reads can be recorded, then call `replay` when an image file is available. Risks: interface exposes raw `IFile*` ownership conventions indirectly through implementation; `TraceOp::WRITE` exists but implementation only records/replays reads in this subset. Tests are in `trace_test.cpp`.
