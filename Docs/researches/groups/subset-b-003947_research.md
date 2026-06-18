# subset-b-003947 research

Grouped research for mlx5 send/receive WQE and UMR declarations plus the Mellanox mthca InfiniBand HCA driver build glue, command channel, resource helpers, completion/event queues, MAD handling, catastrophic reset handling, and PCI probe/remove path.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/umr.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/umr.h

## Purpose
`umr.h` declares the mlx5 RDMA UMR interface used to create, revoke, reregister, and update memory keys and their translation tables through send-queue UMR WQEs. It is the capability gate between generic mlx5 MR code and hardware-specific UMR quirks.

## Important APIs, types, and functions
Key constants define UMR translation limits and alignment: `MLX5_MAX_UMR_PAGES`, `MLX5_MAX_UMR_EXTENDED_SHIFT`, `MLX5_IB_UMR_OCTOWORD`, and `MLX5_IB_UMR_XLT_ALIGNMENT`. `mlx5r_umr_can_load_pas()` rejects PAS-list UMR when firmware cannot modify page size or lacks extended offsets for large MRs. `mlx5r_umr_can_reconfig()` decides whether access-flag changes can be issued by UMR, especially remote atomic and relaxed-ordering changes. `mlx5r_umr_get_xlt_octo()` converts byte counts to aligned octoword counts. `mlx5r_umr_context` stores completion status for synchronous UMR waits, and `mlx5r_umr_wqe` describes the common control/mkey/data WQE layout. Exported functions cover resource init/cleanup, MR revoke, PD/access reregistration, PAS updates, XLT range updates, page-shift changes, and dmabuf page-size updates.

## Control flow
Callers in MR registration/reregistration paths first check capability helpers, build UMR WQEs using the declared layouts, post them through mlx5 send-queue helpers, and wait for completion through `mlx5r_umr_context`. Range APIs allow partial translation refreshes while full helpers update the whole MR.

## State and persistence
The header itself owns no persistent state. It defines contracts for in-memory completion objects and WQE layout, while the actual persistent effects are firmware-owned mkey state, access flags, translation-table pages, page size, and free/enabled mkey status.

## Dependencies and integration points
It depends on `mlx5_ib.h`, mlx5 core capability macros, RDMA access flags, mkey descriptors, completions, and the send path in `wr.c`. It is consumed by mlx5 MR, ODP, dmabuf, and fast-reg code that needs UMR updates.

## Risks
Capability checks encode hardware quirks rather than simple feature bits. If they are relaxed incorrectly, the driver can post UMRs that firmware rejects or, worse, enable an mkey with an invalid translation. Alignment and octoword sizing must match firmware ABI. Access reconfiguration must stay synchronized with implementation-side mkey masks.

## Test signals
Useful tests include MR registration/reregistration on devices with and without `umr_modify_entity_size_disabled`, large MR updates above 64K pages without extended offsets, remote atomic access changes, relaxed-ordering access changes, dmabuf page-size changes, revoke paths, and UMR completion error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/umr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/wr.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/wr.c

## Purpose
`wr.c` implements mlx5 RDMA send and receive posting for QPs. It converts RDMA core work requests into mlx5 WQE control, address, datagram, Ethernet/LSO, data, UMR, memory-registration, local-invalidate, and integrity-signature segments, maintains software queue state, and rings hardware doorbells.

## Important APIs, types, and functions
Public entry points are `mlx5_ib_post_send()`, `mlx5_ib_post_recv()`, `mlx5r_wq_overflow()`, `mlx5r_begin_wqe()`, `mlx5r_finish_wqe()`, and `mlx5r_ring_db()`. Helpers map IB opcodes to mlx5 opcodes, fill remote-address and SGE data segments, copy inline payloads across fragmented SQ edges, build UD/GSI address vectors, build Ethernet LSO/checksum segments, construct UMR segments for fast-reg and local invalidate, configure protection-information BSF/PSV state, and compute optional WQE signatures.

## Control flow
`mlx5_ib_post_send()` rejects non-drain posts during internal device error, delegates GSI posts, locks the SQ, validates opcode and SGE count, begins each WQE, chooses fence mode, dispatches QP-type-specific segment construction, appends inline or SGE data segments, records WR metadata, finishes WQE sizing/indexing, and rings one doorbell for all accepted WQEs. RC/XRC sends handle RDMA, local invalidate, MR registration, and integrity registration; UC handles RDMA writes; UD/GSI writes datagram segments and optional IPoIB offload headers. `mlx5_ib_post_recv()` similarly locks the RQ, validates space/SGEs, fills receive scatter entries, terminates unused SGEs with the terminate lkey, optionally signs the receive WQE, records WR IDs, updates the RQ head, and writes the receive doorbell record.

## State and persistence
The file updates volatile QP SQ/RQ state: head/tail-derived overflow checks, `cur_post`, `cur_edge`, WR IDs, WQE head/next metadata, opcode records, fence carry state, receive head, and doorbell records. Persistent device-visible state is the WQE memory and doorbell writes consumed by the HCA. Integrity registration also changes signature MR bookkeeping such as `sig_status_checked` and `next_fence`.

## Dependencies and integration points
It depends on RDMA core WR structures, mlx5 hardware WQE layouts, `mlx5_ib_qp`, fragmented SQ buffers, BF register mappings, GSI helpers, UMR declarations from `umr.h`, memory-registration structures, and CQ locking for overflow rechecks. The completion path later interprets the WR metadata populated here.

## Risks
This is a high-risk fast path: queue overflow checks race CQ progress and depend on CQ locking; WQE construction must handle fragmented SQ edges exactly; inline LSO and integrity layouts have strict alignment; `nreq` batching means errors after previous WQEs still ring accepted work; fence state is subtle across UMR and PSV WQEs; unsupported atomics return `-EOPNOTSUPP`; and doorbell ordering relies on memory barriers and SQ locking. Any size miscalculation can corrupt adjacent WQEs.

## Test signals
Cover RC/UC/UD/XRC/SMI/GSI posting, chained WRs with mid-chain failure, max SGE and max inline boundaries, fragmented SQ edge crossing, IPoIB LSO and checksum offload, local invalidate, fast-reg MR with inline and DMA descriptors, integrity MR with and without separate PI MR, PSV updates, drain behavior during internal device error, receive zero-length and max-SGE WQEs, signature-enabled QPs, and lockdep/KASAN stress under concurrent CQ polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/wr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/wr.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/wr.h

## Purpose
`wr.h` declares the mlx5 work-request posting interface and inline helpers for safely writing send WQEs into fragmented SQ buffers. It is the small public boundary used by verbs code and UMR helpers to post sends and receives.

## Important APIs, types, and functions
The header defines `MLX5_IB_SQ_UMR_INLINE_THRESHOLD`, `struct mlx5_wqe_eth_pad`, `get_sq_edge()`, `handle_post_send_edge()`, and `mlx5r_memcpy_send_wqe()`. It declares `mlx5r_wq_overflow()`, WQE begin/finish helpers, `mlx5r_ring_db()`, and post-send/post-recv functions plus drain/nodrain wrappers.

## Control flow
WQE writers get the current contiguous SQ edge with `get_sq_edge()`, append 16-byte-aligned segments, call `handle_post_send_edge()` whenever the write cursor reaches an edge, and use `mlx5r_memcpy_send_wqe()` for variable inline bytes that can cross fragments. Higher-level callers begin a WQE, fill segments, finish metadata, and ring the doorbell.

## State and persistence
The helpers mutate caller-provided segment pointers, WQE size counters, and cached edge pointers. They do not persist state themselves, but they protect the integrity of hardware-visible SQ memory and the QP SQ `cur_edge` cache maintained by `wr.c`.

## Dependencies and integration points
It depends on `mlx5_ib.h`, fragmented buffer helpers, mlx5 WQE block sizing, RDMA QP/CQ types, and GSI integration. The declarations are consumed by normal verbs posting and specialized UMR posting paths.

## Risks
Pointer arithmetic is central here. Incorrect edge detection or alignment can wrap to the wrong SQ fragment, corrupt WQEs, or make the posted size disagree with the hardware descriptor size. The inline copy helper assumes callers pass a 16-byte-aligned cursor and maintain accurate `wqe_sz`.

## Test signals
Validate WQE writes at every boundary around fragment ends and SQ wrap, inline copies with 1-byte through multi-fragment lengths, UMR descriptor sizes at the inline threshold, drain/nodrain wrapper binding, and compile coverage for all users of the declared posting functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/wr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/Kconfig

## Purpose
`Kconfig` exposes the mthca low-level InfiniBand HCA driver and its optional verbose debug output in the kernel configuration tree.

## Important APIs, types, and functions
`CONFIG_INFINIBAND_MTHCA` is a tristate depending on PCI and describes support for Mellanox InfiniHost Tavor and Arbel adapters. `CONFIG_INFINIBAND_MTHCA_DEBUG` is a boolean depending on the driver, visible for `EXPERT`, defaulting to enabled, and controls compilation of debug tracing.

## Control flow
The selected config controls whether `ib_mthca.o` is built by the Makefile and whether `mthca_debug_level` and `mthca_dbg()` dynamic debug-style output are compiled in.

## State and persistence
Kconfig state persists in the kernel build configuration. At runtime, the debug option enables a `debug_level` module parameter/sysfs setting used by logging macros.

## Dependencies and integration points
It integrates with the kernel RDMA driver menu, PCI dependency resolution, and `mthca_dev.h` debug macro definitions.

## Risks
Defaulting debug support to `y` under the driver increases code size and leaves verbose paths present unless distributions override it. Missing the PCI dependency would allow invalid builds, but this file declares it.

## Test signals
Build test the driver as `y`, `m`, and disabled; build with and without `CONFIG_INFINIBAND_MTHCA_DEBUG`; verify `debug_level` is present only in debug builds and that `ib_mthca.o` is not built when the tristate is off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/Makefile -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/Makefile

## Purpose
`Makefile` defines how the mthca driver is linked into the kernel build when `CONFIG_INFINIBAND_MTHCA` is selected.

## Important APIs, types, and functions
It adds `ib_mthca.o` under `obj-$(CONFIG_INFINIBAND_MTHCA)` and composes that object from core files including main, command, profile, reset, allocator, EQ, PD, CQ, MR, QP, AV, multicast, MAD, provider, memfree, UAR, SRQ, and catastrophic-error support.

## Control flow
Kbuild compiles the listed objects and links them into `ib_mthca.o`; module or built-in behavior follows the Kconfig tristate.

## State and persistence
The file has no runtime state. It persists the build graph for the driver and determines which source files must remain ABI-compatible at link time.

## Dependencies and integration points
It integrates all mthca implementation units and depends on Kbuild conventions and `CONFIG_INFINIBAND_MTHCA` from Kconfig.

## Risks
Omitting a source file would produce unresolved symbols or missing runtime functionality. Reordering has little effect for normal C objects, but adding new driver subsystems requires updating this list.

## Test signals
Run mthca compile builds as module and built-in, confirm all listed objects are compiled, and verify no unresolved symbols when feature options such as debug or MSI support vary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_allocator.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_allocator.c

## Purpose
`mthca_allocator.c` provides shared allocation primitives for the mthca driver: bitmap-backed numeric resource IDs, lazily allocated pointer arrays, and DMA queue buffers registered as driver memory regions.

## Important APIs, types, and functions
`mthca_alloc_init()`, `mthca_alloc()`, `mthca_free()`, and `mthca_alloc_cleanup()` manage power-of-two ID spaces with reserved low entries and wrapped top bits. `mthca_array_init/get/set/clear/cleanup()` stores pointers in on-demand pages for CQ/QP/SRQ lookup tables. `mthca_buf_alloc()` and `mthca_buf_free()` allocate direct or page-list DMA buffers, build a DMA address list, and register it through `mthca_mr_alloc_phys()`.

## Control flow
ID allocation scans from `last`, wraps at `max`, advances `top` to avoid stale handles, and marks bits under a spinlock. Pointer arrays allocate pages with `GFP_ATOMIC` because callers hold locks. Buffer allocation chooses one coherent allocation for small queues or page-by-page coherent allocations for larger queues, then registers the physical list as an HCA MR; failure unwinds through `mthca_buf_free()`.

## State and persistence
Persistent driver state includes allocation bitmaps, generation-like high bits in allocated IDs, lazy array pages and their used counts, coherent DMA buffers, DMA mappings, and MRs visible to the HCA while queues are active.

## Dependencies and integration points
The file depends on Linux bitmap/slab/DMA APIs, `mthca_dev.h`, memory-region allocation in `mthca_mr.c`, and driver PDs. CQ, QP, SRQ, UAR, PD, AV, and MCG tables use these primitives.

## Risks
`mthca_free()` trusts callers not to double-free; a double clear can corrupt allocation state. `mthca_array_clear()` decrements before validating and only logs negative refcounts. Buffer direct-mode alignment splitting must match DMA address alignment, and error unwinds pass `mr = NULL` before registration completes. Large allocation paths need complete cleanup on partial page allocation.

## Test signals
Test power-of-two validation, reserved ID handling, ID wrap/top masking, exhaustion, double-free detection under debug, lazy array set/clear races under external locking, direct versus page-list buffer allocation, MR registration failure injection, and DMA cleanup under KASAN/dma-debug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_allocator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_av.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_av.c

## Purpose
`mthca_av.c` manages UD address vectors and static-rate conversion for Tavor and mem-free Arbel/Sinai devices.

## Important APIs, types, and functions
`struct mthca_av` is the hardware AV layout. `mthca_rate_to_ib()` and `mthca_get_rate()` translate between mthca static-rate encodings and RDMA `enum ib_rate`, with separate Tavor and mem-free formulas. `mthca_create_ah()`, `mthca_destroy_ah()`, `mthca_read_ah()`, `mthca_ah_query()`, `mthca_ah_grh_present()`, `mthca_init_av_table()`, and `mthca_cleanup_av_table()` implement AH lifecycle and table setup.

## Control flow
AH creation chooses kmalloc AVs for mem-free devices, on-HCA DDR AV slots for Tavor when allowed, or DMA-pool PCI memory as fallback. It fills port, PD, DLID/path bits, SL, static rate, GRH fields, and qkey-related data, then copies on-HCA AVs to mapped DDR space. Query/read paths reconstruct RDMA AH attributes or UD headers for non-on-HCA AVs. Table init creates an ID allocator, DMA pool, and optional DDR mapping.

## State and persistence
AH state persists in `struct mthca_ah`: allocation type, AV pointer or HCA DMA/DDR address, and key. Tavor can persist AV contents in HCA-attached DDR; PCI-pool AVs persist in coherent DMA memory; mem-free AVs are normal kernel memory used during posting.

## Dependencies and integration points
It depends on RDMA AH helpers, port active rate cached by `mthca_mad.c`, PD local DMA lkey, PCI BAR4 DDR mapping, DMA pools, and send WQE construction in QP code.

## Risks
Fallback from on-HCA allocation must free partially allocated indexes and temporary AV memory correctly. `mthca_read_ah()` and `mthca_ah_query()` intentionally reject on-HCA AVs, limiting observability. Rate conversion depends on old firmware quirks and `stat_rate_support`; wrong conversion can silently misprogram packet pacing. GRH gid-index computation assumes table length and port numbering are valid.

## Test signals
Test AH creation/destruction on mem-free, Tavor with visible DDR, Tavor with hidden DDR, exhausted DDR AV table fallback, DMA pool allocation failure, GRH and non-GRH AVs, AH query/read behavior, static-rate conversion for old firmware support masks, and repeated create/destroy under dma-debug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_av.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_catas.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_catas.c

## Purpose
`mthca_catas.c` polls the firmware catastrophic-error buffer, dispatches fatal device events, logs diagnostic words, and optionally schedules PCI-level device restart.

## Important APIs, types, and functions
`mthca_start_catas_poll()` maps the catastrophic buffer and starts a timer. `poll_catas()` scans for nonzero error words. `handle_catas()` marks the device inactive, dispatches `IB_EVENT_DEVICE_FATAL`, decodes error type, logs the buffer, and queues reset work unless `catas_reset_disable` is set. `catas_reset()` restarts queued devices under `mthca_device_mutex`. `mthca_stop_catas_poll()`, `mthca_catas_init()`, and `mthca_catas_cleanup()` manage timer, list, and workqueue lifecycle.

## Control flow
Probe code starts polling after firmware reports the catastrophic buffer address. The timer runs every five seconds. On first detected error, the device is marked inactive and added to a global reset list; ordered work removes devices from the list and calls `__mthca_restart_one()`.

## State and persistence
State includes per-device mapped MMIO buffer address/size, timer, list node, global reset list, global spinlock, ordered workqueue, and module parameter `catas_reset_disable`. Firmware persists the error words until reset or cleanup.

## Dependencies and integration points
It depends on firmware data collected by `mthca_QUERY_FW()`, PCI BAR0 mapping, RDMA event dispatch, main-driver restart/remove/probe code, and global device mutex serialization.

## Risks
`mthca_stop_catas_poll()` unconditionally `list_del()`s the device list node after timer deletion; correctness depends on initialization and reset-list state. Restart invalidates `dev` while work still holds only the PCI pointer after the call. Fatal event dispatch races with user verbs and teardown. Polling interval means detection is delayed.

## Test signals
Inject catastrophic buffer words of each type, verify fatal IB event delivery, logging, no-reset module parameter behavior, successful and failed restart, remove while timer/reset work is pending, repeated catastrophic detections, and lockdep coverage around `mthca_device_mutex` plus `catas_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_catas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_cmd.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_cmd.c

## Purpose
`mthca_cmd.c` implements the firmware command interface for mthca. It posts commands through the HCR or optional firmware command doorbell page, waits by polling or EQ command events, manages command mailboxes, maps firmware/ICM memory, queries capabilities, initializes HCA/IB ports, and wraps resource state transitions for MPT, MTT, EQ, CQ, SRQ, QP, MAD, and multicast objects.

## Important APIs, types, and functions
Core internals include `mthca_cmd_post_hcr()`, `mthca_cmd_post_dbell()`, `mthca_cmd_poll()`, `mthca_cmd_wait()`, `mthca_cmd_box()`, `mthca_cmd_imm()`, and `mthca_status_to_errno()`. Lifecycle APIs are `mthca_cmd_init()`, `mthca_cmd_use_events()`, `mthca_cmd_use_polling()`, and `mthca_cmd_cleanup()`. Mailboxes are allocated by `mthca_alloc_mailbox()`. Public wrappers include `mthca_SYS_EN/DIS`, `QUERY_FW`, `ENABLE_LAM`, `QUERY_DDR`, `QUERY_DEV_LIM`, `QUERY_ADAPTER`, `INIT_HCA`, `INIT_IB`, `SET_IB`, ICM map/unmap commands, resource `SW2HW/HW2SW` commands, `mthca_MODIFY_QP()`, `mthca_MAD_IFC()`, MGM commands, and `mthca_NOP()`.

## Control flow
Before EQ setup, callers use polling mode: post HCR, wait for GO bit to clear, read status/out parameter. After EQ setup, `mthca_cmd_use_events()` allocates token contexts and holds the polling semaphore; commands reserve a context, post with event bit, sleep for completion, and are completed by `mthca_cmd_event()` from EQ processing. Higher wrappers allocate mailboxes, encode firmware command layouts with `MTHCA_PUT`, issue the opcode, decode outputs with `MTHCA_GET`, and free mailboxes. Mapping commands batch ICM chunks into mailbox entries.

## State and persistence
Driver state includes mapped HCR, command DMA pool, HCR mutex, polling and event semaphores, token contexts, command flags, optional doorbell-page mapping, and firmware-discovered limits. Persistent device state includes firmware execution, LAM state, mapped firmware/ICM/aux memory, initialized HCA and IB ports, and hardware object ownership after SW2HW/HW2SW transitions.

## Dependencies and integration points
It depends on PCI MMIO, DMA pools, completions, semaphores, EQ command events from `mthca_eq.c`, mailbox layout macros from `mthca_dev.h`, memfree ICM helpers, RDMA MAD structures, and every table manager that needs firmware object transitions.

## Risks
Timeouts are coarse 60-second waits because firmware can be starved. Late completions are ignored by token mismatch but still imply firmware made progress after callers timed out. Event-mode teardown drains semaphores and assumes no active users remain. Doorbell command posting is optional and gated by firmware plus module parameter. Many command layouts use hard-coded offsets; mistakes silently corrupt firmware requests. `mthca_DISABLE_LAM()` calls `CMD_SYS_DIS`, which is notable because a separate `CMD_DISABLE_LAM` constant exists.

## Test signals
Exercise polling and event modes, HCR busy timeout, command event completion, late completion after timeout, status-to-errno mapping, mailbox allocation failure, firmware doorbell mapping, QUERY_FW parsing for Tavor and Arbel, ICM map batching, INIT_HCA endianness flags, QP state transition matrix, MAD_IFC with and without WC/GRH, and teardown while commands are quiesced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_cmd.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_cmd.h

## Purpose
`mthca_cmd.h` declares the firmware command ABI and shared data structures used by mthca initialization, resource management, QP/CQ/SRQ transitions, MAD handling, and multicast operations.

## Important APIs, types, and functions
It defines command status codes, QP transition identifiers, device-limit feature flags, `MTHCA_MAILBOX_SIZE`, `struct mthca_mailbox`, `struct mthca_dev_lim`, `struct mthca_adapter`, `struct mthca_init_hca_param`, `struct mthca_init_ib_param`, and `struct mthca_set_ib_param`. It declares command lifecycle functions, mailbox allocation, firmware/system commands, ICM mapping, resource SW2HW/HW2SW commands, QP modify/query, special QP config, `mthca_MAD_IFC()`, MGM commands, and `mthca_NOP()`.

## Control flow
Callers allocate mailboxes, fill one of the declared parameter structures or hardware context buffers, call the relevant wrapper, and inspect returned output buffers or immediate values. The implementation selects polling or event completion based on command state.

## State and persistence
The header describes firmware-owned state but stores none itself. Structures mirror persistent hardware capabilities and initialization parameters such as resource table bases, log sizes, port GUIDs, capability masks, and limits.

## Dependencies and integration points
It depends on RDMA verbs types and is included by main setup, EQ/CQ/QP/SRQ/MR/MCG/MAD modules. It is the compile-time contract for `mthca_cmd.c`.

## Risks
Firmware status and layout definitions are ABI-sensitive. Typos in status meanings or structure fields can mislead callers. The comment typo "unallocaterd" is harmless, but the command declarations are broad enough that any signature drift would break many subsystems.

## Test signals
Compile all users, validate command wrapper prototypes against implementations, verify QP transition enums match `mthca_MODIFY_QP()`, and test device-limit parsing against known firmware dumps for Tavor, Arbel native, Arbel compatibility, and Sinai.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_config_reg.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_config_reg.h

## Purpose
`mthca_config_reg.h` centralizes PCI BAR0 register offsets and sizes used for command, event, interrupt-clear, and EQ consumer-index MMIO mappings.

## Important APIs, types, and functions
It defines `MTHCA_HCR_BASE/SIZE`, `MTHCA_ECR_BASE/SIZE`, `MTHCA_ECR_CLR_BASE/SIZE`, `MTHCA_MAP_ECR_SIZE`, `MTHCA_CLR_INT_BASE/SIZE`, and `MTHCA_EQ_SET_CI_SIZE`.

## Control flow
`mthca_cmd.c` maps the HCR using the HCR constants. `mthca_eq.c` maps interrupt clear, Tavor ECR/ECR clear, and Arbel EQ set-CI regions using these constants or firmware-provided bases masked into BAR0.

## State and persistence
No runtime state is stored. These constants represent persistent hardware register layout expectations.

## Dependencies and integration points
The header is included by command, EQ, and main code and depends only on the hardware programming model.

## Risks
Incorrect offsets or sizes cause MMIO writes to the wrong device register, which can hang command submission or interrupt handling. The fixed sizes assume supported HCA generations keep these register windows compatible.

## Test signals
Probe Tavor and Arbel devices, verify HCR command posting, legacy interrupt clear/ECR handling, Arbel EQ set-CI writes, and ioremap failure paths for each mapped range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_config_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_cq.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_cq.c

## Purpose
`mthca_cq.c` implements completion queue allocation, arming, polling, CQE decoding, resize handoff, QP completion cleanup, and CQ event delivery for mthca.

## Important APIs, types, and functions
Important layouts are `struct mthca_cq_context`, `struct mthca_cqe`, and `struct mthca_err_cqe`. Public APIs include `mthca_init_cq()`, `mthca_free_cq()`, `mthca_poll_cq()`, `mthca_tavor_arm_cq()`, `mthca_arbel_arm_cq()`, `mthca_cq_completion()`, `mthca_cq_event()`, `mthca_cq_clean()`, `mthca_cq_resize_copy_cqes()`, `mthca_alloc_cq_buf()`, `mthca_free_cq_buf()`, and table init/cleanup. Internal helpers read CQEs from direct or page-list buffers, test ownership, update consumer indexes, and translate error syndromes.

## Control flow
CQ creation allocates a CQN, maps mem-free ICM and doorbell records when needed, allocates kernel CQ buffers, fills a CQ context, issues `SW2HW_CQ`, publishes the CQ in the lookup array, and initializes the consumer index. Completion events increment arm sequence and invoke the RDMA CQ completion handler. Polling repeatedly consumes software-owned CQEs, locates the QP, derives WR IDs from SQ/RQ/SRQ state, updates WQ tails, translates success or error CQEs into `ib_wc`, returns ownership to hardware, and writes consumer index updates. Freeing transitions the CQ back to software, removes it from the table, synchronizes IRQs, waits for event refs, and releases buffers, DBs, ICM refs, and CQN.

## State and persistence
State includes CQ number, CQ buffer/MR, consumer index, arm sequence, resize buffer state, refcount/waitqueue, kernel/user ownership, doorbell records, and table array entries. Hardware persists CQ context, producer state, CQE ownership bits, and notification state.

## Dependencies and integration points
It depends on command wrappers, allocator/buffer MR helpers, memfree table/doorbell helpers, QP and SRQ tables, RDMA CQ handlers, EQ completion/error events, and architecture MMIO/barrier helpers.

## Risks
CQ polling is concurrency-sensitive. QP lookup assumes QP removal locks CQs. Error CQE handling for Tavor may rewrite CQEs instead of freeing them. Resize swaps buffers only after the old buffer appears empty. Refcounting must prevent event callbacks from racing CQ free. Consumer-index updates differ between Tavor doorbells and Arbel doorbell records, making barriers critical.

## Test signals
Test kernel/user CQ create/free, mem-free and Tavor modes, CQ polling for send/recv/RDMA/atomic/immediate completions, every error syndrome mapping, SRQ receive completions and cleanup, CQ overrun/access-violation async events, arm solicited/all modes, resize while completions exist, QP reset cleanup, IRQ synchronization during free, and KASAN/lockdep stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_cq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_dev.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_dev.h

## Purpose
`mthca_dev.h` is the central private header for the mthca driver. It defines driver identity, capability flags, hardware constants, shared state structures, logging/access macros, and cross-module function prototypes.

## Important APIs, types, and functions
Key types include `mthca_cmd`, `mthca_limits`, `mthca_alloc`, `mthca_array`, resource tables for UAR/PD/MR/EQ/CQ/SRQ/QP/AV/MCG, `mthca_catas_err`, and the top-level `struct mthca_dev`. It defines hardware opcodes, flags such as `MTHCA_FLAG_MEMFREE`, `MTHCA_FLAG_MSI_X`, and `MTHCA_FLAG_SRQ`, EQ indexes, object sizes, `MTHCA_GET`/`MTHCA_PUT` endian helpers, logging macros, `to_mdev()`, and `mthca_is_memfree()`.

## Control flow
All implementation files include this header to share the top-level device object. Probe fills `mthca_dev`, setup initializes its resource tables in order, event and command paths consult table fields, and teardown unwinds the same embedded state.

## State and persistence
`struct mthca_dev` persists runtime driver state for the life of a PCI device: `ib_device`, PCI pointer, flags, firmware/DDRx information, mapped MMIO bases, command state, resource limits, all object tables, catastrophic polling state, driver UAR/PD/MR, MAD agents, SM AHs, cached port rates, and active flag.

## Dependencies and integration points
It includes provider and doorbell headers and depends on Linux PCI/DMA/timer/mutex/list/semaphore APIs plus RDMA core types. It is the nexus connecting command, memory, queue, MAD, provider, and main modules.

## Risks
Because this header exposes many internals, changes have broad blast radius. `MTHCA_GET`/`MTHCA_PUT` rely on exact field sizes and offsets. Table sizes and masks must remain powers of two for allocators. `active` and catastrophic-reset state are shared across async paths. Logging macros compile away in non-debug builds, so side effects in debug arguments would be unsafe.

## Test signals
Full driver build coverage is the primary signal. Runtime tests should cover Tavor/mem-free flag paths, resource-table init and cleanup ordering, endian helpers against known firmware buffers, debug and non-debug builds, catastrophic restart, and all modules using the shared prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_doorbell.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_doorbell.h

## Purpose
`mthca_doorbell.h` defines doorbell register offsets and architecture-specific helpers for 64-bit MMIO doorbells and two-word host doorbell records.

## Important APIs, types, and functions
Offsets include `MTHCA_RD_DOORBELL`, `MTHCA_SEND_DOORBELL`, `MTHCA_RECEIVE_DOORBELL`, `MTHCA_CQ_DOORBELL`, and `MTHCA_EQ_DOORBELL`. On 64-bit systems, doorbell locking macros compile to no-ops and helpers use raw 64-bit writes. On 32-bit systems, the header declares/initializes a spinlock and serializes two 32-bit writes. `mthca_write_db_rec()` writes host-memory doorbell records with the required ordering.

## Control flow
Queue code builds high/low doorbell dwords and calls `mthca_write64()` against the mapped kernel access region. CQ/EQ/receive paths write host doorbell records before ringing MMIO doorbells where required.

## State and persistence
The header itself stores no state. On 32-bit builds it causes `struct mthca_dev` to include a doorbell spinlock. Device-visible persistent effects are MMIO doorbell writes and host doorbell record updates observed by hardware.

## Dependencies and integration points
It depends on Linux types, endian conversion, MMIO raw write functions, memory barriers, and `BITS_PER_LONG`. It is included by `mthca_dev.h` and used throughout QP, CQ, and EQ paths.

## Risks
Doorbell ordering is critical. On 32-bit systems, missing serialization can interleave high/low dwords from different doorbells. On all systems, missing barriers can let descriptor writes become visible after the doorbell. Raw writes intentionally avoid byteswapping beyond explicit conversion, so caller dword order matters.

## Test signals
Compile and sparse-test 32-bit and 64-bit builds, exercise send/receive/CQ/EQ doorbells under stress, run lockdep for 32-bit lock usage, and validate host doorbell record ordering with hardware or MMIO tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_doorbell.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_eq.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_eq.c

## Purpose
`mthca_eq.c` implements event queues, interrupt handlers, event decoding, EQ creation/free, EQ register mapping, and optional MSI-X vector setup for mthca.

## Important APIs, types, and functions
Important layouts are `struct mthca_eq_context` and `struct mthca_eqe`. Public APIs include `mthca_init_eq_table()`, `mthca_cleanup_eq_table()`, `mthca_map_eq_icm()`, and `mthca_unmap_eq_icm()`. Internal handlers include `mthca_eq_int()`, Tavor/Arbel legacy and MSI-X interrupt handlers, `mthca_create_eq()`, `mthca_free_eq()`, EQ CI update helpers, notification request helpers, and `port_change()`.

## Control flow
Initialization allocates an EQ number allocator, maps interrupt/EQ registers, creates completion, async, and command EQs with spare entries, requests either one shared IRQ or three MSI-X IRQs, maps async and command event masks to their EQs, and arms all queues. Interrupt handlers clear interrupt state, process software-owned EQEs, dispatch completion, QP, SRQ, CQ, command, port, and warning events, return EQEs to hardware, update consumer indexes, and rearm notifications. Cleanup frees IRQs, unmaps event masks, transitions EQs back to software, frees DMA pages/MRs, unmaps registers, and destroys the allocator.

## State and persistence
State includes EQ arrays in `dev->eq_table`, EQ numbers/masks, page-list DMA buffers, MR registrations, consumer indexes, IRQ names/vectors, mapped clear/ECR/arm/set-CI registers, ICM page mapping for mem-free EQ contexts, and arm masks. Hardware persists EQ contexts, event masks, owner bits, and interrupt routing.

## Dependencies and integration points
It depends on command wrappers, CQ/QP/SRQ event callbacks, command completion callbacks, memfree ICM mapping, PCI IRQ/MSI-X APIs, MMIO register constants, doorbell helpers, and RDMA event dispatch.

## Risks
Interrupt handling must update owner bits and consumer indexes with strict barriers or hardware can overwrite entries incorrectly. Event mask mapping failures are logged but not fatal, reducing observability. CQ disarm only applies to Tavor. MSI-X fallback is coordinated by main through a NOP interrupt test. Free paths must quiesce IRQs before releasing EQ memory.

## Test signals
Test legacy INTx and MSI-X modes, Tavor and Arbel interrupt handlers, command event completion, CQ completion storms, async QP/CQ/SRQ/port events, EQ overflow warnings, MAP_EQ failures, mem-free EQ ICM mapping/unmapping, IRQ request failure unwind, and cleanup with pending interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_eq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_mad.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_mad.c

## Purpose
`mthca_mad.c` integrates the driver with RDMA management datagrams. It forwards supported MADs to firmware through `MAD_IFC`, snoops subnet-management changes, forwards locally generated traps to the subnet manager, maintains SM address handles, and registers MAD send agents.

## Important APIs, types, and functions
Public APIs are `mthca_process_mad()`, `mthca_create_agents()`, and `mthca_free_agents()`. Helpers include `mthca_update_rate()`, `update_sm_ah()`, `smp_snoop()`, `node_desc_override()`, `forward_trap()`, and `send_handler()`.

## Control flow
MAD processing filters by management class and method. Supported SMP, PMA, and Mellanox vendor MADs are sent to firmware with optional key-check bypass flags and WC/GRH context. Successful SMP SETs are snooped to update cached port rate, SM AH, client-reregister, LID-change, and P_Key-change events. Node description GET responses are overridden with the kernel `ib_device` node description. Locally generated traps are posted via the registered SMI/GSI MAD agent using the cached SM AH.

## State and persistence
State includes per-port SMI/GSI send agents, cached SM AHs, `sm_lock`, and cached active port rates in `dev->rate[]`. Firmware persists management counters and port state; the driver synthesizes RDMA core events from observed MADs.

## Dependencies and integration points
It depends on RDMA MAD/SMP/SMI APIs, AH creation/destruction from `mthca_av.c`, command `mthca_MAD_IFC()`, port query callbacks, RDMA event dispatch, and provider registration that hooks `mthca_process_mad()`.

## Risks
Filtering must avoid sending unsupported SMInfo/vendor SMPs to firmware. Trap forwarding relies on the device not using AH after post, explicitly noted as spec-noncompliant but device-specific. SM AH replacement happens under spinlock while AH destroy is called. `mthca_free_agents()` unregisters `agent` values without a null check after assignment, depending on successful creation or cleanup ordering.

## Test signals
Test SMP GET/SET/TRAP_REPRESS, PMA and vendor GET/SET, unsupported classes/methods, BAD_MKEY/BKEY ignore flags, PortInfo LID change and client-reregister events, P_Key change events, node-desc override, local trap forwarding with and without SM AH, agent registration failure unwind, and port rate update failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_mad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_main.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_main.c

## Purpose
`mthca_main.c` is the top-level PCI/module driver for Mellanox Tavor, Arbel, and Sinai InfiniBand HCAs. It validates module parameters, probes PCI devices, resets and initializes firmware/HCA resources, registers the RDMA device, creates MAD agents, handles MSI-X fallback, removes devices, and supports catastrophic-error restart.

## Important APIs, types, and functions
Module parameters control debug, MSI-X, PCI tuning, and resource profile sizes. Major helpers include `mthca_tune_pci()`, `mthca_dev_lim()`, `mthca_init_tavor()`, `mthca_load_fw()`, `mthca_init_icm()`, `mthca_init_arbel()`, `mthca_close_hca()`, `mthca_init_hca()`, `mthca_setup_hca()`, `mthca_enable_msi_x()`, `__mthca_init_one()`, `__mthca_remove_one()`, `__mthca_restart_one()`, profile validation helpers, and module init/exit. The PCI ID table maps device IDs to Tavor, Arbel compatibility, Arbel native, or Sinai flags.

## Control flow
Module init validates profile parameters, initializes catastrophic-error infrastructure, and registers the PCI driver. Probe enables PCI, validates BARs, requests regions, sets DMA masks and segment size, allocates `mthca_dev`, resets hardware, initializes the command interface, optionally tunes PCI, initializes firmware/HCA differently for Tavor or mem-free devices, warns on old firmware, tries MSI-X, sets up UAR/PD/MR/EQ/CQ/SRQ/QP/AV/MCG tables, switches commands to event mode, verifies command interrupts with NOP, registers the RDMA device, creates MAD agents, stores drvdata, and marks active. Remove reverses agents, RDMA registration, IB ports, tables, command mode, EQs, PD/MR/UAR, firmware state, command interface, IRQ vectors, PCI regions, and device allocation.

## State and persistence
Persistent runtime state lives in `mthca_dev`: firmware version, board ID, HCA type flags, limits, mapped resources, resource tables, IRQ vectors, driver PD/MR/UAR, MAD agents, and active flag. Device persistent state includes firmware loaded into ICM, mapped context tables, initialized HCA/ports, event masks, and hardware object ownership until closed.

## Dependencies and integration points
It integrates Linux PCI and module frameworks, RDMA core registration/provider code, command interface, profile builder, reset code, memfree ICM management, all table managers, MAD agent handling, catastrophic reset worker, MSI-X APIs, and DMA mapping.

## Risks
Initialization has a deep failure tree where unwind order must exactly mirror setup. MSI-X fallback depends on detecting `-EBUSY` from the NOP interrupt test. Tavor and Arbel resource models diverge significantly. Parameter correction silently rounds values to powers of two. Catastrophic restart removes and reinitializes under a global mutex, invalidating old device pointers. Remove closes IB ports after unregistering the RDMA device, so callbacks must already be quiesced.

## Test signals
Test probe/remove for every PCI ID class, BAR validation failures, DMA mask failure, reset failure, firmware query/load/init failures, old firmware warnings, MSI-X success and fallback, NOP interrupt failure, table init unwind at each stage, RDMA registration failure, MAD agent failure, catastrophic restart, module parameter validation, Tavor versus Arbel native/compat/Sinai paths, and repeated load/unload under fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_main.c -->
