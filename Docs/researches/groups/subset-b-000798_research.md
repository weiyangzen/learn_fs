# Research: subset-b-000798

Grouped research for the PowerPC Cell SPUFS implementation and adjacent CHRP platform files. Each section is keyed by its source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/Makefile

Purpose: builds the `spufs` kernel object when `CONFIG_SPU_FS` is enabled and wires together the VFS, scheduler, context-switch, fault, syscall, and optional coredump pieces. It also owns the unusual SPU-side helper build, where `spu_save.c`, `spu_restore.c`, and their crt0 assembly are compiled with an SPU cross toolchain, object-copied into dump headers, and included by `switch.c`.

Important build APIs and artifacts: `spufs-y` lists core objects; `spufs-$(CONFIG_COREDUMP)` adds `coredump.o`; `CFLAGS_sched.o := -I$(src)` exposes local trace headers; `clean-files` removes generated `spu_save_dump.h` and `spu_restore_dump.h`. The SPU tool variables default to `spu-gcc`, `spu-ld`, and `spu-objcopy`.

Control flow and dependencies: `switch.o` depends on generated dump headers, so host context switching cannot build until SPU-side save/restore images exist. Risks include missing SPU cross tools, stale generated headers, and include-path drift between kernel headers and SPU helper compilation. Test signals are successful kernel build with `CONFIG_SPU_FS`, generated dump headers present, and `switch.o` rebuilding when SPU helper sources change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/backing_ops.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/backing_ops.c

Purpose: implements `spu_backing_ops`, the `spu_context_ops` table used while a context is saved and not bound to physical SPU hardware. It makes the saved context save area (`ctx->csa`) behave like SPU problem/privileged registers for filesystem users and scheduler code.

Important functions include mailbox accessors (`spu_backing_mbox_read`, `spu_backing_ibox_read`, `spu_backing_wbox_write`), signal channel accessors, NPC/status/run-control handlers, MFC query helpers, and `spu_backing_restart_dma`. `gen_spu_event()` updates channel event data and count state when mailbox or signal operations create SPU-visible events.

Control flow: operations take `ctx->csa.register_lock`, inspect or mutate collapsed problem-state fields, update mailbox counts, and return byte-count style results matching the hardware ops. `runcntl_write` simulates running/stopped bits in saved status. State is persistent in the allocated CSA and later consumed by `spu_restore()`.

Dependencies: relies on `spu_context_ops` from `spufs.h`, SPU CSA layouts from `asm/spu_csa.h`, and event constants from SPU headers. Risks are semantic mismatch with real hardware, incomplete MFC command support (`send_mfc_command` always reports unavailable), and concurrency around saved register fields. Test signals include mailbox/stat read-write behavior on saved contexts, signal type OR-vs-overwrite semantics, and run-control state transitions before restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/backing_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/context.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/context.c

Purpose: manages the lifecycle and locking discipline for `struct spu_context`. It allocates a context, initializes its CSA and wait queues, holds the owner `mm_struct`, and tears everything down when the final reference is dropped.

Important APIs: `alloc_spu_context`, `destroy_spu_context`, `get_spu_context`, `put_spu_context`, `spu_forget`, `spu_unmap_mappings`, `spu_acquire_saved`, and `spu_release_saved`. `nr_spu_contexts` tracks live contexts for scheduler/proc reporting.

Control flow: allocation initializes `mmio_lock`, mapping/state/run mutexes, wait queues, scheduler lists, saved state, backing ops, owner mm, statistics, and optional gang membership. Destruction acquires `state_mutex`, deactivates any hardware binding, finalizes the CSA, removes gang membership, releases profiling private data, validates runqueue removal, frees switch log storage, and drops memory. `spu_forget()` is used at directory removal to deactivate and release the owner mm before context release.

State and dependencies: mappings are tracked through address_space pointers and invalidated by `spu_unmap_mappings()` during switches or isolate setup. The file depends on scheduler helpers, gang helpers, `spu_init_csa`, and `spu_deactivate`. Risks cluster around lock ordering, use-after-free through mmap faults, and releasing `owner` exactly once. Test signals include create/close loops, mmap invalidation during deactivation, and `nr_spu_contexts` returning to baseline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/coredump.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/coredump.c

Purpose: contributes Cell/SPU-specific ELF notes to process core dumps. It discovers open spufs context directories and emits one note per reader in `spufs_coredump_read`.

Important APIs: `spufs_coredump_extra_notes_size()` computes extra note bytes; `spufs_coredump_extra_notes_write()` writes the notes; `coredump_next_context()` iterates file descriptors; `spufs_arch_write_note()` emits `NT_SPU` note headers and data.

Control flow: `iterate_fd()` finds files whose operations are `spufs_context_fops`; NOSCHED contexts are skipped. Each context is refcounted, acquired in saved state with `spu_acquire_saved()`, sized or dumped, then released. Dump entries either call a binary dump callback or format a getter value as a fixed hexadecimal string.

State and dependencies: depends on `file.c` for `spufs_coredump_read` and on context locking to produce stable saved data. It assumes coredump-time descriptor tables are not shared in a way that invalidates file references. Risks include note-size/write mismatch, early returns leaking context references in error paths, and dump callbacks returning fewer bytes than declared. Test signals are core dumps from processes holding scheduled spufs contexts, verifying `SPU/<fd>/<name>` notes and alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/coredump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/fault.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/fault.c

Purpose: handles SPU class 0 and class 1 exceptions for `spu_run()`. It either reports SPE events to the caller through `event_return` or converts them into Linux signals.

Important functions: `spufs_handle_class0()` handles DMA alignment, invalid DMA command, and SPU error interrupts. `spufs_handle_class1()` handles address-translation faults from MFC accesses. `spufs_handle_event()` centralizes event-vs-signal behavior and restarts DMA for recoverable storage faults.

Control flow: class 1 handling records the faulting EA/DSISR, switches utilization to iowait, releases the context mutex before calling `hash_page()` or `copro_handle_mm_fault()`, reacquires `state_mutex`, clears saved fault registers, updates minor/major fault counters, restarts DMA when possible, or raises a storage event. Class 0 clears pending bits after signaling and returns `-EIO`.

State and dependencies: updates `ctx->stats` and physical SPU stats, uses `ctx->csa.class_*` fields captured by callbacks, and depends on PowerPC hash MMU and copro fault helpers. Risks include races while the context is saved or rescheduled during fault handling, incorrect signal address for alignment faults, and incomplete event delivery if `SPU_CREATE_EVENTS_ENABLED` callers do not drain events. Test signals include induced invalid DMA, page faults, access-denied faults, and event-enabled `spu_run` returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/fault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/file.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/file.c

Purpose: defines the user-visible files inside each spufs context directory. It implements local-store access, register access, mailbox pipes, signal files, MFC DMA proxying, problem-state mmaps, attributes, debug/stat files, switch logging, and coredump reader descriptors.

Important APIs and tables: `spufs_dir_contents`, `spufs_dir_nosched_contents`, and `spufs_dir_debug_contents` define the directory ABI. `spufs_coredump_read` maps coredump note names to dump/get routines. Helpers include `spufs_attr_*`, `spufs_mem_*`, `spufs_ps_fault`, mailbox callbacks and fops, `spufs_mfc_*`, attribute definitions for `npc`, `decr`, `event_mask`, `object-id`, `phys-id`, plus `spu_switch_log_notify()`.

Control flow: most operations acquire a context via `spu_acquire()` or `spu_acquire_saved()` depending on whether live hardware or a stable CSA is needed. Local-store mmap faults map either vmalloc-backed saved LS or physical SPU LS. Problem-state fault handlers wait until the context is runnable before inserting PFNs. Mailbox and MFC files use wait queues and callbacks from `hw_ops`/`sched` to support blocking and poll. MFC writes validate opcode, alignment, size, tag, and class before queueing a command and tracking `tagwait`.

State and dependencies: mapping pointers in `ctx` are reference-counted by per-inode `i_openers` under `mapping_lock`; switch logs are per-context ring buffers; debug/stat reads inspect scheduler and CSA fields. Risks include FIXME-noted `tagwait` locking, poll paths that sleep despite comments, sensitive mmap lifetime interactions, and ABI compatibility of directory entries. Test signals include read/write/mmap for every file, blocking mailbox/MFC poll, coredump note contents, NOSCHED directory differences, and switch log wrap behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/gang.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/gang.c

Purpose: provides refcounted gang containers used to group SPU contexts and carry affinity metadata across those contexts.

Important APIs: `alloc_spu_gang`, `get_spu_gang`, `put_spu_gang`, `spu_gang_add_ctx`, and `spu_gang_remove_ctx`. The destructor validates that no contexts remain and that the list is empty before freeing.

Control flow: allocation initializes gang refcount, list mutex, affinity mutex, context list, affinity list head, and `alive=1`. Adding a context takes the gang mutex, stores a ref in `ctx->gang`, links `ctx->gang_list`, and increments `contexts`. Removal unlinks affinity membership if present, clears offset validity, removes the gang-list node, decrements `contexts`, unlocks, then drops the gang reference.

State and dependencies: the scheduler and inode creation code use gang `aff_*` fields and `alive`; this file only owns lifetime and list membership. Risks include callers failing to serialize against affinity mutation, stale `AFF_OFFSETS_SET` if contexts are removed outside this path, and leaked refs if context creation partially fails. Test signals are gang create/close, adding/removing multiple contexts, affinity context removal, and warning-free destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/gang.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/hw_ops.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/hw_ops.c

Purpose: implements `spu_hw_ops`, the `spu_context_ops` table used when a context is bound to physical SPU hardware. It translates spufs file operations into MMIO reads/writes of SPU problem, priv1, and priv2 registers.

Important functions: hardware mailbox read/status/poll and write helpers, signal notify and signal type accessors, NPC/status/local-store getters, run-control and master-control operations, MFC query/tag/free-element access, MFC command issue, and DMA restart.

Control flow: register accesses use big-endian MMIO helpers and often take `spu->register_lock` with interrupts disabled. Poll helpers either return readiness or enable class 2 interrupts and clear stale status. `runcntl_write` enables isolated load requests before setting isolate run-control. `send_mfc_command` writes LSA/EA/size/tag/class/cmd and decodes command status into `0`, `-EAGAIN`, or `-EINVAL`.

State and dependencies: depends on `ctx->spu` being valid and associated by the scheduler; callbacks in `sched.c` bind `ctx->ops` to this table. Risks are missing locking on simple reads, busy-waiting in `runcntl_stop`, interrupt-mask side effects during poll, and exact hardware status decoding. Test signals include mailbox interrupt readiness, MFC queue full behavior, isolate startup, DMA restart suppression during context switch, and parity with `backing_ops` for saved contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/hw_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/inode.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/inode.c

Purpose: implements the spufs filesystem: inode allocation, context/gang directory creation, mount option parsing, root setup, and module initialization/exit.

Important APIs: `spufs_create()` is the syscall-facing creation entry. `spufs_mkdir()` creates a context directory and fills it from `file.c` descriptors. `spufs_create_context()` validates flags, isolation support, NOSCHED privilege, gang liveness, and affinity constraints. `spufs_create_gang()` creates gang directories. Mount support is provided through `spufs_init_fs_context`, `spufs_parse_param`, `spufs_fill_super`, and `spufs_get_tree`.

Control flow: context creation allocates an inode and `spu_context`, stores the context in `SPUFS_I(inode)`, populates files, optionally adds debug entries, opens the created directory as an fd, and rolls back via recursive removal on failure. Directory release removes the subtree and calls `spu_forget()`. Affinity setup validates neighbor context relationships and available SPUs before linking affinity lists.

State and dependencies: uses a slab cache for `spufs_inode_info`, `spufs_sb_info` for the debug mount flag, device tree `/spu-isolation` loader data, scheduler init/exit, syscall registration, and VFS helpers. Risks include partial-create rollback, affinity race conditions, mount option ownership, and isolated loader lifetime. Test signals include mount options, `spu_create` flag validation, context fd close cleanup, gang close behavior, debug mount contents, and module load/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/lscsa_alloc.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/lscsa_alloc.c

Purpose: allocates and frees the local-store context save area (`lscsa`) used by SPU context switching. This large region contains saved local store and SPU register spill data.

Important APIs: `spu_alloc_lscsa(struct spu_state *csa)` and `spu_free_lscsa(struct spu_state *csa)`.

Control flow: allocation uses `vzalloc(sizeof(struct spu_lscsa))`, stores the pointer in `csa->lscsa`, then marks every page covering the `ls` array as reserved via `SetPageReserved(vmalloc_to_page(p))`. Freeing checks for a null pointer, clears the reserved bit on the same page range, and calls `vfree()`.

State and dependencies: tied to `spu_init_csa()` and `spu_fini_csa()` in `switch.c`, and to mmap handling in `file.c`, where saved local store is mapped through `vmalloc_to_pfn()`. Risks include mismatched reserve clear on partial initialization, page-flag leaks, and assumptions that vmalloc pages are stable for PFN insertion. Test signals are repeated context allocate/free under debug VM, local-store mmap of saved contexts, and no reserved-page warnings after context teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/lscsa_alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/run.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/run.c

Purpose: implements the `spu_run` execution loop and interrupt-level stop callback. It starts a context, waits for stop/fault/syscall events, processes recoverable conditions, and returns updated NPC/status/event data to userspace.

Important functions: `spufs_stop_callback`, `spu_stopped`, `spu_setup_isolated`, `spu_run_init`, `spu_process_callback`, `spu_handle_restartsys`, `spu_run_fini`, and exported `spufs_run_spu`.

Control flow: `spufs_run_spu()` serializes with `run_mutex`, acquires the context, enables the SPU, updates scheduler info, initializes run-control, then waits on `stop_wq` until `spu_stopped()` detects halt/stop/single-step/class events. Stop code `0x2104` triggers a syscall callback from SPU local store. Class 1 and class 0 handlers are invoked before deciding whether to continue. Finalization removes from the runqueue, reads status/NPC, clears run flags, logs exit, releases the context, and maps status/signal cases into return values.

State and dependencies: isolated-mode setup loads a device-tree-provided loader through signal registers and temporarily drops problem state. Syscall callbacks depend on `spu_sys_callback`. Risks include subtle restart semantics, signal interruption while needing `state_mutex`, isolated loader timeouts, and local-store pointer validation. Test signals include normal stop/halt returns, SPU syscall restart cases, single-step trap behavior, class fault recovery, and isolate success/failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/run.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/sched.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/sched.c

Purpose: implements the SPU scheduler, binding saved contexts to physical SPUs, timeslicing, priority queues, NUMA/CPU-mask filtering, affinity gangs, load average accounting, and `/proc/spu_loadavg`.

Important APIs: `spu_set_timeslice`, `__spu_update_sched_info`, `spu_update_sched_info`, `do_notify_spus_active`, `spu_activate`, `spu_deactivate`, `spu_yield`, `spuctx_switch_state`, `spu_sched_init`, and `spu_sched_exit`. Internal helpers include `spu_bind_context`, `spu_unbind_context`, affinity placement functions, `find_victim`, `grab_runnable_context`, and `spusched_tick`.

Control flow: activation tries an idle SPU matching CPU/NUMA and affinity constraints; RT contexts can preempt lower-priority contexts. Binding associates the owner mm, installs callbacks, switches `ctx->ops` to hardware ops, restores CSA to hardware, and wakes run waiters. Unbinding saves hardware state back to the CSA, switches ops to backing ops, clears callbacks, updates statistics, and wakes stopped waiters. A scheduler kthread wakes on a timer and ticks each active SPU context, preempting non-FIFO contexts whose slice expired when a higher-priority queued context exists.

State and dependencies: global `spu_prio` holds runqueue bitmap/lists; `cbe_spu_info` provides physical SPU lists and counters; gang affinity fields are mutated under gang locks. Risks include lock ordering between context, node list, and runqueue locks; starvation during victim retry; affinity placement edge cases; and accounting drift. Test signals include priority preemption, NOSCHED reservation accounting, CPU affinity changes, gang affinity placement, loadavg output, and clean scheduler exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/sched.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/spu_restore.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/spu_restore.c

Purpose: SPU-side restore program loaded by host `switch.c`. It reconstructs the upper local store, special channels, FPCR, decrementer, SRR0, event/tag masks, and final stopped/running behavior from the LSCSA.

Important functions: `fetch_regs_from_mem`, `restore_upper_240kb`, `restore_decr`, `write_ppu_mb`, `write_ppuint_mb`, `restore_fpcr`, `restore_srr0`, `restore_event_mask`, `restore_tag_mask`, `restore_complete`, and `main`.

Control flow: `main()` receives the LSCSA effective address through signal notification channels, fetches the register spill area, masks events/tags, builds DMA lists, GETLs upper local store, clears lock-line reservation, waits for tag completion, restores special state, and calls `restore_complete()`. That function patches instructions at `exit_fini` based on `stopped_status` so the final crt0 exit recreates illegal instruction, halt, stop-and-signal, single-step, running, or infinite-branch state.

State and dependencies: shares `regs_spill` and DMA list utilities with crt0 and `spu_utils.h`; generated into `spu_restore_dump.h` for host use. Risks include self-modifying exit code correctness, exact LSCSA offsets, channel ordering, and DMA list address assumptions. Test signals include context restore after each stopped-status combination, decrementer wrap events, mailbox restore, and successful host `SPU_RESTORE_COMPLETE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/spu_restore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/spu_restore_crt0.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/spu_restore_crt0.S

Purpose: SPU assembly entry/exit runtime for the restore helper. It sets up a minimal stack, calls C `main`, restores all 128 SPU GPRs from `regs_spill`, and exits with a restore-complete stop sequence.

Important symbols: global `regs_spill`, `_start`, `exit`, `_exit`, `exit_fini`, and `_exit_fini`. The `restore_reg_insts` loop is self-modifying-style code that iterates through registers 16-127 four at a time.

Control flow: `_start` initializes stack pointer at 16 KiB minus 16, creates a minimal frame, and branches to `main`. On return, `exit` restores higher registers from the spill area, then restores registers 0-15. `exit_fini` contains `stop SPU_RESTORE_COMPLETE` followed by padding `stop 0` instructions that `spu_restore.c` may patch to recreate the original stopped status.

State and dependencies: depends on `SIZEOF_SPU_SPILL_REGS`, `SPU_RESTORE_COMPLETE`, and the C helper filling `regs_spill`. Risks include register clobbering before all registers are restored, alignment requirements, and patchable instruction layout changing. Test signals are SPU helper object disassembly, generated dump header size/alignment, and successful restore of full register files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/spu_restore_crt0.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/spu_save.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/spu_save.c

Purpose: SPU-side save program loaded by host `switch.c`. It saves local store beyond the first 16 KiB, FPCR, decrementer, SRR0, event/tag masks, and the register spill area into the LSCSA.

Important functions: `save_event_mask`, `save_tag_mask`, `save_upper_240kb`, `save_fpcr`, `save_decr`, `save_srr0`, `spill_regs_to_mem`, `enqueue_sync`, `save_complete`, and `main`.

Control flow: `main()` reads the LSCSA effective address from signal notification channels, relies on crt0 to save registers, saves masks, masks events/tags, builds a DMA list for upper local store, PUTLs that region to CSA, saves special state, issues a PUTLLC to clear lock-line reservation, PUTs the register spill area, syncs tag group 0, reads tag and atomic status, and stops with `SPU_SAVE_COMPLETE`.

State and dependencies: uses `spu_utils.h`, `regs_spill` from `spu_save_crt0.S`, and LSCSA field offsets from `asm/spu_csa.h`. Host `switch.c` waits for the completion stop code. Risks include exact ordering of DMA and channel operations, size/alignment assumptions for the 240 KiB DMA list, and loss of state if crt0 register spill layout changes. Test signals include save/restore round trips, FPCR/decrementer preservation, local-store checksums, and completion status validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/spu_save.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/spu_save_crt0.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/spu_save_crt0.S

Purpose: SPU assembly entry runtime for the save helper. It spills all 128 SPU GPRs into `regs_spill`, sets up a stack, and calls C `main`.

Important symbols: global `regs_spill`, `_start`, `exit`, and `_exit`. The file allocates `SIZEOF_SPU_SPILL_REGS` aligned storage and uses `stqa` for registers 0-15 plus a loop around `save_reg_insts` for registers 16-127.

Control flow: `_start` immediately saves the first 16 registers, then iterates through the remaining registers in blocks of four. After register capture, it initializes the stack at 16 KiB minus 16, creates a minimal frame for `main`, and branches. If `main` unexpectedly returns, `exit` executes `stop 0`, which should be treated as a failed save path by the host because normal completion uses `SPU_SAVE_COMPLETE`.

State and dependencies: tightly coupled to `spu_save.c`, `spu_utils.h`, and SPU ABI register naming. Risks include alignment-sensitive instruction rewriting, stack overlap with save helper code/data, and object size changes affecting host DMA loading. Test signals include disassembly of generated helper, full register preservation, and no accidental return from `main`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/spu_save_crt0.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/spu_utils.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/spu_utils.h

Purpose: shared SPU-side utility header for save and restore helper programs. It defines portable address/register unions, DMA list storage, LSCSA offset macros, and common channel/DMA helper sequences.

Important types and symbols: `addr64`, `spu_reg128v`, `struct dma_list_elem`, global aligned `dma_list[15]`, external `regs_spill`, `LSCSA_BYTE_OFFSET`, and `LSCSA_QW_OFFSET`. Helpers include `set_event_mask`, `set_tag_mask`, `build_dma_list`, `enqueue_putllc`, `set_tag_update`, `read_tag_status`, and `read_llar_status`.

Control flow: save/restore helpers call these routines to mask SPU events, restrict tag completion to tag group 0, prepare 15 DMA-list entries covering the upper 240 KiB of local store, clear lock-line reservation with PUTLLC, and wait for tag/atomic status.

State and dependencies: relies on `struct spu_lscsa` layout, SPU intrinsic channel numbers, and 16 KiB chunks. Risks include global definitions in a header causing duplicate storage if included in multiple linked objects, null-pointer offset calculation assumptions, and hardcoded DMA command opcodes. Test signals include helper build, correct DMA list effective addresses, and save/restore of all local-store ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/spu_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/spufs.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/spufs.h

Purpose: central private interface for spufs. It declares context/gang data structures, filesystem descriptor types, operation tables, syscall hooks, coredump hooks, and cross-file helpers.

Important types: `struct spu_context` combines hardware binding, CSA, mappings, owner mm, refs, wait queues, scheduler fields, statistics, switch log, and affinity links. `struct spu_gang` holds grouped contexts and affinity metadata. `struct spu_context_ops` abstracts live hardware vs saved backing operations. Other key structs are `mfc_dma_command`, `spufs_inode_info`, `spufs_tree_descr`, and `spufs_coredump_reader`.

Integration points: `spu_hw_ops` and `spu_backing_ops` implement the operations ABI; `spufs_dir_contents` and related arrays define VFS contents; `spufs_calls` registers create/run callbacks with architecture syscall glue. The header declares scheduler, context, fault, switch, coredump, gang, and allocation functions used across files.

State and dependencies: includes Linux VFS/refcount/lock headers and PowerPC SPU CSA/info headers. Risks include ABI-wide changes to `spu_context_ops`, lock ownership assumptions not encoded in types, and structure layout dependencies shared with coredump/debug users. Test signals are full `CONFIG_SPU_FS` build, sparse/lockdep coverage, and successful switching between `spu_backing_ops` and `spu_hw_ops`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/spufs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/sputrace.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/sputrace.h

Purpose: defines the spufs tracepoint event used to observe context lifecycle and scheduler transitions.

Important APIs: `TRACE_EVENT(spufs_context)` records a string name, owner thread id, and physical SPU number or `-1`. Convenience macros `spu_context_trace(name, ctx, spu)` and `spu_context_nospu_trace(name, ctx)` stringify call-site names and invoke the tracepoint.

Control flow and dependencies: `sched.c` defines `CREATE_TRACE_POINTS` before including this header, while other files include it for declarations. `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE sputrace` make the tracing generator find the local header; the Makefile adds `-I$(src)` for `sched.o`.

State and integration: trace data is observational only and depends on `ctx->tid` and optional `spu->number`. Risks include trace include path breakage, using a transient string pointer incorrectly, and missing updates if important paths are not instrumented. Test signals are tracepoint generation during build and runtime events around bind, unbind, activate, fault wake, and destroy paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/sputrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/switch.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/switch.c

Purpose: host-side SPU context save/restore engine. It follows the SPE Book IV sequence to quiesce hardware, save privileged/problem state, load SPU-side helper programs, transfer local-store/LSCSA data, restore state, and initialize new CSAs.

Important APIs: exported `spu_save`, `spu_restore`, `spu_init_csa`, and `spu_fini_csa`. Major internal phases are `quiece_spu`, `save_csa`, `save_lscsa`, `harvest`, `restore_lscsa`, `restore_csa`, and `__do_spu_save`/`__do_spu_restore`. Many static helpers map one documented save/restore step to MMIO operations.

Control flow: save disables interrupts, blocks context-switch-sensitive handlers, suspends/purges MFC queues, saves run-control/status/channel/mailbox/query state, configures kernel SLBs for helper code and LSCSA, DMAs save code into local store, waits for tag completion and SPU stop completion, and validates `SPU_SAVE_COMPLETE`. Restore first harvests/reset hardware, configures LSCSA/status/decrementer/mailboxes, DMAs restore code, waits for `SPU_RESTORE_COMPLETE`, restores queues/channels/registers/status/routing, and reenables interrupt masks.

State and dependencies: includes generated `spu_save_dump.h` and `spu_restore_dump.h`, manipulates `struct spu_state`, SPU MMIO, SLBs, interrupts, and `spu->flags`. It also initializes default CSA register values and allocates LSCSA via `lscsa_alloc.c`. Risks are high: busy waits, panic on failed save/restore, incomplete TODO steps for user/other-SPU access, exact hardware sequencing, and isolate exit handling. Test signals include stress preemption, fault during switch, isolate state, mailbox/MFC queue preservation, register/local-store round trips, and lockdep/IRQ assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/switch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/syscalls.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/syscalls.c

Purpose: registers the architecture-facing spufs syscall callbacks for creating contexts and running SPU contexts.

Important functions: `do_spu_run`, `do_spu_create`, and the global `spufs_calls` structure. `spufs_calls` also exposes `do_notify_spus_active` and, under `CONFIG_COREDUMP`, the coredump extra note callbacks.

Control flow: `do_spu_run()` obtains the file for the supplied fd, copies in the user NPC, verifies the file is a spufs context directory (`spufs_context_fops`), calls `spufs_run_spu()`, then writes back NPC and optional status. `do_spu_create()` uses `start_creating_user_path()` with `LOOKUP_DIRECTORY`, delegates to `spufs_create()`, and finishes with `end_creating_path()`.

State and dependencies: this file is glue between generic syscall registration and `inode.c`/`run.c`; module ownership is recorded in `spufs_calls.owner`. Risks include userspace pointer failures overriding prior return status, fd type validation, and create path race/rollback behavior delegated to VFS helpers. Test signals are syscall-level create/run with bad fds, bad user pointers, flags/mode combinations, coredump-enabled registration, and unregister on module exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/syscalls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/Kconfig -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/Kconfig

Purpose: declares the `PPC_CHRP` platform option for 32-bit Book3S Common Hardware Reference Platform machines.

Important configuration behavior: the option is a boolean prompt, depends on `PPC_BOOK3S_32`, defaults to enabled, and selects platform capabilities including PC speaker platform support, MPIC, i8259, indirect PCI, RTAS and RTAS daemon/error logging, MPC106, UDBG 16550, native hash MMU, and forced PCI.

Control flow and integration: selecting this option brings in the CHRP platform build subtree and its setup, PCI, time, NVRAM, and SMP support as controlled by the Makefile. It also constrains the platform to the legacy 32-bit PowerPC environment.

Risks and test signals: broad `select` usage can force dependencies on configurations that do not actually work for a board variant; default `y` affects multi-platform builds. Test signals are Kconfig dependency resolution, `oldconfig` behavior, and boot tests on CHRP/Pegasos/BriQ-like machines with expected interrupt, PCI, RTAS, and hash MMU support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/Makefile

Purpose: selects object files for the CHRP platform directory.

Important build behavior: unconditional objects are `setup.o`, `time.o`, `pegasos_eth.o`, and `pci.o`; `smp.o` is included under `CONFIG_SMP`; `nvram.o` is included when `CONFIG_NVRAM` is built-in or module-compatible through `obj-$(CONFIG_NVRAM:m=y)`.

Integration points: the files listed here provide platform setup, clock/RTC/NVRAM hooks, Pegasos ethernet platform quirks, PCI bridge setup, and SMP startup. The Kconfig `PPC_CHRP` option is the higher-level selector that causes this Makefile to matter.

Risks and test signals: the compact file hides platform coupling, especially the special NVRAM conditional syntax. Build risks include missing object coverage for selected features or module/built-in mismatches. Test signals are CHRP defconfig builds with SMP on/off and NVRAM built-in/module/disabled combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/chrp.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/chrp.h

Purpose: small internal header declaring CHRP platform helper functions shared across the CHRP source files.

Important declarations: `chrp_nvram_init`, `chrp_get_rtc_time`, `chrp_set_rtc_time`, `chrp_time_init`, and `chrp_find_bridges`.

Integration: `nvram.c` implements the NVRAM initializer; `time.c` provides RTC/time functions; `pci.c` provides bridge discovery; setup code includes these declarations to install platform machine hooks. The header relies on `struct rtc_time` being available to includers.

Risks and test signals: the file has no include guard beyond normal C compile context, so duplicate inclusion is benign only because it contains externs. Risks are prototype drift with implementing files and missing includes if function signatures change. Test signals are CHRP allmodconfig/defconfig builds and warnings-as-errors for mismatched prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/chrp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/gg2.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/gg2.h

Purpose: defines VLSI VAS96011/12 Golden Gate 2 chipset memory-map and PCI configuration register constants used by CHRP PCI/setup code.

Important definitions: base addresses for PCI memory, ISA memory/IO, PCI config, interrupt acknowledge/special cycles, and ROM banks; external `gg2_pci_config_base`; register offsets for bus numbers, control registers, ROM timing, cache controller, DRAM banks/timing/control, and error control/status.

Integration: consumed by CHRP PCI code that maps and accesses Golden Gate 2 configuration space. Constants encode CHRP-mode physical addresses and register offsets, not runtime-discovered resources.

Risks and test signals: hardcoded chipset addresses can be wrong for non-GG2 CHRP variants and require correct ioremap usage by callers. The error-status register being cleared on read is a side-effect risk for diagnostics. Test signals include PCI config access on GG2 hardware/emulation, bridge enumeration, and no accidental reads of clear-on-read error status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/gg2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/nvram.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/nvram.c

Purpose: provides CHRP `/dev/nvram` backend hooks through RTAS NVRAM fetch/store calls.

Important functions: `chrp_nvram_read_val`, `chrp_nvram_write_val`, `chrp_nvram_size`, and exported initializer `chrp_nvram_init`. Static state includes `nvram_size`, a four-byte RTAS transfer buffer, and `nvram_lock`.

Control flow: initialization finds the Open Firmware node of type `nvram`, reads its `#bytes` property, stores the size, logs it, and installs `ppc_md.nvram_read_val`, `ppc_md.nvram_write_val`, and `ppc_md.nvram_size`. Reads and writes range-check the byte address, serialize through `nvram_lock`, call RTAS `NVRAM_FETCH` or `NVRAM_STORE` with the physical address of `nvram_buf`, and return `0xff` or log on RTAS failure.

State and dependencies: depends on device tree, RTAS function tokens, `ppc_md` machdep hooks, and a global one-byte transfer buffer protected by a spinlock. Risks include RTAS calls under IRQ-disabled spinlock latency, physical address validity of a static buffer, silent write failures, and returning `0xff` for both real data and error. Test signals are NVRAM size detection, byte read/write round trips, out-of-range logging, and RTAS error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/nvram.c -->
