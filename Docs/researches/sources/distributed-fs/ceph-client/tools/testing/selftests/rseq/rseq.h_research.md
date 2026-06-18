# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/rseq.h

Purpose: `rseq.h` is the public userspace helper API for the rseq selftests. It defines generic wrappers, memory-order modes, per-cpu indexing modes, ABI accessors, injection hooks, and architecture dispatch.

Important APIs, types, and functions: exposed enums are `enum rseq_mo` and `enum rseq_percpu_mode`. Key inline APIs are `rseq_get_abi()`, `rseq_register_current_thread()`, `rseq_current_cpu_raw()`, `rseq_cpu_start()`, `rseq_current_cpu()`, `rseq_node_id_available()`, `rseq_current_node_id()`, `rseq_mm_cid_available()`, `rseq_current_mm_cid()`, `rseq_clear_rseq_cs()`, `rseq_prepare_unload()`, and wrappers for all rseq primitives. External functions and variables are supplied by `rseq.c`.

Control flow: architecture selection includes the correct `rseq-*.h` based on compiler target. Generic wrappers validate memory ordering and per-cpu mode, then dispatch to generated names such as `_relaxed_cpu_id`, `_release_mm_cid`, or `_relaxed`. Unsupported memory-order/mode combinations return `-1`.

State and persistence: the header reads and writes the current thread's `struct rseq_abi` through `rseq_thread_pointer() + rseq_offset`. Feature availability for node ID and mm CID is based on `rseq_size`. `rseq_prepare_unload()` clears the active critical-section pointer so code or descriptor memory can be reclaimed safely.

Dependencies and integration points: depends on `rseq-abi.h`, `compiler.h`, thread-pointer headers, and one architecture header. It is included by all rseq selftest C files and is the contract between high-level tests and low-level assembly.

Risks and test signals: wrapper dispatch must stay aligned with generated symbol names. Returning `-1` for unsupported modes is expected but can cause tests to spin or fail if the caller requested an impossible mode. Test signals are broad: successful builds on all architectures and passing all C selftests.
