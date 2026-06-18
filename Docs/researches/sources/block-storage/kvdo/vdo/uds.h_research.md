# File Research: sources/block-storage/kvdo/vdo/uds.h

This header is the public UDS API definition for index sessions and asynchronous chunk operations. It defines request types (`POST`, `UPDATE`, `DELETE`, `QUERY`, `QUERY_NO_UPDATE`) and index open types (`LOAD`, `CREATE`, `NO_REBUILD`).

Core public data:
- `UDS_CHUNK_NAME_SIZE` and `UDS_METADATA_SIZE` are both 16 bytes.
- `uds_memory_config_size_t` supports positive GB sizes plus negative sub-GB and reduced-chapter constants.
- `struct uds_parameters` configures index storage name, size, offset, memory size, sparse mode, nonce, zone count, and read-thread count.
- `struct uds_index_stats` reports index resource usage, collision/discard counts, operation counters, and current time.

`struct uds_request` is the async operation object. Client-visible fields include chunk name, old/new metadata, callback, session, operation type, status, and found flag. Internal fields carry zone number, queue/list links, index pointer, sparse-cache/zone control message, batching flags, virtual chapter, and lookup location.

The API declares index sizing, session create/open/suspend/resume/flush/close/destroy, parameter/stat retrieval, and `uds_start_chunk_operation()` for asynchronous dedupe/index requests.
