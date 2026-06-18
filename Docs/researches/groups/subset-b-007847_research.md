# subset-b-007847 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/windows/wincommon.h -->
## sources/distributed-fs/orangefs/src/common/windows/wincommon.h

Purpose: Provides a small Windows portability shim for OrangeFS/PVFS code that otherwise assumes POSIX/GNU C names. It includes `Windows.h` and `<sys/timeb.h>`, remaps common C/POSIX identifiers to MSVC spellings, suppresses GCC `__attribute__`, and supplies `gettimeofday()`.

Important APIs, types, and functions: The file defines `__inline__`, `inline`, and `__func__` compatibility macros, maps `index`, `strdup`, `strcasecmp`, `strncasecmp`, `strtoll`, and `strtok_r`, and implements `static int gettimeofday(struct timeval *tv, struct timezone *tz)` using `_ftime_s`. `tz` is ignored, matching the common portability usage of `gettimeofday`.

Control flow and state: The only runtime path zeroes a `_timeb`, calls `_ftime_s`, and on success fills seconds and microseconds. There is no persistent state.

Dependencies and integration points: Included from Windows-only BMI code such as `bmi.c` when `WIN32` is set. It depends on MSVC CRT functions and a visible `struct timeval` definition from the including environment.

Risks and test signals: `strtoll(str,end,base)` ignores `end` and `base`, which can silently change parsing semantics. `snprintf` is commented out, so callers still need a compatible declaration. Build tests should compile Windows BMI paths and exercise timestamp conversion and string parsing callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/windows/wincommon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi-byteswap.h -->
## sources/distributed-fs/orangefs/src/io/bmi/bmi-byteswap.h

Purpose: Defines byte-swap helpers and BMI host/network encoding macros used by BMI wire-format code. The BMI encoding is little-endian on little-endian hosts and swapped on big-endian hosts, preserving the historic PVFS/BMI on-wire convention.

Important APIs, types, and functions: Exposes `__bswap_16`, `__bswap_32`, `__bswap_64` where not already defined, plus `htobmi16/32/64` and `bmitoh16/32/64`. GNU C builds use statement-expression macros for efficient constant and variable swaps; non-GNU builds receive inline functions for 16/32-bit only.

Control flow and state: Header-only arithmetic macros/functions; no runtime state or persistence. The 64-bit GNU path uses a union to split and swap halves unless the value is compile-time constant.

Dependencies and integration points: Includes `pvfs2-internal.h` and relies on `WORDS_BIGENDIAN` to choose conversion direction. BMI methods and protocol encoders should use these macros for fields carried over the network.

Risks and test signals: Non-GNU big-endian builds hit a deliberate 64-bit unsupported error. Macro arguments for host/BMI conversion are not parenthesized in the little-endian identity definitions, so expression use should be checked. Tests should round-trip 16/32/64-bit values on simulated endian configurations and compile non-GNU Windows paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi-byteswap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi-method-callback.h -->
## sources/distributed-fs/orangefs/src/io/bmi/bmi-method-callback.h

Purpose: Declares callback hooks that transport methods use to notify the generic BMI layer about method-discovered address lifecycle events.

Important APIs, types, and functions: `bmi_method_addr_reg_callback(bmi_method_addr_p map)` registers a method address discovered by an unexpected receive and returns a generic `BMI_addr_t`. `bmi_method_addr_forget_callback(BMI_addr_t addr)` asks BMI to consider dropping an inactive address later. `bmi_method_addr_drop_callback(char *method_name)` requests forced cleanup for inactive addresses owned by a method.

Control flow and state: This header has no state. The implementations in `bmi.c` enqueue forget/drop work or create reference-list entries, so method code can avoid direct access to BMI's internal reference list.

Dependencies and integration points: Includes `bmi-method-support.h` for `bmi_method_addr_p` and `pvfs2-internal.h`. Used by methods such as GM when a peer sends an unexpected message from an address not yet known to BMI.

Risks and test signals: Callers must only register truly new method addresses; the generic callback trusts methods and does not deduplicate. Tests should verify unexpected peer discovery, address reuse, forget-list draining, and forced drop behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi-method-callback.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi-method-support.c -->
## sources/distributed-fs/orangefs/src/io/bmi/bmi-method-support.c

Purpose: Implements shared allocation and parsing helpers used by BMI transport methods.

Important APIs, types, and functions: `bmi_alloc_method_op()` allocates a zeroed `method_op_st` plus method-private payload, registers an op id with `id_gen_fast_register`, and points `method_data` after the generic struct. `bmi_dealloc_method_op()` unregisters and frees it. `bmi_alloc_method_addr()` allocates a contiguous `bmi_method_addr` plus method-private payload and sets `method_type`. `bmi_dealloc_method_addr()` frees it. `string_key()` extracts the address payload for a protocol key from a comma/whitespace separated BMI URL list, allowing `protocol-subzone://target`.

Control flow and state: Allocation helpers create contiguous in-memory objects and rely on the global id generator for operation lookup persistence. `string_key()` loops through possible protocol occurrences, validates exact protocol name or optional subzone, requires `://`, and returns a newly allocated substring up to comma or whitespace.

Dependencies and integration points: Uses `id-generator`, `reference-list`, `quicklist` structures defined in `bmi-method-support.h`, and `gossip` for the surrounding BMI environment. GM and other methods depend on the contiguous layout to recover method payloads.

Risks and test signals: `method_data` pointer arithmetic assumes no alignment-sensitive payload beyond malloc's base alignment. `string_key()` is hand-written parsing and rejects many punctuation characters in subzones. Tests should cover duplicate keys, subzones, malformed delimiters, allocation failure, and op-id unregister on deallocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi-method-support.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi-method-support.h -->
## sources/distributed-fs/orangefs/src/io/bmi/bmi-method-support.h

Purpose: Defines the internal BMI method contract and generic operation/address structures shared by all transports.

Important APIs, types, and functions: `struct bmi_method_ops` is the transport vtable: initialize/finalize, info, memory allocation, send/receive, list I/O, tests, context open/close, cancel, reverse lookup, and address range query. `struct bmi_method_addr` wraps method-specific address data. `struct bmi_method_unexpected_info` carries unexpected arrivals. `struct method_op` stores generic operation state: op id, send/recv direction, tag, error, size accounting, address, context, queue links, hash link, method-private data, list I/O fields, and event id. Constants include `BMI_MAX_CONTEXTS`, `BMI_MAGIC_NR`, and `BMI_METHOD_FLAG_NO_POLLING`.

Control flow and state: Header only, but it establishes queueable state used by both BMI core and methods. `method_op` instances move among method queues and are discoverable through the id generator.

Dependencies and integration points: Pulls in `quicklist`, `bmi-types`, and `pint-event`. Every BMI method must provide a compatible `bmi_method_ops` table and honor the semantics expected by `bmi.c`.

Risks and test signals: Optional vtable members are sometimes assumed present by top-level BMI calls, so method implementations need clear coverage for unsupported operations. `BMI_MAX_CONTEXTS` is fixed at 16. Tests should exercise method activation, context creation, list I/O, cancellation, and unsupported callback paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi-method-support.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi-types.h -->
## sources/distributed-fs/orangefs/src/io/bmi/bmi-types.h

Purpose: Defines public BMI scalar types, flags, option constants, and BMI-specific error values while keeping BMI separable from the rest of PVFS where possible.

Important APIs, types, and functions: Type aliases include `bmi_size_t`, `bmi_msg_tag_t`, `bmi_context_id`, `bmi_op_id_t`, `BMI_addr_t`, `bmi_error_code_t`, and `bmi_hint`. Initialization flags include `BMI_INIT_SERVER`, `BMI_TCP_BIND_SPECIFIC`, and `BMI_AUTO_REF_COUNT`. Option constants cover address lifecycle, max sizes, method address access, TCP tuning, trusted settings, unexpected size, and transport method enumeration. Buffer and op enums define send/recv and preallocated/external buffers. Declares `bmi_errno_to_pvfs()` and `bmi_status_string()`.

Control flow and state: No runtime state. Error macros encode PVFS/BMI errno-like values with high bits and a BMI-specific marker, plus non-errno BMI status values such as `BMI_ECANCEL`, `BMI_EDEVINIT`, and `BMI_ETRYAGAIN`.

Dependencies and integration points: Includes `pvfs2-internal.h`; if PVFS types are visible, `BMI_addr_t` aliases `PVFS_BMI_addr_t`, otherwise it falls back to `int64_t`. Used by public `bmi.h`, method support, and transport code.

Risks and test signals: Numeric error encodings must remain stable for callers and logs. Any new option values need coordination across `bmi.c` and method vtables. Tests should validate errno translation and status string coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi.c -->
## sources/distributed-fs/orangefs/src/io/bmi/bmi.c

Purpose: Implements the top-level Buffered Message Interface dispatcher. It owns BMI initialization, method activation, generic address references, contexts, public send/receive/test calls, address lookup/reverse lookup, memory wrappers, cancellation, and error translation.

Important APIs, types, and functions: Public entry points mirror `bmi.h`: `BMI_initialize/finalize`, `BMI_open_context/close_context`, `BMI_post_send`, `BMI_post_recv`, `BMI_post_sendunexpected`, list variants, `BMI_test`, `BMI_testsome`, `BMI_testcontext`, `BMI_testunexpected`, memory helpers, info helpers, `BMI_addr_lookup`, reverse lookup, range query, and cancel. Internal helpers include `activate_method()`, `construct_poll_plan()`, `grow_method_usage()`, callback implementations from `bmi-method-callback.h`, and address drop/forget drains. Static method tables are compiled under `__STATIC_METHOD_BMI_*`.

Control flow and state: `BMI_initialize()` is reference-counted under `bmi_initialize_mutex`, initializes the id generator and reference list, builds the known method table, and activates server-requested methods. Clients lazily activate known methods during `BMI_addr_lookup()`. Public post calls look up `BMI_addr_t` in `cur_ref_list`, then delegate to the owning method vtable. Test calls either dispatch by operation id or adaptively poll active methods using per-method usage counters to favor recently active methods without starving others. `BMI_testunexpected()` also drains method-requested forget and force-drop queues.

State and persistence behavior: Process-local state includes active/known method tables, address reference list, context occupancy array, expected/unexpected poll usage, initialization count, and deferred forget/drop lists. Address refs store method address, id string, interface pointer, BMI address, and ref count. No durable persistence exists.

Dependencies and integration points: Depends on method vtables from compiled transports, `reference-list`, `op-list`, `id-generator`, `gen-locks`, `str-utils`, and `gossip`. Windows builds include `wincommon.h` and call `WSACleanup()` at finalization.

Risks and test signals: Several paths trust id lookups and method callbacks; stale op ids can crash if not guarded by methods. `BMI_post_sendunexpected_list()` checks `post_send_list` before calling `post_sendunexpected_list`, likely a capability-check bug. `BMI_finalize()` assumes initialize/finalize calls are balanced. `BMI_get_info(BMI_CHECK_MAXSIZE)` has an early return path without unlocking on method error. Tests should cover multi-method activation, lazy client activation, context exhaustion/rollback, reference counting, unexpected auto-ref, address drop queues, list I/O unsupported paths, cancellation after natural completion, and errno/status translation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi.h -->
## sources/distributed-fs/orangefs/src/io/bmi/bmi.h

Purpose: Public API declaration for BMI, the network abstraction used by OrangeFS clients, servers, and flow protocols.

Important APIs, types, and functions: Declares initialization/finalization, context management, expected and unexpected sends/receives, completion tests (`BMI_test`, `BMI_testsome`, `BMI_testcontext`, `BMI_testunexpected`), method-native memory allocation/free, unexpected buffer release, set/get info, address lookup/reverse lookup, wildcard range query, list-vector send/recv variants, and cancellation. `struct BMI_unexpected_info` is the public unexpected-message result with error, address, buffer, size, and tag.

Control flow and state: Header only; callers post asynchronous operations, receive `bmi_op_id_t` handles, and poll/test for completion. Context ids partition completion queues when methods support them. Unexpected messages are consumed through `BMI_testunexpected()` and later released via `BMI_unexpected_free()`.

Dependencies and integration points: Includes `bmi-types.h` and `pvfs2-internal.h`. Implemented by `bmi.c`, backed by method vtables from transports such as TCP, GM, MX, IB, RDMA, Portals, and Zoid depending on build flags.

Risks and test signals: The API relies on caller discipline for buffer lifetime, matching tags and addresses, and polling after cancel. List operations require method support and may return `BMI_ENOSYS`. Tests should validate public API contracts with at least one transport, including immediate completion return value `1`, async completion return `0`, and error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/bmi-gm-addr-list.c -->
## sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/bmi-gm-addr-list.c

Purpose: Implements GM method address list operations over OrangeFS quicklists.

Important APIs, types, and functions: `gm_addr_add()` inserts the `struct gm_addr` embedded list node into a provided list. `gm_addr_del()` removes it. `gm_addr_search()` scans a list for matching GM node id and port id and returns the enclosing `bmi_method_addr_p`.

Control flow and state: The list state is owned by the caller, primarily `gm_addr_list` in `bmi-gm.c`. `gm_addr_search()` linearly scans and compares `node_id` and `port_id`.

Dependencies and integration points: Depends on `bmi-gm-addressing.h`, `bmi-method-support.h`, `quicklist`, and GM headers. It assumes `struct bmi_method_addr` and `struct gm_addr` were allocated contiguously by `bmi_alloc_method_addr()`, then reconstructs the generic pointer by subtracting `sizeof(struct bmi_method_addr)` from the method-data pointer.

Risks and test signals: The reverse pointer arithmetic is fragile if allocation layout changes or alignment padding assumptions differ. There is no locking here; callers must hold the GM interface mutex. Tests should cover add/search/delete and duplicate node/port behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/bmi-gm-addr-list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/bmi-gm-addr-list.h -->
## sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/bmi-gm-addr-list.h

Purpose: Declares quicklist helpers for GM method address tracking.

Important APIs, types, and functions: Exposes `gm_addr_add`, `gm_addr_del`, and `gm_addr_search`, and aliases `bmi_gm_errno_to_pvfs` to the generic `bmi_errno_to_pvfs`.

Control flow and state: Header only. The functions mutate caller-owned quicklists of `struct gm_addr` entries.

Dependencies and integration points: Includes `quicklist.h` and `bmi-method-support.h`; paired with `bmi-gm-addressing.h` for `struct gm_addr` details. Included by `bmi-gm.c`.

Risks and test signals: The header does not document locking or ownership; GM code must serialize access around calls. Compile tests should catch mismatches with `bmi-gm-addressing.h`, and unit-style tests should validate search miss/hit paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/bmi-gm-addr-list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/bmi-gm-addressing.h -->
## sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/bmi-gm-addressing.h

Purpose: Defines GM-specific address payload stored inside generic BMI method addresses.

Important APIs, types, and functions: Constants define `BMI_GM_MAX_PORTS` and `BMI_GM_UNIT_NUM`. `struct gm_addr` contains a quicklist link, GM `node_id`, GM `port_id`, associated generic `BMI_addr_t`, and operation queues for send and handshake behavior.

Control flow and state: Header only. Instances are allocated as method-private payloads by `alloc_gm_method_addr()` in `bmi-gm.c`, inserted into `gm_addr_list`, and used to route sends and match incoming events.

Dependencies and integration points: Includes `bmi-types.h`, `quicklist.h`, `op-list.h`, and `<gm.h>`. It bridges generic BMI addresses with GM node/port identifiers.

Risks and test signals: `BMI_GM_UNIT_NUM` is hard-coded to 0, limiting multi-adapter configurations unless changed elsewhere. Queue fields are not initialized in this header; allocation paths must zero or initialize them. Tests should parse GM URLs, verify node/port matching, and exercise unexpected registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/bmi-gm-addressing.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/bmi-gm-bufferpool.c -->
## sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/bmi-gm-bufferpool.c

Purpose: Provides a small DMA buffer free-list used by the GM transport for control messages and optional rendezvous I/O bounce buffers.

Important APIs, types, and functions: `bmi_gm_bufferpool_init()` allocates a `struct bufferpool`, then preallocates `num_buffers` DMA buffers of `buffer_size` with `gm_dma_malloc` and links them as `cache_entry` nodes. `bmi_gm_bufferpool_finalize()` drains and frees all cached buffers. `bmi_gm_bufferpool_get()` pops one buffer or returns `NULL`. `bmi_gm_bufferpool_put()` pushes a buffer back. `bmi_gm_bufferpool_empty()` reports whether the free list is empty.

Control flow and state: The pool owns a quicklist of free DMA buffers. Recently returned buffers are reused first via `qlist_add`. On init failure, the function finalizes partially allocated state.

Dependencies and integration points: Uses GM DMA allocation APIs, `quicklist`, `gossip`, and `bmi-gm-bufferpool.h`. Called by `BMI_gm_initialize()` for `ctrl_send_pool` and, when enabled, `io_pool`.

Risks and test signals: No internal locking; callers must hold GM synchronization. `finalize()` assumes `bp` is non-null. Buffer size must be large enough to hold a `cache_entry`, so tiny buffers fail. Tests should simulate pool exhaustion, partial allocation failure, and put/get reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/bmi-gm-bufferpool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/bmi-gm-bufferpool.h -->
## sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/bmi-gm-bufferpool.h

Purpose: Declares the GM DMA buffer pool structure and operations.

Important APIs, types, and functions: `struct bufferpool` stores the free-list head, owning `gm_port`, and configured buffer count. Function declarations cover init, finalize, get, put, and empty checks.

Control flow and state: Header only. Pool instances are process-local runtime state owned by the GM method.

Dependencies and integration points: Includes `gossip`, `quicklist`, and `<gm.h>`. Used by `bmi-gm.c` to manage reusable GM DMA buffers without repeated allocation in hot paths.

Risks and test signals: The API does not encode buffer size or in-use count, so misuse can return foreign buffers or finalize while buffers are checked out. Tests should cover lifecycle and static analysis should verify all checked-out control buffers are returned in callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/bmi-gm-bufferpool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/bmi-gm.c -->
## sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/bmi-gm.c

Purpose: Implements the Myricom GM transport method for BMI. It maps the generic BMI vtable onto GM ports, send/receive tokens, immediate messages, unexpected messages, and rendezvous directed sends.

Important APIs, types, and functions: Exports `bmi_gm_ops` with method callbacks. Public method functions include `BMI_gm_initialize/finalize`, address lookup, memory allocation/free, info handlers, send/recv/list/unexpected posts, tests, context open/close, and cancel. Internal protocol structures include `ctrl_req`, `ctrl_ack`, `ctrl_immed`, `ctrl_put`, `ctrl_msg`, and method-private `struct gm_op`. Queue indices track operations waiting for high/low send tokens, sending, receiving, needing receive posts, needing control matches, completed unexpected receives, and cancelled rendezvous receives.

Control flow and state: Initialization opens a GM port, divides tokens between high and low priority, posts control receive buffers, initializes send/control and optional I/O buffer pools, enables remote memory access, and records host/node information. Sends choose immediate mode for small payloads, unexpected mode for BMI unexpected sends, and rendezvous mode for larger expected sends. Rendezvous flow is control request, receiver control ack with remote pointer, sender directed data send, sender put announcement, then receiver completion. Receive posts either match already arrived control/immediate messages or queue for future match. Test calls first drain completion queues, then call `gm_do_work()` to process GM events and token-delayed operations.

State and persistence behavior: All state is in process memory under `interface_mutex`: GM port, address list, operation lists, per-context completion queues, buffer pools, host name, token counters, timeout flag, and cancelled rendezvous counters. No durable persistence exists. Cancelled rendezvous receives may retain buffers for up to 15 minutes before reclamation to avoid remote writes into reused memory.

Dependencies and integration points: Depends on GM `<gm.h>`, BMI method support/callbacks, address list helpers, op lists, id generator, locks, debug/gossip, optional GM registration cache, and optional compile-time buffering strategies (`ENABLE_GM_BUFPOOL`, `ENABLE_GM_REGCACHE`, `ENABLE_GM_REGISTER`, `ENABLE_GM_BUFCOPY`). Unexpected receives call `bmi_method_addr_reg_callback()` for new peers.

Risks and test signals: GM is legacy and compile-flag sensitive. Several list-operation paths assert for registration modes other than buffer pool. Address lookup requires `local_port` to resolve hostnames except `NULL`. Many error paths map GM failures coarsely to protocol/host errors. Cancellation is best-effort and relies on delayed buffer reclamation. Tests need GM hardware or mocks for immediate send/recv, unexpected peer discovery, rendezvous handshake, token starvation queues, list I/O, context completions, timeout behavior, and cancellation in each queue state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/bmi-gm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/module.mk.in -->
## sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/module.mk.in

Purpose: Makefile fragment that adds the GM BMI transport sources to OrangeFS builds when configure enables GM support.

Important APIs, types, and functions: Under `ifneq (,$(BUILD_GM))`, it sets `DIR := src/io/bmi/bmi_gm`, lists `bmi-gm-addr-list.c`, `bmi-gm-bufferpool.c`, and `bmi-gm.c`, expands them into `src`, and appends them to `LIBSRC`, `SERVERSRC`, and `LIBBMISRC`. It also sets `MODCFLAGS_$(DIR)` with GM include paths and `-DENABLE_GM_BUFPOOL`.

Control flow and state: Build-system conditional only; no runtime behavior. The selected source list determines whether `bmi_gm_ops` is compiled into relevant libraries/servers.

Dependencies and integration points: Consumes configure substitutions `BUILD_GM` and `@GM_INCDIR@`. Integrates with the top-level OrangeFS make system through aggregate source variables.

Risks and test signals: The fragment always defines `ENABLE_GM_BUFPOOL` for this directory, so code paths for other GM buffering strategies are not built through this default path. Build tests should run configure with and without GM, verify include path substitution, and confirm all GM objects are linked where expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/module.mk.in -->
