## sources/distributed-fs/eos/mgm/bulk-request/FileCollection.hh

Purpose: stores bulk-request files in a `multimap<path, unique_ptr<File>>` while preserving insertion order in a parallel vector of iterators. This supports duplicate paths and stable client-visible ordering.

Important APIs/types: `Files` (`vector<File*>`), `FilesMap`, `FilesInsertOrder`, `addFile()`, `getAllFiles()`, `getFilesMap()`, and `getAllFilesInError()`.

State behavior: constructor initializes shared containers; assignment copies the shared `mFiles` pointer but does not copy `mFilesInsertOrder`, which is a notable shallow-copy hazard. `getAllFiles()` materializes raw pointers in insertion order; `getFilesMap()` exposes the shared mutable map; `getAllFilesInError()` returns a set ordered by path, losing duplicate path entries. Tests should cover duplicate insertion order, error extraction, assignment behavior, and lifetime of raw `File*` snapshots.
