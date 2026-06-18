# Group Research: group_1217_netbsd_src_sources_os_bsd_netbsd_src_lib_libisns_isns_pdu_c_sources_ac7bf2c2bcaa

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/netbsd-src`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libisns/isns_pdu.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libisns/isns_pdu.c

Implements libisns buffer pooling, transaction lifecycle, PDU construction/destruction, TLV append/read helpers, and PDU send task creation. It owns the global `G_buffer_pool`, sorted buffer-size lists, pooled versus malloc/static buffer typing, and deferred transaction freeing via `ISNS_TRANSF_FREE_WHEN_COMPLETE`.

Key behavior:
- `isns_new_trans()` allocates a transaction from an ISNS buffer, assigns a monotonically increasing transaction id, filters PDU flags, creates the first request PDU, and links it into the request list.
- `isns_send_trans()` marks first/last PDU flags, assigns sequence ids, queues a send task through `isns_send_pdu()`, and optionally reads the response status.
- `isns_add_tlv()` writes a network-order TLV header and padded payload into one or more PDU payload buffers, splitting into chained PDUs at `ISNS_MAX_PDU_PAYLOAD`; readers see the padded TLV length.
- `isns_get_tlv()` walks completed response PDUs and buffers, materializing spanning TLV values into extra transaction-owned buffers.
- `isns_abort_trans()` completes a matching current or queued send task.

Important dependencies:
- `isns_config_s` for mutexes, server/client mode, task queue, socket state.
- `isns_task.c` for queued send task creation/wait/abort.
- `isns_util.h` byte-order and allocation macros.

Notable risks:
- `isns_get_next_trans_id()` uses a static unsynchronized `int`, so concurrent callers can race.
- Several reads cast raw buffer data to `uint32_t *`, relying on alignment that the buffer allocator mostly preserves.
- `isns_get_pdu_response_status()` uses `htonl()` when reading a network-ordered status; semantically this should be host conversion, though it is equivalent on common byte-swap implementations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libisns/isns_pdu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libisns/isns_pdu.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libisns/isns_pdu.h

Declares libisns PDU, transaction, TLV, and buffer-pool data structures. It defines the iSNS protocol version, max PDU payload size, default pool sizes, buffer ownership types, and transaction completion flags.

Key contents:
- `struct isns_buffer_s`: length/type/next metadata preceding buffer data.
- `ISNS_INIT_BUFFER()` and `isns_buffer_data()` macros for embedded buffer layout.
- TLV helpers using `memcpy()` plus `isns_htonl/isns_ntohl`, avoiding unaligned access for TLV headers.
- `struct isns_trans_s`: transaction id/function/flags, config pointer, TLV iterator state, request/response PDU lists, disconnect count.
- `struct isns_pdu_s`: config pointer, wire header, host-byteorder marker, payload buffer list, next PDU link.
- Macros for accessing request/response heads and transaction flags.

This header is the central private contract between the iSNS PDU, task, thread, and utility modules.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libisns/isns_pdu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libisns/isns_socketio.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libisns/isns_socketio.c

Provides a thin socket abstraction for libisns. `isns_socket_create/connect/close` either call WEPE wrapper functions when `HAVE_WEPE` is set or normal `socket(2)`, `connect(2)`, and `close(2)` otherwise.

Read/write vector operations delegate to `isns_file_writev()` and `isns_file_readv()`, making socket I/O share file-vector retry behavior from the broader library.

This module intentionally contains no protocol logic; it exists as a portability boundary for socket descriptors.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libisns/isns_socketio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libisns/isns_socketio.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libisns/isns_socketio.h

Declares the socket abstraction used by libisns. It defines `isns_socket_t` as `int`, an IPv4 server address wrapper `struct isns_srv_addr_s`, and prototypes for create/connect/close/readv/writev helpers.

The header pulls in `<sys/socket.h>` and `<netinet/in.h>`, so consumers get socket address and `iovec`-related declarations through the platform headers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libisns/isns_socketio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libisns/isns_task.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libisns/isns_task.c

Implements the libisns task dispatcher and queue operations. Task types include server discovery, reconnect, PDU send, socket I/O initialization, and refresh timer initialization.

Key behavior:
- `isns_run_task()` dispatches by task type through a static handler table.
- `isns_task_send_pdu()` converts PDU headers to network byte order, builds an iovec chain for header plus payload buffers, handles partial `writev()` progress, and processes connection loss on write failure.
- Waitable tasks use a condition variable and `wait_ref_count` so both the waiting caller and task completion path can release safely.
- Reconnect/init handlers manipulate sockets and kqueue events; failed reconnect attempts may leave the current reconnect task active until the reconnect timer succeeds.
- Task queue helpers use `SIMPLEQ` protected by `cfg_p->taskq_mutex`.

Notable risks:
- `write_buf` is a static global buffer, so concurrent send handlers would conflict; current design appears to serialize through one control thread/current task.
- `isns_new_task()` callers assume allocation succeeds; some paths assign task fields without a NULL check.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libisns/isns_task.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libisns/isns_task.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libisns/isns_task.h

Defines libisns task ids, task payload union, and `struct isns_task_s`. The task structure stores task type, owning config, type-specific data, optional wait synchronization fields, wait reference count, and a `SIMPLEQ_ENTRY`.

It declares the dispatcher, end/wait routines, allocation/free helpers, queue insert/remove functions, and transaction-specific queue removal used by abort handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libisns/isns_task.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libisns/isns_thread.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libisns/isns_thread.c

Implements the libisns control thread and kqueue event handlers. The control loop drains queued tasks when no current task is active, then waits for pipe/socket/timer events via `kevent()`.

Key behavior:
- `isns_get_next_task()` requeues non-init tasks and creates a reconnect task when the socket is disconnected.
- `isns_kevent_pipe()` consumes command bytes for processing the task queue, aborting a transaction, or stopping the thread.
- `isns_kevent_socket()` incrementally reads PDU headers and payloads into buffer chains, validates protocol version, converts header fields to host order, and completes matching transactions once all response PDUs arrive.
- Reconnect and refresh timer handlers recreate sockets or send periodic `DevAttrQry` refresh transactions.

Notable risks:
- Header reads have an explicit TODO for short header reads; current code subtracts a full header size after one `readv()`.
- Static `read_buf` assumes serialized access.
- Some response validation is narrow: unsolicited or duplicate PDUs are freed rather than surfaced.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libisns/isns_thread.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libisns/isns_thread.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libisns/isns_thread.h

Declares control-thread command ids, timer event ids, reconnect period, thread-name length, and the `isns_kevent_handler` function type. It exports the control thread entry point and handlers for pipe, socket, reconnect timer, and refresh timer events.

This header binds task/util code to the kqueue-based control loop.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libisns/isns_thread.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libisns/isns_util.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libisns/isns_util.c

Provides libisns command signaling, kqueue event update helpers, config allocation/destruction, control-thread creation/join, and connection-loss retry handling.

Key behavior:
- Commands are written to the control pipe, optionally with payload data via `writev()`.
- `isns_new_config()` initializes file descriptors, socket/PDU/refresh state, task and transaction mutexes, the task queue, and allocates a pthread handle.
- `isns_destroy_config()` closes descriptors, frees refresh transactions, completes pending send tasks, drains the task queue, destroys mutexes, frees copied addrinfo pieces, and frees config storage.
- `isns_process_connection_loss()` retries a send transaction up to three disconnects by freeing partial responses and requeueing the current task.

The thread creation path uses NetBSD `pthread_attr_setname_np()` to name the control thread `isns_control`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libisns/isns_util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libisns/isns_util.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libisns/isns_util.h

Defines basic libisns utility macros and prototypes. Byte-order macros map directly to `<arpa/inet.h>` functions, allocation maps to `malloc/free`, and `ARRAY_ELEMS()` computes static array size.

It declares pipe command helpers, kqueue update helper, config lifecycle, control-thread lifecycle, and connection-loss processing. The header is intentionally small but widely included by the iSNS implementation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libisns/isns_util.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkern/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libkern/Makefile

Builds the private userland `libkern` library from the kernel `sys/lib/libkern` sources. It includes NetBSD make infrastructure, marks the library private, compiles freestanding with `_STANDALONE` and `_KERNTYPES`, disables stack protector/unwind tables, and treats warnings as errors.

The selected libkern source list comes from `${S}/lib/libkern/Makefile.libkern`; the build fails early if no architecture subdirectory is available for the current machine.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkern/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libkvm/Makefile

Builds `libkvm`, the kernel virtual memory access library. Common sources are `kvm.c`, `kvm_file.c`, `kvm_getloadavg.c`, and `kvm_proc.c`; one machine-dependent `kvm_${arch}.c` source is selected by `KVM_MACHINE_ARCH`, `KVM_MACHINE_CPU`, `MACHINE_ARCH`, or `MACHINE_CPU`.

Special cases:
- i386 also builds `kvm_i386pae.c`.
- m68k also builds common/generic and sun-specific support files.
- sparc creates local `machine`/`sparc` symlinks for sparc64-with-sparc-arch header compatibility.
- The library uses shared-library directory support and `USE_FORT`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm.c

Implements core `libkvm` descriptor management, open/close, namelist lookup, crash dump header parsing/writing, and `kvm_read`/`kvm_write`.

Key behavior:
- `_kvm_open()` initializes `kvm_t`, selects kernel namelist (`/dev/ksyms` or kernel file), opens physical memory/dump, optionally opens `/dev/kmem` and swap, and initializes machine-dependent translation for crash dumps.
- `_kvm_get_header()` parses savecore-style `kcore` headers with CPU and memory segments.
- `kvm_dump_mkheader()` handles raw dump-device format and constructs an in-memory `kcore_hdr`.
- `kvm_dump_header()` writes generic, CPU, and data segment headers through a callback.
- `_kvm_pread()` supports mmap-backed dumps and aligned-buffer reads for devices requiring block alignment.
- `kvm_read()` routes live-kernel reads through `/dev/kmem`, rejects reads for `KVM_NO_FILES`, and walks dead-kernel virtual addresses via `_kvm_kvatop()`/`_kvm_pa2off()`.
- `kvm_write()` writes live kernels through `/dev/kmem`; for dead kernels it only works against the mmap-backed dump image.

This is the central architecture-neutral layer that all machine-dependent translation modules serve.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_aarch64.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_aarch64.c

Provides AArch64 machine-dependent crash dump address translation. It supports only dead-kernel translation and rejects live `vatop`.

Key behavior:
- Uses the AArch64 direct-map address range check before walking translation tables.
- Reads TCR/TTBR values from `cpu_kcore_hdr_t`.
- Derives page size from `TCR_TG1`, computes page-table levels from `TCR_T1SZ`, and walks TTBR1 tables until a block or page entry is found.
- `_kvm_pa2off()` maps physical addresses to packed dump offsets by walking `kh_ramsegs`.

`_kvm_mdopen()` sets user VA bounds from `VM_MIN_ADDRESS` and `VM_MAXUSER_ADDRESS`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_aarch64.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_alpha.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_alpha.c

Implements Alpha dead-kernel KVA translation. It handles direct-mapped `K0SEG` addresses and page-table translated `K1SEG` addresses.

Key behavior:
- Reads L1, L2, and L3 Alpha PTEs using the level indexes and `lev1map_pa` from the kcore CPU header.
- Validates `ALPHA_PTE_VALID` at each level.
- Computes physical address from PFN and page offset.
- `_kvm_pa2off()` walks physical RAM segments stored after the CPU kcore header.

User VA bounds are set from Alpha VM constants in `_kvm_mdopen()`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_alpha.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_arm.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_arm.c

Implements ARM32 machine-dependent KVA translation for crash dumps. It validates CPU kcore version/flags, selects kernel or user L1 table based on virtual address, reads L1 descriptors, and handles section, coarse, and fine page-table paths.

Supported mappings:
- L1 section mappings.
- L2 large, small, and tiny page mappings.

`_kvm_pa2off()` maps physical addresses through ARM kcore RAM segments. `_kvm_mdopen()` derives user-space maximum from `__ps_strings + 1` because ARM VM limits vary across machines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_arm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_file.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_file.c

Implements `kvm_getfiles()`, used by tools such as `pstat`, `fstat`, and `netstat` to inspect open kernel file structures.

Key behavior:
- For live/sysctl-capable descriptors, uses `CTL_KERN/KERN_FILE` to retrieve a packed file list into `kd->argspc`.
- For crash dumps, resolves `_nfiles` and `_filehead`, reads the file list head, then copies each `struct file` from kernel memory into the output buffer.
- Validates the copied count against the expected file count for dead kernels.

This module uses `kd->argspc` as reusable scratch/output storage.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_getloadavg.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_getloadavg.c

Implements `kvm_getloadavg()`. For live kernels, it delegates directly to `getloadavg()`. For dead kernels, it resolves `_averunnable` and optional `_fscale`, reads `struct loadavg` from the dump, and converts fixed-point load averages to doubles.

It preserves compatibility with old kernels where `fscale` was a separate symbol.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_getloadavg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_hppa.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_hppa.c

Stub/partial HPPA machine-dependent `libkvm` implementation. The intended page-directory/page-table walk is present under `#if 0`, but active code reports failure for `_kvm_kvatop()` and returns zero for `_kvm_pa2off()`.

`_kvm_mdopen()` still sets normal user VA bounds from HPPA VM constants. Crash dump virtual address translation is effectively unimplemented.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_hppa.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_i386.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_i386.c

Implements i386 machine-dependent crash dump KVA translation and dispatches between non-PAE and PAE walkers.

Key behavior:
- `_kvm_initvtop()` checks `cpu_kcore_hdr_t.pdppaddr` for `I386_KCORE_PAE`.
- `_kvm_kvatop()` delegates to `_kvm_kvatop_i386()` or `_kvm_kvatop_i386pae()`.
- Non-PAE walker reads PDE and PTE entries, supports 4MB large pages, validates `PTE_P`, and computes physical address plus contiguous byte count.
- `_kvm_pa2off()` maps physical addresses through packed RAM segments.

User VA bounds use i386 VM constants.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_i386.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_i386pae.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_i386pae.c

Provides the PAE-specific i386 KVA translator used by `kvm_i386.c`. It compiles with `#define PAE`, reads PAE-format PDE/PTE entries, ignores the per-CPU L3 page for kernel VA translation, supports 2MB large pages, and validates present bits before returning a physical address.

It depends on `_kvm_pa2off()` from the main i386 module for reading page-table entries from dumps.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_i386pae.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_ia64.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_ia64.c

Empty IA64 machine-dependent implementation. `_kvm_initvtop()`, `_kvm_kvatop()`, `_kvm_pa2off()`, and `_kvm_mdopen()` all report not implemented, with `_kvm_mdopen()` returning failure.

This file exists to satisfy build structure for the architecture but does not provide usable `libkvm` translation support.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_ia64.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_m68k.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_m68k.c

Runtime dispatcher for m68k `libkvm` machine-dependent operations. Because one library build must support several m68k machines, it selects a `struct kvm_ops` table based on the machine name embedded in the kcore CPU header.

Key behavior:
- Matches `sun2`, `sun3`, `sun3x`, `gen68k`, or falls back to common m68k ops.
- Allocates `struct vmstate`, stores selected ops, computes page shift and page offset mask from kcore page size, then calls the selected init hook.
- Public MD hooks delegate `kvatop`, `pa2off`, and free operations to the selected ops.
- `_kvm_mdopen()` derives max user VA from `__ps_strings + 1`.

This file is the architecture-family multiplexer; actual translation lives in common/generic/sun modules.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_m68k.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_m68k.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_m68k.h

Defines the m68k operation-vector interface used by `kvm_m68k.c`. `struct kvm_ops` contains init/free/KVA-to-PA/PA-to-offset hooks. `struct vmstate` stores the selected ops, page-shift/mask fields, and a private pointer for lower layers.

Exports ops tables for common, generic 68k, sun2, sun3, and sun3x implementations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_m68k.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_m68k_cmn.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_m68k_cmn.c

Common m68k translation implementation. It chooses 68030-style or 68040/68060-style MMU walkers from kcore MMU type and exports `_kvm_ops_cmn`.

Key behavior:
- `_kvm_cmn_kvatop()` rejects live kernels, selects `vatop_030` or `vatop_040`, and starts from `sysseg_pa`.
- Both walkers special-case early relocation ranges before full translation is available.
- `vatop_030()` reads segment table and page table entries using m68k kcore masks.
- `vatop_040()` walks three descriptor levels before reading a PTE.
- `_kvm_cmn_pa2off()` maps physical addresses through fixed m68k RAM segment arrays.

The implementation avoids machine-specific headers beyond m68k common headers so it can build across all m68k machines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_m68k_cmn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_m68k_gen.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_m68k_gen.c

Generic m68k translation implementation for newer generic kcore data. It exports `_kvm_ops_gen68k` and reconstructs MMU table indexing from the 68851-style TCR fields in the kcore header.

Key behavior:
- Allocates a private `kvm_gen68k_context` with page frame mask, significant VA mask, and up to four table-index descriptors.
- Validates page-shift, initial-shift, and table-index sizes from TCR.
- `mmu_tree_walk()` follows short descriptors from SRP through table levels, rejecting invalid/long descriptors.
- `_kvm_gen68k_kvatop()` handles relocation ranges, otherwise walks the MMU tree and adds page offset.
- `_kvm_gen68k_pa2off()` maps physical addresses through generic m68k RAM segment arrays.

This is the most data-driven m68k translator in the group.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_m68k_gen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_mips.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_mips.c

Implements MIPS machine-dependent crash dump KVA translation.

Key behavior:
- Rejects user-space virtual addresses.
- Handles direct-mapped cached/uncached segments (`KSEG0`, `KSEG1`, and 64-bit `XKPHYS` where applicable).
- For mapped kernel space, validates the address against `sysmapsize`, reads a PTE from `sysmappa`, validates `pg_v`, and computes the physical address using kcore frame/shift fields.
- `_kvm_pa2off()` maps physical addresses through RAM segments after the CPU kcore header.

User VA bounds use MIPS VM constants.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_mips.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_or1k.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_or1k.c

OR1K machine-dependent `libkvm` module. KVA-to-PA translation is not implemented; `_kvm_kvatop()` returns no translation for dead kernels. `_kvm_pa2off()` does work: it scans physical RAM segments in the CPU kcore data and returns the packed dump offset for a matching physical address.

`_kvm_mdopen()` sets user VA bounds from OR1K VM constants.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_or1k.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_powerpc.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_powerpc.c

Implements 32-bit PowerPC machine-dependent crash dump translation.

Key behavior:
- Checks CPU PVR and supports several OEA-era PowerPC CPUs.
- Attempts BAT/direct block translations first, with separate 601 BAT handling.
- Falls back to segment register/hash page table translation via primary and secondary PTEG scans.
- `_kvm_pa2off()` maps physical addresses through kcore RAM segments.
- `_kvm_mdopen()` derives user VA range from `__ps_strings + 1` because limits vary across PowerPC machines.

Notable detail: secondary hash lookup calls `_kvm_scan_pteg()` with secondary flag `0`, matching the source as read; this is worth reviewing if investigating PowerPC translation misses.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_powerpc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_powerpc64.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_powerpc64.c

PowerPC64 machine-dependent module with incomplete KVA translation. `_kvm_kvatop()` rejects live kernels and otherwise returns no translation. `_kvm_pa2off()` scans RAM segments in kcore CPU data and maps physical addresses to packed dump offsets.

`_kvm_mdopen()` uses the same `__ps_strings + 1` max-user-VA heuristic as 32-bit PowerPC.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_powerpc64.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_private.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_private.h

Private `libkvm` header defining the internal `struct __kvm` descriptor and cross-module helper prototypes.

Key fields:
- Open file descriptors for physical memory/dump, virtual memory, swap, and namelist.
- Aliveness mode: dead dump, live files, or sysctl-only.
- Cached process/LWP/file/argv buffers and lengths.
- Crash dump headers, CPU data, dump offset, mmap pointer/size.
- Machine-dependent virtual translation state and cached VM page lookup state.
- Device-aligned I/O scratch buffer and kernel name.

It also defines `ISALIVE`, `ISKMEM`, `ISSYSCTL`, `KREAD`, and `KVM_ALLOC`, which are used throughout `libkvm`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_private.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_proc.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_proc.c

Implements process, LWP, argv, and environment retrieval for `libkvm`. It serves both live/sysctl kernels and dead crash dumps.

Key behavior:
- Dead-kernel process listing resolves `_nprocs`, `_allproc`, and `_zombproc`, walks kernel process lists, reads credentials, process groups, sessions, ttys, VM space, and representative LWP wait messages.
- Live process/LWP listing uses `KERN_PROC`, `KERN_PROC2`, and `KERN_LWP` sysctls.
- `kvm_getproc2()` can synthesize `kinfo_proc2` from old `kinfo_proc` plus representative LWP data for dead kernels.
- `kvm_getlwps()` reads LWP sysctl data live or walks a process LWP list in a dump.
- Argument/environment retrieval for old `kinfo_proc` reads `ps_strings` and user pages from the target process VM map or swap; `kvm_getargv2/getenvv2()` use `KERN_PROC_ARGS` sysctl.
- `_kvm_ureadm()` traverses VM map entries, amaps, anon slots, resident pages, or swap slots to read user-space pages from a dump.

Notable risks:
- The file embeds a private copy of kernel credential layout; kernel credential structure drift can break dump interpretation.
- Dead-kernel argv/env extraction depends on VM internals and swap availability.
- Some synthesized `kinfo_proc2` fields are explicitly zeroed or marked `XXX`, so dead-kernel output is best-effort.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_riscv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_riscv.c

RISC-V machine-dependent `libkvm` module. KVA-to-PA translation is not implemented; `_kvm_kvatop()` returns no translation for dead kernels. `_kvm_pa2off()` scans physical RAM segments in the CPU kcore data and returns packed dump offsets.

`_kvm_mdopen()` sets user VA bounds from RISC-V VM constants. The file header comment still says OR1K, indicating likely copy-forward scaffolding.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_riscv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_sh3.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_sh3.c

SH3 machine-dependent `libkvm` stub. `_kvm_kvatop()` and `_kvm_pa2off()` both report not implemented. Initialization succeeds and `_kvm_mdopen()` sets user VA bounds from SH3 VM constants.

Crash dump address translation is not usable in this module as written.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_sh3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_sparc.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_sparc.c

Implements SPARC/SPARC64-compatible machine-dependent crash dump translation. It uses MMU metadata written into the CPU segment by `pmap_dumpmmu()`.

Key behavior:
- `_kvm_initvtop()` reads CPU type, sets page size/shift for sun4/sun4c/sun4m/sun4u, and computes PTEs per segment group.
- `_kvm_kvatop()` dispatches to sun4/sun4c, sun4m, or sun4u translation.
- sun4/sun4c uses segment maps and PMEG PTE arrays.
- sun4m uses segment maps and reads SRMMU PTEs from the dump.
- sun4u handles a 4MB locked TLB region and then consults sparc64-style segment/page table data.
- `_kvm_pa2off()` maps sparse physical addresses into packed dump offsets using CPU segment memory ranges.
- `_kvm_mdopen()` uses `__ps_strings + 1` for max user VA.

Notable concern: some pointer arithmetic casts `kd->cpu_data` through `int`, reflecting older 32-bit assumptions in code that also handles sparc64-flavored data.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_sparc.c -->