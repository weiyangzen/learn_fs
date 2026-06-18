# subset-b-009683 research

Grouped source-tree-aligned research for the vendored mergerfs libfuse/fmt/khash files in subset B. Each file section is wrapped with reconciliation markers and can be split into its mapped per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/fmt/xchar.h -->
# sources/user-network-fs/mergerfs/vendored/fmt/xchar.h

Purpose: This vendored fmt header adds optional wide-character and non-`char` formatting support on top of `format.h`, `color.h`, `ostream.h`, and `ranges.h`. It exports `wstring_view`, `wformat_context`, `wformat_args`, `wmemory_buffer`, `wformat_string`, wide `format`, `format_to`, `format_to_n`, `formatted_size`, `print`, `println`, `join`, and `to_wstring` APIs, plus generic overloads for exotic character types.

Important flow: compile-time format strings are represented by `basic_fstring<Char,T...>`, which invokes fmt's checker when consteval support is available. Runtime formatting builds a `basic_memory_buffer<Char>`, routes through `detail::vformat_to`, and parses format strings with a `format_handler`. Locale-aware overloads pass `locale_ref` down to `detail::write_loc`, which uses `std::numpunct<wchar_t>` when `FMT_USE_LOCALE` is enabled.

State and integration: the header owns no durable state; it allocates transient buffers and writes to caller-provided output iterators, `FILE*`, or `std::wostream`. It integrates with fmt's buffered context, named-argument support, range joins, text styling, and error handling via `FMT_THROW`.

Risks and test signals: wide output paths depend on C wide I/O semantics and locale availability. Exotic-character overload selection is SFINAE-heavy, so regressions usually appear as compile failures or ambiguous overloads. Useful tests compile wide and exotic string formatting, locale grouping, `format_to_n`, `join` for tuples/ranges, and FILE/wostream print error paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/fmt/xchar.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/khash/khash.h -->
# sources/user-network-fs/mergerfs/vendored/khash/khash.h

Purpose: This is Attractive Chaos' macro-generated C hash table implementation. It provides typed hash maps and sets through `KHASH_INIT`, `KHASH_DECLARE`, `KHASH_MAP_INIT_INT`, `KHASH_MAP_INIT_STR`, and related convenience macros.

Important APIs and types: `khash_t(name)` expands to a struct containing bucket counts, occupancy, flags, keys, and optional values. Public macros wrap generated functions such as `kh_init`, `kh_destroy`, `kh_clear`, `kh_resize`, `kh_put`, `kh_get`, `kh_del`, `kh_exist`, `kh_key`, `kh_val`, `kh_begin`, `kh_end`, and iteration helpers. Built-in hash/equality functions cover 32-bit ints, 64-bit ints, and NUL-terminated strings.

Control flow and state: flags store two bits per bucket for empty/deleted/live state. Lookup and insertion use power-of-two bucket counts and quadratic probing. `kh_put` grows or cleans deleted entries when `n_occupied` reaches the 0.77 upper bound; `kh_resize` rehashes live entries and may shrink arrays. State is entirely heap-resident behind overridable `kcalloc`, `kmalloc`, `krealloc`, and `kfree` macros.

Risks and test signals: tables are not thread-safe, string keys are compared by content but not owned/copied, and allocation failures are reported through `ret = -1` or resize return values that callers must check. Macro expansion can hide type mistakes. Tests should cover insertion, duplicate insert return codes, deletion/tombstone reuse, resize growth/shrink, string-key lifetime assumptions, and allocation-failure behavior if custom allocators are used.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/khash/khash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/Makefile -->
# sources/user-network-fs/mergerfs/vendored/libfuse/Makefile

Purpose: This Makefile builds the vendored mergerfs-flavored libfuse static library and Linux-only helper utilities. The primary output is `build/libfuse.a`, with optional `build/mergerfs-fusermount` and `build/mount.mergerfs`.

Important controls: variables expose tool overrides (`AR`, `INSTALL`, `STRIP`, etc.), build mode flags (`RELEASE`, `SANITIZE`, `LTO`, `STATIC`), standard GNU install directories, and `FUSERMOUNT_DIR`. `SRC_CXX` is all `lib/*.cpp`; object and dependency files live under `build/.objs`. Compilation uses `_FILE_OFFSET_BITS=64`, C++20, GNU99 for C sources, dependency generation, `-D_REENTRANT`, and include paths for `include`, `..`, and `build`.

Control flow and persistence: `all` builds `libfuse.a` and, on Linux, utilities. `build/stamp` creates the build tree. Pattern rules compile C/C++ sources, `ar rcs` archives the library, `strip` mutates utility binaries, `clean` deletes the build directory, and `install-utils` installs utilities and marks `mergerfs-fusermount` setuid root.

Risks and test signals: install behavior is privileged and security-sensitive because of setuid. `LDLIBS` is defined but not used in the `mount.mergerfs` link line, so link failures can reveal missing pthread/rt/atomic needs depending on toolchain. Tests should run `make clean all`, release/sanitize variants, non-Linux utility suppression, and packaging install into a `DESTDIR`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/base_types.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/base_types.h

Purpose: This header centralizes fixed-width primitive aliases used by the vendored libfuse C and C++ headers. It maps `u16/s16/u32/s32/u64/s64` and const variants to `<stdint.h>` types, and defines `f32/f64/f80` floating aliases.

Important behavior: compile-time typedef assertions verify that `float` is 32 bits and `double` is 64 bits. The `f80` assertion is intended to ensure `long double` is at least 64 bits, but the expression checks `sizeof(f64) >= 8`; that always follows from the previous assertion and does not actually validate `f80`.

State and integration: there is no runtime state. This file is included by configuration and connection headers where short aliases make ABI structs more compact to read.

Risks and test signals: typedef names are global and can collide in broad C/C++ include contexts. The `f80` assertion typo is a low-level portability risk. A build on unusual ABIs, plus a focused compile-time static assertion for `sizeof(f80)`, would catch regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/base_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/bounded_queue.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/bounded_queue.hpp

Purpose: `BoundedQueue<T,Traits>` wraps `moodycamel::BlockingConcurrentQueue` with a `LightweightSemaphore` so producers cannot exceed a configured queue depth. It is used by `ThreadPool` to apply backpressure to work submission.

Important APIs: producers can call blocking `enqueue`, nonblocking `try_enqueue`, timed `try_enqueue_for`, or `enqueue_unbounded` for control messages that must bypass the depth limit. Consumers use `wait_dequeue`, which signals a freed slot after removing an item. `make_ptoken` and `make_ctoken` expose moodycamel producer/consumer tokens.

Control flow and state: `_slots` starts at `max_depth`; enqueue waits or decrements before pushing into `_queue`, and successful dequeue increments slots. The queue object is not copyable or movable, preserving token and semaphore invariants.

Risks and test signals: ordinary enqueue calls ignore the return value from the underlying queue, so an allocation/enqueue failure after a slot wait could leak capacity. `enqueue_unbounded` intentionally violates the depth limit and can grow memory use if abused. Tests should stress full queues, timed enqueue expiry, token and non-token paths, consumer slot recovery, and shutdown/control-message scenarios.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/bounded_queue.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/debug.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/debug.hpp

Purpose: This header declares the libfuse debug and syslog tracing API implemented in `lib/debug.cpp`. It is the integration surface for printing decoded FUSE protocol input and output records.

Important APIs: `fuse_debug_set_output` chooses stderr or an append-mode file. The `fuse_debug_*_out` functions format specific reply payloads such as open, init, entry, attr, write, statfs, xattr, lock, bmap, statx, data, ioctl, and poll. `fuse_debug_in_header` and `fuse_debug_out_header` decode generic kernel request and reply headers. `fuse_debug_init_flag_name` converts capability bits to names; syslog helpers summarize init negotiation.

State and integration: the declarations depend on `fuse_kernel.h` structs and route output through the global `fuse_cfg` log sink. They are called from request processing and reply paths to provide line-oriented diagnostics.

Risks and test signals: tracing must stay ABI-synchronized with `fuse_kernel.h`; missing new opcodes or flags silently reduce observability. Tests should enable debug output, exercise representative opcodes, and verify logs are line-complete under concurrent calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/debug.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/extern_c.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/extern_c.h

Purpose: This small compatibility header defines `EXTERN_C_BEGIN` and `EXTERN_C_END` so C ABI declarations can be shared by C and C++ translation units.

Important APIs: under C++ the macros expand to `extern "C" {` and `}`; under C they expand to nothing. Headers such as `fuse.h`, `fuse_common.h`, `fuse_lowlevel.h`, and `fuse_opt.h` use these wrappers around externally visible functions.

State and integration: there is no runtime state. Its only effect is linkage naming, which is critical because the vendored libfuse mixes C-compatible APIs with C++ implementation files.

Risks and test signals: mismatched macro placement can break linkage or nesting. A simple C and C++ compile/link test for public headers is sufficient.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/extern_c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fatal.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fatal.hpp

Purpose: `fatal::abort` provides a formatted fatal-error path for mergerfs. It formats a message with fmt, writes it to stderr with a `mergerfs: FATAL` prefix, logs it to syslog at critical priority, and calls `std::abort`.

Important APIs and flow: the template accepts `fmt::format_string<Args...>` so format checking happens at compile time where fmt supports it. The function is marked `[[noreturn]]`, which helps callers and optimizers understand control never returns.

State and integration: it depends on `SysLog::crit` and fmt. It does not persist state, but it emits to process stderr and the system logger.

Risks and test signals: this path terminates the process and is unsuitable for recoverable errors. Tests should normally isolate it in a subprocess and assert stderr/syslog formatting and abnormal termination. Formatting failures would be compile-time for literal format strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fatal.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fs_dirent64.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fs_dirent64.hpp

Purpose: This header defines `fs::dirent64`, a compact directory-entry record with inode, offset, record length, type, and flexible `name[]` storage.

Important API: `namelen()` returns `strlen(name)`, assuming `name` is NUL-terminated. The layout is used by `fuse_dirents.hpp` overloads to ingest filesystem directory entries into FUSE reply buffers.

State and integration: the struct is a view over variable-sized memory and owns nothing. It bridges lower-level filesystem directory records to the vendored FUSE dirent aggregation layer.

Risks and test signals: because `namelen()` scans until NUL, malformed or non-terminated records can overread. Tests should cover valid names, long names, and callers that pass explicit name lengths to avoid relying on implicit termination.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fs_dirent64.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse.h

Purpose: This is the high-level public API for the vendored FUSE layer. It defines `struct fuse_operations` callbacks used by mergerfs, declares setup/teardown/event-loop functions, and exposes cache/passthrough helpers.

Important APIs and types: `fuse_operations` covers path and file-handle operations including `getattr`, `readlink`, namespace mutation, xattrs, directory iteration, `read`, `write`, `copy_file_range`, `setupmapping`, `removemapping`, `syncfs`, `tmpfile`, and `statx` variants. `fuse_backing_id_is_valid` validates passthrough backing IDs. Public functions include `fuse_new`, `fuse_destroy`, `fuse_exit`, config accessors, `fuse_loop_mt`, `fuse_main`, `fuse_setup`, `fuse_teardown`, cache invalidation, garbage collection, and passthrough open/close.

Control flow and state: callers provide operation tables; the implementation mounts `/dev/fuse`, initializes sessions, dispatches kernel requests to callbacks, and sends replies. Request identity is passed through `fuse_req_ctx_t`. Persistent state lives in the opaque `struct fuse`, sessions, file handles, node caches, and backing IDs.

Risks and test signals: callback signatures must match the dispatcher exactly, especially newer extensions such as passthrough and statx. Missing callbacks may translate to `-ENOSYS` or default success depending on operation. Tests should mount a small filesystem and exercise high-level operations, multithreaded loop behavior, invalidation, passthrough ID lifecycle, and teardown after interrupts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_attr.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_attr.h

Purpose: `fuse_attr_t` is a C ABI attribute struct mirroring most kernel FUSE inode metadata: inode, size, blocks, timestamps with nanoseconds, mode, link count, ownership, device, block size, and padding.

Important behavior: this header is a lightweight wrapper and does not include conversion functions. It is used by `fuse_direntplus_t` and higher-level reply construction where attributes are packed near directory entries.

State and integration: the struct owns no memory and is copied into protocol buffers. It differs slightly from `struct fuse_attr` in `fuse_kernel.h`, where the final field is `flags`; here it is `_padding`, so conversion code must be explicit about which ABI is being used.

Risks and test signals: field-order and size drift can corrupt FUSE replies. ABI size/offset static assertions and readdirplus/getattr integration tests are useful.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_attr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_cfg.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_cfg.hpp

Purpose: `fuse_cfg_t` stores process-wide configuration for the vendored FUSE runtime, including identity overrides, debug logging, kernel negotiation limits, passthrough depth, thread counts, queue depth, CPU pinning policy, and request timeout.

Important APIs and state: `valid_uid`, `valid_gid`, and `valid_umask` validate sentinel-backed settings. `log_file()` and `log_filepath()` getters/setters protect shared log sink state with a `std::shared_mutex`; the default log file is a non-owning `stderr` shared pointer. The header declares global `fuse_cfg`.

Control flow and integration: command-line/config parsing populates this global, debug tracing reads it, and session/init negotiation consumes max background, max pages, passthrough stack depth, thread counts, pinning, and timeouts.

Risks and test signals: global mutable state affects all mounts in-process, and FILE ownership is controlled by custom shared-pointer deleters in debug code. Tests should cover concurrent log sink replacement, defaults, valid/invalid sentinel handling, and config propagation into init replies and thread-pool setup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_cfg.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_common.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_common.h

Purpose: This header defines common FUSE public types and functions shared by high-level and low-level APIs. It enforces 64-bit `off_t`, declares file-info flags, capability bits, mount/daemon utilities, buffer structs, and signal handler helpers.

Important APIs and types: `fuse_file_info_t` stores open flags, bitfield behavior flags, file handle, passthrough backing ID, and lock owner. Capability macros map public `FUSE_CAP_*` bits onto negotiated kernel features. `fuse_mount`, `fuse_unmount`, `fuse_parse_cmdline`, `fuse_daemonize`, `fuse_version`, and `fuse_pollhandle_destroy` are C ABI entry points. `fuse_buf` plus buffer flag enums describe memory or fd-backed data transfers.

Control flow and state: mount helpers create and tear down `/dev/fuse` sessions; signal handlers store a global session until removed. Buffers are transient descriptors and do not own fd lifetimes by themselves.

Risks and test signals: `_FILE_OFFSET_BITS=64` is mandatory. Bitfield layout is ABI-sensitive across compilers, so this header should only be used with the expected toolchain/ABI. Tests should cover command-line parsing, foreground/debug options, mount/unmount cleanup, signal exit behavior, and file-info flag translation into `fuse_open_out`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_conn_info.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_conn_info.hpp

Purpose: `fuse_conn_info_t` records negotiated protocol version and capability masks for a FUSE connection.

Important fields: `proto_major` and `proto_minor` identify the negotiated kernel protocol; `capable` contains features advertised by the kernel/runtime, and `want` contains features requested by the filesystem.

State and integration: a pointer is passed to init callbacks in both high-level and low-level APIs. The same data is embedded in `fuse_req_t`, letting request handling know what features are active.

Risks and test signals: feature bits must stay aligned with `fuse_common.h` and `fuse_kernel.h`. Init negotiation tests should verify capabilities such as writeback cache, max pages, passthrough, and request timeout are reflected correctly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_conn_info.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_dirent.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_dirent.h

Purpose: `fuse_dirent_t` is a vendored directory-entry wire helper with inode, offset, name length, type, and flexible trailing name storage.

Important behavior: it is a C struct used to pack one directory record into a contiguous response buffer. Size and alignment are handled by surrounding code, usually using FUSE record alignment rules.

State and integration: the struct owns no memory; it is embedded in `fuse_direntplus_t` and appended to `fuse_dirents_t` buffers.

Risks and test signals: callers must allocate enough trailing storage and align records correctly. Directory listing tests should validate names, offsets, d_type values, and exact byte layout.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_dirent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_direntplus.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_direntplus.h

Purpose: `fuse_direntplus_t` combines entry cache metadata, inode attributes, and a directory entry for READDIRPLUS-style responses.

Important fields: `entry` is a `fuse_entry_t`, `attr` is a `fuse_attr_t`, and `dirent` is the variable-length directory entry tail.

State and integration: the struct is a packed response-building helper and owns no memory. It depends on the separate local ABI wrappers rather than directly using `struct fuse_entry_out`.

Risks and test signals: flexible-array layout means allocation size must include the filename and alignment padding. Tests should compare generated READDIRPLUS buffers against kernel FUSE expectations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_direntplus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_dirents.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_dirents.hpp

Purpose: `fuse_dirents_t` aggregates directory entries before replying to FUSE readdir/readdirplus requests. It stores raw data bytes and an offset index using `kvec_t`.

Important APIs: `fuse_dirents_init`, `fuse_dirents_free`, and `fuse_dirents_reset` manage the vectors. `fuse_dirents_add` has overloads for POSIX `dirent` and vendored `fs::dirent64`, each taking an explicit name length.

Control flow and state: entries are appended to `data`, and per-entry offsets are appended to `offs`. The state is in heap buffers owned by `kvec`; reset preserves allocations while clearing logical contents, and free releases them.

Risks and test signals: `kvec` allocation failures are not type-safe unless implementations check `realloc`. Offset accounting and record alignment are critical for kernel parsing. Tests should add entries of varied name lengths, reset/reuse the container, and verify byte offsets and final reply size.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_dirents.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_entry.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_entry.h

Purpose: `fuse_entry_t` stores cache metadata for a looked-up node: node ID, generation, entry timeout, attribute timeout, and nanosecond timeout parts.

Important behavior: it is a lightweight C ABI struct used in local response helpers and `fuse_direntplus_t`. It does not contain the attributes themselves.

State and integration: the struct is copied into response buffers and integrates with lookup/readdirplus cache handling. It owns no external resources.

Risks and test signals: node ID/generation semantics are kernel-visible; reuse bugs can break NFS/export support or cache invalidation. Tests should exercise lookup cache timeout encoding and generation stability.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_entry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_kernel.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_kernel.h

Purpose: This is the kernel/userspace FUSE protocol ABI header, updated through protocol minor 45. It defines version constants, opcodes, notify codes, feature flags, request/reply structs, dirent alignment macros, passthrough ioctls, DAX mapping structs, statx structs, io_uring structs, and request-timeout support.

Important APIs and types: core structs include `fuse_in_header`, `fuse_out_header`, `fuse_attr`, `fuse_entry_out`, `fuse_attr_out`, `fuse_open_in/out`, read/write, xattr, lock, ioctl, poll, init, statx, copy-file-range, setup/removemapping, and notification payloads. Macros such as `FUSE_REC_ALIGN`, `FUSE_DIRENT_SIZE`, and `FUSE_DIRENTPLUS_SIZE` define exact buffer layout. Capability flags span both low 32-bit `flags` and high `flags2` bits.

Control flow and state: the kernel sends a `fuse_in_header` plus opcode-specific payload, userspace replies with `fuse_out_header` plus output payload, and init negotiation chooses protocol/features. No state is stored in the header, but every field is an ABI contract for persistent kernel connection state such as lookup counts, file handles, backing IDs, cache timeout, and mapping windows.

Risks and test signals: this file is highly ABI-sensitive; field-size, padding, endian, or flag drift can make the filesystem unusable. Some macros reference platform constants such as `PAGE_SIZE`. Tests should include compile-time size/offset checks against Linux headers, init negotiation for flags2 features, readdir alignment validation, and exercised opcodes for newer features like statx, passthrough, request timeout, and copy_file_range_64.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_kernel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_lowlevel.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_lowlevel.h

Purpose: This header declares the low-level FUSE session API, where handlers receive raw request headers and must explicitly send replies. It is the bridge between kernel protocol dispatch and filesystem-specific operations.

Important APIs and types: `fuse_entry_param` combines inode, generation, `struct stat`, and cache timeouts for entry replies. `fuse_lowlevel_ops` lists handler hooks for all supported opcodes, including newer operations such as `statx`, `syncfs`, `tmpfile`, `setupmapping`, `removemapping`, and `copy_file_range`. Reply functions cover errors, entries, creates, attrs, statx, readlink, open, write, copy_file_range_64, buffers, iovecs, statfs, xattr sizing, bmap, ioctl retry/final, and poll. Notification APIs invalidate inode/entry caches, delete dentries, poll, and retrieve kernel cached data.

Control flow and state: a session receives a buffer, dispatches by opcode to a `fuse_lowlevel_ops` function, and the handler owns the request until it calls a reply function or `fuse_reply_none`. Session APIs manage fd, buffer size, exit state, multithreaded loops, and user data.

Risks and test signals: request pointers other than `fuse_req_t` are only valid during the call unless copied. Missing replies can hang kernel requests; double replies can corrupt lifecycle. Tests should exercise delayed replies, interrupted requests returning `-ENOENT`, session exit/reset, notifications outside operation locks, and multithreaded receive/process loops.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_lowlevel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_msgbuf.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_msgbuf.hpp

Purpose: This header declares allocation and garbage-collection functions for FUSE message buffers. It abstracts page size, configured buffer size, and allocation pooling for `fuse_msgbuf_t`.

Important APIs: `msgbuf_get_pagesize`, `msgbuf_set_bufsize`, and `msgbuf_get_bufsize` expose buffer sizing. `msgbuf_alloc` and `msgbuf_alloc_page_aligned` allocate message buffers; `msgbuf_free` returns them; `msgbuf_clear`, `msgbuf_gc`, and `msgbuf_alloc_count` manage or inspect the backing pool.

State and integration: implementation state is outside this header, likely a global object pool/cache. The buffers are used by receive/process loops to hold raw FUSE kernel messages.

Risks and test signals: buffer size must be large enough for negotiated max write/pages, and page-aligned buffers must really satisfy kernel/direct I/O expectations. Tests should cover allocation/free counts, GC, page alignment, buffer resizing before and after allocations, and large request handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_msgbuf.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_msgbuf_t.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_msgbuf_t.h

Purpose: `fuse_msgbuf_t` is the simple C struct backing message buffers: a 32-bit size and a `char*` memory pointer.

Important behavior: the struct separates metadata from allocated payload memory. It does not encode ownership policy; allocation/free routines in `fuse_msgbuf.hpp` own that contract.

State and integration: instances are passed through receive and processing code to hold raw FUSE messages.

Risks and test signals: size is `uint32_t`, so callers must avoid truncating larger negotiated sizes. Tests should validate allocation sizes, null handling, and max request boundaries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_msgbuf_t.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_opt.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_opt.h

Purpose: This is the FUSE option parsing public interface. It describes templates for command-line and `-o` options, an argument-vector container, and functions to parse, add, insert, escape, free, and match options.

Important APIs and types: `struct fuse_opt` maps a template to either a data offset/value assignment or a processor callback key. `FUSE_OPT_KEY` and `FUSE_OPT_END` build option tables. `struct fuse_args` tracks `argc`, NUL-terminated `argv`, and allocation ownership. `fuse_opt_proc_t` lets callers keep, discard, or transform options.

Control flow and state: `fuse_opt_parse` reads input args, applies all matching option templates, mutates caller data by offset or invokes the callback, and writes an output argument vector. Helper functions allocate or free option strings/argument arrays.

Risks and test signals: offset-based writes are inherently unsafe if tables do not match the target struct. `%s` templates allocate strings that callers must later free through the expected path. Tests should cover `-o` comma lists, escaped commas, two-argument options, non-options after `--`, keep/discard keys, parse errors, and repeated parse/free cycles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_opt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_pollhandle.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_pollhandle.h

Purpose: `fuse_pollhandle_t` records kernel poll handle state for readiness notifications.

Important fields: `kh` is the kernel handle to wake, and `se` points to the owning `fuse_session`.

State and integration: poll callbacks receive these handles and may later call notification functions such as `fuse_notify_poll` or `fuse_lowlevel_notify_poll`. The session pointer ties notifications to the correct mount.

Risks and test signals: handles are only valid until destroyed; stale handles can notify the wrong or freed session. Tests should cover poll callback scheduling, destroy behavior, and notification after release.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_pollhandle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_req.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_req.hpp

Purpose: `fuse_req_t` is the vendored request object used by low-level dispatch and replies. It bundles request context, session pointer, file descriptor, negotiated connection info, and an ioctl mode bit.

Important APIs: `fuse_req_alloc` and `fuse_req_free` allocate and release request objects. Fields expose `fuse_req_ctx_t ctx`, `struct fuse_session *se`, `int fd`, `fuse_conn_info_t conn`, and `ioctl_64bit`.

State and integration: request objects carry per-request identity and connection/session state from receive through reply. They are central to every `fuse_reply_*` call.

Risks and test signals: lifecycle is strict: use after reply/free or double-free can corrupt dispatch. Tests should cover allocation defaults, reply freeing behavior, delayed replies, and ioctl 32/64-bit flag propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_req.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_req_ctx.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_req_ctx.h

Purpose: `fuse_req_ctx_t` is a C ABI snapshot of the FUSE input header fields relevant to filesystem operations.

Important fields: it stores length, opcode, unique request ID, node ID, uid, gid, pid, and umask. These values are passed into high-level operation callbacks.

State and integration: the struct owns no memory and is valid as request metadata. It decouples mergerfs callbacks from raw `fuse_in_header` while preserving caller identity and permission context.

Risks and test signals: incorrect uid/gid/pid/umask propagation can break permission handling. Tests should exercise create/mkdir/mknod umask paths, idmapped invalid uid/gid behavior, and callback-visible request identity.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_req_ctx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_timeouts.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_timeouts.h

Purpose: `fuse_timeouts_t` holds entry and attribute cache timeout values as 64-bit integers.

Important behavior: high-level callbacks receive or fill this struct for operations that return entries or attributes, allowing the dispatcher to encode cache validity in replies.

State and integration: it is copied into reply payloads and owns no resources. It integrates with lookup, getattr, symlink, link, fgetattr, statx, and readdirplus paths.

Risks and test signals: timeout unit consistency matters; mismatched seconds/nanoseconds conversion can cause stale or uncached kernel entries. Tests should verify zero, short, and long timeout encoding.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_timeouts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/invocable.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/invocable.h

Purpose: This header implements `ofats::any_invocable`, a C++ move-only type-erased callable similar to C++23 `std::move_only_function`/`std::any_invocable`. It supports cv/ref/noexcept-qualified function signatures.

Important APIs and flow: small nothrow-movable callables are stored in an inline two-pointer buffer; larger callables are heap allocated. Handler tables provide destroy, move, and call operations. Constructors accept callables or `std::in_place_type_t`, assignment swaps through temporaries, and `operator()` invokes the erased callable with signature-qualified constraints.

State and persistence: each object owns exactly one callable or is empty. Move construction transfers handler and storage, then clears the source handler. There is no global state.

Risks and test signals: calling an empty object dereferences a null call pointer. The large-handler move copies the pointer but relies on clearing the source handler to avoid double delete. Tests should cover small/large callables, move/swap, reference wrappers, noexcept signatures, ref-qualified invocation, exception propagation, and empty checks before calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/invocable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/kvec.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/kvec.h

Purpose: This Attractive Chaos header provides macro-based dynamic arrays for C-style code. It is used by directory aggregation to store byte buffers and offsets.

Important APIs: `kvec_t(type)` declares a vector with `n`, `m`, and `a`. Macros initialize, destroy, resize, copy, push, push pointer slots, indexed auto-growth (`kv_a`), pop, delete-by-swap, and inspect size/capacity.

Control flow and state: capacity doubles on push and rounds up on indexed growth. Storage is managed with `realloc` and freed with `free`; vector state is embedded in the caller's struct.

Risks and test signals: allocation failures are not checked by these macros, which can lose the old pointer on `realloc` failure. The macros evaluate some arguments multiple times and are not thread-safe. Tests should focus on append/growth, indexed holes, copy, reset/free patterns, and out-of-memory behavior if wrapped.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/kvec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/maintenance_thread.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/maintenance_thread.hpp

Purpose: `MaintenanceThread` declares a process-wide background maintenance facility for periodic or queued cleanup tasks.

Important APIs: `setup()` starts or initializes the facility, `stop()` shuts it down, and `push_job(const std::function<void(u64)> &)` queues work that receives a `u64` argument, likely a tick/count/time value.

State and integration: implementation state is external to this header and likely includes a worker thread and job list. It integrates with libfuse cache cleanup, message buffer GC, or other runtime maintenance tasks.

Risks and test signals: lifecycle ordering matters; jobs pushed before setup or after stop need defined behavior. Tests should cover start/stop idempotency, job execution, shutdown while jobs are queued, and exception handling inside jobs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/maintenance_thread.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/mutex.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/mutex.hpp

Purpose: This header selects debug or non-debug pthread mutex wrappers and provides RAII helpers around `pthread_mutex_t`.

Important APIs: `mutex_t` is `pthread_mutex_t`. `Mutex` initializes/destroys a mutex and converts to `mutex_t&`. `LockGuard` locks in its constructor and unlocks in its destructor. The `mutex_lockguard(m)` macro uses a scope guard to lock and defer unlock while preserving call-site file/function/line for debug builds.

State and integration: each `Mutex` owns one pthread mutex. The wrappers are used by object pools, thread vectors, and other low-level shared state.

Risks and test signals: `mutex_lockguard` expands to statements and must be used carefully in control-flow contexts. Copying `Mutex` is not explicitly deleted, so accidental copies would duplicate a pthread mutex object unsafely. Tests should cover debug and release builds, RAII unlock on exceptions, and misuse in single-line `if` statements during review.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/mutex.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/mutex_debug.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/mutex_debug.hpp

Purpose: This debug-mode wrapper instruments pthread mutex operations with call-site-aware error reporting and timed-lock notices.

Important APIs and flow: macros `mutex_init`, `mutex_destroy`, `mutex_lock`, and `mutex_unlock` expand to underscored functions with file/function/line. Initialization uses `PTHREAD_MUTEX_ADAPTIVE_NP` where available. Locking loops with `pthread_mutex_timedlock` using 1 ms deadlines, printing a notice on each timeout until the lock is acquired or an error aborts the process.

State and integration: state is the pthread mutex itself; diagnostics go to stderr through fmt. This file is included by `mutex.hpp` when `DEBUG` is defined.

Risks and test signals: repeated timeout logging can be noisy under legitimate contention, and abort-on-error is intentionally fatal. Tests should cover successful lock/unlock, destroy errors in a subprocess, and contention diagnostics without deadlocking the test suite.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/mutex_debug.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/mutex_ndebug.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/mutex_ndebug.hpp

Purpose: This release-mode wrapper provides compact pthread mutex helpers that abort on pthread errors without formatted diagnostics.

Important APIs: `mutex_init` creates an adaptive mutex, `mutex_lock` locks, `mutex_unlock` unlocks, and `mutex_destroy` destroys. All functions call `std::abort()` if the pthread operation returns nonzero.

State and integration: it is selected by `mutex.hpp` when `DEBUG` is not defined. It owns no extra state beyond caller-provided pthread mutexes.

Risks and test signals: fatal aborts simplify error handling but make recovery impossible. Adaptive mutex availability is normalized to `PTHREAD_MUTEX_NORMAL` where missing. Tests should compile on Linux and FreeBSD-like environments and run basic lock/unlock/destroy paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/mutex_ndebug.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/objpool.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/objpool.hpp

Purpose: `ObjPool<T,Allocator,ShouldPool>` is a thread-safe object pool for nothrow-destructible objects that are at least large enough to overlay pool metadata. It supports variable allocation sizes for flexible-array-style objects.

Important APIs and flow: `alloc` and `alloc_size` pop a node with sufficient allocation size or allocate aligned memory, then placement-new a `T`. `free` and `free_size` run the destructor and either push the memory back onto the free list or deallocate it according to `ShouldPool`. `clear` frees all pooled nodes, `size` returns the current pool count, and `gc` releases about 10 percent, at least one node.

State and integration: the pool stores a singly linked free list protected by `mutex_t`, plus an atomic count for observation. It uses `DefaultAllocator` with aligned `operator new/delete` unless customized. It can back FUSE request/message buffers.

Risks and test signals: `free_size` trusts the caller-provided size, and `to_node` overlays metadata on object memory after destruction. Constructors that throw are handled, but only if allocation metadata is correct. Tests should cover reuse by size, non-pooled predicate deallocation, GC, clear during no live objects, constructor exceptions, and concurrent alloc/free.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/objpool.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/stat_utils.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/stat_utils.h

Purpose: This platform shim exposes nanosecond timestamp access macros for `struct stat`.

Important APIs: on Linux, `ST_ATIM_NSEC`, `ST_CTIM_NSEC`, and `ST_MTIM_NSEC` read `st_atim.tv_nsec`, `st_ctim.tv_nsec`, and `st_mtim.tv_nsec`. On FreeBSD, they read the `st_*timespec.tv_nsec` fields. Other platforms produce a compile-time error.

State and integration: there is no state. Attribute conversion code uses these macros when populating FUSE timestamp fields.

Risks and test signals: unsupported platforms fail compilation, which is preferable to silently losing precision. Tests should compile on target platforms and verify nanosecond values round-trip in getattr/statx replies.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/stat_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/syslog.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/syslog.hpp

Purpose: `SysLog` wraps system syslog calls with fmt formatting and mergerfs defaults.

Important APIs: `open()` calls `openlog` with ident `mergerfs`, `LOG_CONS|LOG_PID`, and `LOG_USER`; `close()` calls `closelog`. `log(priority, format, args...)` formats a message and passes it as `%s` to `syslog`. Convenience functions map to info, debug, notice, warning, error, alert, and critical priorities.

State and integration: syslog state is process-global. The wrapper is used by fatal errors, thread-pool exception logging, and debug init summaries.

Risks and test signals: formatting happens before syslog, so expensive or throwing format operations occur in the caller context. Tests can inject representative format strings and verify that user-controlled percent signs are safe because syslog receives a fixed `%s` format.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/syslog.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/thread_pool.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/thread_pool.hpp

Purpose: `ThreadPool` is a pthread-backed work queue for FUSE processing. It uses `BoundedQueue<ofats::any_invocable<void()>>` to limit normal work backlog while allowing unbounded internal control messages.

Important APIs and flow: the constructor blocks signals while spawning workers, names threads when requested, and throws if none start. Workers wait on queue tokens, disable cancellation while executing a task, catch/log ordinary exceptions, clear the callable, then re-enable cancellation. Public methods add/remove/set thread count, enqueue work with or without producer tokens, try/timed enqueue work, enqueue future-returning tasks, snapshot thread IDs, and create producer tokens.

State and integration: state includes queue, pool name, pthread vector, and a `Mutex` protecting the vector. Destructor cancels and joins all known threads. `remove_thread` enqueues a control task that erases its own thread ID, sets a promise, and exits.

Risks and test signals: `pthread_cancel`-based shutdown relies on workers being in cancellation-enabled regions, so long-running tasks delay destruction. `enqueue_task` uses `std::invoke_result_t<FuncType>` without explicit argument list, suitable only for nullary callables. Tests should cover queue backpressure, dynamic resize, exception logging, future results/exceptions, thread naming length, destructor with idle and busy workers, and signal mask behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/thread_pool.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/cpu.cpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/lib/cpu.cpp

Purpose: This implementation provides CPU affinity and topology helpers for thread pinning.

Important functions: `CPU::getaffinity` reads the current process affinity mask with `sched_getaffinity`; `setaffinity` overloads set a pthread to a mask, one CPU, or a set of CPUs. `count` returns the number of CPUs in the current affinity mask. `cpus` returns allowed CPU IDs. `cpu2core` and `core2cpus` read `/sys/devices/system/cpu/cpuN/topology/core_id` to map logical CPUs to core IDs.

Control flow and state: no persistent state is stored. Each query reads the current affinity mask and, for topology, sysfs files. Topology loops stop early if a core_id file cannot be opened.

Risks and test signals: this implementation is Linux/sysfs oriented despite some FreeBSD include handling in the header. Ignoring `getaffinity` errors in `cpus` and topology functions can yield empty or partial maps. Tests should mock or run on systems with restricted affinity, missing sysfs topology files, hyperthreaded cores, and invalid CPU IDs for `setaffinity`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/cpu.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/cpu.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/lib/cpu.hpp

Purpose: This header declares the `CPU` utility class used for CPU affinity and topology-aware thread placement.

Important APIs and types: aliases define vectors of pthread IDs and CPU IDs, plus maps from CPU to core and core to CPU set. Static methods count available CPUs, get/set affinity masks, set affinity for a single CPU or CPU set, list CPUs, and build topology maps.

State and integration: the class is stateless. It depends on pthreads, `sched.h`, and platform-specific pthread headers on FreeBSD. It likely integrates with FUSE thread pinning configured by `fuse_cfg.pin_threads`.

Risks and test signals: callers must handle negative errno-style returns from affinity setters/getters. Tests should compile on supported platforms and verify class declarations match the Linux implementation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/cpu.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/crc32b.cpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/lib/crc32b.cpp

Purpose: This file implements table-driven CRC-32B checksum calculation.

Important functions and flow: `crc32b_start` returns the initial `0xFFFFFFFF` seed. `crc32b_continue` iterates each input byte, updates the CRC using `CRC32BTABLE[(crc ^ byte) & 0xFF] ^ (crc >> 8)`, and allows incremental updates. `crc32b_finish` xor-finalizes with `0xFFFFFFFF`. `crc32b` performs the start/continue/finish sequence for one buffer.

State and integration: the 256-entry lookup table is static const data; functions keep all computation in local variables. The C ABI is declared by `crc32b.h`.

Risks and test signals: `crc32b_t` and length are unsigned int, limiting single-call length on platforms where unsigned int is 32-bit. `char` signedness is masked after xor, so ordinary byte input remains stable. Tests should compare known vectors such as empty string and `123456789`, and verify chunked `continue` equals one-shot `crc32b`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/crc32b.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/crc32b.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/lib/crc32b.h

Purpose: This header declares the C ABI for CRC-32B helpers.

Important APIs: `crc32b_t` is `unsigned int`. `crc32b_start`, `crc32b_continue`, and `crc32b_finish` support streaming checksums, while `crc32b` computes a one-shot checksum over a buffer and length.

State and integration: functions own no persistent state; streaming state is the CRC value carried by the caller. The header is C++ compatible through `extern "C"`.

Risks and test signals: callers must pass the prior intermediate CRC to `crc32b_continue`, not the finalized value unless intentionally starting a new stream. Tests should compile from C and C++ and verify known checksum vectors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/crc32b.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/debug.cpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/lib/debug.cpp

Purpose: This file implements line-oriented FUSE protocol tracing. It decodes request and reply payloads into readable key/value logs and emits init summaries to syslog.

Important APIs and flow: `fuse_debug_set_output` switches `fuse_cfg` logging to stderr or an append-mode line-buffered file with safe `FILE*` ownership. Helpers quote strings/data, format open/FUSE/write/fopen/init flags, print xattr values as text or hex, and timestamp records with `CLOCK_MONOTONIC`. `fuse_debug_in_header` locks the output `FILE`, prints common request header fields, switches on opcode, and delegates to opcode-specific payload printers. Output functions print structured replies for open, init, entry, attr, entry+open, readlink, write, statfs, xattr, locks, bmap, statx, data, ioctl, poll, and generic error headers.

State and integration: persistent state is the global `fuse_cfg` log sink and path. The implementation depends on `fuse_kernel.h` ABI structs, fmt, libc `FILE*`, syslog wrappers, and errno/string helpers. It is called from request dispatch and reply functions when debug logging is enabled.

Risks and test signals: debug decoding must stay synchronized with opcodes and struct layouts. Some newer open flags are not included in `_fuse_fopen_flag_to_str`, so logs may omit flags such as passthrough or noflush. String parsing assumes kernel payloads are NUL-terminated where the protocol promises names. Tests should feed synthetic request buffers for each opcode, check concurrency does not interleave lines, verify file-output switching/closing, and compare init flag names for high `flags2` bits.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/debug.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/format.cpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/lib/format.cpp

Purpose: This vendored fmt translation unit provides explicit template instantiations for fmt formatting internals, reducing header-only duplication for the libfuse build.

Important APIs: it includes `fmt/format-inl.h`, opens the fmt namespace, and explicitly instantiates locale references, Dragonbox float/double conversion, thousands separator and decimal point helpers for `char` and `wchar_t`, and deprecated `buffer<Char>::append` overloads.

State and integration: there is no runtime state beyond fmt internals. The object file is included in `libfuse.a` through the Makefile's `lib/*.cpp` glob and satisfies symbols used by both narrow and wide formatting paths.

Risks and test signals: the file must match the vendored fmt version and compile flags; mismatched headers can produce duplicate or missing symbols. Tests should link a binary using fmt narrow/wide formatting, locale formatting when enabled, and floating-point formatting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/format.cpp -->
