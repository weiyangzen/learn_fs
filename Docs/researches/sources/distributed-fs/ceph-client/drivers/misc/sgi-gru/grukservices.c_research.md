# sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grukservices.c

Purpose: implements kernel-facing GRU services for SGI UV/SN platforms. It provides demand-loaded per-blade kernel GRU contexts, per-CPU control-block/data-segment resources, async resource reservations, GRU-backed message queues, GPA read/copy helpers, exception handling, and debug quicktests.

Important APIs and functions: exported entry points include `gru_create_message_queue()`, `gru_send_message_gpa()`, `gru_free_message()`, `gru_get_next_message()`, `gru_read_gpa()`, `gru_copy_gpa()`, `gru_reserve_async_resources()`, `gru_release_async_resources()`, `gru_wait_async_cbr()`, `gru_lock_async_resource()`, and `gru_unlock_async_resource()`. Internal resource helpers are `gru_load_kernel_context()`, `gru_lock_kernel_context()`, `gru_get_cpu_resources()`, and `gru_free_kernel_contexts()`. Exception helpers include `gru_wait_proc()`, `gru_check_status_proc()`, `gru_retry_exception()`, and `gru_get_cb_exception_detail()`.

Control flow: kernel callers obtain resources through `gru_get_cpu_resources()`, which locks and, if needed, loads the local blade kernel context. Message sends copy the caller payload into a reserved DSR, set GRU message header flags, issue `gru_mesq()`, and retry or repair based on CB substatus. Queue-full handling flips the message queue head between halves with GRU atomic operations. PUT-nack recovery rewrites possibly partial messages and may send a NOOP to force interrupt delivery. Receivers poll a memory queue directly and free entries in order with `gru_free_message()`.

State and persistence: state is mostly hardware-backed and in-memory: `bs_kgts`, `kernel_cb`, `kernel_dsr`, async reservation counters, message queue head/next/limit pointers, and per-message present bits. No disk persistence exists. The kernel context may be unloaded and reloaded, with hardware context state discarded for kernel use.

Dependencies and integration: depends on GRU instruction helpers, `grutables.h` state, UV blade/GPA translation helpers, kernel completions, wait queues, and cache flush/barrier primitives. XP UV code uses `gru_read_gpa()` and `gru_copy_gpa()` for cross-partition memory operations.

Risks: heavy use of `BUG_ON()` and `panic()` makes unexpected GRU failures fatal. Locking is subtle around `bs_kgts_sema` downgrade/reload and context stealing. Message recovery depends on GRU substatus semantics and correct two-cacheline present-bit handling. Async resources support only one reservation per blade and assume callers pair reserve/lock/unlock/release correctly.

Test signals: `gru_ktest()` exposes quicktests for GPA load/store, message queue capacity/order, async completion, and block copy. Runtime signals include `STAT()` counters for message send/receive failures, congestion, queue-full transitions, context loads, and GPA copy/read operations.
