# subset-b-007854 research

This grouped report covers the OrangeFS ZOID BMI server-side shared-memory allocator and build glue under `sources/distributed-fs/orangefs/src/io/bmi/bmi_zoid/`. Each section is source-path aligned for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_zoid/dlmalloc.c -->
# sources/distributed-fs/orangefs/src/io/bmi/bmi_zoid/dlmalloc.c

## Purpose

`dlmalloc.c` is Doug Lea malloc 2.8.4 embedded as a single translation-unit allocator implementation. In this OrangeFS directory it is not normally compiled as a standalone `malloc` replacement; `zbmi_pool.c` includes this file directly after defining `ONLY_MSPACES=1`, `MSPACES=1`, `MALLOC_ALIGNMENT=16`, `USE_LOCKS=1`, and `HAVE_MMAP=0`. That means the active integration path is the mspace allocator API over an externally supplied shared-memory range, not the global `dlmalloc`/`dlfree` path.

The allocator provides boundary-tag heap management, small-bin lists, large-bin size tries, a designated-victim chunk, a top chunk, optional segment tracking, optional locking, and optional diagnostics. It is used by the ZOID BMI server to suballocate the expected-message portion of the shared memory block exchanged with the ZBMI plugin.

## Important APIs, types, and functions

- Public global APIs when `ONLY_MSPACES` is false: `dlmalloc`, `dlfree`, `dlcalloc`, `dlrealloc`, `dlmemalign`, `dlvalloc`, `dlpvalloc`, `dlmallopt`, `dlmalloc_trim`, `dlmalloc_stats`, `dlmalloc_footprint`, `dlmalloc_max_footprint`, `dlmalloc_usable_size`, `dlindependent_calloc`, and `dlindependent_comalloc`.
- Public mspace APIs when `MSPACES` is true: `create_mspace`, `destroy_mspace`, `create_mspace_with_base`, `mspace_track_large_chunks`, `mspace_malloc`, `mspace_free`, `mspace_realloc`, `mspace_calloc`, `mspace_memalign`, `mspace_independent_calloc`, `mspace_independent_comalloc`, `mspace_trim`, `mspace_malloc_stats`, `mspace_footprint`, `mspace_max_footprint`, `mspace_mallinfo`, `mspace_usable_size`, and `mspace_mallopt`.
- Internal heap structures include `struct malloc_chunk`, `struct malloc_tree_chunk`, `struct malloc_segment`, `struct malloc_state`, and `struct malloc_params`.
- `init_mparams()` initializes process-wide allocator parameters such as page size, granularity, mmap threshold, trim threshold, default flags, lock state, and a magic value.
- `init_user_mstate()` initializes a per-mspace `malloc_state` inside the supplied arena.
- `create_mspace_with_base()` is the key function for this tree: it creates an allocator state inside the caller-provided buffer, marks the segment with `EXTERN_BIT`, and optionally enables the mspace lock.
- `mspace_malloc()` selects a chunk from small bins, tree bins, the designated-victim chunk, the top chunk, or `sys_alloc()`.
- `mspace_free()` validates, coalesces backward and forward, returns top space where possible, and reinserts free chunks into small or tree bins.

## Control flow

Allocation first normalizes the request to an internal chunk size. Small requests prefer exact or near-exact small-bin chunks, then the designated-victim chunk, then tree-bin fallback, then top chunk splitting, and finally `sys_alloc()`. Large requests search tree bins for best fit, fall back to the designated-victim chunk, top chunk, or system allocation. Freeing converts the user pointer back to a chunk, checks mspace magic and in-use bits, coalesces adjacent free chunks, updates `dv` or `top` when applicable, and otherwise links the consolidated chunk into a small bin or tree bin.

For the OrangeFS `zbmi_pool.c` embedding, the allocator is initialized with `create_mspace_with_base(start, len, 1)`. The provided shared-memory region holds the `malloc_state` and all chunks. Because `HAVE_MMAP=0` and `ONLY_MSPACES=1` makes `HAVE_MORECORE` default to 0, normal growth through `sys_alloc()` is effectively unavailable after the supplied arena is exhausted. Allocation failure returns `NULL` after `MALLOC_FAILURE_ACTION`; the server then queues some operations until memory is freed.

## State and persistence behavior

Allocator state is process-local metadata stored inside the shared-memory expected-buffer region. It is not persistent across server restarts and should not be interpreted by the external ZBMI plugin except as opaque memory offsets for posted buffers. `destroy_mspace()` skips unmapping `EXTERN_BIT` segments, so final arena lifetime remains owned by the caller (`server.c`, through `munmap`). With locks enabled and `locked=1`, public mspace calls acquire the per-mspace mutex embedded in `struct malloc_state`.

The allocator also has global process state in `mparams` and, if global malloc mode is compiled, `_gm_`. In this usage, `mparams` still initializes and stores page/alignment/magic/tuning data, but `_gm_` and global allocation APIs are compiled out by `ONLY_MSPACES`.

## Dependencies and integration points

This file depends on standard C/POSIX headers selected by compile-time macros: `errno.h`, `stdlib.h`, `string.h`, `unistd.h`, `pthread.h`, and optionally `sys/mman.h`/`fcntl.h` when mmap support is enabled. The active OrangeFS integration comes from direct inclusion in `zbmi_pool.c`, not from linking `dlmalloc.c` as its own object. `module.mk.in` lists `zbmi_pool.c` but not `dlmalloc.c`, which is consistent with the inclusion model.

The exported mspace APIs are wrapped by `zbmi_pool_init`, `zbmi_pool_malloc`, `zbmi_pool_free`, and `zbmi_pool_fini`, which are then called by `server.c` for BMI shared-memory allocation.

## Risks and edge cases

- This is old vendored allocator code with many macro-heavy pointer operations. It assumes `size_t` has pointer width, chunk alignment is a power of two, and compiler/platform behavior matches its supported matrix.
- The OrangeFS build defines `HAVE_MMAP=0` and does not define a custom `MORECORE`, so the mspace is a fixed-capacity arena. Any allocator path that reaches system allocation will fail; server-side queuing must handle that correctly.
- `create_mspace_with_base()` stores allocator metadata inside the caller-supplied arena, reducing usable space by the padded `malloc_state` and top-foot overhead.
- With `FOOTERS=0`, freeing to the wrong mspace is not strongly checked. The wrapper must never pass non-pool pointers to `mspace_free`.
- Default corruption and usage error actions call `abort()` unless overridden. A pool metadata overwrite can terminate the BMI server process.
- The direct include model means compile definitions in `zbmi_pool.c` are part of the allocator ABI. Compiling `dlmalloc.c` independently with different options would create a different symbol and behavior surface.

## Test signals

Useful test signals include building the ZOID-enabled OrangeFS target, initializing a pool over a fixed buffer, checking 16-byte alignment of returned pointers, exhausting the pool and verifying `NULL` is returned rather than writing past the arena, freeing and reallocating varied small/large sizes to exercise small bins and tree bins, and running concurrent `zbmi_pool_malloc/free` calls to validate the locked mspace path. AddressSanitizer or valgrind can help catch wrapper misuse, but allocator-internal metadata in shared memory may require suppressions or focused harnesses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_zoid/dlmalloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_zoid/dlmalloc.h -->
# sources/distributed-fs/orangefs/src/io/bmi/bmi_zoid/dlmalloc.h

## Purpose

`dlmalloc.h` is the public declaration header for Doug Lea malloc 2.8.x. It documents compile-time configuration, declares the optional global allocation APIs, declares the `mspace` APIs when `MSPACES` is enabled, and defines mallinfo/tuning symbols when system headers do not provide them. In this directory the header is not included by `zbmi_pool.c` because that file directly includes `dlmalloc.c`; it remains the formal API contract for consumers that compile dlmalloc as a normal component.

## Important APIs, types, and functions

- Configuration macros include `ONLY_MSPACES`, `NO_MALLINFO`, `USE_DL_PREFIX`, `HAVE_USR_INCLUDE_MALLOC_H`, and `MSPACES`.
- Name remapping macros map `dlmalloc` names to standard libc names when `USE_DL_PREFIX` is not defined and `ONLY_MSPACES` is false.
- `struct mallinfo` is declared with `MALLINFO_FIELD_TYPE` fields when no compatible system declaration is being used.
- Global allocator declarations cover `dlmalloc`, `dlfree`, `dlcalloc`, `dlrealloc`, `dlmemalign`, `dlvalloc`, `dlpvalloc`, `dlmallopt`, `dlmalloc_trim`, `dlmalloc_stats`, `dlmalloc_footprint`, `dlmalloc_usable_size`, `dlindependent_calloc`, and `dlindependent_comalloc`.
- `M_TRIM_THRESHOLD`, `M_GRANULARITY`, and `M_MMAP_THRESHOLD` define nonstandard `mallopt` tuning parameter numbers.
- `typedef void* mspace` and the mspace declarations expose independent allocator arenas: creation/destruction, allocation/free/realloc/calloc, memalign, batched allocation helpers, footprint/statistics, trimming, mallinfo, usable size, and mallopt.

## Control flow

The header has no runtime control flow, but its preprocessor branches decide which symbols a translation unit expects. If `ONLY_MSPACES` is true, the global malloc-like declarations are skipped. If `MSPACES` is true, independent arena declarations are emitted. If `NO_MALLINFO` is false, mallinfo-compatible types and functions are exposed.

## State and persistence behavior

The header declares interfaces to allocator-managed process memory but owns no state. The important state contract is that `mspace` is opaque to callers, and all pointers allocated from an mspace must normally be returned through the corresponding mspace API unless the allocator is compiled with footer dispatch support. In the OrangeFS embedding, `FOOTERS` is not set and `zbmi_pool` maintains the single `mspace` handle.

## Dependencies and integration points

The only direct include is `<stddef.h>` for `size_t`. For OrangeFS, the declarations align with the implementation embedded in `zbmi_pool.c`, but `zbmi_pool.c` comments out `#include "dlmalloc.h"` and includes `dlmalloc.c` directly after local compile-time definitions. External users that include this header must compile the allocator implementation with matching macro settings or the declarations will not match linked symbols.

## Risks and edge cases

- The header is generic upstream dlmalloc API material, while this directory's actual build path specializes the implementation through `zbmi_pool.c`. A maintainer can easily infer that `dlmalloc.c` is built separately from this header, but `module.mk.in` does not do that.
- If `USE_DL_PREFIX` is not defined and global APIs are enabled, the header maps `dlmalloc` names to standard allocator names, which can collide with libc declarations.
- `struct mallinfo` compatibility depends on system header choices and `MALLINFO_FIELD_TYPE`; mismatches can cause ABI problems.
- `mspace` is `void *`, so type safety is weak. Passing a destroyed or unrelated mspace is only detected by runtime magic checks in the implementation.

## Test signals

Compile-time tests should check the header under the same macro combinations used by `zbmi_pool.c`: `ONLY_MSPACES=1`, `MSPACES=1`, and the desired alignment/locking settings. A small mspace harness can include the header, link a matching dlmalloc build, create an mspace with a fixed buffer, allocate/free, and verify that no global malloc symbols are required when `ONLY_MSPACES` is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_zoid/dlmalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_zoid/module.mk.in -->
# sources/distributed-fs/orangefs/src/io/bmi/bmi_zoid/module.mk.in

## Purpose

`module.mk.in` is the OrangeFS build-system fragment for the ZOID BMI method. It conditionally adds the ZOID BMI sources to the relevant library/server source lists only when configure sets `BUILD_ZOID`.

## Important APIs, variables, and targets

- `ifneq (,$(BUILD_ZOID))` gates all content behind configure-time ZOID support.
- `DIR := src/io/bmi/bmi_zoid` defines the source directory used in top-level source lists.
- `cfiles := zoid.c server.c zbmi_pool.c` lists the C files compiled for this module.
- `src := $(patsubst %,$(DIR)/%,$(cfiles))` expands the source paths.
- `LIBSRC += $(src)`, `SERVERSRC += $(src)`, and `LIBBMISRC += $(src)` register the same sources for the broader OrangeFS build categories.
- `MODCFLAGS_$(DIR)` adds include paths for ZOID headers and the ZBMI implementation under `@ZOID_SRCDIR@`.

## Control flow

The make fragment is declarative. If `BUILD_ZOID` is empty, the build ignores this module entirely. If it is non-empty, the three source files are added to OrangeFS build lists, and directory-specific compiler flags are set to find ZOID/ZBMI headers.

## State and persistence behavior

There is no runtime state. The persistent behavior is build configuration state produced by `configure`: `BUILD_ZOID` and `@ZOID_SRCDIR@` determine whether this module compiles and where it finds external ZOID headers.

## Dependencies and integration points

This file integrates with OrangeFS's generated make infrastructure and depends on configure substituting `@ZOID_SRCDIR@`. It deliberately omits `dlmalloc.c` because `zbmi_pool.c` includes that source file directly after setting allocator configuration macros. It also depends on external ZOID headers in `include`, `zbmi`, and `zbmi/implementation`.

## Risks and edge cases

- Because `dlmalloc.c` is included from `zbmi_pool.c`, tools that look only at make source lists may miss the allocator implementation.
- The same source set is added to `LIBSRC`, `SERVERSRC`, and `LIBBMISRC`; changes to these files can affect both library and server build surfaces.
- If `@ZOID_SRCDIR@` is wrong or stale, compile failures will appear as missing ZOID/ZBMI headers rather than local source errors.
- If `BUILD_ZOID` is accidentally set in an environment without compatible ZOID libraries, the build may progress to later link failures.

## Test signals

Regenerate or run configure with ZOID enabled and disabled. With `BUILD_ZOID` enabled, verify that `zoid.c`, `server.c`, and `zbmi_pool.c` compile with the substituted include paths and that no separate `dlmalloc.c` object is expected. With `BUILD_ZOID` disabled, verify the build excludes this module cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_zoid/module.mk.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_zoid/server.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_zoid/server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_zoid/zbmi_pool.c -->
# sources/distributed-fs/orangefs/src/io/bmi/bmi_zoid/zbmi_pool.c

## Purpose

`zbmi_pool.c` adapts dlmalloc's mspace allocator into a tiny fixed-buffer allocator for the ZOID BMI expected shared-memory region. It configures dlmalloc at compile time, includes `dlmalloc.c` directly, stores one global `mspace`, and exports init/fini/malloc/free wrappers used by `server.c`.

## Important APIs and functions

- Compile-time defines: `ONLY_MSPACES=1`, `MSPACES=1`, `MALLOC_ALIGNMENT=16`, `USE_LOCKS=1`, and `HAVE_MMAP=0`.
- Weak pragmas are declared for mspace symbols to avoid duplicate symbol errors with ZeptoOS MPI compilers.
- `static mspace pool = NULL` holds the single allocator instance.
- `zbmi_pool_init(void *start, size_t len)` creates the mspace with `create_mspace_with_base(start, len, 1)`.
- `zbmi_pool_fini(void)` destroys the mspace and clears the global handle.
- `zbmi_pool_malloc(size_t bytes)` delegates to `mspace_malloc(pool, bytes)`.
- `zbmi_pool_free(void *mem)` delegates to `mspace_free(pool, mem)`.

## Control flow

The server calls `zbmi_pool_init` after mapping the ZBMI shared memory and selecting the expected-buffer subrange. Subsequent BMI memory allocation or temporary expected-buffer allocation calls enter `zbmi_pool_malloc`, which returns pointers inside the supplied shared-memory region. Frees return memory through `zbmi_pool_free`. Finalization calls `zbmi_pool_fini` before unmapping the shared memory.

## State and persistence behavior

The only module state is the process-global `pool` pointer. Allocator metadata lives inside the supplied shared-memory range because `create_mspace_with_base` embeds the mspace state in that memory. No state persists after `zbmi_pool_fini` and the server's `munmap`; the ZBMI peer should treat expected-buffer offsets as transient.

## Dependencies and integration points

This file depends on `dlmalloc.c` being available in the same directory and on the compiler accepting direct inclusion of a `.c` file. It is compiled via `module.mk.in` as part of the ZOID BMI module. `server.c` uses the functions through `zbmi_pool.h` for `BMI_memalloc`, `BMI_memfree`, and temporary buffers for `BMI_EXT_ALLOC`.

## Risks and edge cases

- There is no guard for `create_mspace_with_base` failure. If `start`/`len` are invalid or too small, `pool` remains `NULL`, and later malloc/free calls enter dlmalloc with a bad mspace.
- There are no double-init or use-after-fini checks.
- `HAVE_MMAP=0` with `ONLY_MSPACES=1` means the pool cannot grow outside the supplied shared-memory range. This is intended but makes allocation failure a normal server condition.
- Directly including `dlmalloc.c` means all compile definitions above the include are critical; moving them or compiling `dlmalloc.c` separately changes behavior.
- The weak pragmas are toolchain-specific and may be ignored or warned on non-GNU/non-compatible compilers.

## Test signals

Create a fixed aligned buffer, call `zbmi_pool_init`, allocate and free several sizes, verify returned pointers are inside the buffer and 16-byte aligned, exhaust the pool to check `NULL` behavior, and call `zbmi_pool_fini`. Negative tests should cover too-small buffers and accidental malloc/free before init or after fini, since the current code does not protect those cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_zoid/zbmi_pool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_zoid/zbmi_pool.h -->
# sources/distributed-fs/orangefs/src/io/bmi/bmi_zoid/zbmi_pool.h

## Purpose

`zbmi_pool.h` declares the fixed shared-memory pool wrapper used by the ZOID BMI server. It hides the dlmalloc mspace implementation behind four functions for initialization, teardown, allocation, and free.

## Important APIs

- `zbmi_pool_init(void *start, size_t len)` initializes the allocator over a caller-provided memory range.
- `zbmi_pool_fini(void)` destroys allocator state.
- `zbmi_pool_malloc(size_t bytes)` allocates bytes from the initialized pool.
- `zbmi_pool_free(void *mem)` frees a pointer previously returned by `zbmi_pool_malloc`.

## Control flow

The header has no runtime control flow. The expected lifecycle is strict: initialize once with the expected shared-memory region, allocate/free while the server is active, then finalize before the backing memory is unmapped.

## State and persistence behavior

The header declares operations over hidden process-local state in `zbmi_pool.c`. The backing storage is supplied by the caller, so memory lifetime is external: callers must not unmap or reuse the region while the pool is active.

## Dependencies and integration points

The declarations use `size_t` but the header does not include `<stddef.h>` itself. In current usage, `server.c` includes system and BMI headers before `zbmi_pool.h`, so `size_t` is already available. The header is included by `server.c` and implemented by `zbmi_pool.c`.

## Risks and edge cases

- Missing `<stddef.h>` makes the header fragile if included first in a new translation unit.
- The API does not expose initialization failure, usable capacity, or ownership checks.
- The API accepts any pointer in `zbmi_pool_free`; invalid pointers are handled only by dlmalloc's runtime checks, which may abort.
- The single hidden pool means this interface cannot manage multiple independent shared-memory regions without modification.

## Test signals

A compile test should include `zbmi_pool.h` first to reveal the missing `size_t` include. Runtime tests should validate the lifecycle, alignment, exhaustion, free/reuse behavior, and invalid-order calls around init/fini.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_zoid/zbmi_pool.h -->
