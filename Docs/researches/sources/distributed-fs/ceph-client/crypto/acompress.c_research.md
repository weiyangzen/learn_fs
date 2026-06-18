# sources/distributed-fs/ceph-client/crypto/acompress.c

Purpose: implements the asynchronous compression (`acomp`) crypto API front end, including transform allocation, algorithm registration, request dispatch, virtual/scatterlist conversion, synchronous fallback handling, per-CPU stream context management, and compression scatter-walk helpers.

Important APIs, types, and functions: exported entry points include `crypto_alloc_acomp()`, `crypto_alloc_acomp_node()`, `crypto_acomp_compress()`, `crypto_acomp_decompress()`, `crypto_register_acomp()`, `crypto_unregister_acomp()`, batch registration helpers, stream helpers `crypto_acomp_alloc_streams()`, `_crypto_acomp_lock_stream_bh()`, and walk helpers `acomp_walk_virt()`, `acomp_walk_next_src()`, `acomp_walk_next_dst()`, `acomp_walk_done_src()`, `acomp_walk_done_dst()`, plus `acomp_request_clone()`.

Control flow and behavior: `crypto_acomp_init_tfm()` sets algorithm callbacks and, for async algorithms, allocates a same-name synchronous fallback constrained by `MAX_SYNC_COMP_REQSIZE`. Request entry points reject stack requests on async transforms, direct-dispatch scatterlist or native-virtual requests, and otherwise convert virtual buffers into one-entry scatterlists. Completion wrappers save/restore the original callback and request data so chained fallback or converted requests complete as if submitted directly.

State and persistence: transform state lives in `struct crypto_acomp` and optional fallback `tfm->fb`. Request mutation is transient in `struct acomp_req_chain`, which stores original callback/data and virtual buffer metadata. Stream state persists per CPU in `struct crypto_acomp_streams` until explicitly freed; missing CPU-local contexts are allocated asynchronously by `stream_work`.

Dependencies and integration points: depends on `crypto/internal/acompress.h`, `crypto/scatterwalk.h`, generic `crypto_register_alg()`, proc/netlink reporting, percpu allocation, workqueues, cpumasks, and `compress.h` for scomp integration. Compression algorithms such as deflate/lzo/lz4/zstd register through this front end.

Risks and correctness concerns: virtual-buffer conversion rewrites request source/destination and must restore them exactly, especially across async completion. Stack requests cannot be safely queued to async algorithms. Per-CPU stream fallback to the first possible CPU must avoid unlocked access; cleanup must cancel work before freeing contexts. Walk helpers must handle sleeping, linear buffers, scatterwalk advancement, and zero-length validation consistently.

Test signals: exercise compression/decompression with SG and virtual buffers, async and sync algorithms, stack request rejection, fallback request size limits, callback ordering with `-EINPROGRESS` and `-EBUSY`, CPU hotplug/per-CPU streams, and scatterwalk chunking under preemptible and non-preemptible builds.
