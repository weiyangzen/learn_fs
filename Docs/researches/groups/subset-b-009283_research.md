# subset-b-009283 liburing source research

This grouped report covers the requested liburing headers, library sources, and regression tests. Each section preserves the source path in its title and is bounded by the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/include/liburing.h -->
## sources/test-tools/liburing/src/include/liburing.h

Purpose: this is liburing's primary public API header. It exposes the user-space ring structures (`io_uring`, `io_uring_sq`, `io_uring_cq`, `io_uring_zcrx_rq`), queue setup/teardown entry points, submit/wait functions, registration wrappers, version APIs, and a large inline family of SQE preparation helpers.

Important APIs/types/functions: public initialization includes `io_uring_queue_init*`, `io_uring_queue_mmap`, `io_uring_ring_dontfork`, and `io_uring_queue_exit`. Completion APIs include `io_uring_wait_cqe*`, `io_uring_wait_cqes*`, `io_uring_peek_cqe`, `io_uring_peek_batch_cqe`, `io_uring_cqe_seen`, and `io_uring_cq_advance`. Submission helpers include `io_uring_get_sqe`, `io_uring_get_sqe128`, `io_uring_submit*`, and dozens of `io_uring_prep_*` functions for read/write, networking, poll, timeouts, file operations, xattrs, futex, uring command, pipe, fixed files, and zerocopy features. It also exposes buffer-ring helpers such as `io_uring_buf_ring_init`, `io_uring_buf_ring_add`, `io_uring_buf_ring_advance`, and `io_uring_buf_ring_available`.

Control flow: applications allocate or map a ring, fetch SQEs through `io_uring_get_sqe`, fill them with `io_uring_prep_*`, submit with `io_uring_submit*`, consume CQEs with peek/wait helpers, and release CQ head with `io_uring_cqe_seen` or `io_uring_cq_advance`. Inline CQ iteration uses acquire reads of kernel tail and release stores of user head. Mixed/big SQE and CQE modes are handled by shift helpers and skip-CQE logic.

State and persistence behavior: the header defines in-memory shared-ring state only. Persistent state is file-descriptor based through `ring_fd`/`enter_ring_fd` and registered resources owned by the kernel. User data is carried in `sqe->user_data` and returned in CQEs. SQ/CQ indices, ring masks, flags, and entry counts are shared with the kernel and must be updated with the barrier helpers.

Dependencies and integration points: includes the UAPI `io_uring.h`, query and BPF filter headers, compatibility headers, socket/stat/uio/time/fcntl/signal system headers, and `barrier.h`. The declarations are implemented across `setup.c`, `queue.c`, `register.c`, `syscall.c`, `sanitize.c`, and `version.c`. C++20 module compatibility is addressed through `IOURINGINLINE` and `_LOCAL_INLINE`.

Risks: this header is ABI-sensitive. Incorrect field initialization in prep helpers can corrupt kernel requests, and wrong memory ordering around SQ/CQ head/tail can race the kernel. Direct descriptors encode indexes as `index + 1`, with special handling for `IORING_FILE_INDEX_ALLOC`; mistakes there can close or allocate the wrong fixed slot. The inline receive-message accessors guard against integer overflow, but callers must still pass matching buffers and `msghdr` sizes.

Test signals: the listed tests exercise read/write over sockets, accept variants, fixed files, multishot accept, SQ array compatibility, cross-fork mapping behavior, and syzkaller regressions. This header's prep helpers and queue helpers are directly used by almost every test file.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/include/liburing.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/include/liburing/barrier.h -->
## sources/test-tools/liburing/src/include/liburing/barrier.h

Purpose: provides the small memory-ordering layer used by liburing's shared SQ/CQ ring accesses. It abstracts C and C++ atomic operations behind `IO_URING_READ_ONCE`, `IO_URING_WRITE_ONCE`, `io_uring_smp_store_release`, `io_uring_smp_load_acquire`, and `io_uring_smp_mb`.

Important APIs/types/functions: in C++ it uses `<atomic>` templates over reinterpret-cast `std::atomic<T>` pointers. In C it uses `<stdatomic.h>` and `_Atomic __typeof__` casts. `LIBURING_NOEXCEPT` is defined for C++ use.

Control flow: the macros and inline templates are called from queue/head/tail handling. Release stores publish SQ tail, CQ head, and buffer-ring tail after SQE/CQE/buffer contents are ready; acquire loads pair with kernel publications of CQ tail and SQ head.

State and persistence behavior: no storage is owned here. It constrains ordering of existing shared memory updates between userspace and kernel.

Dependencies and integration points: included from `liburing.h` after `_LOCAL_INLINE` is defined. It is consumed by `queue.c`, public inline helpers, tests such as `accept-reuse.c`, and any caller manipulating ring head/tail directly.

Risks: using relaxed operations where release/acquire is required can expose partially initialized SQEs or stale CQEs. The atomic casts assume compatible object layout and are intentionally low-level; changes must preserve compiler and architecture semantics.

Test signals: queueing and CQ iteration tests indirectly validate that tail/head ordering works under concurrent kernel/user updates, especially SQPOLL and direct SQ array tests.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/include/liburing/barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/include/liburing/io_uring.h -->
## sources/test-tools/liburing/src/include/liburing/io_uring.h

Purpose: this is the copied/shared Linux UAPI definition for io_uring. It defines the binary contract for submission queue entries, completion queue entries, ring setup parameters, feature bits, opcodes, register opcodes, resource-registration structures, provided-buffer rings, wait arguments, zero-copy receive configuration, BPF/filter/query-facing structures, and command-specific flags.

Important APIs/types/functions: key types are `io_uring_sqe`, `io_uring_cqe`, `io_sqring_offsets`, `io_cqring_offsets`, `io_uring_params`, `io_uring_rsrc_register`, `io_uring_rsrc_update*`, `io_uring_probe*`, `io_uring_restriction`, `io_uring_buf`, `io_uring_buf_ring`, `io_uring_buf_reg`, `io_uring_reg_wait`, `io_uring_getevents_arg`, `io_uring_sync_cancel_reg`, `io_uring_zcrx_*`, and `zcrx_ctrl`. Important enums/defines include `IORING_OP_*`, `IOSQE_*`, `IORING_SETUP_*`, `IORING_FEAT_*`, `IORING_REGISTER_*`, CQE flags, enter flags, timeout/cancel/poll/send/recv/accept flags, and fixed-file allocation constants.

Control flow: there is no executable flow. The file describes how userspace populates an SQE and how the kernel returns CQEs and setup offsets. `io_uring_setup` fills `io_uring_params`; liburing maps ring regions using offset fields; `io_uring_register` consumes the register argument structs by opcode.

State and persistence behavior: the structs model shared kernel/userspace state. Ring offsets, head/tail indices, CQ flags, registered resources, provided buffer rings, and zero-copy receive objects persist for the lifetime of the ring or registered object.

Dependencies and integration points: includes Linux types, fs definitions, and optionally `linux/time_types.h`. `liburing.h`, `setup.c`, `queue.c`, and `register.c` rely on field names and flag values exactly matching the kernel. Tests use many feature flags and opcodes to gate behavior.

Risks: this file is ABI-critical. Padding, union layout, numeric opcode/register values, and bit assignments must track the kernel UAPI. Changing it without matching kernel support can cause silent request misinterpretation. Mixed 32-byte CQE and 128-byte SQE modes add index and skip-entry complexity.

Test signals: the accept, fixed-file, registered wait, buffer-ring, and syzkaller tests serve as regression signals for specific UAPI combinations. Build failures here are usually broad because the public header and C sources include this file everywhere.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/include/liburing/io_uring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/include/liburing/io_uring/bpf_filter.h -->
## sources/test-tools/liburing/src/include/liburing/io_uring/bpf_filter.h

Purpose: defines the UAPI argument shapes for registering io_uring BPF filters. Filters can inspect request context and allow or deny operations based on opcode and operation-specific packed data.

Important APIs/types/functions: `io_uring_bpf_ctx` carries `user_data`, opcode, SQE flags, auxiliary data size, and per-op unions for socket and open fields. `io_uring_bpf_filter` describes one opcode filter with flags, BPF instruction length, expected PDU size, and pointer to the filter program. `io_uring_bpf` groups filters under a ring fd and task-filter flags. Flags include `IO_URING_BPF_FILTER_DENY_REST`, `IO_URING_BPF_FILTER_SZ_STRICT`, and `IO_URING_BPF_TASK`.

Control flow: not executable by itself. `register.c` passes `io_uring_bpf` to `IORING_REGISTER_BPF_FILTER`, either against a ring or task-wide with fd `-1`.

State and persistence behavior: registered filters persist in kernel state according to the registration target. The header reserves fields for future UAPI extension.

Dependencies and integration points: included by `liburing.h` and `register.c`. Depends on Linux fixed-width types and BPF filter program memory supplied by userspace.

Risks: user and kernel must agree on `pdu_size` for strict registrations. Bad filter pointers or lengths are kernel-facing inputs; liburing only wraps the syscall and does not validate program semantics.

Test signals: not directly covered by the listed tests, but Makefile includes broader BPF-related tests in the suite. Registration failure paths would show through `io_uring_register_bpf_filter*` callers.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/include/liburing/io_uring/bpf_filter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/include/liburing/io_uring/query.h -->
## sources/test-tools/liburing/src/include/liburing/io_uring/query.h

Purpose: defines query UAPI structures used with `IORING_REGISTER_QUERY` for probing aspects of io_uring support and configuration without a specific ring fd.

Important APIs/types/functions: `io_uring_query_hdr` is the common header with query type, flags, item count, and item pointer. Query types include opcode, zero-copy receive, and send-completion-queue queries. `io_uring_query_opcode` reports opcode support and command-specific flags; `io_uring_query_zcrx` and `io_uring_query_scq` report feature masks.

Control flow: userspace fills a header with one query type and pointer to an array of items; `register.c` invokes `__sys_io_uring_register(-1, IORING_REGISTER_QUERY, query, 0)`.

State and persistence behavior: no local persistence. Results are written back into the provided query item buffers.

Dependencies and integration points: included by `liburing.h`; its public wrapper is `io_uring_register_query`. Values must align with kernel UAPI support.

Risks: query buffers and `nr` must match the requested type. As an evolving UAPI, unknown flags or item layouts need conservative handling by callers.

Test signals: no direct listed test, but query support can be validated through feature-probing tests in the wider suite.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/include/liburing/io_uring/query.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/include/liburing/sanitize.h -->
## sources/test-tools/liburing/src/include/liburing/sanitize.h

Purpose: declares sanitizer hooks used when liburing is built with address-sanitizer support. Without `CONFIG_USE_SANITIZER`, the same function names compile to no-op macros.

Important APIs/types/functions: declares `liburing_sanitize_ring`, `liburing_sanitize_address`, `liburing_sanitize_region`, and `liburing_sanitize_iovecs` when sanitizer support is enabled; otherwise each macro expands to an empty do-while block.

Control flow: `queue.c` calls `liburing_sanitize_ring` before submit, and `register.c` calls address/iovec sanitizers before kernel registrations. The implementation in `sanitize.c` checks submitted SQE addresses by opcode.

State and persistence behavior: no state is owned. Sanitizer mode may terminate the process on poisoned memory before a syscall reaches the kernel.

Dependencies and integration points: paired with `sanitize.c` and controlled by generated config defines. It keeps production builds free of ASAN runtime dependency.

Risks: the no-op path means normal builds rely on kernel/user errors rather than early ASAN diagnostics. The enabled path must stay synchronized with `IORING_OP_LAST`.

Test signals: the test Makefile adds sanitizer flags when configured; syzkaller-derived tests are compiled out or skipped under some sanitizer modes to avoid incompatibilities.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/include/liburing/sanitize.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/int_flags.h -->
## sources/test-tools/liburing/src/int_flags.h

Purpose: defines liburing-private internal flag bits stored in `struct io_uring::int_flags` and computes enter flags for registered-ring and iowait behavior.

Important APIs/types/functions: `INT_FLAGS_MASK` covers `IORING_ENTER_REGISTERED_RING` and `IORING_ENTER_NO_IOWAIT`. Internal bits are `INT_FLAG_REG_RING`, `INT_FLAG_APP_MEM`, `INT_FLAG_REG_REG_RING`, `INT_FLAG_CQ_ENTER`, and `INT_FLAG_NO_IOWAIT`. `ring_enter_flags()` masks `int_flags` down to syscall-visible enter flags.

Control flow: setup/registration code mutates `int_flags`; queue submission and wait code calls `ring_enter_flags()` before `io_uring_enter`.

State and persistence behavior: `int_flags` records runtime state such as whether the ring fd is registered, whether app memory backs a no-mmap ring, whether CQ enter is required, and whether to suppress iowait.

Dependencies and integration points: included by `queue.c`, `setup.c`, and `register.c`, and depends on public enter flag constants from `io_uring.h`.

Risks: internal bits share an 8-bit field and must not collide with syscall-visible flag bits used by `INT_FLAGS_MASK`. Incorrect flags can send io_uring_enter to the wrong fd mode or leak/unmap app memory incorrectly.

Test signals: registered ring-fd tests, no-mmap setup tests, IOPOLL/SQPOLL behavior, and iowait feature tests validate this indirectly.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/int_flags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/lib.h -->
## sources/test-tools/liburing/src/lib.h

Purpose: central internal convenience header for liburing C sources. It normalizes declarations and optionally redirects libc allocation/memory primitives to liburing's nolibc replacements.

Important APIs/types/functions: defines `offsetof`, `container_of`, `__maybe_unused`, `__hot`, and `__cold` if absent. Under `CONFIG_NOLIBC`, it declares `__uring_memset`, `__uring_malloc`, and `__uring_free`, then remaps `malloc`, `free`, and `memset`.

Control flow: no runtime flow except through remapped allocation/memory calls when nolibc is enabled.

State and persistence behavior: no owned state. It affects which allocator backs probe allocation and setup/register helper memory paths.

Dependencies and integration points: included by `queue.c`, `setup.c`, `register.c`, `nolibc.c`, `syscall.c`, and `version.c`. It includes `config-host.h` to see build options.

Risks: macro remapping is global for translation units that include it, so new code must avoid relying on libc-only semantics in nolibc builds. Attribute and `container_of` definitions are low-level and should stay compatible with compiler expectations.

Test signals: successful build under normal and nolibc configurations is the main signal; runtime probe allocation and setup tests exercise remapped allocation.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/nolibc.c -->
## sources/test-tools/liburing/src/nolibc.c

Purpose: implements minimal memory primitives for `CONFIG_NOLIBC` builds so liburing can operate without standard libc allocation helpers.

Important APIs/types/functions: `__uring_memset` fills bytes manually. `struct uring_heap` stores allocation length before the returned pointer. `__uring_malloc` uses `__sys_mmap` for anonymous private memory and returns the payload after the header. `__uring_free` derives the header and unmaps the stored length.

Control flow: allocation size is increased by the heap header, mapped with read/write permissions, checked with `IS_ERR`, and later unmapped as one region. Null free is ignored.

State and persistence behavior: allocation length is persisted in-band immediately before the returned pointer. No allocator freelist exists; every allocation is its own mmap region.

Dependencies and integration points: depends on `lib.h` declarations and syscall wrappers from `syscall.h`. Used only when `lib.h` remaps `malloc`, `free`, and `memset`.

Risks: one-mmap-per-allocation is simple but expensive. Integer overflow around `len + sizeof(*heap)` is not explicitly guarded. Callers must only pass pointers returned by this allocator to `__uring_free`.

Test signals: setup/probe paths using allocation should continue to work in nolibc builds. Memory leak or munmap errors would show under sanitizers or platform-specific nolibc tests.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/nolibc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/queue.c -->
## sources/test-tools/liburing/src/queue.c

Purpose: implements liburing's runtime queue operations: flushing SQEs, entering the kernel, waiting and peeking for CQEs, submitting with optional waits/timeouts, batch completion retrieval, and the exported `io_uring_get_sqe` symbol for ABI compatibility.

Important APIs/types/functions: core internals are `sq_ring_needs_enter`, `cq_ring_needs_flush`, `cq_ring_needs_enter`, `_io_uring_get_cqe`, `__io_uring_flush_sq`, `io_uring_wait_cqes_new`, `__io_uring_submit_timeout`, `__io_uring_submit_and_wait_timeout`, and `__io_uring_submit`. Public functions include `__io_uring_get_cqe`, `io_uring_get_events`, `io_uring_peek_batch_cqe`, `io_uring_wait_cqes`, `io_uring_wait_cqes_min_timeout`, `io_uring_submit_and_wait_reg`, `io_uring_submit_and_wait_timeout`, `io_uring_wait_cqe_timeout`, `io_uring_submit`, `io_uring_submit_and_wait`, `io_uring_submit_and_get_events`, and `__io_uring_sqring_wait`.

Control flow: submission begins by flushing local SQ state to kernel-visible tail. The code decides whether `io_uring_enter` is needed based on SQPOLL wakeup flags, CQ overflow/taskrun flags, wait requirements, and IOPOLL internal flags. Completion wait loops first peek locally, then enter the kernel if it must submit, wait, flush CQ overflow, or run task work. Timeouts use `IORING_ENTER_EXT_ARG` on newer kernels and an internal timeout SQE with `LIBURING_UDATA_TIMEOUT` on older kernels.

State and persistence behavior: mutates `sq.sqe_head`, `sq.sqe_tail`, `*sq.ktail`, `*cq.khead`, and uses `int_flags` and `features` to choose behavior. It also consumes internal timeout CQEs and skip CQEs so applications do not see them as normal completions.

Dependencies and integration points: depends on public inline helpers from `liburing.h`, memory barriers, syscall wrappers, `int_flags.h`, and sanitizer hooks. It is the central implementation behind application submit/wait calls.

Risks: subtle races exist around SQPOLL wakeup, CQ overflow, taskrun flags, registered wait offsets, mixed CQEs, and timeout CQE filtering. The code also warns that fallback timeout SQEs manipulate both SQ and CQ, making split producer/consumer threading unsafe on older kernels without synchronization.

Test signals: socket read/write tests, accept tests, timeout-link tests, registered wait tests, overflow tests, SQPOLL tests, and syzkaller reproductions stress this file. ASAN builds additionally validate SQE pointer fields before submit.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/register.c -->
## sources/test-tools/liburing/src/register.c

Purpose: implements liburing's wrappers around `io_uring_register` for buffers, files, eventfds, probes, personalities, restrictions, io-wq settings, registered ring fds, provided buffer rings, synchronous cancellation, NAPI, clock selection, buffer cloning, zero-copy receive, ring resize, memory regions, iowait control, BPF filters, and query registration.

Important APIs/types/functions: `do_register` is the common path, adding `IORING_REGISTER_USE_REGISTERED_RING` when appropriate and selecting `enter_ring_fd` versus `ring_fd`. Resource APIs include `io_uring_register_buffers*`, `io_uring_register_files*`, `io_uring_register_files_update*`, `io_uring_register_files_sparse`, and unregister variants. Ring-fd APIs include `io_uring_register_ring_fd`, `io_uring_unregister_ring_fd`, and `io_uring_close_ring_fd`. Newer UAPI wrappers include `io_uring_resize_rings`, `io_uring_register_region`, `io_uring_register_bpf_filter*`, and `io_uring_register_query`.

Control flow: most wrappers validate or sanitize pointers, populate the relevant UAPI struct, and call `do_register`. File registration retries once after increasing `RLIMIT_NOFILE` on `-EMFILE`. Ring-fd registration updates `enter_ring_fd` and internal flags on success. Resize registers new sizes, mmaps a replacement ring, preserves local SQ head/tail, unmaps the old ring, and repopulates SQ array indexes.

State and persistence behavior: kernel registration state persists until unregistered or ring exit. Local `int_flags`, `ring_fd`, `enter_ring_fd`, SQ/CQ mappings, and fixed-file/buffer registration expectations change in several APIs.

Dependencies and integration points: uses `syscall.h`, `setup.h`, `int_flags.h`, sanitizer hooks, BPF/filter headers, and UAPI structs from `io_uring.h`. Accept fixed-file tests, buffer-ring tests, and ring-fd tests depend heavily on this file.

Risks: wrong `nr_args` values or struct shapes break kernel ABI calls. Registered-ring mode changes which fd is passed, so stale flags can make registrations fail or hit the wrong target. Resize must avoid leaks and preserve queue state; no-mmap rings are rejected. `io_uring_register_wait_reg` is stubbed to `-EINVAL`, which is an intentional unsupported path in this source version.

Test signals: accept fixed/direct tests, `accept-reuse.c`, buffer-ring tests, probe tests, registered-file tests, and ring resize tests cover important branches.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/register.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/sanitize.c -->
## sources/test-tools/liburing/src/sanitize.c

Purpose: provides AddressSanitizer-aware validation for SQEs and registration inputs before liburing hands pointers to the kernel.

Important APIs/types/functions: small handlers validate `sqe->addr`, `addr2`, `addr3`, `optval` regions, combinations of those fields, or no pointer. `sanitize_handlers[IORING_OP_LAST]` maps every opcode to the relevant handler and is guarded by `_Static_assert`. Public functions are `liburing_sanitize_ring`, `liburing_sanitize_address`, `liburing_sanitize_region`, and `liburing_sanitize_iovecs`.

Control flow: `liburing_sanitize_ring` walks from kernel SQ head to local SQE tail, looks up each opcode handler, and validates relevant pointer fields. On poisoned addresses or regions, ASAN describes the address and the process exits with status 1.

State and persistence behavior: no state is changed except process termination on failure. The scan reads ring SQ state and SQE contents.

Dependencies and integration points: compiled only for sanitizer-enabled builds through `sanitize.h`; depends on `<sanitizer/asan_interface.h>` and public opcode definitions. `queue.c` and `register.c` are direct callers.

Risks: handler mappings must stay in sync with `IORING_OP_LAST` and each opcode's pointer semantics. Some opcodes use fields that can be validly null or ignored by flags; overly strict checks can produce sanitizer-only false positives, while missing handlers can let bad pointers reach the kernel in tests.

Test signals: sanitizer builds and syzkaller regression tests are the primary signal. Build failure on `_Static_assert` catches new opcodes missing sanitizer coverage.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/sanitize.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/setup.c -->
## sources/test-tools/liburing/src/setup.c

Purpose: implements ring setup, mmap/no-mmap memory layout, teardown, probe allocation, memory-size helpers, memlock-size helpers, and provided-buffer-ring allocation/free helpers.

Important APIs/types/functions: setup internals include `get_sq_cq_entries`, `io_uring_mmap`, `io_uring_alloc_huge`, `__io_uring_queue_init_params`, and `io_uring_queue_init_try_nosqarr`. Public APIs include `io_uring_queue_mmap`, `io_uring_ring_dontfork`, `io_uring_queue_init_mem`, `io_uring_queue_init_params`, `io_uring_queue_init`, `io_uring_queue_exit`, `io_uring_get_probe_ring`, `io_uring_get_probe`, `io_uring_free_probe`, `io_uring_memory_size*`, `io_uring_mlock_size*`, `io_uring_setup_buf_ring`, and `io_uring_free_buf_ring`.

Control flow: setup validates entry counts, optionally allocates user/no-mmap ring memory, calls `io_uring_setup`, maps SQ/CQ/SQE regions or uses supplied memory, initializes ring pointers and SQ array indexes, records feature/flag/fd state, and sets internal CQ-enter flags for IOPOLL. Teardown unmaps or preserves app memory, unregisters ring fd if needed, and closes the ring fd. Buffer-ring setup either maps kernel-provided rings on hppa or allocates anonymous memory and registers it on other architectures.

State and persistence behavior: initializes all `struct io_uring` fields, shared ring mappings, kernel ring fd, registered-ring internal flags, SQ/CQ masks and entries, and app-memory ownership. Probe helpers allocate temporary probe buffers and sometimes temporary rings.

Dependencies and integration points: uses syscall wrappers, `setup.h`, `int_flags.h`, `liburing.h`, `io_uring.h`, page size helpers, and register wrappers for probe and buffer rings.

Risks: ring memory calculations are ABI- and page-size-sensitive, especially with `IORING_SETUP_SQE128`, `IORING_SETUP_CQE32`, `IORING_SETUP_NO_SQARRAY`, and huge-page no-mmap mode. Error cleanup must avoid unmapping app-owned memory and must close fds after partial setup failures. Registered-fd-only requires no-mmap and updates fd ownership.

Test signals: `across-fork.c` checks fork mapping behavior; setup tests and no-mmap/init-mem tests validate memory sizing and supplied memory paths; accept SQPOLL tests exercise setup flags and feature negotiation.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/setup.h -->
## sources/test-tools/liburing/src/setup.h

Purpose: declares internal setup helpers shared between setup and registration code.

Important APIs/types/functions: declares `__io_uring_queue_init_params`, `io_uring_unmap_rings`, `io_uring_mmap`, and `io_uring_setup_ring_pointers`.

Control flow: no implementation here. `register.c` uses `io_uring_mmap` and `io_uring_unmap_rings` during resize, while `setup.c` implements all declarations.

State and persistence behavior: declarations cover functions that initialize or replace ring mappings and ring pointer fields.

Dependencies and integration points: included by `setup.c` and `register.c`; depends on `struct io_uring`, SQ/CQ structs, and `io_uring_params` being visible through included headers.

Risks: declarations must stay synchronized with `setup.c`; mismatches would break builds or resize/setup linkage.

Test signals: ring setup and resize tests indirectly verify these internal interfaces.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/syscall.c -->
## sources/test-tools/liburing/src/syscall.c

Purpose: exposes public syscall wrapper symbols for `io_uring_enter`, `io_uring_enter2`, `io_uring_setup`, and `io_uring_register`.

Important APIs/types/functions: each wrapper delegates to the corresponding internal `__sys_io_uring_*` helper declared in `syscall.h`. `io_uring_enter` takes a signal mask pointer; `io_uring_enter2` takes the extended argument pointer and size.

Control flow: one syscall wrapper call per function, returning the internal helper result, which is normalized to negative errno on failure.

State and persistence behavior: no local state. Kernel ring state is changed by the syscalls.

Dependencies and integration points: uses `liburing.h`, `syscall.h`, and `io_uring.h`. Public applications may call these lower-level wrappers directly, while higher-level setup/queue/register code uses internal wrappers.

Risks: public wrappers must preserve liburing's convention of returning negative errno rather than setting `errno` only. Signature drift would break ABI consumers.

Test signals: low-level tests and direct syscall-path tests validate these wrappers; most suite tests use higher-level APIs that transitively use the same syscall layer.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/syscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/syscall.h -->
## sources/test-tools/liburing/src/syscall.h

Purpose: centralizes low-level syscall wrapper declarations and error-pointer helpers used by liburing sources.

Important APIs/types/functions: `ERR_PTR`, `PTR_ERR`, and `IS_ERR` encode negative errno values as pointer values for mmap-like helpers. Declares `__sys_io_uring_register`, `__sys_io_uring_setup`, `__sys_io_uring_enter`, `__sys_io_uring_enter2`, `__sys_mmap`, `__sys_munmap`, `__sys_madvise`, `__sys_getrlimit`, `__sys_setrlimit`, `__sys_close`, and `get_page_size`.

Control flow: implementation lives elsewhere in platform syscall code; this header standardizes call sites.

State and persistence behavior: no state. Helpers interpret syscall results and pointer-encoded errors.

Dependencies and integration points: included by setup, queue, register, nolibc, and syscall translation units. It includes system resource/mman headers and public liburing declarations.

Risks: `ERR_PTR`/`IS_ERR` rely on negative errno range and pointer casts. Incorrect normalization would cause mmap failures to be treated as valid mappings or valid low addresses as errors.

Test signals: setup memory mapping, registered resource operations, and nolibc allocation all exercise this layer.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/version.c -->
## sources/test-tools/liburing/src/version.c

Purpose: implements runtime liburing version checks.

Important APIs/types/functions: `io_uring_major_version` returns `IO_URING_VERSION_MAJOR`; `io_uring_minor_version` returns `IO_URING_VERSION_MINOR`; `io_uring_check_version` returns true when the runtime library is at least the requested major/minor pair.

Control flow: `io_uring_check_version` first compares major, then minor when majors match.

State and persistence behavior: no mutable state. Values come from generated `io_uring_version.h`.

Dependencies and integration points: included through `liburing.h` declarations and version macros. Applications can use both runtime and compile-time version checks.

Risks: the compile-time macro `IO_URING_CHECK_VERSION` in the header appears to express "requested version is newer than current" semantics, while the runtime function expresses "current is at least requested"; callers must choose the right one.

Test signals: simple ABI/version tests would catch symbol availability. Most functional tests do not depend on this file.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/version.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/232c93d07b74.c -->
## sources/test-tools/liburing/test/232c93d07b74.c

Purpose: regression test for socket read/write via `IORING_OP_READV` and `IORING_OP_WRITEV` across TCP and Unix sockets, in blocking and nonblocking modes.

Important APIs/types/functions: `struct params` configures transport and nonblocking mode. `rcv` creates/listens/accepts a server socket and repeatedly submits readv SQEs. `snd` connects and repeatedly submits writev SQEs. `set_rcv_ready`/`wait_for_rcv_ready` coordinate threads with a mutex/condition.

Control flow: `main` runs four combinations of TCP/unix and blocking/nonblocking. Receiver binds/listens, signals readiness, accepts, initializes a ring, submits two-byte reads, and validates increasing byte values until 33 bytes are received. Sender waits for readiness, connects, initializes a ring, sends three-byte chunks until 33 bytes are written, tolerating `-EAGAIN` and stopping on `-EPIPE`.

State and persistence behavior: thread-shared readiness state and TCP bind port are transient. Rings and sockets are per-thread and cleaned up after each run.

Dependencies and integration points: uses `helpers.h` for ephemeral port and nonblock helpers, pthreads, sockets, and public liburing queue/prep APIs.

Risks: relies on local networking and timing with `usleep`. Nonblocking paths must correctly handle `-EAGAIN` without corrupting byte ordering. Abstract Unix socket name reuse can collide if cleanup is abnormal.

Test signals: pass confirms readv/writev socket SQEs, CQ iteration, and submit/advance loops behave across blocking modes.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/232c93d07b74.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/35fa71a030ca.c -->
## sources/test-tools/liburing/test/35fa71a030ca.c

Purpose: syzkaller-generated regression reproducer guarded out under sanitizer builds. It stresses fork/thread/signal/syscall interactions around io_uring setup/enter/register behavior.

Important APIs/types/functions: utility functions implement sleeps, monotonic time, thread spawning with small stacks, futex-backed events, cgroup/test setup helpers, child kill/wait, and a worker loop. `execute_call` issues the reproduced syscall sequence and stores returned descriptors in a small global result array.

Control flow: the non-sanitizer build sets up test environment, repeatedly forks children, runs `execute_one`, supervises with timeouts, and restarts on hangs or failures. Worker threads synchronize through futex events and execute individual calls. The sanitizer build path provides a skip `main`.

State and persistence behavior: global `r[]`, thread array, futex event states, child processes, and any created kernel objects are transient. Cgroup/proc/sysfs writes may affect the test environment during execution.

Dependencies and integration points: uses raw syscalls, pthreads, futex, mmap, prctl, liburing, helper exit codes, and `../src/syscall.h`.

Risks: generated tests are intentionally sharp-edged: timeouts, process cleanup, and environment setup can be flaky on restricted systems. It is skipped under sanitizer because instrumentation may perturb the reproducer or make it unsafe.

Test signals: pass means the historical syzkaller reproducer no longer triggers the kernel/liburing failure it was added for; skip under sanitizer is expected.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/35fa71a030ca.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/500f9fbadef8.c -->
## sources/test-tools/liburing/test/500f9fbadef8.c

Purpose: small regression test for fixed-buffer registration and large-ish I/O submission behavior.

Important APIs/types/functions: defines `BLOCKS` as 4096 and uses public ring setup, buffer registration, SQE prep, submit, wait, and cleanup helpers. The body allocates or maps memory, registers it as an iovec-backed fixed buffer, and submits I/O that historically reproduced a bug.

Control flow: `main` skips when invoked with arguments, initializes resources, prepares one or more SQEs against registered buffers, submits them, checks CQE results for expected success or supported failure, unregisters resources, and exits with liburing test status.

State and persistence behavior: temporary buffers and registered kernel buffer state live for the ring lifetime and are cleaned before exit.

Dependencies and integration points: depends on `liburing.h`, `helpers.h`, file/buffer syscalls, and fixed-buffer registration paths in `register.c`.

Risks: exact behavior can depend on kernel support for fixed buffers and filesystem backing. Memory alignment and iovec length errors would turn into registration or CQE failures.

Test signals: validates that registering and using a substantial fixed buffer does not regress the historical failure associated with this numbered reproducer.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/500f9fbadef8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/7ad0e4b2f83c.c -->
## sources/test-tools/liburing/test/7ad0e4b2f83c.c

Purpose: compact regression program for a specific historical io_uring issue identified by the filename hash.

Important APIs/types/functions: uses public liburing setup/submission/completion APIs and helper exit status conventions. The single `main` function contains the reproduced sequence.

Control flow: the test skips when command-line arguments are present, initializes an io_uring instance, issues the target operation sequence, checks the returned CQE or syscall result, and tears down before returning pass/fail/skip.

State and persistence behavior: state is limited to the test ring and any temporary descriptors allocated during the reproducer.

Dependencies and integration points: depends on `liburing.h`, `helpers.h`, and kernel support for the opcodes in the reproducer. It exercises the public prep/submit/wait pipeline.

Risks: because this is a minimized reproducer, failures may be kernel-version specific. The expected result may be skip on unsupported kernels rather than pass.

Test signals: pass or intentional skip confirms the historical regression is not present in the current kernel/liburing combination.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/7ad0e4b2f83c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/8a9973408177.c -->
## sources/test-tools/liburing/test/8a9973408177.c

Purpose: regression test around file registration and fsync submission.

Important APIs/types/functions: `register_file` registers a file descriptor into a ring's fixed-file table. `test_single_fsync` prepares and submits an `IORING_OP_FSYNC` operation, likely using a registered file path. `main` initializes the ring and drives the single-fsync scenario.

Control flow: the test skips on arguments, creates/open a test file, registers it, obtains an SQE, prepares fsync, submits, waits for a CQE, validates the result, unregisters/closes resources, and exits.

State and persistence behavior: temporary file contents and registered file table state persist only during the test. The ring is torn down after validation.

Dependencies and integration points: uses `io_uring_register_files`, `io_uring_prep_fsync`, submit/wait APIs, and helper file setup. It tests `register.c` file paths and queue submit/wait behavior.

Risks: filesystem semantics can affect fsync behavior; unsupported fixed files or fsync opcodes should return skip-compatible errors. Missing cleanup could leave temporary files.

Test signals: validates that fixed-file fsync works and returns a sane CQE result.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/8a9973408177.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/917257daa0fe.c -->
## sources/test-tools/liburing/test/917257daa0fe.c

Purpose: syzkaller-style minimized regression test with sanitizer skip path.

Important APIs/types/functions: the non-sanitizer `main` issues a compact raw/liburing syscall sequence and checks for crash-free completion. The sanitizer path supplies a skip-returning `main`.

Control flow: if built without sanitizer, the test sets up the required descriptors/ring state, runs the reproduced call sequence, and exits pass unless an expected unsupported condition occurs. With sanitizer, it returns `T_EXIT_SKIP`.

State and persistence behavior: transient ring, descriptors, and syscall return slots. No persistent repository state is touched.

Dependencies and integration points: uses `liburing.h`, helper exit codes, and likely `../src/syscall.h` for raw syscall wrappers.

Risks: minimized reproducers can depend on kernel configuration and may need skips for unsupported syscalls or features. Sanitizer instrumentation is explicitly not part of the intended signal.

Test signals: pass means the kernel/liburing path does not reproduce the original crash or bad return handling.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/917257daa0fe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/Makefile -->
## sources/test-tools/liburing/test/Makefile

Purpose: builds the liburing test suite and declares the sorted list of C/C++ test sources, including every test in this subset.

Important APIs/types/functions: variables define root, install prefix, clang/bpftool locations, BPF output paths, CPPFLAGS, CFLAGS/CXXFLAGS, sanitizer/TSAN additions, and LDFLAGS linking against `../src/liburing` and pthreads. `test_srcs` is the central sorted manifest of test programs.

Control flow: make includes `../config-host.mak` except for clean, appends include paths and generated config header, sets `LIBURING_BUILD_TEST`, applies warning suppressions based on config probes, and links tests with liburing. Later rules outside the shown prefix build binaries, BPF objects, install, and clean artifacts.

State and persistence behavior: build outputs are generated under the test/build output tree and BPF output directory. The makefile itself is declarative and does not persist runtime test state.

Dependencies and integration points: depends on configured liburing source tree, generated `config-host.h`, `config-host.mak`, clang/bpftool for BPF tests, pthreads, and the full test source manifest.

Risks: the sorted manifest is easy to accidentally desynchronize when adding tests. Sanitizer and TSAN flags change execution behavior; syzkaller reproducers often skip under sanitizer. Missing bpftool/clang affects BPF-specific tests but should not break unrelated builds.

Test signals: successful make confirms headers and library objects compile against all listed regression tests; individual test execution supplies behavioral coverage.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/a0908ae19763.c -->
## sources/test-tools/liburing/test/a0908ae19763.c

Purpose: syzkaller-style minimized regression test with a compact io_uring syscall sequence.

Important APIs/types/functions: global result array `r[1]` stores a descriptor/result from an early call for reuse by later calls. The non-sanitizer `main` runs the reproducer; sanitizer builds use a skip path.

Control flow: skips on extra arguments or sanitizer configuration, performs setup syscalls and io_uring operations in the exact reproduced order, checks for fatal errors only where the reproducer requires it, and exits.

State and persistence behavior: transient descriptor/ring state held in `r[0]`. No persistent files are intended.

Dependencies and integration points: uses `liburing.h`, `helpers.h`, and raw syscall wrappers. It exercises low-level setup/register/enter compatibility more than high-level helper ergonomics.

Risks: minimal generated code often lacks broad cleanup and can be sensitive to kernel feature availability. Expected unsupported returns should be treated as skip rather than hard failure when coded that way.

Test signals: crash-free pass indicates the historical issue is not reproduced.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/a0908ae19763.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/a4c0b3decb33.c -->
## sources/test-tools/liburing/test/a4c0b3decb33.c

Purpose: syzkaller-generated regression with process supervision and raw io_uring interactions.

Important APIs/types/functions: includes time helpers, environment/setup helpers, `kill_and_wait`, `setup_test`, `loop`, and `execute_one`. The sanitizer build provides an alternate skip `main`.

Control flow: non-sanitizer execution sets up the test environment, repeatedly forks/runs the reproduced sequence, kills timed-out children, and exits on interrupt or completion. `execute_one` performs the minimized syscall/liburing calls.

State and persistence behavior: temporary child processes, descriptors, and any kernel ring state are cleaned by process exit and supervisor kill paths. Environment setup may write to proc/sysfs/cgroup locations.

Dependencies and integration points: uses pthread/syscall/process APIs, `liburing.h`, `helpers.h`, and raw syscall conventions.

Risks: generated supervisor code can be timing-sensitive and platform-sensitive. The reproducer is intentionally narrow, so changes to syscall return values across kernels may require skip handling.

Test signals: pass or controlled skip means the original crash/hang reproducer is no longer active in the tested environment.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/a4c0b3decb33.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/accept-link.c -->
## sources/test-tools/liburing/test/accept-link.c

Purpose: tests linked accept and timeout behavior, including cases where a client connects before or after timeout and where linked requests should complete with expected result combinations.

Important APIs/types/functions: thread coordination helpers `signal_var` and `wait_for_var`; `struct data` records expected CQE results, timeout, endpoint address, and stop flag. `send_thread` connects to the receiver. `recv_thread` prepares accept linked with timeout and validates completions. `test_accept_timeout` drives scenarios.

Control flow: for each scenario, receiver creates a listen socket, queues an accept SQE linked to a timeout SQE, starts or suppresses a client connection, submits, and validates two CQEs against expected result classes. Threads synchronize readiness and completion with condition variables.

State and persistence behavior: only per-test socket descriptors, thread flags, ring state, and port/address values are retained. They are cleaned at test end.

Dependencies and integration points: uses pthreads, TCP sockets, poll-related timing, `io_uring_prep_accept`, `io_uring_prep_link_timeout`, linked SQE flags, submit/wait, and helper networking functions.

Risks: timeout tests are inherently timing-sensitive. A slow system can produce borderline ordering failures if timeout and connect race differently than expected. Correct handling of linked timeout cancellation is the key behavioral risk.

Test signals: validates accept/link-timeout CQE ordering and result propagation.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/accept-link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/accept-mshot-stress.c -->
## sources/test-tools/liburing/test/accept-mshot-stress.c

Purpose: stress-tests multishot accept under sustained connections, bursty connection waves, and repeated reconnects.

Important APIs/types/functions: constants set connection counts, burst rounds, reconnect loops, user data, and payload byte. Context structs track listen address, rings, counters, and client state. Helpers include `create_listen_sock`, `arm_mshot_accept`, `stress_client_fn`, `test_accept_mshot_stress`, `burst_client_fn`, `test_accept_mshot_burst`, `reconnect_client_fn`, and `test_accept_mshot_reconnect`.

Control flow: each test arms a multishot accept SQE, starts one or more client threads, then drains CQEs. The stress variant accepts many concurrent clients and verifies one-byte data exchange. The burst variant checks multiple rounds of clustered clients. The reconnect variant repeatedly connects/disconnects to ensure the multishot accept remains armed or is rearmed correctly.

State and persistence behavior: `no_mshot_accept` records unsupported-kernel skip state. Sockets, threads, counters, and the ring are per scenario.

Dependencies and integration points: uses pthreads, TCP sockets, `io_uring_prep_multishot_accept`, CQE `IORING_CQE_F_MORE`, send/recv helpers, and liburing queue APIs.

Risks: high connection counts can hit local resource limits or timing issues. The test must distinguish unsupported multishot accept from real failures. CQE `MORE` handling and rearming behavior are central risk points.

Test signals: strong coverage for multishot accept reliability under load and repeated connection churn.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/accept-mshot-stress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/accept-non-empty.c -->
## sources/test-tools/liburing/test/accept-non-empty.c

Purpose: verifies `IORING_CQE_F_SOCK_NONEMPTY` on accept completions when more pending connections remain.

Important APIs/types/functions: `struct data` holds connector thread/barriers and connection count. `start_accept_listen` creates the listener. `connect_fn` opens a chosen number of client sockets. `setup_thread` initializes barriers and starts the client. `test_maccept` performs accepts in normal or fixed-file mode. `test` runs single-connection and multi-connection cases for a flag/fixed combination.

Control flow: the test initializes a ring, checks for `IORING_FEAT_RECVSEND_BUNDLE` as a feature gate, optionally registers fixed files, starts clients, waits until connections are queued, then issues one accept at a time. It asserts the nonempty flag is clear for single/last accept and set for earlier accepts in a multi-connection backlog.

State and persistence behavior: `no_more_accept` records global skip state when the feature is unavailable. Fixed file slots and accepted sockets live only for one scenario.

Dependencies and integration points: uses TCP sockets, pthread barriers, `io_uring_prep_accept`, `io_uring_prep_accept_direct`, ring-fd/file registration, and CQE flag inspection.

Risks: uses a fixed localhost port (`0x1235 + port_off`), so collisions are possible. Backlog timing matters: connections must be queued before accept checks. Fixed mode requires kernel fixed-file support.

Test signals: validates socket-nonempty CQE flag behavior for normal, defer-taskrun/single-issuer, and fixed-file modes.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/accept-non-empty.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/accept-reuse.c -->
## sources/test-tools/liburing/test/accept-reuse.c

Purpose: regression test for manually reusing an SQE/SQ array slot for accept submission while relying on `IORING_FEAT_SUBMIT_STABLE`.

Important APIs/types/functions: global `struct io_uring io_uring`; `sys_io_uring_enter` wraps the internal syscall helper; `submit_sqe` writes `sq->array[tail & mask] = 0`, release-stores `ktail`, and enters the ring directly.

Control flow: `main` initializes a ring with an SQ array, checks `IORING_FEAT_SUBMIT_STABLE`, creates a listening socket using `getaddrinfo`, prepares an accept SQE in slot 0, submits it through the manual SQ array path, connects a client, waits for and validates the accepted socket address, then repeats as needed.

State and persistence behavior: manually mutated SQ tail/array state is the core state under test. Sockets and ring state are cleaned at exit.

Dependencies and integration points: uses `t_io_uring_init_sqarray`, raw `__sys_io_uring_enter`, memory barriers, networking helpers, and public SQE prep.

Risks: direct SQ manipulation bypasses some high-level helper protections. The test is skipped without `IORING_FEAT_SUBMIT_STABLE` because kernel stability guarantees are required for slot reuse.

Test signals: validates that SQE contents remain stable after submission and direct SQ array reuse does not corrupt accept handling.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/accept-reuse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/accept-test.c -->
## sources/test-tools/liburing/test/accept-test.c

Purpose: small focused accept smoke test.

Important APIs/types/functions: single `main` creates a listening socket, initializes an io_uring, prepares `IORING_OP_ACCEPT`, connects a client, waits for completion, and validates the accepted descriptor.

Control flow: skip on arguments, set up local TCP listener, queue accept SQE, submit, initiate client connection, wait for CQE, check nonnegative result or supported skip error, close descriptors, and tear down the ring.

State and persistence behavior: transient listener, client, accepted socket, and ring. No persistent state.

Dependencies and integration points: depends on socket helpers, `io_uring_prep_accept`, submit/wait APIs, and CQE result semantics.

Risks: local port allocation and connection timing are the main external risks. Unsupported accept opcode should be represented as skip rather than failure.

Test signals: basic confidence that accept SQEs complete and return usable fds.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/accept-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/accept.c -->
## sources/test-tools/liburing/test/accept.c

Purpose: comprehensive accept regression suite covering normal accept, queued-before-connect accept, nonblocking listeners, fixed direct descriptors, multishot accept, overflow interactions, SQPOLL restrictions, cancellation, and pending accepts during ring exit.

Important APIs/types/functions: helper structs `data`, `accept_test_args`, and `test_accept_many_args`; helpers `queue_send`, `queue_recv`, `queue_accept_multishot`, `queue_accept_conn`, `accept_conn`, `start_accept_listen`, `set_client_fd`, `cause_overflow`, `clear_overflow`, `test_loop`, `test`, `test_accept_many`, `test_accept_cancel`, and scenario wrappers for normal/multishot/fixed/SQPOLL cases.

Control flow: main runs a sequence of scenarios, stopping on hard failure and skipping when feature detection shows accept or multishot accept unsupported. Each loop creates listen/client sockets, queues accepts before or after client connection, accepts CQEs while ignoring synthetic NOP overflow CQEs, optionally validates data transfer through accepted sockets, and checks direct/fixed file indexes. Cancellation tests queue accepts, then async cancels by user data and verify `-ECANCELED`, `-EINTR`, `-EALREADY`, or zero as appropriate.

State and persistence behavior: `no_accept` and `no_accept_multi` globally record unsupported features. Fixed file tables, overflow CQEs, socket arrays, and rings are per scenario and cleaned. `test_accept_many` temporarily lowers/restores `RLIMIT_NPROC`.

Dependencies and integration points: exercises `liburing.h` accept prep variants, fixed-file registration, multishot `IORING_CQE_F_MORE`, cancellation, SQPOLL setup, queue overflow handling, and read/write verification.

Risks: broad coverage means multiple kernel features influence outcomes. Overflow handling, multishot rearming, fixed-slot allocation, and cancellation timing are the most fragile behaviors. Resource-limit manipulation must restore state even on failures.

Test signals: this is the strongest signal for accept correctness across liburing's high-level helper surface and kernel feature matrix.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/accept.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/across-fork.c -->
## sources/test-tools/liburing/test/across-fork.c

Purpose: tests ring behavior across fork boundaries, including whether `io_uring_ring_dontfork` prevents unsafe inherited mappings and whether parent/child can perform expected writes.

Important APIs/types/functions: `struct forktestmem` stores shared test state. `open_tempfile`, `submit_write`, `wait_cqe`, `verify_file`, and `cleanup` manage file I/O and validation. `main` coordinates parent/child execution.

Control flow: creates a temporary directory/file, initializes a ring, optionally marks ring mappings `MADV_DONTFORK`, forks, submits writes from parent and/or child depending on the scenario, waits for CQEs, verifies file content, and cleans up.

State and persistence behavior: temporary files persist only for test duration. Ring mappings may or may not be inherited across fork depending on the tested call. Shared memory or process-local state coordinates expected content.

Dependencies and integration points: uses `io_uring_queue_init`, `io_uring_ring_dontfork`, write prep, submit/wait, fork/wait, file helpers, and cleanup syscalls.

Risks: forked processes using inherited shared mappings can fail in subtle ways if kernel/liburing expectations change. Cleanup must handle child failure paths and temporary directory removal.

Test signals: validates setup.c's `io_uring_ring_dontfork` and safe behavior around forked processes.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/across-fork.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/b19062a56726.c -->
## sources/test-tools/liburing/test/b19062a56726.c

Purpose: minimized regression test for a historical issue identified by the filename hash, with sanitizer skip handling.

Important APIs/types/functions: non-sanitizer `main` performs the reproduced io_uring sequence. Sanitizer-enabled builds provide an alternate skip `main`.

Control flow: skip on arguments or sanitizer, initialize any required descriptors/ring state, execute the compact syscall/liburing calls, and return pass if the process survives and expected return handling is observed.

State and persistence behavior: transient descriptors and ring/kernel objects only.

Dependencies and integration points: uses `liburing.h`, helper status values, and raw syscall helpers where needed.

Risks: generated/minimized reproducer behavior may vary by kernel version and configuration. It is not a broad correctness test; its value is guarding one known crash/regression.

Test signals: pass confirms the historical reproducer no longer fails in the tested environment.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/b19062a56726.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/b5837bd5311d.c -->
## sources/test-tools/liburing/test/b5837bd5311d.c

Purpose: compact regression test for a specific historical io_uring issue.

Important APIs/types/functions: single `main` function uses liburing/helper APIs to reproduce the issue and validate return behavior.

Control flow: skips when command-line arguments are present, performs the setup and request sequence, waits for completion or syscall result, checks expected outcome, cleans up, and returns the liburing test status.

State and persistence behavior: only temporary ring/descriptors/resources are used. No durable state is intended.

Dependencies and integration points: depends on public liburing headers and helper routines, and may touch low-level syscall wrappers depending on the reproduced sequence.

Risks: as with other hash-named tests, the code is intentionally narrow and kernel-feature-sensitive. Unsupported environments should skip rather than fail when the source encodes that expectation.

Test signals: pass indicates the regression associated with this reproducer remains fixed.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/b5837bd5311d.c -->
