# sources/distributed-fs/orangefs/src/io/bmi/bmi_zoid/server.c

## Purpose

`server.c` implements the I/O-node server side of the OrangeFS BMI method for ZOID. It bridges BMI operations to the ZBMI plugin running in the ZOID daemon over Unix-domain control sockets and shared memory. Expected message buffers are allocated from the shared-memory expected region via `zbmi_pool`; unexpected message buffers are owned by the ZBMI plugin and freed back through a control command.

## Important APIs, types, and functions

- `struct ZoidServerMethodData` is attached to BMI method operations. It tracks an optional temporary shared-memory buffer for `BMI_EXT_ALLOC` operations and the ZOID-side buffer id returned by the plugin.
- `struct NoMemDescriptor` records operations waiting for temporary shared-memory allocation, sorted by descending total size.
- Global socket state: `zbmi_sockets`, `zbmi_sockets_inuse`, `zbmi_sockets_len`, `zbmi_sockets_used`, protected by `zbmi_sockets_mutex`.
- Global client address cache: `clients_addr` and `clients_len`, protected by `clients_mutex`.
- Global shared-memory state: `zbmi_shm`, `zbmi_shm_unexp`, `zbmi_shm_exp`, `zbmi_shm_size_total`, and `zbmi_shm_size_unexp`.
- Queues: `no_mem_queue_first/last` for operations waiting on temporary memory and `error_ops` for failed or locally canceled operations.
- Public server hooks include `BMI_zoid_server_initialize`, `BMI_zoid_server_finalize`, `BMI_zoid_server_memalloc`, `BMI_zoid_server_memfree`, `BMI_zoid_server_unexpected_free`, `BMI_zoid_server_testunexpected`, `zoid_server_send_common`, `zoid_server_recv_common`, `zoid_server_test_common`, `BMI_zoid_server_cancel`, and `zoid_server_free_client_addr`.
- Internal helpers include `socket_read`, `socket_write`, `get_zoid_socket`, `release_zoid_socket`, `get_client_addr`, `enqueue_no_mem`, and `send_post_cmd`.

## Control flow

Initialization obtains a ZOID control socket, sends `ZBMI_CONTROL_INIT`, reads shared-memory sizes, opens and maps `ZBMI_SHM_NAME`, splits the mapping into unexpected and expected regions, initializes `zbmi_pool` over the expected region, and creates `error_ops`.

Expected send and receive posting goes through `zoid_server_send_common` and `zoid_server_recv_common`. Each allocates a BMI method op and fills BMI metadata. For `BMI_EXT_ALLOC`, the server allocates a temporary shared-memory buffer; sends copy user buffers into it before posting, while receives copy out of it after test completion. If temporary memory is unavailable, the op is queued with `enqueue_no_mem`. For non-`BMI_EXT_ALLOC`, the server verifies that every user buffer lies inside the expected shared-memory region. `send_post_cmd` serializes buffer offsets relative to `zbmi_shm_exp`, sends `ZBMI_CONTROL_POST_SEND` or `ZBMI_CONTROL_POST_RECV`, reads the ZOID buffer id, and stores it in method data.

Completion testing starts by draining local `error_ops` for canceled or failed operations. It then sends `ZBMI_CONTROL_TEST`, with positive count for explicit tests and negative count for testcontext. Completed ZOID entries are mapped back to BMI ids, error codes, actual sizes, and user pointers. Temporary receive buffers are copied into user buffer lists before freeing. Method ops are deallocated after completion handling.

Unexpected receive polling sends `ZBMI_CONTROL_UNEXP_TEST`, reads a variable-length response of buffer descriptors, translates ZOID client ids to BMI method addresses, and returns pointers into `zbmi_shm_unexp`. `BMI_zoid_server_unexpected_free` validates that the pointer is in the unexpected region and sends `ZBMI_CONTROL_UNEXP_FREE` with an offset.

Finalization cleans `error_ops`, destroys the pool, unmaps shared memory, closes all opened control sockets, and frees socket bookkeeping arrays.

## State and persistence behavior

All state is process-local except the mapped shared-memory object and control connection to the ZOID daemon. The shared-memory layout is negotiated at initialization and is assumed stable until finalization. Expected-region allocations are owned by this server process through `zbmi_pool`; unexpected-region buffers are owned by the ZBMI plugin until explicitly freed. Client BMI addresses are cached by ZOID pid in a growable array and registered through `bmi_method_addr_reg_callback`.

No durable persistence exists. On restart, the server repeats the handshake, remaps shared memory, and recreates all local queues/caches.

## Dependencies and integration points

This file depends on POSIX facilities: pthread mutexes, Unix-domain sockets, POSIX shared memory (`shm_open`/`mmap`), `read`, `write`, `close`, `sleep`, and filesystem socket paths. It also depends on OrangeFS BMI internals (`bmi-method-support.h`, `bmi-method-callback.h`, `id-generator.h`, `op-list.h`) and local ZOID protocol definitions (`zoid.h`, `zbmi_pool.h`, `zbmi_protocol.h`). `shm_open` and `shm_unlink` are declared weak to avoid forcing client-side linkage when server symbols are not invoked.

The integration contract with the ZBMI plugin is command-based: INIT, unexpected free/test, expected post send/recv, test, and cancel. Buffer descriptors use offsets into either the unexpected or expected shared-memory region.

## Risks and edge cases

- `BMI_zoid_server_cancel` sends `ZBMI_CONTROL_CANCEL` but returns 0 without calling `release_zoid_socket`, which can leave a socket marked in use and eventually force unnecessary socket growth or deadlock under repeated cancels.
- Pointer arithmetic is performed on `void *` in several places (`zbmi_shm + offset`, buffer range checks, `buf_cur += size`, pointer offset subtraction). This relies on GNU C extensions and is not portable ISO C.
- `send_post_cmd` returns `-BMI_ENOMEM` when the plugin returns no ZOID id, but the already allocated method op and temporary buffer are not always cleaned by the caller.
- Finalization does not visibly drain `no_mem_queue` or free `clients_addr`, and it assumes no operations are live.
- In `zoid_server_test_common`, after local error handling with `incount`, command filling still loops over `i < incount` while `cmd_len` is sized for `incount_fwd`; if completed error operations were removed from the front/middle, this deserves careful test coverage for array indexing and stale ids.
- Buffer validation for non-`BMI_EXT_ALLOC` relies on pointer range comparisons and arithmetic against shared-memory boundaries; invalid pointer provenance is undefined in strict C and can miss overflow-style issues.
- The no-memory queue is sorted descending by total size. Large operations are retried first after any free, which may starve smaller requests if the largest request cannot be satisfied.
- Socket connection retry loops sleep forever on `ENOENT`/`ECONNREFUSED`, so initialization or new socket creation can hang if the ZOID daemon never appears.

## Test signals

Important tests include a mocked ZBMI control socket that exercises INIT, POST, TEST, CANCEL, UNEXP_TEST, and UNEXP_FREE; fixed-size shared-memory pool exhaustion to drive `enqueue_no_mem` and retry on `BMI_zoid_server_memfree`; cancellation before and after a ZOID buffer id is assigned; multi-list send/recv with `BMI_EXT_ALLOC` copy-in/copy-out; invalid buffer pointers for non-`BMI_EXT_ALLOC`; repeated cancel calls to detect socket release leaks; and finalize with queued/no-live/live operations. Threaded tests should contend `get_zoid_socket`, `get_client_addr`, no-memory retry, and completion polling.
