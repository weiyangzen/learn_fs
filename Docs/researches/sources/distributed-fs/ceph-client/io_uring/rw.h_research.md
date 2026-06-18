# sources/distributed-fs/ceph-client/io_uring/rw.h

Purpose: declares read/write operation APIs and defines async read/write request state shared with completion, retry, and resource-import paths.

Important APIs/types/functions: `struct io_meta_state` stores protection-information iterator state. `struct io_async_rw` contains cached iovec storage, `bytes_done`, data iterator/state, fast iovec, buffer group, and a union of buffered-IO `wait_page_queue` or direct-IO metadata fields. Prototypes cover all read/write prep and issue variants, multishot read, cleanup, failure fixup, completion, and cache free.

Control flow: no complex header flow; the struct layout uses `struct_group(clear, ...)` so allocation paths can clear retry-sensitive state consistently.

State and persistence: all state is per-request transient async IO state. It may retain allocated iovec arrays across cache reuse until cleanup or KASAN-forced free.

Dependencies/integration: includes `io_uring_types.h` and `pagemap.h`; used by `rw.c`, task-work indirect calls, and opdef cleanup hooks.

Risks/test signals: the union means buffered waitqueue and metadata cannot coexist; `rw.c` enforces that metadata is direct IO only. Compile layout checks plus read/write metadata and buffered retry tests cover this contract.
