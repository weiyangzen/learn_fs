# Research: subset-b-005964

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/devlink.h -->
# sources/distributed-fs/ceph-client/include/trace/events/devlink.h

## Purpose
Defines the `devlink` tracepoint surface for network device-management diagnostics when `CONFIG_NET_DEVLINK` is enabled, plus small no-op stubs for selected trace calls when devlink support is compiled out. The header records hardware messages, hardware errors, health-reporter transitions, aborted recovery attempts, and packet trap reports.

## APIs, Control Flow, and State
The exported trace call sites are generated from `TRACE_EVENT()` declarations: `devlink_hwmsg`, `devlink_hwerr`, `devlink_health_report`, `devlink_health_recover_aborted`, `devlink_health_reporter_state_update`, and `devlink_trap_report`. Events capture stable device identity through `devlink_bus_name()`, `devlink_dev_name()`, and `devlink_dev_driver_name()`. `devlink_hwmsg` copies an arbitrary byte buffer into a dynamic trace array; health events copy reporter names, messages, state, and recovery timing; trap reports copy trap/group names and the optional input netdev name. The header itself persists no runtime state beyond trace buffers owned by ftrace/perf; disabled builds only define empty `trace_devlink_hwmsg()` and `trace_devlink_hwerr()` helpers.

## Dependencies, Integration, Risks, and Tests
Depends on `<net/devlink.h>`, device helpers, `sk_buff`, `devlink_trap_metadata`, and the tracepoint generator. Integration points are devlink driver hardware command paths, health reporters, and packet trap delivery. Risks include tracing large or sensitive hardware buffers, passing metadata whose string fields are not valid for the tracepoint lifetime, assuming health/trap stubs exist in !`CONFIG_NET_DEVLINK` builds, and copying buffers from paths where trace overhead matters. Test signals include enabling `/sys/kernel/tracing/events/devlink/*`, exercising devlink health report/recover flows, generating traps, and building both devlink-enabled and disabled configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/devlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/dlm.h -->
# sources/distributed-fs/ceph-client/include/trace/events/dlm.h

## Purpose
Declares the Distributed Lock Manager tracepoint ABI. It covers local lock/unlock API entry and completion, AST/BAST callbacks, recovery communication (`rcom`) traffic, DLM protocol messages, userspace plock messages, and low-level send/receive return codes.

## APIs, Control Flow, and State
Important events are `dlm_lock_start/end`, `dlm_unlock_start/end`, `dlm_bast`, `dlm_ast`, `dlm_send_rcom`, `dlm_recv_rcom`, `dlm_send_message`, `dlm_recv_message`, `dlm_plock_read`, `dlm_plock_write`, `dlm_send`, and `dlm_recv`. Formatter macros decode lock flags (`DLM_LKF_*`), modes (`NL`, `CR`, `CW`, `PR`, `PW`, `EX`), status-block flags, lock-block flags, header commands, message versions, message types, and rcom types. The message tracepoints convert little-endian wire fields with `le*_to_cpu()` before storing them. Dynamic arrays carry resource names, message extras, and recovery payloads. The only state held by the header is event payload schema; live lockspace, lock block, and resource state remains in `fs/dlm`.

## Dependencies, Integration, Risks, and Tests
Depends on DLM public constants, `uapi/linux/dlm_plock.h`, tracepoint APIs, and the private `fs/dlm/dlm_internal.h`, making it tightly coupled to on-wire and in-memory DLM structures. Integration spans cluster lock acquisition, conversion, cancellation, unlock, recovery membership exchange, plock coordination, and transport send/receive paths. Risks are ABI drift between struct fields and trace formatting, excessive payload copying for resource names or variable message sections, kernel-lock error normalization in `dlm_lock_end`, and tracepoints reading partially initialized message data. Test signals include `dlm_tool`/cluster lock traffic with tracing enabled, recovery scenarios that emit rcoms, plock tests, endian-sensitive protocol checks, and compile coverage when DLM internals change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/dlm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/dma.h -->
# sources/distributed-fs/ceph-client/include/trace/events/dma.h

## Purpose
Defines tracepoints for the generic DMA mapping API. It makes map/unmap/allocation/free/synchronization behavior observable across single buffers, pages, scatter-gather tables, and DMA-coherent allocations.

## APIs, Control Flow, and State
The header declares event classes for `dma_map`, `dma_unmap`, `dma_alloc_class`, `dma_free_class`, `dma_sync_single`, and `dma_sync_sg`, then instantiates events such as `dma_map_phys`, `dma_unmap_phys`, `dma_alloc`, `dma_alloc_pages`, `dma_alloc_sgt`, `dma_alloc_sgt_err`, `dma_free`, `dma_free_pages`, `dma_free_sgt`, `dma_map_sg`, `dma_map_sg_err`, `dma_unmap_sg`, `dma_sync_single_for_cpu/device`, and `dma_sync_sg_for_cpu/device`. `TRACE_DEFINE_ENUM()` exports DMA directions, while helper formatters decode directions, DMA attributes, GFP flags, and scatterlist arrays. `dma_map_sg` caps traced arrays at `DMA_TRACE_MAX_ENTRIES` and records whether output was truncated. The header persists no mapping state; it only snapshots arguments and scatterlist-derived physical/DMA addresses at call time.

## Dependencies, Integration, Risks, and Tests
Depends on `<linux/dma-direction.h>`, `<linux/dma-mapping.h>`, scatterlist helpers, device names, and `trace/events/mmflags.h`. Integration points are DMA API instrumentation in architecture or core DMA mapping paths, IOMMU-backed devices, confidential-computing DMA attributes, and driver debugging. Risks include exposing physical/DMA addresses, allocating large dynamic arrays for scatterlists, inconsistent address semantics for unmap events that print physical addresses, and missing entries after the 128-entry cap. Test signals include DMA API debug runs, IOMMU map/unmap traces, SG mapping with more than 128 entries, cache sync paths, allocation/free pairing, and build checks as new `DMA_ATTR_*` bits are added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/dma_buf.h -->
# sources/distributed-fs/ceph-client/include/trace/events/dma_buf.h

## Purpose
Provides tracepoints for dma-buf lifetime, mapping, file-descriptor export/import, and device attachment operations. It is aimed at shared-buffer debugging across graphics, media, and accelerator drivers.

## APIs, Control Flow, and State
Three event classes model common payloads: `dma_buf` records exporter name, size, and backing inode; `dma_buf_attach_dev` adds attachment pointer, dynamic-attach flag, and device name; `dma_buf_fd` adds the file descriptor. Instances include `dma_buf_export`, `dma_buf_mmap_internal`, `dma_buf_mmap`, `dma_buf_put`, `dma_buf_dynamic_attach`, `dma_buf_detach`, `dma_buf_fd`, and `dma_buf_get`. `dma_buf_fd` uses `DEFINE_EVENT_CONDITION()` so failed fd installation with negative descriptors is not emitted. No persistent state is created here; the tracepoint payload snapshots `struct dma_buf`, `struct dma_buf_attachment`, and `struct device` fields.

## Dependencies, Integration, Risks, and Tests
Depends on `<linux/dma-buf.h>`, inode access through `dmabuf->file`, device names, and tracepoint macros. Integration points are dma-buf export/import, mmap, reference dropping, attachment setup/teardown, and fd lookup/creation paths. Risks include dereferencing partially constructed dma-bufs, stale or null `dmabuf->file`, tracing attachment pointers that can be reused, and assuming fd traces include failed negative-fd attempts. Test signals include dma-buf selftests, GPU/media buffer sharing workloads, fd leak diagnosis, mmap tracing, and attach/detach pairing under dynamic attachment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/dma_buf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/dma_fence.h -->
# sources/distributed-fs/ceph-client/include/trace/events/dma_fence.h

## Purpose
Declares dma-fence lifecycle and wait tracepoints used to diagnose synchronization between GPU, display, media, and other asynchronous DMA users.

## APIs, Control Flow, and State
The `dma_fence` event class emits driver name, timeline name, context, and sequence number from a `struct dma_fence`. It is instantiated as `dma_fence_emit`, `dma_fence_init`, `dma_fence_destroy`, `dma_fence_enable_signal`, `dma_fence_signaled`, `dma_fence_wait_start`, and `dma_fence_wait_end`. The header explicitly documents that calling sites must not race with signaling unless they hold `fence->lock`, have already checked not-signaled state, or are on the signaling path. It stores no state beyond trace event records.

## Dependencies, Integration, Risks, and Tests
Depends on `struct dma_fence` and its ops callbacks for driver/timeline strings. Integration points include fence initialization/destruction, signal enablement, signaling, emit paths, and wait begin/end accounting. Risks are use-after-free or stale ops if tracepoints are placed outside the documented locking rules, callback implementations that sleep or return unstable names, and incomplete wait pairing if error paths omit start/end calls. Test signals include GPU scheduler traces, dma-fence selftests, lockdep/KASAN around signaling races, wait latency analysis, and checking that context/seqno ordering matches expected timelines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/dma_fence.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/erofs.h -->
# sources/distributed-fs/ceph-client/include/trace/events/erofs.h

## Purpose
Defines EROFS filesystem tracepoints for lookup, inode loading, folio reads/readahead, and logical-to-physical block mapping.

## APIs, Control Flow, and State
Events are `erofs_lookup`, `erofs_fill_inode`, `erofs_read_folio`, `erofs_readahead`, `erofs_map_blocks_enter`, and `erofs_map_blocks_exit`. Formatting helpers print major/minor device and EROFS nid pairs, file type, block-map request flags (`FIEMAP`, `READMORE`, `FINDTAIL`), and resulting map flags (`MAPPED`, `META`, `PARTIAL_MAPPED`, `PARTIAL_REF`, `FRAGMENT`). Mapping entry captures logical address and requested length; exit adds physical address, physical length, result flags, and return code. The header stores no filesystem state; it snapshots inode fields and `struct erofs_map_blocks`.

## Dependencies, Integration, Risks, and Tests
Depends on EROFS inode helpers such as `EROFS_I()`, `erofs_iloc()`, `erofs_blknr()`, and map flag definitions supplied by including implementation files. Integration points are VFS lookup, inode fill from metadata, compressed or raw folio read paths, readahead, fiemap, and map-block resolution. Risks include formatter/header coupling to EROFS private definitions without direct includes, tracing invalid map structures on failed paths, and confusing raw-vs-compressed read interpretation. Test signals include mount/read workloads with trace events enabled, lookup of files/directories, fiemap over fragmented data, compressed-file readahead, and negative map return coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/erofs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/error_report.h -->
# sources/distributed-fs/ceph-client/include/trace/events/error_report.h

## Purpose
Declares a generic post-report tracepoint for kernel bug detectors. It lets tooling correlate the end of reports produced by KFENCE, KASAN, and WARN paths with a pseudo-unique report id.

## APIs, Control Flow, and State
The header defines `enum error_detector` with `ERROR_DETECTOR_KFENCE`, `ERROR_DETECTOR_KASAN`, and `ERROR_DETECTOR_WARN`, registers those enum values with `TRACE_DEFINE_ENUM()`, and maps them to strings via `show_error_detector_list()`. The `error_report_template` event class records detector and `unsigned long id`; `error_report_end` instantiates it and is documented as firing after the detector finishes printing the report. There is no persistence outside trace buffers.

## Dependencies, Integration, Risks, and Tests
Depends only on tracepoint infrastructure and callers in debugging subsystems. Integration points are KASAN reports, KFENCE reports, warning emission, and any log consumer that needs a structured marker after verbose text output. Risks include treating the id as globally unique when the comment only promises pseudo-uniqueness, adding new detectors without updating the enum/list pair, and emitting before report text is complete. Test signals include fault-injection reports for each detector, `tracefs` event decoding, enum format validation, and checking report-end ordering against console logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/error_report.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/exceptions.h -->
# sources/distributed-fs/ceph-client/include/trace/events/exceptions.h

## Purpose
Defines generic page-fault tracepoints under the `exceptions` trace system for user and kernel faults.

## APIs, Control Flow, and State
The `exceptions` event class takes a fault address, `struct pt_regs *`, and architecture error code. It records the faulting address, instruction pointer via `instruction_pointer(regs)`, and raw error code. `page_fault_user` and `page_fault_kernel` are the concrete events. Output uses `%ps` for symbolic address formatting where possible. The header has no persistent state and relies entirely on the exception handling path to classify user vs kernel faults correctly.

## Dependencies, Integration, Risks, and Tests
Depends on tracepoints, `struct pt_regs`, and architecture-provided `instruction_pointer()`. Integration points are architecture page fault handlers and MM diagnostics. Risks include arch-specific error-code interpretation not being decoded here, invalid or incomplete register frames, symbolization leaking kernel addresses depending on pointer restrictions, and fault-path overhead if enabled at high rate. Test signals include user and kernel fault injection, tracefs event enablement during page fault tests, architecture build coverage, and comparing emitted IP/address values with oops or perf samples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/exceptions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/ext4.h -->
# sources/distributed-fs/ceph-client/include/trace/events/ext4.h

## Purpose
Provides the comprehensive ext4 tracepoint ABI. It instruments inode lifecycle, write paths, delayed allocation, block allocation/freeing, multiblock allocator decisions, folio operations, fallocate/truncate/unlink, extent conversion/removal, extent status cache, fsmap, journal starts, trim, shutdown/error handling, fast commit/replay, superblock updates, and extent-moving operations.

## APIs, Control Flow, and State
The header defines enum exports and display helpers for buffer-head flags, extent-status bits, fallocate modes, fast-commit stop reasons, allocation criteria, map flags, mballoc flags, and free flags. Major event groups include inode operations (`ext4_free_inode`, `ext4_allocate_inode`, `ext4_evict_inode`, `ext4_mark_inode_dirty`), writeback (`ext4_write_begin/end`, `ext4_da_write_begin/end`, `ext4_writepages`, `ext4_da_write_folios_start/end`, `ext4_writepages_result`), folio operations, preallocation and mballoc (`ext4_mb_new_inode_pa`, `ext4_request_blocks`, `ext4_allocate_blocks`, `ext4_mballoc_alloc/prealloc`, discard/free events), delayed allocation reserve/release/update events, bitmap loading, fallocate/punch/zero range, unlink/truncate, map-block enter/exit for extent and indirect paths, extent loading/unwritten conversion/removal, extent-status insert/cache/remove/lookup/shrink, fsmap/getfsmap classes, error/shutdown, lazy inode table init, fast-commit commit/replay/stats/tracking/cleanup, `ext4_update_sb`, and `ext4_move_extent_enter/exit`. The header stores no filesystem state; it snapshots `inode`, `super_block`, `ext4_allocation_context`, `ext4_allocation_request`, `ext4_map_blocks`, `extent_status`, and fast-commit arguments into trace records.

## Dependencies, Integration, Risks, and Tests
Depends on ext4 private structures, jbd2 context, VFS inode/address-space state, buffer-head flags, extent status definitions, fsmap structs, and tracepoint infrastructure. Integration spans nearly every ext4 data and metadata mutation path, making it a debugging contract for allocator fragmentation, delayed allocation accounting, journaling credits, fast commit eligibility/fallback, fsync, trim, and extent surgery. Risks include schema drift when ext4 structs change, high overhead if verbose allocator/writeback events are enabled under load, leaking physical block layout, misinterpreting counters that are only snapshots, and missing event pairs on error paths. Test signals include xfstests ext4 groups, fast-commit replay tests, fallocate/punch/collapse/insert range tests, delayed allocation ENOSPC tests, mballoc fragmentation traces, fsmap/fiemap validation, trim/discard checks, and trace event format compile tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/ext4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/f2fs.h -->
# sources/distributed-fs/ceph-client/include/trace/events/f2fs.h

## Purpose
Declares the F2FS tracepoint ABI for lifecycle, writeback, checkpoint, GC, segment allocation, mapping, directory operations, direct I/O, discard/zone reset, extent caches, compression, iostat, latency, rw timing, and lock timing.

## APIs, Control Flow, and State
The header registers many enum values for block/data temperatures, curseg types, GC modes, request flags, checkpoint reasons and phases, extent types, shutdown modes, and compression algorithms. Common classes include `f2fs__inode`, `f2fs__inode_exit`, truncate classes, submit-folio/bio classes, folio classes, mmap classes, discard/reset-zone classes, dirty-inode sync, zip start/end, rw start/end, and priority update. Concrete events cover sync/iget/evict/new/unlink/drop/truncate, write iter, fadvise, `f2fs_map_blocks`, background/foreground GC begin/end and victim selection, lookup/rename/readdir/fallocate, direct I/O, block reservation, bio preparation/submission, write begin/end, writepage/readpage/read_folio/dirty, atomic-write replacement, mmap faults, writepages/readpages, checkpoint, discard and zone reset issue paths, flush, extent tree lookup/update/shrink/destroy, shutdown, compression/decompression start/end, `f2fs_iostat`, `f2fs_iostat_latency`, `f2fs_bmap`, `f2fs_fiemap`, data read/write timing, lock elapsed time, and block priority uplift/restore. State is not persisted by the header; it snapshots F2FS private structs such as `f2fs_sb_info`, `f2fs_io_info`, `extent_info`, `victim_sel_policy`, and `f2fs_map_blocks`.

## Dependencies, Integration, Risks, and Tests
Depends on F2FS private constants/structs, block-layer request flags, inode and address-space state, compression definitions, and tracepoints. Integration points cover F2FS mount runtime behavior across hot/cold data separation, log-structured vs SSR allocation, GC, checkpoint/recovery, discard/zone management, compression, and performance accounting. Risks include trace format drift as private enums change, high event volume in I/O-heavy workloads, exposing physical block and segment layout, conditional events hiding disabled bio paths, and misreading latency buckets without matching iostat configuration. Test signals include f2fs xfstests, GC/victim-selection stress, checkpoint/recovery tests, compression tests, zoned-device discard/reset coverage, direct-I/O and mmap tests, iostat latency validation, and trace format builds after enum changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/f2fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/fib.h -->
# sources/distributed-fs/ceph-client/include/trace/events/fib.h

## Purpose
Defines IPv4 FIB lookup tracing for route-decision diagnostics.

## APIs, Control Flow, and State
The single `fib_table_lookup` event records table id, lookup error, output/input interface indexes, protocol, DS field derived from `flowi4_dscp`, scope, flow flags, source/destination IPv4 addresses, optional TCP/UDP ports, selected device name, and IPv4 or IPv6 gateway from `struct fib_nh_common`. It stores IPv4 and IPv6 gateway slots so IPv4 lookups through common nexthop objects can show either address family. No route state is persisted by the header; it snapshots `struct flowi4` and selected nexthop data after lookup.

## Dependencies, Integration, Risks, and Tests
Depends on `skbuff`, netdevice names, `flowi4`, DSCP helpers, `ip_fib.h`, nexthop common structures, and tracepoints. Integration points are IPv4 route table lookup, policy/routing diagnostics, nexthop selection, and packet-flow debugging. Risks include null nexthop handling, only decoding ports for TCP/UDP, route changes after trace emission, and gateway arrays needing initialization on all branches. Test signals include route lookup tracing for connected, gateway, unreachable, TCP/UDP, and non-TCP flows; multipath/nexthop tests; DSCP/tos checks; and namespace-specific route scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/fib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/fib6.h -->
# sources/distributed-fs/ceph-client/include/trace/events/fib6.h

## Purpose
Defines IPv6 FIB lookup tracing for route diagnostics.

## APIs, Control Flow, and State
The `fib6_table_lookup` event records IPv6 table id, route error from `ip6_rt_type_to_error()`, output/input interfaces, flow label, traffic class, scope, flags, source and destination IPv6 addresses, TCP/UDP ports when applicable, protocol, route type, output device name, and gateway. It treats the namespace null route as an all-zero gateway and otherwise records `res->nh->fib_nh_gw6` when a nexthop exists. The header stores no routing state; it snapshots `struct fib6_result`, `struct fib6_table`, and `struct flowi6`.

## Dependencies, Integration, Risks, and Tests
Depends on IPv6 address helpers, `flowi6`, `ip6_fib.h`, namespace IPv6 null-entry state, netdevice names, and tracepoints. Integration points are IPv6 route lookup, policy routing diagnostics, nexthop and gateway resolution, and protocol/port-sensitive flows. Risks include leaving gateway contents undefined if a non-null route has no nexthop, only capturing ports for TCP/UDP, and interpreting route errors without full policy context. Test signals include IPv6 route lookup traces for local, gateway, unreachable, TCP/UDP and ICMPv6 flows, flow-label/tclass checks, netns null-route cases, and nexthop deletion races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/fib6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/filelock.h -->
# sources/distributed-fs/ceph-client/include/trace/events/filelock.h

## Purpose
Defines VFS file lock and lease tracepoints for POSIX locks, flock locks, open-file-description locks, leases, and lease conflict/break handling.

## APIs, Control Flow, and State
Format helpers decode `FL_*` flags and `F_RDLCK`/`F_WRLCK`/`F_UNLCK` types. `locks_get_lock_context` reports inode device/number, requested type, and lock context pointer. The `filelock_lock` class is instantiated as `posix_lock_inode`, `fcntl_setlk`, `locks_remove_posix`, and `flock_lock_inode`; it records lock pointer, blocker, owner, pid, flags, type, byte range, inode identity, and return code. The `filelock_lease` class is instantiated for lease break/delete/timeouts and records lease pointer, blocker, owner, flags, type, break time, and downgrade time. `generic_add_lease` captures inode read/write/open counts when adding a lease, and `leases_conflict` records both lease and breaker attributes plus conflict result. No lock state is owned here; the header snapshots `struct file_lock`, `struct file_lease`, inode counters, and contexts.

## Dependencies, Integration, Risks, and Tests
Depends on VFS inode/file-lock structures, device number helpers, atomic inode counters, and tracepoints. Integration points are `fcntl(F_SETLK*)`, flock, OFD locks, NFS/cluster lock layers using VFS helpers, lease acquisition/break, and lock context allocation. Risks include null lock handling differences across events, exposing owner pointers, stale pointer reuse after lock teardown, and interpreting byte ranges without knowing mandatory/advisory context. Test signals include locktests for POSIX/flock/OFD locks, blocking conflict scenarios, lease break and timeout tests, NFS lock integration, and tracing error returns for nonblocking locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/filelock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/filemap.h -->
# sources/distributed-fs/ceph-client/include/trace/events/filemap.h

## Purpose
Declares filemap and page-cache tracepoints for folio insertion/removal, page-cache range lookup/mapping, filemap faults, and writeback error sequence handling.

## APIs, Control Flow, and State
The `mm_filemap_op_page_cache` class backs `mm_filemap_delete_from_page_cache` and `mm_filemap_add_to_page_cache`, recording inode identity, device, folio PFN, page-cache index, and folio order. The range class backs `mm_filemap_get_pages` and `mm_filemap_map_pages`, recording address-space host identity and index range. `mm_filemap_fault` records a faulting mapping and index. `filemap_set_wb_err` records a mapping and errseq value; `file_check_and_advance_wb_err` records file pointer, inode identity, old errseq, and the file's new `f_wb_err`. Device selection falls back from `host->i_sb->s_dev` to `host->i_rdev` for special mappings. The header does not own page-cache or errseq state.

## Dependencies, Integration, Risks, and Tests
Depends on folio/page-cache structures, `address_space`, memcg-visible MM includes, device number helpers, and errseq APIs. Integration points are add/delete page-cache paths, buffered read fault handling, readahead/page-cache lookup, mmap fault mapping, and writeback error propagation to files. Risks include assuming `folio->mapping` and `mapping->host` are valid at trace time, offset calculations overflowing in unusual index ranges, and confusing per-mapping writeback errors with per-file advanced state. Test signals include buffered read/write tests with tracing, page-cache add/delete under reclaim, mmap fault tests, writeback error injection, special-file mapping coverage, and large folio order tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/filemap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/firewire.h -->
# sources/distributed-fs/ceph-client/include/trace/events/firewire.h

## Purpose
Defines high-level FireWire core tracepoints for asynchronous transactions, PHY packets, bus reset handling, self-ID packets, isochronous context allocation/lifecycle, packet queueing, and completion reporting.

## APIs, Control Flow, and State
The header provides bit-extraction helpers for async packet headers and PHY self-ID fields. Event classes cover async outbound initiation/completion, async inbound packets, bus reset arrangement, isochronous destroy/start/stop/flush/completion templates, and single-completion templates. Concrete events include async request/response outbound/inbound initiation/completion, PHY outbound/inbound, `bus_reset_initiate/schedule/postpone/handle`, `self_id_sequence`, isochronous outbound/inbound allocation and destruction, multiple-channel reporting, start/stop/flush/flush_completions, outbound and inbound queue events, outbound/inbound single completions, and inbound multiple completions. Conditional events suppress disabled or irrelevant isochronous traces. The header stores no FireWire state; it snapshots card index, transaction labels/codes, node IDs, offsets, rcodes, packet quadlets, bus-generation metadata, channel/speed/tag/sync fields, and context-completion causes.

## Dependencies, Integration, Risks, and Tests
Depends on FireWire core packet formats, isochronous context structures, tracepoint macros, and constants defined by FireWire headers or including translation units. Integration points are transaction layer send/receive, bus reset scheduling and handling, self-ID processing, and isochronous DMA queue/completion paths. Risks include packet-format drift, endian or quadlet-order mistakes, high trace volume for isochronous streaming, exposing bus topology/addresses, and conditional events hiding state when contexts are not enabled. Test signals include FireWire transaction tests, bus reset/self-ID traces, isochronous streaming under trace, PHY packet injection, completion cause coverage, and build checks after packet macro changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/firewire.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/firewire_ohci.h -->
# sources/distributed-fs/ceph-client/include/trace/events/firewire_ohci.h

## Purpose
Declares OHCI-1394 controller tracepoints for interrupt events and self-ID completion data.

## APIs, Control Flow, and State
`irqs` records a controller card index and an OHCI event bitmask, formatting notable bits such as self-ID completion, async request/response packets, transmit completions, isochronous RX/TX, posted write errors, cycle timer anomalies, register access failure, unrecoverable errors, and bus reset. `self_id_complete` records the card index, SelfIDCount register, and a dynamic array of self-ID receive quadlets sized by `ohci1394_self_id_count_get_size(reg)`. Helper macros decode self-ID error state, generation, receive generation, and timestamp; `cond_le32_to_cpu()` handles the big-endian header quirk before trace storage. No controller state is owned by the header.

## Dependencies, Integration, Risks, and Tests
Depends on OHCI1394 register constants and helper functions defined in `drivers/firewire/ohci.c` or nearby headers, plus tracepoint support. Integration points are OHCI interrupt handling and self-ID buffer completion after bus resets. Risks include dynamic-array sizing trusting register contents, endian quirk handling mistakes, reading empty self-ID buffers while formatting index zero, and losing interrupt sequencing if event bits are coalesced. Test signals include OHCI interrupt tracing during device activity, bus reset/self-ID completion tests, controllers with and without the big-endian header quirk, malformed self-ID error paths, and compile checks when OHCI bit definitions change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/firewire_ohci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/fs_dax.h -->
# sources/distributed-fs/ceph-client/include/trace/events/fs_dax.h

## Purpose
Defines filesystem DAX tracepoints for PMD/PTE faults, load-hole handling, PFN insertion, and DAX writeback ranges.

## APIs, Control Flow, and State
Event classes include `dax_pmd_fault_class`, `dax_pmd_load_hole_class`, `dax_pte_fault_class`, and `dax_writeback_range_class`. Instances are `dax_pmd_fault`, `dax_pmd_fault_done`, `dax_pmd_load_hole`, `dax_pmd_load_hole_fallback`, `dax_pte_fault`, `dax_pte_fault_done`, `dax_load_hole`, `dax_insert_pfn_mkwrite_no_entry`, `dax_insert_pfn_mkwrite`, `dax_writeback_range`, `dax_writeback_range_done`, and `dax_writeback_one`. Fault events record inode/device identity, VMA range, shared/private VMA mode, VM fault flags, fault address, page offset, max pgoff for PMD faults, and VM fault result flags. Load-hole events additionally record zero folio and radix entry pointers. Writeback events record pgoff ranges or a single pgoff/page length. The header owns no DAX radix or mapping state.

## Dependencies, Integration, Risks, and Tests
Depends on inode/VMA/vm_fault definitions, `FAULT_FLAG_TRACE`, `VM_FAULT_RESULT_TRACE`, device number helpers, and DAX implementation call sites. Integration points are fs-DAX mmap fault handling for PMD and PTE mappings, hole faults, PFN dirty/write faults, and writeback over persistent memory ranges. Risks include exposing DAX physical layout indirectly through pgoff ranges, tracing pointer values for zero folios/radix entries, interpreting result flags without fault retry context, and assuming PMD events fire on filesystems or hardware that only support PTE DAX. Test signals include DAX xfstests, mmap shared/private DAX faults, hole-fault fallback tests, pfn_mkwrite paths, writeback range tracing, and PMD-vs-PTE configuration coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/fs_dax.h -->
