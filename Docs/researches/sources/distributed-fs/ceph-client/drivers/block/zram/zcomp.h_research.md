# sources/distributed-fs/ceph-client/drivers/block/zram/zcomp.h

Purpose: shared zram compression abstraction between the zram driver, the compression frontend, and backend adapters.

Important APIs/types/functions: `ZCOMP_PARAM_NOT_SET` marks unset tunables. `struct zcomp_params` contains shared dictionary, level, deflate-specific params, and backend private data. `struct zcomp_ctx` is mutable per-stream backend context. `struct zcomp_strm` adds a mutex, compression buffer, local copy buffer, and context. `struct zcomp_req` describes one compression/decompression operation. `struct zcomp_ops` is the backend vtable. `struct zcomp` binds per-CPU streams, ops, params, and a CPU-hotplug node.

Control flow and state: the header defines contracts only. Backend setup/release operates on shared params; create/destroy operates on runtime contexts; compress/decompress operates on requests and can mutate context. Public functions cover CPU hotplug, availability display, lookup, create/destroy, stream locking, and request execution.

Dependencies and integration: depends on kernel mutex definitions and is included by every backend plus `zcomp.c`. It is the integration boundary between zram device logic and compression libraries.

Risks: params are shared across contexts and must be treated as immutable after setup except for backend-owned data. Contexts are not shareable and rely on `zcomp_stream_get()` locking. Backend return-code conventions vary, so frontend callers should treat any nonzero as failure.

Test signals: compile all backend implementations against vtable signature, validate unset parameter defaults, and test concurrent per-CPU stream use through the public API.
