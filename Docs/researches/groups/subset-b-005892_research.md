# subset-b-005892 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mm_types.h -->
# sources/distributed-fs/ceph-client/include/linux/mm_types.h

## Purpose
`mm_types.h` is the central Linux memory-management type contract for this tree. It defines the physical-page descriptors (`struct page`, `struct folio`, `struct ptdesc`), virtual memory descriptors (`struct vm_area_struct`, `struct vm_area_desc`, `struct mmap_action`), process address-space state (`struct mm_struct`), fault and pin flag enums, VMA/MM flag helpers, and iterator/accessor glue used by most MM, filesystem, driver, and architecture code.

## Important APIs, Types, And Functions
Important exported types include `memdesc_flags_t`, `struct page`, `struct encoded_page`, `swp_entry_t`, `softleaf_t`, `struct folio`, `struct ptdesc`, `struct vm_region`, `struct vm_userfaultfd_ctx`, `struct anon_vma_name`, `struct vma_numab_state`, `struct mmap_action`, `vma_flags_t`, `struct vm_area_desc`, `struct vm_area_struct`, `mm_flags_t`, `struct mm_struct`, `struct lru_gen_mm_list`, `struct vma_iterator`, `vm_fault_t`, `struct vm_special_mapping`, `enum fault_flag`, `zap_flags_t`, and `cydp_t`. Inline helpers cover encoded-page packing (`encode_page()`, `encoded_page_flags()`, `encoded_page_ptr()`, `encode_nr_pages()`, `encoded_nr_pages()`), page/folio/private conversion, page-table descriptor conversion (`ptdesc_page()`, `page_ptdesc()`), HugeTLB page-table share counts, VMA flag bitmap operations, MM flag word access, cpumask/CID flexible-array access, LRU generation hooks, VMA iterator initialization, and MMF legacy flag inheritance.

## Control Flow And State
The file is declarative but encodes major lifecycle rules. `struct page` overlays many users in a fixed union layout, while `struct folio` and `struct ptdesc` deliberately alias `struct page` and enforce offset compatibility with `static_assert()`. `struct vm_area_struct` records a single address range and its backing, reverse-map, userfaultfd, NUMA, PFNMAP, and optional per-VMA lock state. `struct mm_struct` owns the maple tree of VMAs, page-table root, counters, mmap lock, RSS counters, architecture context, notifier subscriptions, TLB flush state, KSM/LRU/CID extensions, and a flexible array holding CPU masks. State is persistent for the lifetime of pages, VMAs, and mms; most fields are guarded by locks named in comments (`mmap_lock`, page-table lock, RMAP locks, seqcounts, RCU, refcounts).

## Dependencies And Integration Points
Dependencies include `mm_types_task.h`, maple tree, rwsem, seqlock, percpu counters, cpumasks, RCU, workqueues, rseq, bitmap helpers, architecture `mmu.h`, and many config-specific MM subsystems. Integration points are broad: page allocator, slab, page cache, DAX, swap, migration, rmap, userfaultfd, drivers using `mmap_prepare`, NUMA balancing, TLB gather, page-fault handlers, get-user-pages/pin-user-pages, coredump policy, KSM, LRU generation, membarrier, futex private hashes, AIO, memcg, mmu notifiers, IOMMU, and architecture context switching.

## Risks And Test Signals
Risks are ABI/layout breakage in overlaid descriptors, refcount/mapcount misuse, stale VMA access without the right lock or RCU reference, incorrect VMA flag conversion during the bitmap transition, per-VMA lock sequence overflow assumptions, mis-sized flexible-array masks, and stale MMF inheritance. Test signals include MM build coverage under many config combinations, `static_assert()` layout checks, page/folio/refcount debug tests, mmap/fault/rmap/munmap stress, GUP and FOLL_PIN release tests, KSM/NUMA/LRU generation tests, coredump-filter tests, and lockdep/KCSAN/KASAN runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mm_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mm_types_task.h -->
# sources/distributed-fs/ceph-client/include/linux/mm_types_task.h

## Purpose
`mm_types_task.h` contains MM data types embedded in `struct task_struct` without forcing scheduler headers to include the much larger `mm_types.h`. It provides lightweight counters, page-fragment caches, batched TLB flush tracking, and lazy MMU state used by task and network/MM paths.

## Important APIs, Types, And Functions
The file defines resident set counter indexes (`MM_FILEPAGES`, `MM_ANONPAGES`, `MM_SWAPENTS`, `MM_SHMEMPAGES`, `NR_MM_COUNTERS`), `struct page_frag`, `struct page_frag_cache`, `struct tlbflush_unmap_batch`, and `struct lazy_mmu_state`. `ALLOC_SPLIT_PTLOCKS` determines whether page-table locks are allocated separately based on spinlock size. `PAGE_FRAG_CACHE_MAX_SIZE` and `PAGE_FRAG_CACHE_MAX_ORDER` size page-fragment cache allocation.

## Control Flow And State
There are no functions, but the structs define runtime state. `page_frag_cache` packs an encoded page pointer, pfmemalloc bit, order, current offset, and biased page count to reduce `_refcount` cacheline traffic during repeated fragment allocations. `tlbflush_unmap_batch` holds optional architecture batch state plus flags indicating whether a flush is required and whether a dirty writable PTE was unmapped. `lazy_mmu_state` tracks nesting of lazy MMU enable and pause sections.

## Dependencies And Integration Points
Dependencies include alignment/type headers, `asm/page.h`, and optionally `asm/tlbbatch.h`. Integration points include `task_struct`, RSS accounting in `mm_struct`, network page-fragment allocation, page-table locking policy, TLB unmap batching, and architecture-specific TLB flush code.

## Risks And Test Signals
Risks include counter order mismatch with `kernel/fork.c`, page-fragment integer width overflow on small systems, stale dirty writable TLB entries before I/O, and architecture batch semantics that fail the promised barrier/flush ordering. Test signals are RSS counter initialization checks, network fragment stress, high-order page fragment allocation tests, batched unmap/TLB shootdown tests, and architecture builds with and without `CONFIG_ARCH_WANT_BATCHED_UNMAP_TLB_FLUSH`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mm_types_task.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mman.h -->
# sources/distributed-fs/ceph-client/include/linux/mman.h

## Purpose
`mman.h` bridges user `mmap()`/`mprotect()` flags to kernel VMA flags and declares VM overcommit accounting helpers. It also provides architecture override points for protection validation, flag validation, and architecture-specific VMA flag calculation.

## Important APIs, Types, And Functions
Important symbols are `LEGACY_MAP_MASK`, `sysctl_overcommit_memory`, `vm_committed_as`, `vm_committed_as_batch`, `mm_compute_batch()`, `vm_memory_committed()`, `vm_acct_memory()`, `vm_unacct_memory()`, `arch_calc_vm_prot_bits()`, `arch_calc_vm_flag_bits()`, `arch_validate_prot()`, `arch_validate_flags()`, `_calc_vm_trans()`, `calc_vm_prot_bits()`, `calc_vm_flag_bits()`, `vm_commit_limit()`, and `arch_memory_deny_write_exec_supported()`.

## Control Flow And State
The control path is inline translation and accounting. `vm_acct_memory()` and `vm_unacct_memory()` update the global committed-address-space percpu counter using the SMP batch size. `calc_vm_prot_bits()` maps `PROT_READ`, `PROT_WRITE`, `PROT_EXEC`, and architecture pkey bits into `VM_*` flags. `calc_vm_flag_bits()` maps supported `MAP_*` bits such as grow-down, locked, sync, and stack/nohugepage into internal flags. Legacy or undefined architecture map flags default to zero so common code can mask them uniformly.

## Dependencies And Integration Points
The header depends on `fs.h`, `mm.h`, percpu counters, atomics, and UAPI `linux/mman.h`. It integrates with `mmap()`, `mprotect()`, overcommit policy, transparent hugepage stack handling, architecture protection keys, MDWE support, and file operations that either provide or omit `->mmap_validate()`.

## Risks And Test Signals
Risks include accepting unsupported mapping bits, dropping architecture protection semantics, incorrect overcommit accounting batch sizes, and treating ignored historical flags as meaningful. Test signals include mmap/mprotect flag validation tests, overcommit limit and accounting tests, architecture pkey and W+X policy tests, THP stack mapping tests, and builds for architectures with custom `MAP_*` flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmap_lock.h -->
# sources/distributed-fs/ceph-client/include/linux/mmap_lock.h

## Purpose
`mmap_lock.h` defines the public locking API for `mm_struct::mmap_lock` and optional per-VMA locking. It wraps rwsem operations with tracing, assertions, seqcount updates, RCU-oriented VMA read locking, and cleanup guards.

## Important APIs, Types, And Functions
The file provides `MMAP_LOCK_INITIALIZER()`, mmap lock tracepoints, `mmap_assert_locked()`, `mmap_assert_write_locked()`, `mm_lock_seqcount_*()`, `mmap_lock_speculate_try_begin()`, `mmap_lock_speculate_retry()`, `vma_lock_init()`, `vma_start_read_locked_nested()`, `vma_start_read_locked()`, `vma_end_read()`, `vma_start_write()`, `vma_start_write_killable()`, VMA lock assertions, VMA attach/detach helpers, `lock_vma_under_rcu()`, `lock_next_vma()`, and the standard `mmap_write_*()`/`mmap_read_*()` APIs including `DEFINE_GUARD(mmap_read_lock, ...)`.

## Control Flow And State
All mmap lock acquisitions trace start/acquire/release when tracing is enabled. Write acquisition takes the rwsem and begins the per-mm seqcount; write unlock or downgrade ends all per-VMA write locks by ending the seqcount before releasing or downgrading the rwsem. With `CONFIG_PER_VMA_LOCK`, VMA read locks increment `vm_refcnt`, lockdep marks a shared lock, and `vma_refcount_put()` wakes waiters when the final reader blocking an exclusive writer leaves. VMA write locking compares `vma->vm_lock_seq` with `mm->mm_lock_seq` and can sleep while excluding readers. Without per-VMA locks, helpers collapse to mmap-lock assertions or no-ops.

## Dependencies And Integration Points
Dependencies include lockdep, `mm_types.h`, `mmdebug.h`, rwsems, tracepoint definitions, cleanup guards, and scheduler MM helpers. Integration points include page-fault fast paths, RCU VMA lookup, mmap/munmap/mprotect writers, lockdep, tracepoints, per-VMA lock sequence state in `mm_struct`/`vm_area_struct`, and the maple-tree VMA iterator.

## Risks And Test Signals
Risks include unmatched seqcount begin/end, retaining per-VMA write locks after releasing mmap write lock, unsafe detached VMA access, refcount overflow or missed wakeups, false assumptions when lockdep is disabled, and nonblock paths accidentally sleeping. Test signals include lockdep runs, mmap/fault/munmap/mremap stress with per-VMA locking enabled and disabled, RCU VMA lookup races, signal-interrupted write locking, tracepoint coverage, and KCSAN/rwsem contention tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmap_lock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmc/card.h -->
# sources/distributed-fs/ceph-client/include/linux/mmc/card.h

## Purpose
`mmc/card.h` defines the MMC core's card-facing state. It models parsed CID/CSD/EXT_CSD/SCR/SSR data, SD switch and extension capabilities, UHS-II card configuration, SDIO common/function data, physical partitions, quirks, and the main `struct mmc_card` device object.

## Important APIs, Types, And Functions
Key types are `struct mmc_cid`, `struct mmc_csd`, `struct mmc_ext_csd`, `struct sd_scr`, `struct sd_ssr`, `struct sd_switch_caps`, `struct sd_ext_reg`, `struct sd_uhs2_config`, `struct sdio_cccr`, `struct sdio_cis`, `struct mmc_part`, and `struct mmc_card`. Helper macros identify card types (`mmc_card_mmc()`, `mmc_card_sd()`, `mmc_card_sdio()`, `mmc_card_sd_combo()`), and inline helpers expose 4 KiB sector and async IRQ support. The only external function declared here is `mmc_card_is_blockaddr()`.

## Control Flow And State
The header itself has no active control flow; it defines persistent card state populated during card detection and mode negotiation. `struct mmc_card` binds a `struct device` to a host, OCR/RCA/type/state, raw and parsed register snapshots, erase/trim/cache/HPI/CQE capabilities, SDIO functions and tuples, selected bus speed/drive strength, debugfs root, eMMC physical partition descriptors, and a completion workqueue. Quirk bits alter later block, SDIO, erase, cache, tuning, and power-off behavior.

## Dependencies And Integration Points
Dependencies include the device model and module device tables. Integration points include MMC block, SD, SDIO, CQE, debugfs, eMMC partition handling, card detection, mode switching, power management, and host capabilities from `host.h`.

## Risks And Test Signals
Risks include mis-parsed register fields, unit conversion errors for sectors/bytes/timeouts, stale raw-vs-parsed capability state, quirk bit regressions, SDIO function count overflow, and wrong partition access flags. Test signals include card enumeration across MMC/SD/SDIO/combo media, EXT_CSD parsing tests, erase/trim/cache/HPI/CQE behavior tests, debugfs inspection, partition exposure tests, and known-bad-card quirk coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmc/card.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmc/core.h -->
# sources/distributed-fs/ceph-client/include/linux/mmc/core.h

## Purpose
`mmc/core.h` defines the request, command, data, and UHS-II command objects passed between MMC core, block layer, card logic, and host drivers. It also declares synchronous request/command helpers and reset/timeout helpers.

## Important APIs, Types, And Functions
Important types are `struct uhs2_command`, `struct mmc_command`, `struct mmc_data`, and `struct mmc_request`. Macros describe native and SPI response bits, response presets (`MMC_RSP_R1`, `MMC_RSP_R1B`, `MMC_RSP_R2`, etc.), command classes (`MMC_CMD_AC`, `MMC_CMD_ADTC`, `MMC_CMD_BC`, `MMC_CMD_BCR`), data flags (`MMC_DATA_WRITE`, `MMC_DATA_READ`, CQE flags), and helpers `mmc_resp_type()`, `mmc_spi_resp_type()`, and `mmc_cmd_type()`. Declared functions include `mmc_wait_for_req()`, `mmc_wait_for_cmd()`, `mmc_hw_reset()`, `mmc_sw_reset()`, and `mmc_set_data_timeout()`.

## Control Flow And State
The normal flow is: fill a `mmc_command`, optional `mmc_data`, optional SET_BLOCK_COUNT/STOP commands, and a `mmc_request`; submit to the host; complete via the request completions or `done()` callback; inspect `cmd->error`, `data->error`, `bytes_xfered`, and optional recovery notifier. UHS-II native packet data can be attached through `uhs2_command`. State is per-request and transient, with optional crypto context and key slot when MMC crypto is enabled.

## Dependencies And Integration Points
Dependencies include completions, scatterlists via forward declarations, MMC host/card structures, optional inline crypto, and UHS-II support. Integration points include host `request()`/CQE operations, MMC block requests, SD/MMC command encoding headers, error recovery, tuning, reset handling, and data timeout computation.

## Risks And Test Signals
Risks include response flag mismatch, SPI/native response confusion, incorrect busy timeout, invalid scatter-gather counts, completion ordering bugs, CQE recovery omissions, and crypto context lifetime issues. Test signals include command encode/decode tests, host simulator tests, block read/write/multiblock I/O, timeout/retry injection, CQE recovery tests, UHS-II command responses, and crypto-enabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmc/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmc/host.h -->
# sources/distributed-fs/ceph-client/include/linux/mmc/host.h

## Purpose
`mmc/host.h` defines the MMC host-controller contract. It describes bus electrical state, timing, host operations, CQE operations, slot helpers, supplies, host capabilities, runtime state, allocation/registration APIs, regulator helpers, SDIO IRQ handling, retuning helpers, and utility predicates.

## Important APIs, Types, And Functions
Key types are `struct mmc_ios`, `struct mmc_clk_phase`, `struct mmc_clk_phase_map`, `struct sd_uhs2_caps`, `enum sd_uhs2_operation`, `enum mmc_err_stat`, `struct mmc_host_ops`, `struct mmc_cqe_ops`, `struct mmc_slot`, `struct mmc_supply`, `struct mmc_ctx`, and `struct mmc_host`. Capability macros cover bus width, SPI, polling, high-speed, DDR/UHS/HS200/HS400/UHS-II/SD Express/CQE/crypto, card-detect/write-protect polarity, power cycling, and command-during-transfer support. APIs include host allocation/add/remove/free, OF parsing, request completion, CQE completion, regulator setup, SDIO IRQ signaling, PM flag helpers, retune helpers, DMA direction, debug error stats, SD switch/status/tuning/ext-csd helpers, and `mmc_priv()`/`mmc_from_priv()`.

## Control Flow And State
Host drivers allocate a host, fill `ops`, capabilities, voltage/current limits, request limits, optional CQE ops, private data, and register it with `mmc_add_host()`. The core claims the host using `lock`, `wq`, `claimer`, and `claim_cnt`, sets `ios` through `set_ios()`, submits requests through `request()` or `request_atomic()`, completes with `mmc_request_done()`, handles card detection through delayed work and slot state, and manages retuning through flags and `retune_timer`. CQE state (`cqe_enabled`, `cqe_on`, depth, ops) controls queued eMMC requests. Supply state tracks regulators and undervoltage events.

## Dependencies And Integration Points
Dependencies include scheduler, device model, fault injection, debugfs, MMC core/card/PM, DMA direction, block crypto profile, and UHS-II definitions. Integration points include platform/OF parsing, regulators, wakeup sources, PM, SDIO IRQ threads/work, block layer request limits, CQE, inline encryption, debugfs error counters, card detection GPIO helpers, and host-specific tuning/voltage switching callbacks.

## Risks And Test Signals
Risks include incorrect capability advertising, sleeping callbacks used in atomic context, lost request completion, retune races, regulator voltage mismatch, SDIO IRQ wake mishandling, CQE recovery errors, incorrect DMA direction, and card-detect/write-protect polarity bugs. Test signals include host probe/remove, hotplug, suspend/resume, voltage switch, tuning and retuning stress, multiblock I/O, CQE timeout recovery, SDIO IRQ tests, regulator fault/undervoltage tests, and debugfs error counter checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmc/host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmc/mmc.h -->
# sources/distributed-fs/ceph-client/include/linux/mmc/mmc.h

## Purpose
`mmc/mmc.h` is the protocol constant header for native MMC/eMMC commands, status bits, command classes, CSD/EXT_CSD field offsets, EXT_CSD field values, card type capability bits, bus width/timing values, power notification values, command queue bits, switch modes, and erase/trim arguments.

## Important APIs, Types, And Functions
The header defines command opcodes such as `MMC_GO_IDLE_STATE`, `MMC_SEND_OP_COND`, `MMC_SWITCH`, `MMC_SEND_EXT_CSD`, read/write/erase commands, tuning commands, application commands, and command-queue task commands. Inline helpers `mmc_op_multi()`, `mmc_op_tuning()`, and `mmc_ready_for_data()` classify commands/status. Status macros include R1 native error/state bits, SPI R1/R2 bits, OCR busy, CCC capabilities, CSD versions, EXT_CSD offsets, HS/DDR/HS200/HS400 card type bits, bus width/strobe values, secure erase bits, BKOPS bits, CMDQ bits, and `mmc_driver_type_mask()`.

## Control Flow And State
No state is stored here. Control flow is encoded through constants consumed by MMC command construction and response parsing. For example, block code selects multiblock or tuning behavior with `mmc_op_multi()`/`mmc_op_tuning()`, polling code uses `mmc_ready_for_data()` to require both ready and TRAN state, and switch logic builds `MMC_SWITCH` arguments from access mode, EXT_CSD byte, value, and command set.

## Dependencies And Integration Points
The file depends on Linux integer types and integrates with `core.h` command structures, `card.h` EXT_CSD parsing, host tuning, block erase/trim/discard, eMMC partitioning, power-off notification, BKOPS, HPI, HS200/HS400 setup, and command queue support.

## Risks And Test Signals
Risks include opcode/field offset drift against eMMC specs, status-bit misinterpretation, incorrect ready polling for broken cards, unsafe secure erase/trim argument use, and capability bits that do not match parsed EXT_CSD revision. Test signals include EXT_CSD parser tests, status decode tests, switch-mode tests, multiblock/tuning command tests, erase/trim/discard integration tests, and conformance checks against known card register dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmc/mmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmc/pm.h -->
# sources/distributed-fs/ceph-client/include/linux/mmc/pm.h

## Purpose
`mmc/pm.h` provides shared power-management flag definitions for MMC hosts, core code, SDIO core, and SDIO function drivers. It exists so all layers use the same suspend capability/request bits.

## Important APIs, Types, And Functions
The file defines `mmc_pm_flag_t` and two flags: `MMC_PM_KEEP_POWER`, requesting card power preservation across suspend, and `MMC_PM_WAKE_SDIO_IRQ`, requesting SDIO IRQ wake capability during suspend.

## Control Flow And State
There is no direct control flow. The flags become persistent host and function state through `mmc_host::pm_caps`, `mmc_host::pm_flags`, and SDIO PM helper calls. Suspend/resume paths test these bits to decide whether to power-cycle cards and whether SDIO IRQs may wake the system.

## Dependencies And Integration Points
This header is intentionally standalone and is included by MMC host and SDIO function headers. Integration points include host PM capability declaration, SDIO function driver PM requests, system suspend, runtime PM, wakeup-source handling, and card power sequencing.

## Risks And Test Signals
Risks include hosts advertising unsupported wake/power retention, SDIO drivers requesting flags outside host capabilities, and suspend paths dropping card state despite `KEEP_POWER`. Test signals include suspend/resume with SDIO wake, power-retention tests on removable and nonremovable cards, host capability masking tests, and SDIO driver PM negotiation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmc/pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmc/sd.h -->
# sources/distributed-fs/ceph-client/include/linux/mmc/sd.h

## Purpose
`mmc/sd.h` defines SD memory-card protocol constants distinct from native MMC. It covers SD command opcodes, application commands, OCR bits, switch argument layout, interface-condition layout, SCR versions, bus widths, switch modes, access modes, and erase/discard arguments.

## Important APIs, Types, And Functions
Important constants include `SD_SEND_RELATIVE_ADDR`, `SD_SEND_IF_COND`, `SD_SWITCH_VOLTAGE`, `SD_ADDR_EXT`, `SD_SWITCH`, erase block commands, ACMD bus/status/OCR/SCR commands, extension read/write commands, OCR capability bits (`SD_OCR_S18R`, `SD_OCR_2T`, `SD_OCR_XPC`, `SD_OCR_CCS`), SCR spec versions, `SD_BUS_WIDTH_1`, `SD_BUS_WIDTH_4`, `SD_SWITCH_CHECK`, `SD_SWITCH_SET`, `SD_SWITCH_GRP_ACCESS`, `SD_SWITCH_ACCESS_HS`, `SD_ERASE_ARG`, and `SD_DISCARD_ARG`.

## Control Flow And State
The header stores no state. Core SD enumeration uses these constants to probe voltage and capacity, issue application commands after `APP_CMD`, switch speed modes, configure bus width, read status/SCR data, and set erase or discard command arguments. SDUC address extension support is represented by `SD_ADDR_EXT`.

## Dependencies And Integration Points
It has no includes and integrates with MMC command construction in `core.h`, SD card parsing in `card.h`, host voltage switching in `host.h`, and block erase/discard paths.

## Risks And Test Signals
Risks include MMC/SD opcode confusion, wrong OCR capability handling during voltage switch, bad switch function group encoding, SDHC/SDXC/SDUC capacity/addressing mistakes, and discard-vs-erase argument confusion. Test signals include SD card enumeration at multiple spec levels, 1.8 V switch tests, bus-width switching, high-speed switch tests, SCR/status parsing, and erase/discard command tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmc/sd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmc/sd_uhs2.h -->
# sources/distributed-fs/ceph-client/include/linux/mmc/sd_uhs2.h

## Purpose
`mmc/sd_uhs2.h` defines SD UHS-II packet, command, response, message, register, capability, setting, and clock constants. It is the protocol vocabulary used by host and card code that initializes and operates UHS-II cards.

## Important APIs, Types, And Functions
The header defines link-layer packet fields (`UHS2_NATIVE_PACKET`, packet type, source/destination IDs, transaction ID), message categories/codes, native CCMD/DCMD read/write and payload length fields, device init/enumeration/config payload and response lengths, response NACK/error codes, device register IO addresses, SD application packet bits, device configuration register offsets, generic/PHY/link capability and setting masks, interrupt/status/command register offsets, dormant and init-complete bits, and `UHS2_RCLK_MAX`/`UHS2_RCLK_MIN`.

## Control Flow And State
No state is stored here. Initialization code builds native packets using the header and argument bitfields, reads generic/PHY/link capabilities, writes selected settings, waits for device initialization and enumeration responses, enables interrupts and clocks, and optionally enters dormant/hibernate states. Data transfer setup uses DCMD transfer mode bits such as half-duplex and length mode.

## Dependencies And Integration Points
It relies on common bit macros from surrounding kernel headers and is included by `host.h`. Integration points include UHS-II host controller operations, `struct uhs2_command` in `core.h`, UHS-II card config in `card.h`, SD application command transport, and host timing constants.

## Risks And Test Signals
Risks include bit-position mistakes in packet assembly, response length mismatch, unsupported lane/speed setting selection, mishandled NACK error codes, and clocks outside UHS-II reference limits. Test signals include UHS-II initialization traces, capability/register decode tests, packet encode/decode tests, dormant/resume tests, interrupt enable/disable tests, and hardware or emulator validation for speed A/B and half-duplex modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmc/sd_uhs2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmc/sdio.h -->
# sources/distributed-fs/ceph-client/include/linux/mmc/sdio.h

## Purpose
`mmc/sdio.h` defines SDIO protocol constants: SDIO command opcodes, CMD52/CMD53 argument layouts, R4/R5 response bits, Card Common Control Register addresses and bits, and Function Basic Register addresses and bits.

## Important APIs, Types, And Functions
Important constants include `SD_IO_SEND_OP_COND`, `SD_IO_RW_DIRECT`, `SD_IO_RW_EXTENDED`, R4 voltage/memory bits, R5 error and state macros, CCCR revisions, SD physical revisions, IO enable/ready/interrupt registers, bus interface bits, capabilities bits, CIS pointer, suspend/select/exec/ready registers, block size, power control, high-speed/UHS/drive strength/interrupt extension registers, and FBR base, interface, power, CIS, CSA, and block-size registers.

## Control Flow And State
There is no active code. The SDIO core uses these constants to enumerate function 0 and functions 1-7, enable functions, set block sizes, route interrupts, choose bus width and speed, parse CIS/FBR data, and issue byte or extended transfers. CMD52 handles direct register access; CMD53 handles byte or block data transfers with fixed or incrementing address semantics.

## Dependencies And Integration Points
The file is standalone and integrates with `sdio_func.h` I/O APIs, `card.h` SDIO CCCR/CIS state, host SDIO IRQ callbacks, SDIO function drivers, and MMC command submission from `core.h`.

## Risks And Test Signals
Risks include bad CMD52/CMD53 argument encoding, incorrect R5 error handling, CCCR/FBR revision drift, enabling interrupts or high-speed mode on unsupported cards, and mishandled low-speed 4-bit constraints. Test signals include SDIO enumeration, function enable/disable, block-size negotiation, byte and block I/O, IRQ claim/release, high-speed/UHS switching, and CIS/FBR parsing tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmc/sdio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmc/sdio_func.h -->
# sources/distributed-fs/ceph-client/include/linux/mmc/sdio_func.h

## Purpose
`mmc/sdio_func.h` defines the Linux SDIO function device model and driver API. It exposes function descriptors, driver registration helpers, host claim/release, function enable/disable, block-size setup, IRQ registration, aligned transfer sizing, byte/word/dword I/O, buffer I/O, function-0 I/O, PM flags, and retune controls.

## Important APIs, Types, And Functions
Key types are `sdio_irq_handler_t`, `struct sdio_func_tuple`, `struct sdio_func`, and `struct sdio_driver`. Matching helpers are `SDIO_DEVICE()` and `SDIO_DEVICE_CLASS()`. Registration helpers include `sdio_register_driver()`, `__sdio_register_driver()`, `sdio_unregister_driver()`, and `module_sdio_driver()`. I/O APIs include `sdio_claim_host()`, `sdio_release_host()`, `sdio_enable_func()`, `sdio_disable_func()`, `sdio_set_block_size()`, `sdio_claim_irq()`, `sdio_release_irq()`, `sdio_align_size()`, `sdio_readb/w/l()`, `sdio_memcpy_fromio()`, `sdio_readsb()`, `sdio_writeb/w/l()`, `sdio_writeb_readb()`, `sdio_memcpy_toio()`, `sdio_writesb()`, `sdio_f0_readb()`, and `sdio_f0_writeb()`.

## Control Flow And State
An SDIO driver registers a `struct sdio_driver` with probe/remove/shutdown callbacks and an ID table. The core creates one `struct sdio_func` per enumerated function and tracks card pointer, function number, class/vendor/device IDs, max/current block sizes, enable timeout, presence state, DMA-capable scratch buffer, revision/info strings, and unknown CIS tuples. Drivers claim the host before sequences of I/O, enable the function, set block size, perform CMD52/CMD53-backed I/O, optionally claim IRQs, set PM flags, and release retune holds when done.

## Dependencies And Integration Points
Dependencies include the device model, module device tables, and MMC PM flags. Integration points include SDIO bus matching, SDIO IDs, MMC host claiming, retuning, suspend/resume, SDIO IRQ thread/work handling, and function drivers such as WLAN, Bluetooth, GPS, and vendor-specific devices.

## Risks And Test Signals
Risks include unclaimed-host I/O, IRQ handler lifetime races, DMA-unsafe buffers, block size larger than function maximum, leaked CIS tuples, PM flags unsupported by host, and retune held across long operations. Test signals include SDIO driver probe/remove, host claim lockdep checks, function enable/disable, byte/block I/O, IRQ storms and release races, suspend wake tests, retune hold/release tests, and module registration/unregistration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmc/sdio_func.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmc/sdio_ids.h -->
# sources/distributed-fs/ceph-client/include/linux/mmc/sdio_ids.h

## Purpose
`mmc/sdio_ids.h` is the central SDIO class/vendor/device ID registry used by SDIO function drivers for device matching. It defines standard SDIO function interface classes and known vendor/device identifiers.

## Important APIs, Types, And Functions
The file defines standard classes such as `SDIO_CLASS_NONE`, UART, Bluetooth type A/B, GPS, camera, PHS, WLAN, ATA, and Bluetooth AMP. Vendor/device IDs cover STE, Intel, C-Guys, TI, Atheros/Qualcomm, Broadcom/Cypress, Marvell, MediaTek, Microchip WILC, NXP, Realtek, Siano, RSI, and TI WL1251 devices. There are no functions or structs.

## Control Flow And State
There is no runtime state. SDIO drivers reference these constants in `struct sdio_device_id` tables, usually through `SDIO_DEVICE()` or `SDIO_DEVICE_CLASS()` from `sdio_func.h`. The bus match layer compares enumerated function class/vendor/device values against those tables during probe.

## Dependencies And Integration Points
The header is standalone and integrates with module device tables, SDIO bus matching, SDIO function drivers, udev/module autoloading metadata, and probe dispatch.

## Risks And Test Signals
Risks include duplicate or incorrect IDs, unsorted additions that increase maintenance cost, device IDs assigned to the wrong vendor, and missing IDs that prevent module autoload or probe. Test signals include modalias generation, SDIO device matching, driver autoload tests, probe on real hardware, and review against vendor specifications or existing driver tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmc/sdio_ids.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmc/slot-gpio.h -->
# sources/distributed-fs/ceph-client/include/linux/mmc/slot-gpio.h

## Purpose
`mmc/slot-gpio.h` declares generic GPIO-backed MMC slot helpers for card-detect and write-protect signals. It lets host drivers reuse common GPIO descriptor, IRQ, debounce, polarity, wake, and capability logic.

## Important APIs, Types, And Functions
The API surface is `mmc_gpio_get_ro()`, `mmc_gpio_get_cd()`, `mmc_gpio_set_cd_irq()`, `mmc_gpiod_request_cd()`, `mmc_gpiod_request_ro()`, `mmc_gpiod_set_cd_config()`, `mmc_gpio_set_cd_wake()`, `mmc_gpiod_request_cd_irq()`, `mmc_host_can_gpio_cd()`, and `mmc_host_can_gpio_ro()`.

## Control Flow And State
Host drivers request CD/RO GPIOs during probe, then use get helpers from host callbacks or let the helper request a CD IRQ that drives detect work. `mmc_gpio_set_cd_irq()` records the IRQ in `mmc_host::slot`, and wake control toggles whether card-detect can wake the system. Persistent state lives in host slot fields and helper-private GPIO context.

## Dependencies And Integration Points
Dependencies include interrupt and type headers plus `struct mmc_host`. Integration points include host `get_cd()`/`get_ro()` callbacks, device tree or platform GPIO descriptors, debounce configuration, card-detect IRQ handling, PM wake, and the host slot state in `host.h`.

## Risks And Test Signals
Risks include active-level polarity mistakes, debounce omissions, wake IRQ misconfiguration, IRQ leaks on remove, and hosts mixing native and GPIO CD/RO sources inconsistently. Test signals include card insertion/removal, write-protect readback, active-high/active-low DT configurations, debounce behavior, suspend wake on CD IRQ, and probe/remove resource cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmc/slot-gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmdebug.h -->
# sources/distributed-fs/ceph-client/include/linux/mmdebug.h

## Purpose
`mmdebug.h` defines MM-specific debug dump declarations and assertion/warning macros. It gives memory-management code contextual BUG/WARN helpers for pages, folios, VMAs, mm structs, VMA merge state, virtual address checks, IRQ state checks, and page-flag checks.

## Important APIs, Types, And Functions
Declared dump helpers are `dump_page()`, `dump_vma()`, `dump_mm()`, `dump_vmg()`, and `vma_iter_dump_tree()`. Under `CONFIG_DEBUG_VM`, macros include `VM_BUG_ON*`, `VM_WARN_ON*`, folio/page/VMA/MM/VMG variants, once variants, formatted `VM_WARN()`/`VM_WARN_ONCE()`, `VM_WARN_ON_IRQS_ENABLED()`, `VIRTUAL_BUG_ON()`, and `VM_BUG_ON_PGFLAGS()`. Without debug configs, most macros compile expressions through `BUILD_BUG_ON_INVALID()` or become no-ops.

## Control Flow And State
Debug builds evaluate conditions, dump the relevant object, and call `BUG()` or `WARN_ON()` when violated. Once variants keep static `__warned` state in `.data..once`. Non-debug builds preserve compile-time checking of expression validity without runtime cost. IRQ, virtual, and page-flag checks are controlled by separate debug configs.

## Dependencies And Integration Points
Dependencies include `bug.h` and `stringify.h`, plus forward declarations for MM types. Integration points include page/folio/VMA/mm invariant checks across the MM subsystem, lock and refcount assertions, VMA merge diagnostics, virtual address debug instrumentation, and page flag debug code.

## Risks And Test Signals
Risks include side effects in conditions that disappear in non-debug builds, crashes from BUG assertions in recoverable paths, missing object dump context, and false positives when invariants differ by config. Test signals include debug-VM builds, intentional invariant violation tests, object dump readability, once-warning behavior, IRQ-off assertions, and allconfig build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmdebug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmiotrace.h -->
# sources/distributed-fs/ceph-client/include/linux/mmiotrace.h

## Purpose
`mmiotrace.h` declares kernel MMIO tracing and kmmio probe interfaces. It lets tracing code intercept MMIO page faults, observe ioremap/iounmap mappings, record MMIO reads/writes, and insert trace markers.

## Important APIs, Types, And Functions
Key types are `kmmio_pre_handler_t`, `kmmio_post_handler_t`, `struct kmmio_probe`, `enum mm_io_opcode`, `struct mmiotrace_rw`, and `struct mmiotrace_map`. APIs include `register_kmmio_probe()`, `unregister_kmmio_probe()`, `kmmio_init()`, `kmmio_cleanup()`, `is_kmmio_active()`, `kmmio_handler()`, `mmiotrace_ioremap()`, `mmiotrace_iounmap()`, `mmiotrace_printk()`, `enable_mmiotrace()`, `disable_mmiotrace()`, `mmio_trace_rw()`, `mmio_trace_mapping()`, and `mmio_trace_printk()`.

## Control Flow And State
When enabled, registered `kmmio_probe` entries describe address ranges and pre/post handlers. The page fault handler calls `kmmio_handler()` for trapped MMIO accesses, ioremap/iounmap hooks report mappings, and trace code emits `mmiotrace_rw` or `mmiotrace_map` records. `kmmio_count` indicates active probe count. Without `CONFIG_MMIOTRACE`, runtime helpers become inert stubs and report no active tracing.

## Dependencies And Integration Points
Dependencies include types and lists, plus `pt_regs`, resource sizes, and `__iomem` annotations from broader kernel headers. Integration points include page fault handling, ioremap/iounmap code, ftrace tracing output, driver MMIO debugging, PCI register tracing, and architecture fault semantics.

## Risks And Test Signals
Risks include trapping the wrong range, probe lifetime/list races, recursion from tracing MMIO while handling MMIO, address/width mismatches, and stale map IDs. Test signals include enabling/disabling tracing, registering overlapping probes, ioremap/iounmap trace records, read/write trace validation against a test driver, fault handler coverage, and non-`CONFIG_MMIOTRACE` build stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmiotrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmu_context.h -->
# sources/distributed-fs/ceph-client/include/linux/mmu_context.h

## Purpose
`mmu_context.h` provides generic wrappers and defaults around architecture MMU context handling. It includes architecture context headers and supplies fallbacks for IRQ-off MM switching, leaving an mm, task CPU masks, pointer untagging masks, and page-table DMA compatibility.

## Important APIs, Types, And Functions
Important defaults are `switch_mm_irqs_off` aliasing `switch_mm`, no-op `leave_mm()`, `task_cpu_possible_mask()`, `task_cpu_possible()`, `task_cpu_fallback_mask()`, `mm_untag_mask()`, and `arch_pgtable_dma_compat()`. Architectures can override these before including or through their `asm/mmu_context.h`/`asm/mmu.h`.

## Control Flow And State
The header itself stores no state. Scheduler and architecture code call `switch_mm_irqs_off()` when interrupts are disabled if an architecture needs a distinct implementation. CPU placement code uses task CPU possible/fallback masks for heterogeneous systems. `mm_untag_mask()` supplies an address-mask default for architectures without tagged user pointers, and `arch_pgtable_dma_compat()` defaults to permitting DMA compatibility.

## Dependencies And Integration Points
Dependencies are architecture `mmu_context.h` and `mmu.h`. Integration points include scheduler context switching, TLB/MMU context loading, CPU hotplug and heterogeneous CPU placement, housekeeping CPU fallback, tagged-address architectures, and DMA/IOMMU checks involving page tables.

## Risks And Test Signals
Risks include architecture fallbacks being too permissive, switching an mm with incorrect IRQ assumptions, wrong possible CPU masks on heterogeneous systems, failure to clear pointer tags, and DMA incompatibility hidden by the default true return. Test signals include architecture builds, context-switch stress, CPU hotplug and affinity tests, tagged-pointer syscall/MM tests, and DMA mapping tests on architectures with special page-table constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmu_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmu_notifier.h -->
# sources/distributed-fs/ceph-client/include/linux/mmu_notifier.h

## Purpose
`mmu_notifier.h` defines the callback contract that lets secondary MMUs and device page-table users stay coherent with CPU page-table changes. It covers notifier events, subscription ops, interval notifiers, invalidate range setup, young/accessed-bit callbacks, secondary TLB invalidation, registration/lifetime APIs, and no-op fallbacks when MMU notifier support is disabled.

## Important APIs, Types, And Functions
Key types are `enum mmu_notifier_event`, `struct mmu_notifier_ops`, `struct mmu_notifier`, `struct mmu_interval_notifier_finish`, `struct mmu_interval_notifier_ops`, `struct mmu_interval_notifier`, and `struct mmu_notifier_range`. APIs include `mmu_notifier_get_locked()`, `mmu_notifier_get()`, `mmu_notifier_put()`, `mmu_notifier_synchronize()`, register/unregister helpers, `mmu_interval_read_begin()`, interval insert/remove helpers, `mmu_interval_set_seq()`, `mmu_interval_read_retry()`, `mmu_interval_check_retry()`, release/subscription destroy helpers, clear/test young helpers, invalidate range start/end variants, architecture secondary TLB invalidation, range init helpers, `mm_has_notifiers()`, and `mmu_notifier_range_blockable()`.

## Control Flow And State
Subscribers register against an `mm_struct`. MM teardown calls `release()` before freeing pages. Page-table operations create a `mmu_notifier_range`, call invalidate start while pages are still mapped, modify CPU page tables, then call invalidate end after unmapping/freeing. Nonblock start clears `MMU_NOTIFIER_RANGE_BLOCKABLE` and returns an error if a notifier would need to sleep. Interval notifiers use sequence numbers: readers snapshot with `mmu_interval_read_begin()`, invalidation callbacks set the odd sequence under the user's lock, and readers retry if the sequence changed. Subscription lists are protected by mmap/RMAP locks, RCU, and SRCU lifetime rules.

## Dependencies And Integration Points
Dependencies include lists, spinlocks, `mm_types.h`, `mmap_lock.h`, SRCU, and interval trees. Integration points include KVM and other secondary MMUs, GPU/IOMMU/SVA drivers, HMM/device-private memory migration, device-exclusive entries, aging/reclaim, soft-dirty tracking, mprotect, munmap, mremap, OOM reaping, TLB invalidation, and `mm_struct::notifier_subscriptions`.

## Risks And Test Signals
Risks include failing to block new secondary mappings during invalidation, sleeping in nonblock callbacks, missing start/end pairing, freeing pages while devices retain DMA/SPTE references, sequence misuse in interval readers, callback lifetime races, and implementing both failing start and end callbacks incorrectly. Test signals include KVM/GPU notifier stress, munmap/mprotect/migrate/OOM invalidation tests, nonblock `-EAGAIN` paths, SRCU synchronization tests, interval notifier retry tests, accessed-bit aging tests, and builds with `CONFIG_MMU_NOTIFIER` disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mmu_notifier.h -->
