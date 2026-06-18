# subset-b-001250 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/sw_sync.c -->
## sources/distributed-fs/ceph-client/drivers/dma-buf/sw_sync.c

### Purpose
`sw_sync.c` implements the debugfs software sync timeline used to validate and exercise `sync_file`/`dma_fence` behavior without hardware. Opening `debugfs/sync/sw_sync` creates a private timeline, ioctls create sync_file file descriptors backed by timeline fences, increment the timeline counter, and query deadline hints.

### Important APIs, Types, And Functions
The user ABI structures are local `sw_sync_create_fence_data` and `sw_sync_get_deadline`, with ioctls `SW_SYNC_IOC_CREATE_FENCE`, `SW_SYNC_IOC_INC`, and `SW_SYNC_GET_DEADLINE`. Core helpers are `sync_timeline_create()`, `sync_timeline_signal()`, `sync_pt_create()`, `sw_sync_ioctl_create_fence()`, `sw_sync_ioctl_inc()`, and `sw_sync_ioctl_get_deadline()`. `timeline_fence_ops` implements `dma_fence_ops` for driver name, timeline name, signaled predicate, release, and deadline storage.

### Control Flow, State, And Persistence
Open allocates a `sync_timeline` named after the current task and registers it with sync debugfs tracking. `sync_pt_create()` initializes a `dma_fence` under the timeline lock and inserts unsignaled points into both an rbtree and ordered list by sequence number; duplicate sequence numbers can reuse an existing fence if it can be referenced. Incrementing the timeline updates `obj->value`, moves newly signaled fences to a temporary list, signals them while locked, then drops temporary references after unlocking. Closing the timeline marks all remaining fences `-ENOENT`, signals them, and releases the timeline reference.

### Dependencies, Integration Points, Risks, And Test Signals
This file depends on `dma_fence`, `sync_file_create()`, debugfs file operations from `sync_debug.c`, `sync_debug.h` timeline types, and `sync_trace.h` tracepoints. It taints the kernel on fence creation because user-controlled software fences can deadlock kernel drivers. Risks include lock ordering around `obj->lock`, duplicate-fence reuse under RCU, counter wrap/large increments, user ABI copy failures, deadline flag lifetime, and debug-only interfaces being misused by production userspace. Test signals include opening multiple timelines, creating fences at lower/equal/higher seqnos, incrementing across many fences including values over `INT_MAX`, poll/readiness through sync_file, close-time `-ENOENT`, and `SW_SYNC_GET_DEADLINE` for absent, invalid, and set deadlines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/sw_sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/sync_debug.c -->
## sources/distributed-fs/ceph-client/drivers/dma-buf/sync_debug.c

### Purpose
`sync_debug.c` creates the `debugfs/sync` directory and exposes debug/validation views for software sync timelines. It tracks live timelines globally and provides `info` and `sw_sync` debugfs files.

### Important APIs, Types, And Functions
The public helpers for the software sync implementation are `sync_timeline_debug_add()` and `sync_timeline_debug_remove()`. Internals include global `sync_timeline_list_head`, `sync_timeline_list_lock`, `sync_status_str()`, `sync_print_fence()`, `sync_print_obj()`, `sync_info_debugfs_show()`, `DEFINE_SHOW_ATTRIBUTE(sync_info_debugfs)`, and `sync_debugfs_init()`.

### Control Flow, State, And Persistence
`sync_debugfs_init()` runs as a `late_initcall`, creates `debugfs/sync`, then creates `info` and `sw_sync` with `debugfs_create_file_unsafe()` because entries are never removed. Timeline add/remove operations splice timeline objects into a global list under a spinlock. The `info` show path disables IRQs while walking the global list, then prints each timeline name/value and its active fences under the timeline lock.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on `CONFIG_DEBUG_FS`, `seq_file`, debugfs, `sync_debug.h`, and `sw_sync_debugfs_fops` from `sw_sync.c`. It integrates with fence timestamps and status via `dma_fence_get_status_locked()` and `dma_fence_parent()`. Risks include debugfs lifetime assumptions, holding the global list lock while printing many timelines, lock nesting with per-timeline locks, and stale timeline list membership if create/free paths diverge. Test signals include mounting debugfs, reading `sync/info` with no timelines and with active/signaled/error fences, concurrent timeline open/close while reading, and verifying `sync/sw_sync` file operations are reachable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/sync_debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/sync_debug.h -->
## sources/distributed-fs/ceph-client/drivers/dma-buf/sync_debug.h

### Purpose
`sync_debug.h` defines the private types shared by the software sync timeline implementation, debugfs reporting, and tracepoints. It is not a public userspace ABI header; it binds `sw_sync.c`, `sync_debug.c`, and `sync_trace.h` together.

### Important APIs, Types, And Functions
The key types are `struct sync_timeline`, which owns the kref, name, context, current value, active fence rbtree/list, lock, and debug list node, and `struct sync_pt`, which embeds `struct dma_fence` plus timeline list/tree nodes and deadline storage. `dma_fence_parent()` recovers the timeline from the fence external lock. The header declares `sw_sync_debugfs_fops`, `sync_timeline_debug_add()`, and `sync_timeline_debug_remove()`.

### Control Flow, State, And Persistence
Objects persist through kref ownership in `sync_timeline` and `dma_fence` references in `sync_pt`. The timeline's lock protects active-point ordering and the timeline counter. The debug list node lets `sync_debug.c` enumerate live timelines while the fence parent relationship is inferred from the external spinlock passed to `dma_fence_init()`.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies are kernel list/rbtree/spinlock/kref concepts, `linux/dma-fence.h`, `linux/sync_file.h`, and `uapi/linux/sync_file.h`. Risks are structural: changing the fence lock parent assumption or list/tree invariants would break release, debug printing, and signaling. Test signals are mostly compile-time and behavioral through `sw_sync.c`: fence parent names, active list ordering, debug list membership, and deadline query correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/sync_debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/sync_file.c -->
## sources/distributed-fs/ceph-client/drivers/dma-buf/sync_file.c

### Purpose
`sync_file.c` implements the anonymous-file wrapper around `dma_fence` objects used by Android-style explicit synchronization. It exports creation and fence retrieval helpers and provides ioctl, poll, merge, deadline, and fence-info behavior for userspace file descriptors.

### Important APIs, Types, And Functions
Exported APIs are `sync_file_create()` and `sync_file_get_fence()`. Important helpers include `sync_file_alloc()`, `sync_file_fdget()`, `sync_file_get_name()`, `sync_file_merge()`, `sync_file_poll()`, `sync_file_ioctl_merge()`, `sync_file_ioctl_fence_info()`, `sync_fill_fence_info()`, and `sync_file_ioctl_set_deadline()`. The anonymous inode uses private `sync_file_fops`.

### Control Flow, State, And Persistence
Allocation creates an anonymous inode file whose private data is the `sync_file`, initializes a waitqueue and callback node, and stores a referenced fence. Poll registers a fence callback once and wakes waiters immediately if registration reports the fence is already signaled. Merge validates userspace flags, fetches the second sync_file, builds a merged fence with `dma_fence_unwrap_merge()`, stores the user name, and installs a new fd. Info ioctl first counts unwrapped fences, optionally allocates an array of per-fence status records, copies them to userspace, fills the aggregate name/status/count, and returns it.

### Dependencies, Integration Points, Risks, And Test Signals
This file depends on `dma_fence`, `dma_fence_unwrap`, anonymous inodes, poll waitqueues, uapi sync_file structures, and deadline propagation through `dma_fence_set_deadline()`. It integrates with `sw_sync.c`, GPU/display drivers that export fences, and userspace synchronization libraries. Risks include fd lifetime/reference ordering in error paths, callback removal only after poll enabled, aggregate status semantics for merged fences, userspace buffer sizing, RCU-protected fence names, and correct deadline fanout for fence arrays. Test signals include poll before/after fence signal, merge of valid and invalid fds, `SYNC_IOC_FILE_INFO` with zero and insufficient `num_fences`, name generation versus user-provided merge name, deadline ioctl, and release after callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/sync_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/sync_trace.h -->
## sources/distributed-fs/ceph-client/drivers/dma-buf/sync_trace.h

### Purpose
`sync_trace.h` defines the tracepoint used by the software sync timeline code to record timeline value changes.

### Important APIs, Types, And Functions
It sets `TRACE_SYSTEM` to `sync_trace`, points `TRACE_INCLUDE_PATH` at `drivers/dma-buf`, includes `sync_debug.h`, and declares `TRACE_EVENT(sync_timeline)` with the timeline name and current value as fields.

### Control Flow, State, And Persistence
When `sw_sync.c` defines `CREATE_TRACE_POINTS` before including this header, `trace/define_trace.h` materializes the tracepoint provider. Each `sync_timeline_signal()` call emits the event before updating/signaling under the timeline lock, making trace output a signal of timeline activity rather than a persistent state store.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include kernel tracepoint infrastructure and `struct sync_timeline`. Integration is limited to `trace_sync_timeline(obj)` in `sw_sync.c`. Risks are build-time path correctness, field type mismatch if `sync_timeline.value` changes, and relying on trace ordering for precise post-update values when the event is emitted before the increment. Test signals include successful trace event generation, enabling the event in ftrace/perf, and observing name/value output during `SW_SYNC_IOC_INC`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/sync_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/udmabuf.c -->
## sources/distributed-fs/ceph-client/drivers/dma-buf/udmabuf.c

### Purpose
`udmabuf.c` implements `/dev/udmabuf`, a misc device that exports sealed memfd/shmem/hugetlb-backed pages as dma-buf objects. It lets userspace build DMA-shareable buffers from one or more memfd ranges while preserving page pinning and dma-buf mapping semantics.

### Important APIs, Types, And Functions
The central type is `struct udmabuf`, holding page count, folio and offset arrays, pinned-folio tracking, a cached CPU-access sg table, and the miscdevice. Important operations are `mmap_udmabuf()`, `vmap_udmabuf()`, `get_sg_table()`, `begin_cpu_udmabuf()`, `end_cpu_udmabuf()`, `check_memfd_seals()`, `udmabuf_pin_folios()`, `udmabuf_create()`, `udmabuf_ioctl_create()`, and `udmabuf_ioctl_create_list()`. Module parameters `list_limit` and `size_limit_mb` bound list count and exported buffer size.

### Control Flow, State, And Persistence
An ioctl copies either a single create request or a list, validates page alignment and size limit, allocates arrays, then for each memfd range obtains the file, locks the inode in shared mode, validates seals, pins folios with `memfd_pin_folios()`, and expands large folios into page/offset entries. `dma_buf_export()` transfers ownership of the `udmabuf` to dma-buf release. Mapping for devices builds a fresh scatterlist and maps it with `dma_map_sgtable()`. CPU access lazily creates and caches a bidirectional sg table, then syncs it for CPU/device. `mmap` inserts PFNs fault-by-fault and prefaults the VMA range.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include dma-buf, dma-resv locking for vmap/vunmap, memfd sealing, shmem/hugetlb, folio pinning, scatterlists, DMA mapping API, misc devices, and uapi `linux/udmabuf.h`. Risks include long-term pin accounting, huge-folio subpage offsets, seal races with `memfd_add_seals()`, off-by-one range end computation, cached sg table direction reuse, PFNMAP mmap semantics, and user-controlled list size/total size. Test signals include single and multi-range creates, missing/incorrect seals, unaligned offset/size rejection, hugepage ranges, mmap faults beyond `pagecount` returning SIGBUS, device attach/detach map/unmap, CPU begin/end access, and close-time unpin count matching duplicate pinned folios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma-buf/udmabuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/dma/Kconfig

### Purpose
`drivers/dma/Kconfig` defines the top-level DMA engine feature menu, core support options, platform controller driver selections, and DMA client options such as async_tx and dmatest.

### Important APIs, Types, And Functions
Key symbols include `DMADEVICES`, `DMADEVICES_DEBUG`, `DMADEVICES_VDEBUG`, `DMA_ENGINE`, `DMA_VIRTUAL_CHANNELS`, `DMA_ACPI`, `DMA_OF`, many controller symbols such as `ALTERA_MSGDMA`, `AMBA_PL08X`, and `AMD_*` through sourced sub-Kconfigs, plus clients `ASYNC_TX_DMA`, `DMATEST`, and `DMA_ENGINE_RAID`.

### Control Flow, State, And Persistence
The menu is gated by `HAS_DMA`; inside `if DMADEVICES`, core helper symbols are selected by controller drivers. Each driver entry declares architecture, bus, I/O memory, MSI, reset, or framework dependencies and selects required common pieces. At the end, subdirectory Kconfigs are sourced and client features become selectable only when the DMA engine core exists.

### Dependencies, Integration Points, Risks, And Test Signals
This file controls which C files in `drivers/dma/Makefile` participate in builds and which framework code is available. Risks include mismatched select/depend relationships, enabling drivers for unsupported architectures, hidden dependency cycles, and stale help text for hardware capabilities. Test signals are allmodconfig/allyesconfig across major architectures, COMPILE_TEST coverage, `DMA_ACPI`/`DMA_OF` auto-selection, AMD subconfig visibility, and dmatest availability when `DMA_ENGINE` is selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/Makefile -->
## sources/distributed-fs/ceph-client/drivers/dma/Makefile

### Purpose
`drivers/dma/Makefile` maps DMA engine Kconfig selections to built objects and subdirectories, composing core objects, test clients, and controller drivers.

### Important APIs, Types, And Functions
It adds debug compiler flags for `CONFIG_DMADEVICES_DEBUG` and verbose debug, builds `dmaengine.o`, `virt-dma.o`, `acpi-dma.o`, `of-dma.o`, and `dmatest.o`, then lists controller objects and subdirectories including `altera-msgdma.o`, `amba-pl08x.o`, `idxd/`, `amd/`, and vendor folders. Some composite objects, such as `fsl-edma.o`, include trace objects conditionally.

### Control Flow, State, And Persistence
The build system includes objects through `obj-$(CONFIG_...)` variables. Always-descended directories such as `amd/`, `loongson/`, `mediatek/`, `qcom/`, `stm32/`, `ti/`, and `xilinx/` rely on their own Makefiles and Kconfig symbols to decide final object inclusion.

### Dependencies, Integration Points, Risks, And Test Signals
The Makefile must stay synchronized with `Kconfig` symbols and source filenames. Risks include orphaned drivers, unconditional subdirectory descent hiding missing dependencies, object name mismatches for composite modules, and debug flags changing timing-sensitive driver behavior. Test signals include incremental builds for each referenced Kconfig symbol, module names matching expected aliases, and link coverage for tracing-enabled and disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/acpi-dma.c -->
## sources/distributed-fs/ceph-client/drivers/dma/acpi-dma.c

### Purpose
`acpi-dma.c` provides ACPI-side DMA controller registration and slave-channel lookup helpers. It lets DMA controller drivers register translation callbacks and lets ACPI-enumerated client devices request channels by FixedDMA descriptor index or name.

### Important APIs, Types, And Functions
Exported APIs are `acpi_dma_controller_register()`, `acpi_dma_controller_free()`, `devm_acpi_dma_controller_register()`, `acpi_dma_request_slave_chan_by_index()`, `acpi_dma_request_slave_chan_by_name()`, and `acpi_dma_simple_xlate()`. Important internals include global `acpi_dma_list`, `acpi_dma_lock`, `acpi_dma_parse_csrt()`, `acpi_dma_parse_resource_group()`, `acpi_dma_update_dma_spec()`, and `acpi_dma_parse_fixed_dma()`.

### Control Flow, State, And Persistence
Controller registration validates the ACPI companion, allocates `struct acpi_dma`, stores the translation callback and driver data, optionally parses CSRT to discover controller-relative request-line ranges and DMA mask, then appends the controller to a global list. Client lookup parses FixedDMA resources into channel/request IDs, walks registered controllers under the mutex, adjusts request lines to controller-relative IDs when CSRT ranges are available, and invokes the controller's xlate function. Name lookup uses `dma-names` when present and falls back to conventional `tx` index 0 and `rx` index 1.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include ACPI resource parsing, CSRT tables, device properties, DMA masks, `dma_request_channel()`, and `linux/acpi_dma.h`. Integration points are ACPI-aware DMA controller drivers and client drivers using common channel request helpers. Risks include incomplete CSRT data, GSI registration side effects while matching IRQs, request-line range mismatches producing `-EPROBE_DEFER`, global list lifetime under device detach, and fallback name assumptions. Test signals include controller register/free/devm unwind, FixedDMA index and name lookup, CSRT present/absent paths, request line rebasing, invalid ACPI companions, and deferred probe when no controller has registered yet.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/acpi-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/altera-msgdma.c -->
## sources/distributed-fs/ceph-client/drivers/dma/altera-msgdma.c

### Purpose
`altera-msgdma.c` implements a dmaengine driver for the Altera/Intel mSGDMA IP core. It exposes one DMA channel supporting memcpy and slave scatter-gather transfers backed by mSGDMA extended descriptors and descriptor/response FIFOs.

### Important APIs, Types, And Functions
Key types are `struct msgdma_extended_desc`, `struct msgdma_sw_desc`, and `struct msgdma_device`. Important functions include descriptor pool helpers `msgdma_get_descriptor()`, `msgdma_free_descriptor()`, preparation paths `msgdma_prep_memcpy()` and `msgdma_prep_slave_sg()`, submission `msgdma_tx_submit()`, hardware control `msgdma_reset()`, `msgdma_copy_one()`, `msgdma_start_transfer()`, interrupt paths `msgdma_irq_handler()` and `msgdma_tasklet()`, and probe/remove functions.

### Control Flow, State, And Persistence
Channel resource allocation creates 1024 software descriptors and populates a free list. Prep functions reserve enough descriptors, split large transfers at `U32_MAX`, fill source/destination/stride/control fields, chain child descriptors on `tx_list`, and marks only the last descriptor for completion interrupt. Submit assigns a cookie and moves the transaction to `pending_list`; `issue_pending` starts transfer only when idle by splicing pending descriptors to `active_list` and writing descriptors into the hardware FIFO. The IRQ handler clears controller IRQ, marks the device idle if not busy, starts the next transfer, and schedules a tasklet that drains response FIFO entries, completes active descriptors, invokes callbacks, and returns descriptors to the free list.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include platform resources named `csr`, `desc`, optional `resp`, OF DMA controller registration, dmaengine cookies, tasklets, and memory-mapped I/O. Risks include descriptor free-count/list races, busy-waiting on full descriptor FIFO with `mdelay(1)`, no detailed error handling from response status, optional response FIFO count behavior, single-channel serialization, and cleanup ordering with tasklets and IRQs. Test signals include DT probe for `altr,socfpga-msgdma`, memcpy and MEM_TO_DEV/DEV_TO_MEM slave transfers, descriptor exhaustion, transfers split across multiple descriptors, response FIFO and no-response variants, IRQ-driven completion/callbacks, reset timeout handling, and removal after active/pending descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/altera-msgdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/amba-pl08x.c -->
## sources/distributed-fs/ceph-client/drivers/dma/amba-pl08x.c

### Purpose
`amba-pl08x.c` implements the ARM PrimeCell PL080/PL081 DMA controller family and derivatives, including Samsung PL080S, ST Nomadik variants, and Faraday FTDMAC020. It registers dmaengine memcpy and optional slave/cyclic engines, constructs hardware linked-list items, arbitrates virtual channels over physical channels, and supports platform data or Device Tree routing.

### Important APIs, Types, And Functions
Important state types are `struct vendor_data`, `struct pl08x_phy_chan`, `struct pl08x_dma_chan`, `struct pl08x_txd`, `struct pl08x_sg`, and `struct pl08x_driver_data`. Major paths include mux helpers `pl08x_request_mux()`/`pl08x_release_mux()`, physical channel management `pl08x_get_phy_channel()`, `pl08x_phy_alloc_and_start()`, `pl08x_phy_free()`, LLI generation `pl08x_fill_llis_for_desc()`, prep callbacks `pl08x_prep_dma_memcpy()`, `pl08x_prep_slave_sg()`, `pl08x_prep_dma_cyclic()`, control callbacks `pl08x_issue_pending()`, `pl08x_pause()`, `pl08x_resume()`, `pl08x_terminate_all()`, status `pl08x_dma_tx_status()`, IRQ handler `pl08x_irq()`, OF xlate `pl08x_of_xlate()`, and AMBA probe `pl08x_probe()`.

### Control Flow, State, And Persistence
Probe maps AMBA registers, derives vendor capabilities, configures dmaengine callback tables, obtains platform data or parses DT bus/burst/width/channel data, creates an LLI DMA pool, enables the controller, clears interrupts, registers an IRQ, initializes physical channels, creates virtual memcpy and slave channels, then registers dmaengine devices. Transfers allocate a `pl08x_txd`, build one or more `pl08x_sg` entries, request a slave mux when needed, allocate an LLI array from the DMA pool, encode alignment-sensitive LLIs, and queue through `virt-dma`. `issue_pending` assigns a free physical channel or marks the virtual channel waiting. Interrupts clear error/terminal count bits, complete cyclic callbacks or one-shot descriptors, release mux reservations, start queued descriptors on the same physical channel, or reassign/free it fairly to the oldest waiting virtual channel.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include AMBA/PrimeCell IDs, `linux/amba/pl080.h`, platform data `linux/amba/pl08x.h`, optional OF DMA, dmaengine/virt-dma, DMA pools, debugfs, runtime hardware registers, and IRQs. Risks include complex vendor-specific register layouts, busy-wait loops without timeouts in start paths, LLI alignment/width/transfer-size corner cases, physical-channel fairness and locking, mux reference balancing, cyclic transfers never releasing mux until termination, DT-created channel-name memory not freed in all paths, and error IRQs completing descriptors like terminal count. Test signals include PL080/PL081/PL080S/FTDMAC020 probe matrices, memcpy and slave SG transfers with misaligned addresses, cyclic audio-style transfers, peripheral flow-control rejection on PL080S, residue reporting while paused/running, channel waiting/reassignment under contention, secure Nomadik locked channels, OF two-cell translation, debugfs state output, and removal/error-path leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/amba-pl08x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/amd/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/dma/amd/Kconfig

### Purpose
`drivers/dma/amd/Kconfig` defines selectable AMD DMA engine drivers for AE4DMA, PTDMA, and QDMA.

### Important APIs, Types, And Functions
Symbols are `AMD_AE4DMA`, `AMD_PTDMA`, and `AMD_QDMA`. AE4DMA depends on x86_64 or COMPILE_TEST plus PCI and also depends on PTDMA; PTDMA depends on x86_64 and PCI; QDMA depends on `HAS_IOMEM`. All select `DMA_ENGINE`, virtual-channel support, and QDMA additionally selects `REGMAP_MMIO`.

### Control Flow, State, And Persistence
These symbols control descent into `amd/ae4dma`, `amd/ptdma`, and `amd/qdma` Makefiles. AE4DMA reuses PTDMA's dmaengine layer, so the dependency on `AMD_PTDMA` is part of the functional build contract.

### Dependencies, Integration Points, Risks, And Test Signals
Risks include incorrect dependency visibility for COMPILE_TEST, hidden build assumptions between AE4DMA and PTDMA headers/exports, and QDMA register definitions being built without its core. Test signals include AMD submenu visibility, module and built-in combinations, AE4DMA with PTDMA enabled, QDMA allmodconfig coverage, and x86_64 PCI-only PTDMA selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/amd/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/amd/Makefile -->
## sources/distributed-fs/ceph-client/drivers/dma/amd/Makefile

### Purpose
`drivers/dma/amd/Makefile` routes AMD DMA Kconfig symbols to their driver subdirectories.

### Important APIs, Types, And Functions
It descends into `ae4dma/`, `ptdma/`, and `qdma/` through `obj-$(CONFIG_AMD_AE4DMA)`, `obj-$(CONFIG_AMD_PTDMA)`, and `obj-$(CONFIG_AMD_QDMA)`.

### Control Flow, State, And Persistence
No runtime state exists. The file is pure build orchestration and relies on subdirectory Makefiles to compose final module objects.

### Dependencies, Integration Points, Risks, And Test Signals
The file must match `amd/Kconfig` symbol names and subdirectory names. Test signals include enabling each AMD symbol independently where dependencies allow and verifying expected module objects are emitted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/amd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/amd/ae4dma/Makefile -->
## sources/distributed-fs/ceph-client/drivers/dma/amd/ae4dma/Makefile

### Purpose
This Makefile builds the AMD AE4DMA driver module/object from its device core and optional PCI bus glue.

### Important APIs, Types, And Functions
It creates `ae4dma.o` when `CONFIG_AMD_AE4DMA` is enabled, always includes `ae4dma-dev.o`, and adds `ae4dma-pci.o` when `CONFIG_PCI` is enabled.

### Control Flow, State, And Persistence
The build composition mirrors AE4DMA's runtime split: queue/work/IRQ core in `ae4dma-dev.c` and PCI discovery/resource setup in `ae4dma-pci.c`.

### Dependencies, Integration Points, Risks, And Test Signals
Risks include AE4DMA being selected without PCI support even though its Kconfig depends on PCI, and unresolved symbols if PTDMA exports are unavailable. Test signals include module link with `CONFIG_AMD_AE4DMA=m/y`, PCI enabled builds, and dependency on PTDMA object availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/amd/ae4dma/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/amd/ae4dma/ae4dma-dev.c -->
## sources/distributed-fs/ceph-client/drivers/dma/amd/ae4dma/ae4dma-dev.c

### Purpose
`ae4dma-dev.c` initializes and services AMD AE4DMA hardware queues, then registers them through the shared PTDMA dmaengine layer. It handles per-queue coherent descriptor rings, IRQs, completion workqueues, and debugfs setup.

### Important APIs, Types, And Functions
The module parameter `max_hw_q` controls how many hardware queues to initialize. Key functions are `ae4_pending_work()`, `ae4_core_irq_handler()`, `ae4_destroy_work()`, and `ae4_core_init()`. It uses `struct ae4_device`, `struct ae4_cmd_queue`, `struct pt_cmd_queue`, AE4 register offsets, and shared functions `ae4_check_status_error()`, `pt_dmaengine_register()`, and `ptdma_debugfs_setup()`.

### Control Flow, State, And Persistence
Initialization writes the requested queue count to the device, loops over queues allocating IRQs and coherent rings, programs max index and base address registers, initializes command lists/waitqueues/completions, starts an ordered workqueue per hardware queue, and registers dmaengine channels. IRQs increment per-queue interrupt counters, clear status bits, and wake the pending worker. The worker waits until interrupt count exceeds done count, then under `cmd_lock` drains completed descriptors from the software command list based on hardware read index, checks descriptor errors, invokes callbacks, decrements queue count, advances read index, and completes waiters.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include PCI-provided IRQ numbers and BAR mapping, AE4 descriptor layout, coherent DMA allocation, ordered workqueues, waitqueues, shared PTDMA dmaengine code, and debugfs. Risks include unbounded `max_hw_q` relative to `MAX_AE4_HW_QUEUES`, delayed work that loops forever and relies on cancellation, interrupt/counter races, completion wakeups under queue-full conditions, queue count/list mismatch, and lack of explicit dmaengine unregister in AE4 remove path. Test signals include probing with one and many queues, MSI-X vector mapping, descriptor completion and error logging, queue-full timeout path, workqueue cancellation during remove, and dmaengine channel count matching initialized queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/amd/ae4dma/ae4dma-dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/amd/ae4dma/ae4dma-pci.c -->
## sources/distributed-fs/ceph-client/drivers/dma/amd/ae4dma/ae4dma-pci.c

### Purpose
`ae4dma-pci.c` is the PCI bus glue for AMD AE4DMA. It allocates device state, maps PCI BARs, configures MSI-X/MSI interrupts and DMA mask, then calls AE4 core initialization.

### Important APIs, Types, And Functions
Important functions are `ae4_get_irqs()`, `ae4_free_irqs()`, `ae4_deinit()`, `ae4_pci_probe()`, and `ae4_pci_remove()`. The PCI ID table matches AMD device `0x149B`, and `module_pci_driver()` registers the driver named `ae4dma`.

### Control Flow, State, And Persistence
Probe devm-allocates `struct ae4_device` and MSI-X bookkeeping, enables the PCI function, maps all memory BARs via pcim helpers, stores BAR0 as `pt->io_regs`, obtains MSI-X vectors for all queue slots or falls back to a single MSI vector shared across queue entries, sets bus mastering, requests a 48-bit coherent DMA mask, stores driver data, and invokes `ae4_core_init()`. Remove cancels/destroys workqueues and frees IRQ vectors.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include PCI core, managed PCI I/O mapping, IRQ vector allocation, AE4 core code, and shared PTDMA device fields. Risks include mapping all BARs but assuming index 0, fallback MSI sharing all queues, not checking `dma_set_mask_and_coherent()` return, partial initialization cleanup relying on devm/pcim, and remove not explicitly unregistering dmaengine channels if core init succeeded. Test signals include matching device `0x149B`, MSI-X and MSI fallback paths, BAR mapping failures, 48-bit DMA mask behavior, probe error cleanup, and remove after active DMA submissions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/amd/ae4dma/ae4dma-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/amd/ae4dma/ae4dma.h -->
## sources/distributed-fs/ceph-client/drivers/dma/amd/ae4dma/ae4dma.h

### Purpose
`ae4dma.h` defines AE4DMA register offsets, descriptor formats, queue state, device state, and core function prototypes. It is the contract between AE4 PCI/core code and the shared PTDMA dmaengine implementation.

### Important APIs, Types, And Functions
Important constants include `MAX_AE4_HW_QUEUES`, AE4 queue register offsets, `AE4_DMA_VERSION`, `CMD_AE4_DESC_DW0_VAL`, and `AE4_TIME_OUT`. Types include `struct ae4_msix`, `struct ae4_cmd_queue`, `union dwou`, `struct dword1`, `struct ae4dma_desc`, and `struct ae4_device`. Declared functions are `ae4_core_init()`, `ae4_destroy_work()`, and `ae4_check_status_error()`.

### Control Flow, State, And Persistence
The header embeds a `struct pt_device` inside `struct ae4_device`, making AE4 appear as a PTDMA-compatible device with version `AE4_DMA_VERSION`. Each AE4 queue embeds a `struct pt_cmd_queue`, a command list, workqueue, completion, counters, and hardware index tracking used by both AE4 core and `ptdma-dmaengine.c`.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include `ptdma.h`, `virt-dma.h`, PCI/device/dmaengine headers, workqueues, waitqueues, and completions. Risks include descriptor field ordering/endian assumptions, high/low address naming inconsistencies relative to PTDMA descriptors, queue array bounds, and cross-directory header coupling. Test signals include compile coverage with PTDMA enabled, descriptor size/register programming validation, multi-queue channel registration, and AE4 error status decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/amd/ae4dma/ae4dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/amd/ptdma/Makefile -->
## sources/distributed-fs/ceph-client/drivers/dma/amd/ptdma/Makefile

### Purpose
This Makefile builds AMD PTDMA from core device, dmaengine, debugfs, and optional PCI glue objects.

### Important APIs, Types, And Functions
It builds `ptdma.o` when `CONFIG_AMD_PTDMA` is enabled from `ptdma-dev.o`, `ptdma-dmaengine.o`, and `ptdma-debugfs.o`, plus `ptdma-pci.o` when PCI is enabled.

### Control Flow, State, And Persistence
The composition mirrors the runtime split: PCI probe/resource setup, PT hardware queue management, dmaengine channel implementation, and debugfs reporting.

### Dependencies, Integration Points, Risks, And Test Signals
Risks include PCI-specific assumptions because PTDMA Kconfig already depends on PCI, and shared exports used by AE4DMA needing to be present when AE4DMA is enabled. Test signals include module link for PTDMA and AE4DMA users, debugfs object inclusion, and PCI object inclusion under expected configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/amd/ptdma/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/amd/ptdma/ptdma-debugfs.c -->
## sources/distributed-fs/ceph-client/drivers/dma/amd/ptdma/ptdma-debugfs.c

### Purpose
`ptdma-debugfs.c` exposes PTDMA/AE4DMA runtime information under the dmaengine debugfs device root. It reports device version, queue counts, total interrupts, per-queue operation counts, and enabled interrupt status.

### Important APIs, Types, And Functions
The exported setup function is `ptdma_debugfs_setup()`. Show callbacks are `pt_debugfs_info_show()`, `pt_debugfs_stats_show()`, and `pt_debugfs_queue_show()`, each wrapped by `DEFINE_SHOW_ATTRIBUTE`.

### Control Flow, State, And Persistence
Setup first checks `debugfs_initialized()`, then creates `info` and `stats` files. For AE4DMA version devices it creates one `qN` directory per AE4 command queue and attaches queue stats to each; for PTDMA it creates a single `q` directory. Reads inspect device registers and in-memory counters on demand; no persistent data is stored by debugfs beyond dentries.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include debugfs, seq_file, `ptdma.h`, AE4 queue types, and dmaengine debugfs root initialization. Risks include reading registers after device teardown if debugfs lifetime is not coupled to dmaengine unregister, version-specific offset assumptions, and unsynchronized counter reads. Test signals include debugfs presence after PTDMA and AE4DMA probe, correct queue directory count, total interrupt counter updates, enabled interrupt text for both versions, and no crashes when debugfs is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/amd/ptdma/ptdma-debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/amd/ptdma/ptdma-dev.c -->
## sources/distributed-fs/ceph-client/drivers/dma/amd/ptdma/ptdma-dev.c

### Purpose
`ptdma-dev.c` initializes and drives the original AMD PassThru DMA hardware queue. It programs queue registers, submits 32-byte passthrough descriptors, handles queue interrupts and errors, registers dmaengine support, and tears hardware down.

### Important APIs, Types, And Functions
Important functions are `pt_start_queue()`, `pt_stop_queue()`, `pt_core_execute_cmd()`, exported `pt_core_perform_passthru()`, `pt_check_status_trans()`, `pt_core_irq_handler()`, `pt_core_init()`, and `pt_core_destroy()`. State is held in `struct pt_device`, `struct pt_cmd_queue`, `struct pt_cmd`, `struct pt_passthru_engine`, and hardware descriptor `struct ptdma_desc`.

### Control Flow, State, And Persistence
Core init creates a DMA pool, writes global PTDMA configuration registers, allocates a coherent ring, disables queue interrupts, sets queue base/tail/head and size bits, requests an IRQ, enables interrupts, registers the dmaengine device, and installs debugfs. A passthrough request fills source/destination/length descriptor fields, toggles interrupt enable based on the queued dmaengine descriptor flags, copies the descriptor to the ring under `q_lock`, advances the ring index, performs a memory barrier, writes the tail register, and starts the queue. IRQ handling disables interrupts, reads/acknowledges status, records first command error, may advance the head pointer on error, invokes the current command callback, and reenables interrupts.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include coherent DMA allocation, DMA pools, PCI-provided MMIO/IRQ, bitfield helpers, shared dmaengine registration, and debugfs setup. Risks include only one global `tdata.cmd` for in-flight callback state, ring-full handling mostly delegated to higher layers, error-code array indexing without bounds checks, interrupt disable/reenable races, and destroy flushing `pt->cmd` even though normal PT submission primarily uses virt-dma descriptors. Test signals include PTDMA device probe, memcpy submission/completion with and without interrupt flag, hardware error injection/status handling, IRQ storm avoidance, dmaengine unregister on remove, and cleanup after `pt_core_init()` failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/amd/ptdma/ptdma-dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/amd/ptdma/ptdma-dmaengine.c -->
## sources/distributed-fs/ceph-client/drivers/dma/amd/ptdma/ptdma-dmaengine.c

### Purpose
`ptdma-dmaengine.c` adapts PTDMA and AE4DMA hardware queues to the Linux dmaengine API. It provides virtual-channel backed memcpy and interrupt descriptors, status/pause/resume/terminate callbacks, descriptor allocation/freeing, and AE4-specific multi-queue command flow.

### Important APIs, Types, And Functions
Exported functions are `ae4_check_status_error()`, `pt_dmaengine_register()`, and `pt_dmaengine_unregister()`. Key internals include `pt_create_desc()`, `pt_prep_dma_memcpy()`, `pt_prep_dma_interrupt()`, `pt_issue_pending()`, `pt_dma_start_desc()`, `pt_handle_active_desc()`, `pt_cmd_callback()`, `pt_cmd_callback_work()`, `pt_tx_status()`, `pt_pause()`, `pt_resume()`, and `pt_terminate_all()`. AE4 helpers include `ae4_core_execute_cmd()`, `pt_core_perform_passthru_ae4()`, and `ae4_core_queue_full()`.

### Control Flow, State, And Persistence
Registration allocates one channel for PTDMA or one channel per AE4 queue, creates a descriptor cache, advertises `DMA_MEMCPY`, `DMA_INTERRUPT`, and `DMA_PRIVATE`, initializes `virt-dma` channels, and registers the dmaengine device. Prep allocates a `pt_dma_desc`, fills passthrough source/destination/length, installs callbacks, and for AE4 adds the command to the per-queue software list. `issue_pending` moves virt-dma descriptors to the issued list and starts processing if the engine is idle. PTDMA completion marks descriptors complete synchronously in the callback path; AE4 completion is driven by AE4 workqueue callbacks that use `pt_cmd_callback_work()`. Status checks poll hardware status/error fields before reporting cookie state.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include `virt-dma`, dmaengine cookies, PTDMA core queue operations, AE4 queue structures, kmem_cache descriptors, and DMA descriptor unmapping. Risks include divergent PTDMA versus AE4 completion paths, AE4 queue-full wait timing, descriptor status races under `vc.lock`, missing residue accounting beyond descriptor granularity, terminate freeing descriptors while AE4 command lists may still contain command entries, and AE4 high/low address field ordering. Test signals include dmaengine memcpy through PTDMA and AE4, multiple AE4 channels submitting concurrently, queue-full timeout behavior, pause/resume/terminate with active and queued descriptors, cookie status before/after completion, interrupt-only descriptor prep, and error propagation from hardware status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/amd/ptdma/ptdma-dmaengine.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/amd/ptdma/ptdma-pci.c -->
## sources/distributed-fs/ceph-client/drivers/dma/amd/ptdma/ptdma-pci.c

### Purpose
`ptdma-pci.c` is the PCI bus driver for AMD PassThru DMA. It allocates PT device state, maps the configured BAR, obtains MSI-X/MSI interrupts, configures DMA masks, and calls PTDMA core initialization.

### Important APIs, Types, And Functions
Important functions are `pt_alloc_struct()`, `pt_get_msix_irqs()`, `pt_get_msi_irq()`, `pt_get_irqs()`, `pt_free_irqs()`, `pt_pci_probe()`, and `pt_pci_remove()`. It matches AMD PCI device `0x1498` with `struct pt_dev_vdata` selecting BAR 2.

### Control Flow, State, And Persistence
Probe allocates `struct pt_device` and MSI-X state with devm, enables the PCI device, maps all memory BARs, selects BAR 2 from the ioremap table, obtains MSI-X or MSI, sets bus mastering, attempts 48-bit then 32-bit coherent DMA mask, stores driver data, and invokes `pt_core_init()`. Remove calls `pt_core_destroy()` when initialized and frees the interrupt mode.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include PCI/pcim resource management, MSI/MSI-X APIs, DMA masks, PT core functions, and device IDs. Risks include legacy `pci_enable_msix_range()`/`pci_enable_msi()` cleanup differences, mapping all BARs while using only one, returning from failed probe without freeing IRQs in some error paths after allocation, and assuming driver data is always present for matched IDs. Test signals include probe for device `0x1498`, BAR 2 mapping, MSI-X success and MSI fallback, 48-bit mask fallback to 32-bit, init failure unwind, and remove after registered dmaengine activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/amd/ptdma/ptdma-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/amd/ptdma/ptdma.h -->
## sources/distributed-fs/ceph-client/drivers/dma/amd/ptdma/ptdma.h

### Purpose
`ptdma.h` defines AMD PassThru DMA register constants, descriptor formats, device/queue/channel state, and cross-file function prototypes. It is also consumed by AE4DMA because AE4 reuses the PTDMA dmaengine abstraction.

### Important APIs, Types, And Functions
Important constants include command queue register offsets, queue sizing macros, interrupt bits, PT engine identifiers, descriptor sizes, and block sizes. Key types are `struct pt_tasklet_data`, `struct pt_passthru_engine`, `struct pt_cmd`, `struct pt_dma_desc`, `struct pt_dma_chan`, `struct pt_cmd_queue`, `struct pt_device`, `struct ptdma_desc`, and `struct pt_dev_vdata`. Prototypes cover dmaengine registration, debugfs setup, core init/destroy, passthrough execution, status checking, queue start/stop, and inline interrupt enable/disable helpers.

### Control Flow, State, And Persistence
The header captures persistent driver state: the PT device owns PCI/device info, MMIO base, one hardware command queue, dmaengine channels, descriptor cache, counters, and callback tasklet data. Queue state tracks coherent ring memory, register base, cached control word, interrupt enable state, status/error snapshots, and total passthrough operations. Descriptor bitfields encode the 8-word hardware command format for passthrough copies.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include dmaengine, PCI, dmapool, lists, waitqueues, spinlocks, mutexes, and `virt-dma`. Risks include register offset drift with hardware revisions, bitfield layout portability, macro precedence in pointer mask sizing, shared inline interrupt helpers being PTDMA-specific even though AE4 embeds PT structures, and ABI-like coupling between PTDMA and AE4DMA. Test signals include compile of PTDMA and AE4DMA users, descriptor size/layout checks, queue register programming validation, interrupt enable/disable register writes, and debugfs field access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/amd/ptdma/ptdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/amd/qdma/Makefile -->
## sources/distributed-fs/ceph-client/drivers/dma/amd/qdma/Makefile

### Purpose
This Makefile builds the AMD QDMA driver object from the core QDMA implementation and shared register-definition file.

### Important APIs, Types, And Functions
It creates `amd-qdma.o` when `CONFIG_AMD_QDMA` is enabled and composes it from `qdma.o` and `qdma-comm-regs.o`.

### Control Flow, State, And Persistence
No runtime state exists. The Makefile ensures the register offset/field tables are linked into the QDMA driver module with the core implementation.

### Dependencies, Integration Points, Risks, And Test Signals
The file must match the `AMD_QDMA` Kconfig symbol and source filenames. Risks include missing register table linkage if object names change and redundant `-$(CONFIG_AMD_QDMA)` conditional inside a directory only reached for the same config. Test signals include successful `amd-qdma` module link and symbol resolution for `qdma_regos_default` and `qdma_regfs_default`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/amd/qdma/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/amd/qdma/qdma-comm-regs.c -->
## sources/distributed-fs/ceph-client/drivers/dma/amd/qdma/qdma-comm-regs.c

### Purpose
`qdma-comm-regs.c` provides the default AMD QDMA register offset and bit-field tables used by the QDMA core. It centralizes common hardware register layout data for context, queue, interrupt, and error programming.

### Important APIs, Types, And Functions
The file defines two constant arrays: `qdma_regos_default[QDMA_REGO_MAX]` of `struct qdma_reg` entries and `qdma_regfs_default[QDMA_REGF_MAX]` of `struct qdma_reg_field` entries. It uses `QDMA_REGO()` and `QDMA_REGF()` macros and enumerators declared in `qdma.h`.

### Control Flow, State, And Persistence
There is no executable control flow. The arrays are read-only driver data describing offsets and word counts for context data/cmd/mask, H2C/C2H MM controls, queue count, ring size, producer/consumer indices, function ID, and error registers, plus bit ranges for queue context, interrupt context, command fields, queue count, and error interrupt fields.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies are `qdma.h` enum ordering and field extraction helpers in the QDMA core. Risks include table index drift when enum values change, incorrect bit positions silently corrupting hardware contexts, and lack of per-IP-version differentiation if newer hardware layouts diverge. Test signals include QDMA probe reading expected queue count/function ID, context programming round trips, interrupt vector programming, error interrupt arming, and compile-time array bounds coverage through `QDMA_REGO_MAX` and `QDMA_REGF_MAX`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/amd/qdma/qdma-comm-regs.c -->
