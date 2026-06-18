<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ocf_namespace.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ocf_namespace.cpp

## Purpose
Implements a filesystem-backed namespace that assigns every source path a stable block-index range in the global OCF core address space.

## Important APIs, Types, And Functions
`OcfNamespaceOnFs` implements `init` and `locate_file`. Private helpers include `get_ns_info`, `append_ns`, and `write_ns_info`. Namespace files store `NsFileFormat` with magic, CRC32C checksum, and `NsInfo`.

## Control Flow
`init` validates the OCF cache-line/block size, walks existing namespace files, loads their mappings, and computes the next free block index. `locate_file` loads existing mapping if present; otherwise it stats the source file and appends a new namespace entry under a mutex. Writes go to `path.tmp` and are atomically renamed.

## State And Persistence
Persists namespace records in `m_fs`, one source-path-shaped record per file. In-memory `m_total_blocks` tracks the append frontier. The namespace file's CRC guards corruption of `NsInfo`.

## Dependencies And Integration Points
Uses Photon filesystem walking/path helpers, mutex, localfs, CRC32C from zfile, and OCF cache-line constants. Called from `OcfCachedFs::open`.

## Risks And Test Signals
`init` computes total blocks by the maximum starting block plus that file's size; corrupted or missing namespace files fail startup/open. Concurrent append is serialized only within one process. Source file growth after namespace creation is not represented unless a new namespace is written. Source size reviewed: 178 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ocf_namespace.cpp -->
