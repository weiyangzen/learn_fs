# Research: subset-b-005910

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/qede_rdma.h -->
# sources/distributed-fs/ceph-client/include/linux/qed/qede_rdma.h

Purpose: defines the coupling contract between the QED Ethernet driver (`qede`) and the QED RoCE/RDMA driver (`qedr`). It lets the RDMA layer register callbacks for device add/remove and link/address/MTU events while keeping non-RDMA builds compilable through inline stubs.

Important APIs and types: `enum qede_rdma_event` classifies lifecycle and netdev events (`QEDE_UP`, `QEDE_DOWN`, `QEDE_CHANGE_ADDR`, `QEDE_CLOSE`, `QEDE_CHANGE_MTU`). `struct qede_rdma_event_work` wraps event workqueue state and payload. `struct qedr_driver` carries the RDMA driver's name and `add`, `remove`, and `notify` hooks. Public entry points are `qede_rdma_register_driver()`, `qede_rdma_unregister_driver()`, `qede_rdma_supported()`, and RDMA device/event helpers gated by `CONFIG_QED_RDMA`.

Control flow: a `qedr_driver` registers once; Ethernet device probing or recovery calls `qede_rdma_dev_add()`, which can invoke the driver's `add()` callback with QED, PCI, and netdev handles. Netdev open/close/address/MTU changes are forwarded through event helpers to RDMA notification paths, often via queued work.

State and persistence: this header owns no persistent state. Runtime state is the registered RDMA driver, per-device `qedr_dev` handles, and queued `qede_rdma_event_work`; all are kernel-lifetime or device-lifetime only.

Dependencies and integration points: depends on PCI, netdevice, workqueue, and QED/qede/qedr forward declarations. It integrates Ethernet link management, PCI function state, and RDMA upper-layer device registration.

Risks and test signals: risks include callback lifetime races during remove/recovery, event ordering across close/down/remove, and build drift between `CONFIG_QED_RDMA` and non-RDMA stubs. The disabled branch omits a stub for `qede_rdma_event_change_mtu()`, so call sites must be configuration-safe. Test by building both RDMA and non-RDMA configs and exercising netdev up/down, MAC address changes, MTU changes, PCI recovery, and module unregister with pending event work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/qede_rdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/rdma_common.h -->
# sources/distributed-fs/ceph-client/include/linux/qed/rdma_common.h

Purpose: publishes QED firmware-facing RDMA constants and small shared structures used by RoCE/RDMA command queues and shared receive queue handling.

Important APIs and types: constants define reserved LKEY, ring page size, maximum SGEs per SQ/RQ WQE, maximum data size, atomic element sizes, CQ/TID/PD/SRQ limits, IRQ elements per page, per-vport statistic counter counts, and `RDMA_TASK_TYPE`. `struct rdma_srq_id` carries an SRQ index plus opaque function ID in little-endian layout. `struct rdma_srq_producers` exposes SGE and WQE producer indexes.

Control flow: QED RDMA code uses these values when sizing hardware resources, programming firmware ramrods, validating WQE layout, and exchanging SRQ producer state with firmware. There are no executable functions in this header.

State and persistence: no state is stored here. The structures describe memory shared between driver and firmware; persistence is limited to device runtime queues and firmware contexts.

Dependencies and integration points: relies on protocol constants such as `PROTOCOLID_ROCE` and vport count macros from adjacent QED firmware headers. It is consumed by QED core and RDMA/RoCE provider code.

Risks and test signals: risks are ABI/layout drift with firmware, endian mistakes, and resource-limit mismatches that surface only under large queue/table counts. Test with compile-time structure layout checks where available, RDMA resource exhaustion tests, SRQ create/use/destroy, CQ/TID/PD maximum boundary tests, and firmware compatibility matrices across supported QED devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/rdma_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/roce_common.h -->
# sources/distributed-fs/ceph-client/include/linux/qed/roce_common.h

Purpose: defines RoCE-specific firmware constants and asynchronous event identifiers shared between QED firmware command handling and the RDMA provider.

Important APIs and types: constants include request inline-data and WQE sizing, maximum QP counts, DCQCN NP/RP QP limits, and the LKEY memory-window DIF enable bit. `enum roce_async_events_type` enumerates firmware-reported events and errors such as communication established, SQ drained, SRQ limit/empty, CQ errors/overflow, local access/request/catastrophic errors, QP catastrophic errors, destroy-QP completion, and XRC errors.

Control flow: firmware completion/event handlers translate async event codes into RDMA core events and provider callbacks. QP/SRQ/CQ management code also uses the sizing constants to validate resource creation and command construction.

State and persistence: no state is owned. Event values represent transient firmware notifications; resource limits constrain in-memory/device contexts.

Dependencies and integration points: integrates QED firmware protocol definitions with the RoCE provider and upper RDMA core event model.

Risks and test signals: risks include event-number ABI mismatch, incomplete translation of catastrophic/error events, and off-by-one resource sizing around `ROCE_MAX_QPS`. Test async event injection or firmware fault paths, CQ overflow handling, SRQ limit/empty events, destroy-QP completion, DCQCN-enabled configurations, and RDMA userspace verbs boundary cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/roce_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/storage_common.h -->
# sources/distributed-fs/ceph-client/include/linux/qed/storage_common.h

Purpose: describes common QED firmware data structures and constants for storage offloads, especially SCSI-class iSCSI/FCoE queues, buffer descriptors, SGEs, and function initialization.

Important APIs and types: constants define SCSI command queue count, BDQ resources/IDs, SGL thresholds, BDQ ring limits, and selected SCSI opcodes. `struct iscsi_drv_opaque`, `union scsi_opaque`, `struct scsi_bd`, `struct scsi_sge`, `struct scsi_cached_sges`, `struct scsi_drv_cmdq`, and `struct scsi_tqe` describe firmware-visible descriptors. `struct scsi_init_func_params` and `struct scsi_init_func_queues` carry function and queue initialization parameters, including validity bits, status-block indexes, PBL bases, and flow-control thresholds. `enum scsi_sgl_mode`, `struct scsi_sgl_params`, and `struct scsi_terminate_extra_params` model SGL selection and termination accounting.

Control flow: storage drivers fill initialization structures during function setup, hand BDQ/CQ/CMDQ addresses to firmware, post descriptors for receive/immediate/task queues, and use SGL metadata to represent command payload buffers. Termination paths pass pending CQ/CMDQ counts to firmware.

State and persistence: state is firmware/device runtime state: queue indices, external producers, BDQ PBLs, SGL descriptors, and task IDs. It is not persistent across device reset except as reconstructed by driver initialization.

Dependencies and integration points: depends on QED common register-pair definitions, global queue constants, bitfield conventions, and Linux fixed-width endian types. It integrates storage upper layers with QED firmware ramrods and DMA queues.

Risks and test signals: risks include little-endian layout errors, bitfield mask/shift misuse, queue count mismatches, threshold misconfiguration causing deadlock, and SGL mode selection bugs around the cached-SGE threshold. Test iSCSI/FCoE login, large and small SGL I/O, BDQ exhaustion/replenishment, queue initialization on multi-queue devices, termination with outstanding commands, and firmware ABI compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/storage_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/tcp_common.h -->
# sources/distributed-fs/ceph-client/include/linux/qed/tcp_common.h

Purpose: provides firmware-facing TCP offload data contracts for QED storage/network offload flows, including connection setup, update, upload, timers, and out-of-order placement metadata.

Important APIs and types: `struct ooo_opaque` carries LL2 out-of-order placement metadata. `enum tcp_connect_mode`, `enum tcp_ip_version`, and `enum tcp_seg_placement_event` classify connection role, IPv4/IPv6, and segment placement actions. `struct tcp_init_params` sets global timers. `struct tcp_offload_params` and `struct tcp_offload_params_opt2` encode MAC/VLAN/IP/port tuple, offload flags, flow label, TTL/TOS, MSS, window scales, RTT/cwnd/sequence state, keepalive and retransmission timers, delayed-ACK/Nagle/ECN flags, and optional SYN payload DMA. `struct tcp_update_params` carries changed-field flags and replacement values. `struct tcp_upload_params` exports firmware TCP state back to the host.

Control flow: a connection starts with init/offload parameters programmed into firmware; later parameter changes are sent through `tcp_update_params`; teardown or fallback can upload TCP sequence/window/timer state to the host stack. OOO metadata guides segment placement and drop decisions.

State and persistence: state lives in firmware connection contexts and host command buffers: sequence numbers, windows, timers, congestion-control variables, keepalive counters, and placement counters. It is runtime state reconstructed or uploaded during offload transitions.

Dependencies and integration points: integrates QED firmware with TCP offload consumers such as iSCSI. It depends on endian-specific integer layout and QED bitfield conventions.

Risks and test signals: risks include invalid byte order, stale sequence/window state on upload, incorrect changed-field flags, IPv6 address array ordering, keepalive/retransmission timer drift, and mismatch between `opt2` and full offload formats. Test active/passive connections, IPv4/IPv6, ECN/Nagle/keepalive toggles, MTU/MSS changes, retransmission and keepalive timeouts, OOO placement, and offload-to-host upload correctness under packet loss.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/tcp_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qnx6_fs.h -->
# sources/distributed-fs/ceph-client/include/linux/qnx6_fs.h

Purpose: defines on-disk QNX6 filesystem constants and structures used by the Linux QNX6 filesystem driver to parse superblocks, inodes, directory entries, long names, and Audi MMI variant metadata.

Important APIs and types: constants specify root inode, file status values, superblock/bootblock/directory/inode sizes, direct pointer count, indirect pointer depth, short/long filename sizes, and `QNX6_MOUNT_MMI_FS`. `struct qnx6_inode_entry` is the 128-byte on-disk inode. `struct qnx6_dir_entry`, `struct qnx6_long_dir_entry`, and `struct qnx6_long_filename` model directory records and long filename indirection. `struct qnx6_root_node` points to inode, bitmap, longfile, and unknown metadata trees. `struct qnx6_super_block` and `struct qnx6_mmi_super_block` represent standard and Audi MMI superblock layouts.

Control flow: mount code reads the boot/superblock area, validates magic/checksum/version/block size, chooses standard or MMI layout, then uses root nodes to find inode, bitmap, and long-name trees. Directory lookup interprets short entries directly or resolves long-name entries through the longfile area.

State and persistence: all structures are persistent on-disk filesystem metadata with filesystem-endian fields. In-memory state is derived by the QNX6 driver during mount and lookup.

Dependencies and integration points: depends on Linux integer/filesystem endian types and magic constants. It integrates the VFS inode/directory code with QNX6 disk format parsing.

Risks and test signals: risks include incorrect endian conversion, trusting malformed sizes/levels/pointers, long filename checksum errors, MMI layout confusion, and out-of-bounds indirect tree traversal. Test mounting standard and MMI QNX6 images, corrupted superblocks/checksums, long and short filenames, deleted/status variants, maximum file levels, and fuzzed directory entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qnx6_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/quota.h -->
# sources/distributed-fs/ceph-client/include/linux/quota.h

Purpose: defines the VFS quota core data model: quota identifier typing, in-memory quota blocks and quota-file information, dquot lifecycle state, format operations, filesystem quota operations, quotactl operation vectors, and state flags.

Important APIs and types: `enum quota_type` covers user, group, and project quotas with bit masks. `struct kqid` stores a typed kernel quota ID; helpers create, invalidate, and map IDs through user namespaces. `struct mem_dqblk`, `struct mem_dqinfo`, and `struct dquot` hold per-ID usage/limits/grace times, per-quota-file metadata, and active cached quota objects. `struct quota_format_ops`, `struct dquot_operations`, and `struct quotactl_ops` define format, dquot, and userspace control callbacks. `struct qc_dqblk`, `struct qc_info`, `struct qc_state`, and `struct qc_type_state` are filesystem-agnostic query/set payloads. `struct quota_info` is embedded in `super_block` and tracks active files, flags, formats, and locks.

Control flow: quotaon loads a format and `mem_dqinfo`; inode operations acquire or initialize relevant `dquot`s, charge/free blocks and inodes, mark dquots dirty, and write back through format ops. quotactl requests pass through `quotactl_ops` to read/set limits, state, and info. Remount and quotaoff disable, suspend, or release quota state.

State and persistence: persistent state is quota files and filesystem-specific quota metadata. In-memory state includes dquot hash/inuse/free/dirty lists, `dq_count`, flags, locks, `dq_off`, usage/reservation counters, grace times, quota statistics, and superblock quota flags.

Dependencies and integration points: depends on VFS `super_block`/inode concepts, user namespace UID/GID/projid mapping, percpu counters, quota format headers, UAPI quota constants, modules, locks, and optional netlink warnings.

Risks and test signals: risks include namespace mapping bugs, dquot lifetime races, dirty-list corruption, inconsistent reservation vs usage accounting, grace-time/warning misbehavior, project quota ID errors, and format callback mismatch. Test user/group/project quota enable/disable, remount suspend/resume, quota file formats v1/v2/XFS-facing paths, namespace mappings, delayed allocation reservation/claim/reclaim, dirty writeback, quota warnings, and concurrent inode ownership/size changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/quota.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/quotaops.h -->
# sources/distributed-fs/ceph-client/include/linux/quotaops.h

Purpose: exposes VFS quota operation helpers to filesystems and supplies no-op or inode-byte-accounting fallbacks when `CONFIG_QUOTA` is disabled.

Important APIs and types: `sb_dqopt()` returns the superblock's `quota_info`. `is_quota_modification()` detects attribute changes needing quota transfer. In quota builds, declarations include `dquot_initialize()`, `dqget()`, `dqgrab()`, `dqput()`, allocation/free/reservation helpers, quota on/off/load/sync/state functions, `dquot_transfer()`, and exported `dquot_operations`/`dquot_quotactl_sysfile_ops`. Inline status helpers test usage, limits, suspension, loaded, and active state. Common wrappers translate blocks to bytes via `inode->i_blkbits` and mark inodes dirty after successful accounting.

Control flow: filesystems call initialization before operations that charge quota, call allocation/reservation/free helpers during block and inode changes, transfer quota on owner/project changes, sync/writeback dirty dquots, and use quotaon/off helpers at mount or quotactl time. Disabled builds preserve basic `i_blocks`/byte accounting while accepting all quota operations.

State and persistence: state is owned by `quota.h` structures and filesystem quota files. This header controls when quota changes mark inodes dirty and when reservations are converted into real usage.

Dependencies and integration points: depends on VFS `fs.h`, quota core declarations, mount idmaps, inode dirtying, and filesystem block-size semantics. It is the normal integration point for filesystem write, truncate, chown, and quota-control paths.

Risks and test signals: risks include missing `dquot_initialize()`, incorrect block-to-byte shifts, inode dirtying omissions, nofail allocation masking quota failures, transfer races under `i_rwsem`, and disabled-config behavior diverging from quota-enabled behavior. Test quota enforcement during create/write/truncate/chown/project-ID changes, delayed allocation reserve/claim/reclaim, quota disabled builds, remount suspend/resume, quota sync/writeback, and ENOSPC/EDQUOT handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/quotaops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/radix-tree.h -->
# sources/distributed-fs/ceph-client/include/linux/radix-tree.h

Purpose: provides the legacy radix-tree API as an XArray-backed compatibility interface, including lookup, insert/delete, replacement, tag operations, gang lookup, preload, IDR free-slot search, and iteration macros.

Important APIs and types: `radix_tree_root` aliases `xarray`, and `radix_tree_node` aliases `xa_node`. `struct radix_tree_preload` manages per-CPU preallocated nodes protected by `local_lock_t`. Slot encoding uses low bits to distinguish data pointers, internal nodes, and value entries. `struct radix_tree_iter` tracks chunk index, next index, tag mask, and node. Key APIs include `radix_tree_insert()`, lookup/slot lookup, replace/delete, gang lookup, preload, tag set/clear/get/tagged, `radix_tree_next_chunk()`, `radix_tree_next_slot()`, and `radix_tree_for_each_slot()`/`radix_tree_for_each_tagged()`.

Control flow: users optionally preload nodes, perform locked updates to insert/delete/tag/replace entries, and may perform selected lockless lookups under RCU. Iteration proceeds by chunks found from `next_index`; tagged iteration consumes a per-chunk tag bitmask, and retry/resume helpers handle concurrent modification or lock dropping.

State and persistence: state is in-memory XArray/radix-tree nodes, root flags/tags, per-node slots/tags, and per-CPU preload lists. No persistence exists.

Dependencies and integration points: depends on bitops, GFP, list, lockdep, percpu, preempt, RCU, spinlocks, XArray, and local locks. It integrates older radix-tree users with the modern XArray implementation.

Risks and test signals: risks include storing misaligned/value/internal-looking pointers, freeing objects before RCU readers finish, relying on tag reads under concurrent updates, iterator misuse after deletion, preload local-lock imbalance, and legacy API assumptions diverging from XArray behavior. Test lockless lookup under RCU, concurrent insert/delete/tag operations, gang lookup/tagged lookup, iterator retry/resume, IDR allocation paths, and memory pressure with preload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/radix-tree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/raid/detect.h -->
# sources/distributed-fs/ceph-client/include/linux/raid/detect.h

Purpose: declares Linux MD RAID autodetection hooks used by block-device discovery and early setup.

Important APIs and types: `md_autodetect_dev(dev_t dev)` records a block device for MD autodetection. `md_run_setup()` is available when `CONFIG_BLK_DEV_MD` is enabled and becomes an inline no-op otherwise.

Control flow: early block-device probing can call `md_autodetect_dev()` for candidate devices; later setup calls `md_run_setup()` to assemble detected arrays when MD support is built.

State and persistence: this header stores no state. The MD subsystem owns any autodetect lists and assembled array state; persistence is on-disk RAID metadata.

Dependencies and integration points: integrates device-number based block discovery with the MD driver and init/setup paths.

Risks and test signals: risks include no-op behavior in non-MD builds, duplicate/autodetect ordering issues, and stale device-number assumptions during early boot. Test builds with and without `CONFIG_BLK_DEV_MD`, boot-time autodetection of legacy MD arrays, duplicate candidates, and degraded arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/raid/detect.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/raid/pq.h -->
# sources/distributed-fs/ceph-client/include/linux/raid/pq.h

Purpose: declares RAID6 P/Q syndrome generation, recovery algorithms, Galois-field tables, algorithm selection, and user-space test scaffolding for the RAID6 library.

Important APIs and types: `struct raid6_calls` contains `gen_syndrome`, `xor_syndrome`, `valid`, algorithm name, and priority. `struct raid6_recov_calls` contains two-data and data-plus-P recovery functions. Externs list scalar and architecture-optimized implementations for MMX/SSE/AVX/AVX512/Altivec/S390/NEON/LoongArch/RISC-V variants. `raid6_call`, `raid6_select_algo()`, `raid6_2data_recov`, `raid6_datap_recov()`, `raid6_dual_recov()`, and GF tables form the public surface. `raid6_get_zero_page()` supplies a zero page in kernel or test mode.

Control flow: initialization benchmarks or validates available algorithms, chooses `raid6_call`, and sets recovery function pointers. RAID5/6 code calls syndrome generation on writes and recovery functions when one or two devices are missing.

State and persistence: runtime state is selected function pointers and immutable GF tables. Persistent data is array parity on disks, not owned here.

Dependencies and integration points: depends on kernel block/MM headers in-kernel and provides replacements for userspace test builds. It integrates MD RAID5/6, crypto-like optimized math routines, and architecture feature detection.

Risks and test signals: risks include wrong CPU feature `valid()` checks, SIMD state handling, GF table alignment, algorithm priority mistakes, and recovery corruption for edge disk counts/byte sizes. Test RAID6 selftests/benchmarks, syndrome consistency across all algorithms, degraded one/two-disk recovery, unaligned sizes, userspace test builds, and CPU hotplug/feature variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/raid/pq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/raid/xor.h -->
# sources/distributed-fs/ceph-client/include/linux/raid/xor.h

Purpose: declares the generic XOR generation entry point used by RAID parity code.

Important APIs and types: `xor_gen(void *dest, void **srcs, unsigned int src_cnt, unsigned int bytes)` XORs `src_cnt` source buffers into `dest` for `bytes` bytes.

Control flow: RAID code calls `xor_gen()` to build or update parity from data stripes; implementation selection lives outside this header.

State and persistence: no state is kept here. The output buffer contributes to persistent RAID parity only after higher layers write it.

Dependencies and integration points: integrates MD RAID parity paths with architecture-optimized XOR implementations.

Risks and test signals: risks include overlapping buffers, zero/one source edge cases, unaligned lengths, and optimized implementation mismatch. Test parity generation against a scalar reference, varied source counts, unaligned buffer/length combinations, and degraded RAID rebuilds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/raid/xor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/raid_class.h -->
# sources/distributed-fs/ceph-client/include/linux/raid_class.h

Purpose: defines the generic SCSI transport-style RAID class used to expose RAID level, state, resync progress, and components through the device model.

Important APIs and types: `struct raid_template` wraps a `transport_container`. `struct raid_function_template` supplies driver callbacks for RAID detection, resync, and state refresh. `enum raid_state` and `enum raid_level` classify exported status. `struct raid_data` stores component list/count, level, state, and resync value. `DEFINE_RAID_ATTRIBUTE()` generates inline setter/getter helpers for `level`, `resync`, and `state`. `raid_class_attach()` and `raid_class_release()` manage templates.

Control flow: a lower driver attaches a RAID class template, class devices are associated with real devices, callbacks refresh state, and generated setters/getters update the class device's `raid_data`.

State and persistence: state is device-model runtime state; real RAID metadata and persistence are owned by the hardware, firmware, or MD layer.

Dependencies and integration points: depends on `transport_class.h`, device model attributes, driver data, and component lists. It integrates SCSI/storage drivers with user-visible RAID status.

Risks and test signals: risks include missing class device causing `BUG_ON`, stale resync/state values, component list lifetime, and mismatch between driver callback output and class attributes. Test attach/release, sysfs attribute reads, hot-unplug during reads, resync progress updates, and all RAID level/state mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/raid_class.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ramfs.h -->
# sources/distributed-fs/ceph-client/include/linux/ramfs.h

Purpose: declares the ramfs filesystem helpers, operations, mount-parameter table, and NOMMU expansion hook.

Important APIs and types: `ramfs_get_inode()` allocates ramfs inodes; `ramfs_init_fs_context()` initializes mount context; `ramfs_kill_sb()` tears down a superblock. `ramfs_nommu_expand_for_mapping()` is a no-op with MMU and an extern for NOMMU. Externs expose `ramfs_fs_parameters`, `ramfs_file_operations`, and `generic_file_vm_ops`.

Control flow: mount creates an fs context, fills a superblock, allocates inodes through `ramfs_get_inode()`, and uses generic file/mmap operations. NOMMU mappings may need explicit file growth before mapping.

State and persistence: ramfs data lives only in page cache/inodes and is not persistent. There is no backing store or writeback.

Dependencies and integration points: depends on VFS fs context and parser machinery, file operations, VM operations, and NOMMU support. It is a simple in-memory filesystem integration point for initramfs-like users.

Risks and test signals: risks include unbounded memory growth, incorrect NOMMU expansion, mount-parameter parsing drift, and inode mode/device handling. Test mount/unmount, file/dir/device inode creation, mmap/read/write, NOMMU builds, and memory pressure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ramfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/random.h -->
# sources/distributed-fs/ceph-client/include/linux/random.h

Purpose: declares the kernel random-number and entropy-input API, including device/input/interrupt/hardware entropy injection, byte and scalar random output, bounded uniform integer helpers, initialization readiness, VM fork notifications, CPU hotplug hooks, and `/dev/random` file operations.

Important APIs and types: entropy input functions include `add_device_randomness()`, bootloader/input/interrupt/hwgenerator variants, and `add_latent_entropy()`. Output functions include `get_random_bytes()`, `get_random_u8/u16/u32/u64()`, `get_random_long()`, `get_random_u32_below()`, `get_random_u32_above()`, and `get_random_u32_inclusive()`. Initialization APIs include `random_init_early()`, `random_init()`, `rng_is_initialized()`, `wait_for_random_bytes()`, `execute_with_initialized_rng()`, and `get_random_bytes_wait()`. Optional VMGENID and SMP hooks handle VM fork reseeding and CPU state.

Control flow: boot adds early entropy, initializes RNG state, later producers mix environmental entropy, and consumers either read immediately or wait for initialization. Bounded helpers use reciprocal multiplication with rejection to avoid modulo bias and specialize constant ceilings at compile time.

State and persistence: RNG state is global in-kernel cryptographic state plus per-CPU/backend state outside this header. It is runtime-only but may be reseeded by bootloader, devices, interrupts, hardware RNGs, and VM-generation events.

Dependencies and integration points: depends on UAPI random definitions, notifier blocks, file operations, latent entropy plugin, VMGENID, SMP hotplug, and kernel math/build assertions. It integrates crypto/security-sensitive consumers, device drivers, boot code, and character devices.

Risks and test signals: risks include use before initialization where blocking is required, zero/overflow bounds, modulo bias regressions, entropy over-crediting, VM clone reuse, and hotplug reseeding bugs. Test boot readiness, `get_random_u32_below()` boundaries and distribution, VM fork notifier paths, hardware RNG injection, CPU online/offline hooks, and `/dev/random`/`urandom` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/random.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/randomize_kstack.h -->
# sources/distributed-fs/ceph-client/include/linux/randomize_kstack.h

Purpose: implements the architecture-agnostic macro used by syscall entry paths to add a bounded random stack offset for stack-layout hardening when `CONFIG_RANDOMIZE_KSTACK_OFFSET` is enabled.

Important APIs and types: `randomize_kstack_offset` is a static key controlling enablement. `__kstack_alloca` selects uninitialized alloca when supported. `KSTACK_OFFSET_MAX()` masks random values to a bounded, alignment-friendly range. `DECLARE_PER_CPU(struct rnd_state, kstack_rnd_state)` stores per-CPU PRNG state. `get_kstack_offset()` samples per-CPU random state, and `add_random_kstack_offset()` performs the stack allocation and compiler barrier.

Control flow: syscall entry invokes `add_random_kstack_offset()` after user registers are stored. If the static branch is enabled, it samples a per-CPU PRNG value, masks it to the maximum offset, allocates that much stack with alloca, and uses inline asm to keep the allocation live.

State and persistence: runtime state is per-CPU pseudo-random state and the static-key enable flag. No persistent data is stored.

Dependencies and integration points: depends on jump labels, percpu definitions, `prandom`, compiler builtins, stack initialization behavior, and syscall entry architecture code.

Risks and test signals: risks include excessive stack use, compiler optimizing away the allocation, unwanted stack zeroing overhead, use in unsafe noinstr contexts, per-CPU PRNG quality, and architecture alignment mismatches. Test enabled/disabled configs, runtime static-key toggling, LKDTM stack entropy selftest, syscall stress under small stacks, and GCC/Clang code generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/randomize_kstack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/range.h -->
# sources/distributed-fs/ceph-client/include/linux/range.h

Purpose: defines a simple inclusive `u64` range helper type and operations for adding, merging, subtracting, sorting, and cleaning range arrays.

Important APIs and types: `struct range` has inclusive `start` and `end`. Inline helpers include `range_len()`, `range_contains()`, `range_overlaps()`, and `DEFINE_RANGE()`. Extern functions include `add_range()`, `add_range_with_merge()`, `subtract_range()`, `clean_sort_range()`, and `sort_range()`.

Control flow: callers maintain a fixed-size array of ranges, add or merge intervals, subtract excluded intervals, then sort and clean overlapping or invalid entries before consuming the result.

State and persistence: state is caller-owned in-memory range arrays. There is no persistence.

Dependencies and integration points: depends only on Linux types and is commonly useful for memory/resource maps, firmware reservations, and architecture setup code.

Risks and test signals: risks include inclusive-end overflow in `range_len()`, invalid `start > end` ranges, array capacity truncation, merge/subtract boundary mistakes, and unsorted input assumptions. Test adjacent/overlapping/disjoint intervals, zero-length single-element ranges, full `u64` boundaries, subtraction splitting, and capacity exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/range.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ras.h -->
# sources/distributed-fs/ceph-client/include/linux/ras.h

Purpose: declares Reliability, Availability, and Serviceability hooks for debugfs consumers, corrected-error collection, CPER event logging, ARM hardware error logging, AMD address translation/row retirement, and MPIDR-to-logical CPU mapping.

Important APIs and types: debugfs helpers include `ras_userspace_consumers()`, `ras_debugfs_init()`, and `ras_add_daemon_trace()`. `parse_cec_param()` is available for corrected-error collection. `log_non_standard_event()` and `log_arm_hw_error()` report CPER-style records when `CONFIG_RAS` is enabled. `struct atl_err` carries AMD translation input (`addr`, `ipid`, `cpu`). AMD ATL hooks register/unregister decoders, retire DRAM rows, and convert UMC MCA addresses. `GET_LOGICAL_INDEX()` maps ARM MPIDR to CPU index where supported.

Control flow: platform error handlers parse machine-check/firmware records, log standard or non-standard CPER sections, optionally notify userspace/debugfs consumers, and use AMD or ARM helpers for address/CPU translation.

State and persistence: this header owns no state. Logged errors may reach trace buffers, debugfs, firmware-first logs, or userspace daemons; hardware row retirement has platform persistence outside this header.

Dependencies and integration points: depends on errno, UUID/GUID, CPER, debugfs, AMD ATL, ARM SMP platform headers, and RAS configs. It integrates EDAC/MCE/APEI-style reporting with architecture/platform decoders.

Risks and test signals: risks include disabled-config no-op surprises, wrong severity/section lengths, MPIDR mapping errors, AMD decoder registration races, and address translation failures. Test config matrices, CPER non-standard and ARM records, corrected-error parameter parsing, AMD UMC address conversion, row retirement paths, and userspace RAS daemon detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ras.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/raspberrypi/vchiq.h -->
# sources/distributed-fs/ceph-client/include/linux/raspberrypi/vchiq.h

Purpose: defines the public in-kernel VCHIQ client API for Raspberry Pi VideoCore communication: service setup, callbacks, message queuing, message release/hold, bulk transfers, and version/userdata queries.

Important APIs and types: `VCHIQ_MAKE_FOURCC()` builds service identifiers. `enum vchiq_reason` reports service opened/closed, message availability, and bulk completion/abort reasons. `enum vchiq_bulk_mode` selects callback, blocking, no-callback, or internal waiting behavior. `enum vchiq_service_option` controls autoclose, quotas, synchronous mode, and tracing. `struct vchiq_header`, `struct vchiq_element`, `struct vchiq_service_base`, `struct vchiq_completion_data_kernel`, and `struct vchiq_service_params_kernel` define callbacks and message payload metadata. API functions cover instance initialization/shutdown/connect, service open/close/use/release, queue/release/hold message, bulk transmit/receive, userdata, and peer version.

Control flow: a client initializes an instance, connects to the firmware side, opens a FOURCC service, receives callbacks for messages or bulk completions, releases message headers after processing, and can queue in-band or bulk data.

State and persistence: state is per-instance/service runtime state in VCHIQ core structures and shared memory; messages and bulk transfers are transient.

Dependencies and integration points: integrates kernel clients with the VCHIQ core, character-device/user interfaces, and Raspberry Pi firmware/VideoCore services.

Risks and test signals: risks include callback reentrancy, failure to release messages, mismatched service versions, invalid handles, bulk mode confusion, and user pointer lifetime for callback userdata. Test service open/close, callback delivery order, message hold/release, peer-version negotiation, blocking and callback bulk transfers, abort paths, and shutdown with pending messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/raspberrypi/vchiq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/raspberrypi/vchiq_arm.h -->
# sources/distributed-fs/ceph-client/include/linux/raspberrypi/vchiq_arm.h

Purpose: defines the ARM-host side VCHIQ management structures for driver state, user instances/services, completion queues, bulk waiters, debugfs nodes, character-device registration, and service use/release management.

Important APIs and types: constants set per-instance completion, service, element, message queue, and deferred-callback limits. `struct vchiq_platform_info` records cache-line size. `struct vchiq_drv_mgmt` owns firmware handle, platform info, connection state, deferred callbacks, fragment buffers/semaphores, MMIO registers, and `vchiq_state`. `struct user_service` tracks a service visible to userspace, message queue positions, completion events, and close/dequeue state. `struct bulk_waiter_node` links blocking bulk waiters by PID. `struct vchiq_instance` owns completions, mutexes, connection/closing flags, PID, tracing, bulk waiter list, and debugfs node.

Control flow: platform probe initializes `vchiq_drv_mgmt`, registers cdev if configured, creates instances, dispatches service callbacks into completion/message queues, and coordinates service use/release to keep firmware resources active while clients hold references.

State and persistence: all state is runtime host-side state: queues, completions, semaphores, fragments, connection flags, and debugfs nodes. It does not persist across driver unload or reboot.

Dependencies and integration points: depends on platform devices, firmware API, semaphores, mutexes, atomics, VCHIQ core/debugfs, optional cdev support, and user-copy-facing service data.

Risks and test signals: risks include completion queue overflow, fragment allocator races, close/dequeue ordering, leaked bulk waiters, cdev disabled behavior, and connected callback ordering. Test character-device and in-kernel client paths, many concurrent services, close with queued messages, blocking bulk cancellation, debugfs lifetime, driver unbind, and firmware reconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/raspberrypi/vchiq_arm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/raspberrypi/vchiq_bus.h -->
# sources/distributed-fs/ceph-client/include/linux/raspberrypi/vchiq_bus.h

Purpose: defines the VCHIQ bus abstraction used to register VCHIQ child devices and bind kernel VCHIQ client drivers through the Linux device model.

Important APIs and types: `struct vchiq_device` embeds a `struct device` and points to `vchiq_drv_mgmt`. `struct vchiq_driver` supplies `probe`, `remove`, `resume`, `suspend`, an ID table, and embedded `device_driver`. Helpers `to_vchiq_device()` and `to_vchiq_driver()` perform container conversion. Externs expose `vchiq_bus_type`, `vchiq_device_register()`, `vchiq_device_unregister()`, `vchiq_driver_register()`, and `vchiq_driver_unregister()`. `module_vchiq_driver()` wraps module init/exit registration.

Control flow: the core registers VCHIQ devices under a parent device; client drivers register against `vchiq_bus_type`; probe/remove and PM callbacks are dispatched through the bus.

State and persistence: device-model runtime state is stored in `struct device`, `struct vchiq_device`, and driver bindings. No persistent state is stored.

Dependencies and integration points: depends on Linux device model, module driver helpers, mod_devicetable IDs, PM messages, and VCHIQ management state.

Risks and test signals: risks include device/driver lifetime mismatches, missing ID tables, PM callback ordering around firmware connection state, and parent unbind races. Test driver registration/unregistration, probe/remove failure paths, suspend/resume, module unload, and multiple VCHIQ child devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/raspberrypi/vchiq_bus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/raspberrypi/vchiq_cfg.h -->
# sources/distributed-fs/ceph-client/include/linux/raspberrypi/vchiq_cfg.h

Purpose: centralizes VCHIQ protocol versioning, shared-memory limits, slot/service counts, bulk queue sizing, and default debug/statistics enablement.

Important APIs and types: `VCHIQ_MAGIC`, `VCHIQ_VERSION`, `VCHIQ_VERSION_MIN`, and feature-version constants define compatibility. Resource constants include maximum states, services, slots, slots per side, current bulks, and service bulks. `VCHIQ_ENABLE_DEBUG` and `VCHIQ_ENABLE_STATS` default to enabled unless overridden.

Control flow: initialization writes and validates version/magic/resource values in shared memory; service open/version negotiation uses the compatibility constants; queue allocation and array sizing use max counts.

State and persistence: no state is stored here. Values shape shared-memory layout and runtime arrays.

Dependencies and integration points: depends on `VCHIQ_MAKE_FOURCC()` from `vchiq.h` and is consumed by `vchiq_core.h` and implementation files.

Risks and test signals: risks include incompatible version changes without updating `VERSION_MIN`, resource constants mismatching firmware, and debug/stat fields altering layout or overhead. Test version negotiation with firmware, max service/slot/bulk boundaries, debug/stat enabled and disabled builds, and shared-memory layout validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/raspberrypi/vchiq_cfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/raspberrypi/vchiq_core.h -->
# sources/distributed-fs/ceph-client/include/linux/raspberrypi/vchiq_core.h

Purpose: defines the internal VCHIQ protocol state machine, shared-memory layout, service and bulk queues, slot accounting, remote events, quotas, debug/stat counters, core lookup/reference helpers, and platform hooks for Raspberry Pi VideoCore messaging.

Important APIs and types: constants define slot size, message max, queue masks, and service handle invalid value. Debug macros track selected line/value/count fields when enabled. `enum vchiq_connstate`, service state constants, and `enum vchiq_bulk_dir` define connection/service/bulk state. Core structures include `struct vchiq_bulk`, `struct vchiq_bulk_queue`, `struct remote_event`, `struct vchiq_slot`, `struct vchiq_slot_info`, `struct vchiq_service`, `struct vchiq_service_quota`, `struct vchiq_shared_state`, `struct vchiq_slot_zero`, `struct vchiq_state`, `struct pagelist`, `struct vchiq_pagelist_info`, `struct bulk_waiter`, and `struct vchiq_config`. Functions initialize slots/state, connect, add/open/close/terminate/free services, queue messages, process bulk waits/callbacks, find services by handle/port/instance, refcount services, dump debug state, set service options, and signal platform use/release/connection changes.

Control flow: platform init creates slot-zero shared memory, local/remote shared states, slot queues, and handler/recycle/sync threads. Services move through listening/opening/open/close states. Messages are written to slots, remote events wake the peer, slot handlers parse incoming messages, and released slots are recycled. Bulk transfers use per-service TX/RX queues and pagelist DMA metadata. Quotas and poll bitsets coordinate flow control and callbacks.

State and persistence: all state is runtime shared memory or host private state: connection state, service table under RCU, slot queues, tx/rx positions, quotas, completions, kthreads, wait queues, bulk queues, DMA pagelists, stats, and platform state. It does not persist, but must remain coherent across host/VPU ownership transitions.

Dependencies and integration points: depends on VCHIQ public/config headers, completions, DMA mapping, kthreads, krefs, RCU, seq_file dumping, spinlocks, wait queues, device logging, and Raspberry Pi firmware/platform hooks. It is the central integration surface between kernel clients, cdev users, firmware, DMA, and debugfs.

Risks and test signals: risks include shared-memory ABI mismatch, remote event lost wakeups, service refcount/RCU lifetime errors, quota deadlocks, slot ownership bugs, bulk DMA mapping leaks, pagelist page release mistakes, synchronous-channel starvation, and close/remove races with callbacks. Test connection state transitions, max-slot pressure, message queue full paths, service open/close/autoclose, synchronous services, bulk transmit/receive/abort, DMA mapping errors, firmware reset, debug dumps, and RCU/service lookup under concurrent close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/raspberrypi/vchiq_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/raspberrypi/vchiq_debugfs.h -->
# sources/distributed-fs/ceph-client/include/linux/raspberrypi/vchiq_debugfs.h

Purpose: declares VCHIQ debugfs integration for global state and per-instance debug nodes.

Important APIs and types: `struct vchiq_debugfs_node` stores a `struct dentry *`. Functions include `vchiq_debugfs_init()`, `vchiq_debugfs_deinit()`, `vchiq_debugfs_add_instance()`, and `vchiq_debugfs_remove_instance()`.

Control flow: driver/core initialization creates debugfs roots for a `vchiq_state`; instances are added and removed as clients open/close; deinit tears down the debugfs hierarchy.

State and persistence: debugfs dentries and per-instance nodes are runtime diagnostic state only.

Dependencies and integration points: integrates VCHIQ core/instance state with debugfs. The header forward-declares VCHIQ types and leaves debugfs implementation details in source files.

Risks and test signals: risks include stale dentries after instance removal, debugfs disabled build assumptions, teardown races with readers, and leaking per-instance nodes. Test mount/unmount debugfs, instance add/remove while reading files, driver unload, and multiple concurrent instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/raspberrypi/vchiq_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ratelimit.h -->
# sources/distributed-fs/ceph-client/include/linux/ratelimit.h

Purpose: provides helper routines and warning macros around `struct ratelimit_state` for suppressing repeated kernel messages.

Important APIs and types: `ratelimit_state_init()`, `ratelimit_default_init()`, miss counter helpers, `ratelimit_state_reset_interval()`, `ratelimit_state_exit()`, and `ratelimit_set_flags()` manage a ratelimit state. `printk_ratelimit_state` is the global printk state. `WARN_ON_RATELIMIT()` and `WARN_RATELIMIT()` emit warnings only when `__ratelimit()` permits them under `CONFIG_PRINTK`.

Control flow: callers initialize a state with interval/burst, call `__ratelimit()` directly or through macros before emitting messages, count missed events, optionally reset intervals, and report suppressed counts on release if configured.

State and persistence: state is in-memory per ratelimit object: raw spinlock, interval, burst, remaining count, missed count, flags, and begin timestamp.

Dependencies and integration points: depends on ratelimit types, scheduler `current`, spinlocks, atomics, printk/WARN infrastructure, and `___ratelimit()`.

Risks and test signals: risks include using uninitialized states, interval reset races, missing suppressed-line accounting, disabled printk semantic changes, and hot-path overhead. Test burst/interval boundaries, concurrent callers, reset while active, `RATELIMIT_MSG_ON_RELEASE`, disabled interval, and `CONFIG_PRINTK=n` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ratelimit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ratelimit_types.h -->
# sources/distributed-fs/ceph-client/include/linux/ratelimit_types.h

Purpose: defines the ratelimit state structure, default interval/burst constants, flags, initializers, and the `__ratelimit()` wrapper macro.

Important APIs and types: defaults are `DEFAULT_RATELIMIT_INTERVAL` of five seconds and `DEFAULT_RATELIMIT_BURST` of ten. Flags include `RATELIMIT_MSG_ON_RELEASE` and `RATELIMIT_INITIALIZED`. `struct ratelimit_state` stores a raw spinlock, interval, burst, atomic remaining count, atomic missed count, flags, and begin time. Initializer macros include `RATELIMIT_STATE_INIT_FLAGS`, `RATELIMIT_STATE_INIT`, disabled initializer, and `DEFINE_RATELIMIT_STATE`. `___ratelimit()` is the external implementation, with `__ratelimit(state)` passing `__func__`.

Control flow: static or dynamic callers initialize `ratelimit_state`, then `___ratelimit()` updates counters and determines whether an event should be emitted.

State and persistence: all state is runtime memory in each `ratelimit_state`.

Dependencies and integration points: depends on bit macros, HZ, raw spinlock types, and atomics. It is shared by printk, WARN, networking, drivers, and other throttled logging paths.

Risks and test signals: risks include initializer drift, atomic count underflow, wrong HZ-derived intervals, and disabled-state interpretation. Test static initialization, dynamic initialization, disabled interval behavior, multi-CPU contention, and suppressed message accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ratelimit_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rational.h -->
# sources/distributed-fs/ceph-client/include/linux/rational.h

Purpose: declares a helper for finding the best bounded rational approximation to a given fraction, commonly used for clock, PLL, and divider programming.

Important APIs and types: `rational_best_approximation(given_numerator, given_denominator, max_numerator, max_denominator, best_numerator, best_denominator)` computes a numerator/denominator pair within provided limits.

Control flow: drivers call the helper with a target ratio and hardware numerator/denominator maxima, then program registers from the returned approximation.

State and persistence: no state is stored.

Dependencies and integration points: integrates generic continued-fraction style approximation logic with clock/media/display/audio drivers that need constrained ratios.

Risks and test signals: risks include zero denominators, overflow in intermediate products, tie-breaking surprises, and hardware maxima that cannot represent a useful ratio. Test exact ratios, prime/coprime ratios, zero/one limits, large unsigned-long boundaries, and known PLL divider examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rational.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rbtree.h -->
# sources/distributed-fs/ceph-client/include/linux/rbtree.h

Purpose: exposes Linux's intrusive red-black tree API, including core insertion/erase/replacement, traversal, cached-leftmost trees, linked-node trees, and generic find/add helpers that let users supply comparison callbacks without per-node virtual dispatch.

Important APIs and types: `rb_parent()`, `rb_entry()`, `RB_EMPTY_ROOT()`, and node clear/empty macros manage node state. Core externs include `rb_insert_color()`, `rb_erase()`, `rb_erase_linked()`, `rb_next()`, `rb_prev()`, postorder traversal, `rb_replace_node()`, and RCU replacement. Inline helpers include `rb_first()`, `rb_last()`, `rb_link_node()`, `rb_link_node_rcu()`, cached insert/erase/replace, `rb_add()`, `rb_add_cached()`, `rb_add_linked()`, `rb_find_add()`, `rb_find_add_cached()`, `rb_find_add_rcu()`, `rb_find()`, `rb_find_rcu()`, `rb_find_first()`, `rb_next_match()`, and `rb_for_each()`.

Control flow: callers implement comparison/search logic, link a node under the located parent, then rebalance with insert helpers. Erase removes and rebalances. Cached roots maintain O(1) leftmost access. RCU helpers publish pointers with release semantics but still require serialized writers and grace-period-safe object lifetime.

State and persistence: state is caller-owned intrusive tree nodes and roots in memory. Linked nodes add prev/next ordering links; cached roots store leftmost. No persistence is provided.

Dependencies and integration points: depends on container macros, rbtree type definitions, RCU, and standard kernel macros. It is used broadly for ordered indexes such as VMAs, timers, extents, and scheduler structures.

Risks and test signals: risks include double insertion without `RB_CLEAR_NODE`, comparison functions that violate ordering, RCU false negatives during rotations, missing writer serialization, stale cached leftmost, and freeing nodes before readers finish. Test insert/find/erase ordering, duplicate-key handling, cached leftmost updates, postorder destruction, RCU lookup under concurrent replacement, and linked-node prev/next consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rbtree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rbtree_augmented.h -->
# sources/distributed-fs/ceph-client/include/linux/rbtree_augmented.h

Purpose: provides augmented red-black tree support, where user-maintained aggregate data is propagated, copied, and rotated consistently during insert and erase rebalancing.

Important APIs and types: `struct rb_augment_callbacks` supplies `propagate`, `copy`, and `rotate` callbacks. Public helpers include `rb_insert_augmented()`, `rb_insert_augmented_cached()`, `rb_add_augmented_cached()`, `rb_erase_augmented()`, and `rb_erase_augmented_cached()`. Template macros `RB_DECLARE_CALLBACKS()` and `RB_DECLARE_CALLBACKS_MAX()` generate callbacks for common subtree aggregate patterns. Implementation helpers define RB colors, parent/color setters, child replacement, RCU child replacement, and `__rb_erase_augmented()`.

Control flow: users update augmented data on the insertion path before linking, then call augmented insert so rotations update aggregates. Erase selects simple or successor cases, uses `copy()` when a successor replaces a node, propagates changed aggregates, then rebalances with rotation callbacks if needed.

State and persistence: state is caller-owned tree nodes plus caller-defined augmented fields, usually subtree maxima/minima or interval metadata. No persistence exists.

Dependencies and integration points: depends on generic rbtree and RCU helpers. It underpins interval trees and other ordered indexes needing subtree summaries.

Risks and test signals: risks include incorrect compute callbacks, failure to update the insertion path before rebalance, stale augmented data after erase successor replacement, cached-leftmost drift, and RCU replacement ordering errors. Test interval queries after random insert/delete, rotations, duplicate ranges, cached augmented roots, and debug validation of aggregate fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rbtree_augmented.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rbtree_latch.h -->
# sources/distributed-fs/ceph-client/include/linux/rbtree_latch.h

Purpose: implements latched red-black trees that maintain two tree copies coordinated by `seqcount_latch_t`, allowing lockless lookups even from contexts such as NMI where readers cannot retry by blocking writers.

Important APIs and types: `struct latch_tree_node` embeds two `rb_node`s. `struct latch_tree_root` stores a latch seqcount and two `rb_root`s. `struct latch_tree_ops` supplies `less` and `comp` operators. Internal helpers insert, erase, and find in one indexed tree. Public helpers are `latch_tree_insert()`, `latch_tree_erase()`, and `latch_tree_find()`.

Control flow: serialized writers update tree 0, flip the latch, update tree 1, then end the latch update so at least one tree copy is stable. Readers sample the latch sequence, search the indicated tree with RCU dereferences, and retry if the latch changed.

State and persistence: state is in-memory dual rbtrees and per-node dual links. Removed nodes must survive an RCU grace period before reuse/free.

Dependencies and integration points: depends on rbtree, seqlock latch, and RCU. It integrates ordered lookup with tracing/perf/NMI-style contexts requiring unconditional lockless access.

Risks and test signals: risks include non-serialized writers, freeing nodes before grace period, comparator inconsistency between insert and lookup, assuming iteration stability, and missing RCU read-side protection. Test concurrent insert/erase/find, NMI-like lockless lookups, duplicate-key behavior, RCU delayed free, and randomized ordering validation across both tree copies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rbtree_latch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rbtree_types.h -->
# sources/distributed-fs/ceph-client/include/linux/rbtree_types.h

Purpose: defines the minimal red-black tree node and root types shared by rbtree users without pulling in the full operation API.

Important APIs and types: `struct rb_node` stores parent/color in one aligned word plus left and right children. `struct rb_node_linked` adds prev/next links around an embedded `rb_node`. `struct rb_root`, `struct rb_root_cached`, and `struct rb_root_linked` represent plain, leftmost-cached, and linked-leftmost trees. Initializer macros are `RB_ROOT`, `RB_ROOT_CACHED`, and `RB_ROOT_LINKED`.

Control flow: callers embed one of the node types in their own objects, initialize a root, then use operations from `rbtree.h` or augmented/latch variants.

State and persistence: state is intrusive in-memory tree topology. Color is encoded in parent low bits, relying on node alignment.

Dependencies and integration points: standalone type header used by low-level code that needs declarations without rbtree helper macros.

Risks and test signals: risks include alignment assumptions on unusual architectures, copying live nodes, embedding one node in multiple trees at once, and failing to initialize roots. Test architecture builds, static initializers, linked tree insertion/erase, and debug checks for empty/linked node state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rbtree_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rcu_node_tree.h -->
# sources/distributed-fs/ceph-client/include/linux/rcu_node_tree.h

Purpose: computes the compile-time hierarchy shape of TREE RCU/SRCU combining nodes based on `NR_CPUS`, `CONFIG_RCU_FANOUT`, and `CONFIG_RCU_FANOUT_LEAF`.

Important APIs and types: macros define fanout defaults, `RCU_FANOUT_1` through `RCU_FANOUT_4`, `RCU_NUM_LVLS`, per-level node counts, total `NUM_RCU_NODES`, level initializer arrays, node-name initializers, and force-quiescent-state node-name initializers. It emits a compile error if the configured fanout cannot cover `NR_CPUS`.

Control flow: RCU and SRCU structures use these macros at compile time to size arrays and initialize hierarchy metadata. The hierarchy limits contention by escalating only one contender per lower-level group.

State and persistence: no runtime state is stored here, but the macros determine the size/layout of RCU node arrays compiled into the kernel.

Dependencies and integration points: depends on `NR_CPUS`, RCU Kconfig values, and `DIV_ROUND_UP`. It is included by RCU internals and TREE SRCU because `srcu_struct` sizing depends on it.

Risks and test signals: risks include insufficient fanout for large CPU counts, poor fanout choices causing contention, and ABI/layout changes for SRCU structures. Test compile matrices for small and very large `NR_CPUS`, 32-bit vs 64-bit defaults, custom fanout values, CPU hotplug stress, and RCU torture scalability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rcu_node_tree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rcu_notifier.h -->
# sources/distributed-fs/ceph-client/include/linux/rcu_notifier.h

Purpose: declares optional RCU CPU stall notifier registration APIs without forcing inclusion of the full RCU update header.

Important APIs and types: action constants `RCU_STALL_NOTIFY_NORM` and `RCU_STALL_NOTIFY_EXP` distinguish normal and expedited stall notifications. When stall notifier support is enabled, `rcu_stall_chain_notifier_register()` and `rcu_stall_chain_notifier_unregister()` register a notifier block; otherwise inline fallbacks return `-EEXIST` and `-ENOENT`.

Control flow: diagnostics or platform code register a notifier to observe RCU stall warnings. RCU stall detection invokes the chain with the appropriate action when configured.

State and persistence: notifier-chain state is owned by RCU internals when enabled. This header has no persistence.

Dependencies and integration points: depends conditionally on notifier and type headers, and on `CONFIG_RCU_STALL_COMMON` plus `CONFIG_RCU_CPU_STALL_NOTIFIER`.

Risks and test signals: risks include code assuming registration succeeds in Tiny/disabled configs, notifier callback deadlocks during stall handling, and action-code drift. Test config-enabled/disabled builds, register/unregister error handling, induced RCU stalls, and notifier callback robustness under distressed systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rcu_notifier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rcu_segcblist.h -->
# sources/distributed-fs/ceph-client/include/linux/rcu_segcblist.h

Purpose: defines simple and segmented RCU callback-list structures used by RCU and TREE SRCU to track callbacks across grace-period phases and optional no-CB CPU offloading.

Important APIs and types: `struct rcu_cblist` is a simple head/tail/length callback list with `RCU_CBLIST_INITIALIZER`. Segment indexes `RCU_DONE_TAIL`, `RCU_WAIT_TAIL`, `RCU_NEXT_READY_TAIL`, and `RCU_NEXT_TAIL` split callbacks into done, waiting for current GP, ready for next GP, and unassigned next callbacks. `struct rcu_segcblist` stores head, segment tails, per-segment grace-period sequence numbers, total length, per-segment lengths, and flags. Flags include `SEGCBLIST_ENABLED` and `SEGCBLIST_OFFLOADED`. `RCU_SEGCBLIST_INITIALIZER` initializes all tails to the head.

Control flow: callbacks enter the next segment, are assigned grace-period sequence numbers, advance through wait/ready/done segments as GPs complete, and are invoked when in the done segment. NOCB offloading state transitions move callback processing between local `rcu_core()` and offloaded callback/GP kthreads while preserving locking and bypass semantics.

State and persistence: state is in-memory callback queues and GP sequence metadata. With `CONFIG_RCU_NOCB_CPU`, length is atomic for offloaded coordination.

Dependencies and integration points: depends on `rcu_head`, atomics, RCU NOCB config, and SRCU sizing requirements. It integrates RCU callback queuing, grace-period accounting, and no-CB CPU offload.

Risks and test signals: risks include corrupt tail pointers, wrong segment advancement, GP sequence misassignment, length/seglen divergence, offload/deoffload state-machine races, and callbacks invoked too early or stranded. Test RCU torture, callback flood, NOCB offload/deoffload, CPU hotplug, expedited and normal grace periods, and debug validation of segment lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rcu_segcblist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rcu_sync.h -->
# sources/distributed-fs/ceph-client/include/linux/rcu_sync.h

Purpose: declares lightweight infrastructure that lets readers use a fast path while updaters temporarily force a grace-period-synchronized slow path.

Important APIs and types: `struct rcu_sync` stores `gp_state`, nested updater `gp_count`, a wait queue, and an RCU callback head. `rcu_sync_is_idle()` tells RCU read-side callers whether fast paths are permitted. Lifecycle APIs are `rcu_sync_init()`, `rcu_sync_enter()`, `rcu_sync_exit()`, and `rcu_sync_dtor()`. `DEFINE_RCU_SYNC()` provides static initialization.

Control flow: readers check `rcu_sync_is_idle()` inside an RCU read-side critical section. Updaters call `rcu_sync_enter()` to transition state and wait for prior fast-path readers to drain, perform update-sensitive work, and call `rcu_sync_exit()` to eventually return to idle after grace-period handling.

State and persistence: state is runtime synchronization state in `struct rcu_sync`. No persistence exists.

Dependencies and integration points: depends on wait queues and RCU primitives. It integrates subsystems needing temporary writer exclusion from reader fast paths without permanently forcing heavy locking.

Risks and test signals: risks include calling `rcu_sync_is_idle()` outside RCU read-side protection, unbalanced enter/exit, teardown while callbacks are pending, and state races around nested updaters. Test lockdep warnings, nested enter/exit, concurrent readers/updaters, destructor after active use, and stress with expedited/normal grace periods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rcu_sync.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rculist.h -->
# sources/distributed-fs/ceph-client/include/linux/rculist.h

Purpose: provides RCU-safe list and hlist mutation/traversal primitives for regular doubly linked lists and hash lists, including SRCU, lockless, bidirectional, splice, replace, and tracing variants.

Important APIs and types: initialization and pointer helpers include `INIT_LIST_HEAD_RCU()`, `list_next_rcu()`, `list_bidir_prev_rcu()`, `list_tail_rcu()`, `hlist_first_rcu()`, `hlist_next_rcu()`, and `hlist_pprev_rcu()`. Mutators include `list_add_rcu()`, `list_add_tail_rcu()`, `list_del_rcu()`, `list_bidir_del_rcu()`, `list_replace_rcu()`, RCU splice helpers, `hlist_add_head_rcu()`, tail/before/behind add helpers, `hlist_del_rcu()`, `hlist_del_init_rcu()`, `hlist_replace_rcu()`, and `hlists_swap_heads_rcu()`. Traversal macros cover list/hlist RCU, SRCU, lockless, continue/from, BH, and notrace variants.

Control flow: writers serialize with other writers, update links with `rcu_assign_pointer()` where readers may observe them, and defer freeing deleted nodes until a grace period. Readers traverse under `rcu_read_lock()` or an explicitly validated alternate protection condition. Splice-init first hides the source list from new readers, waits for a grace period, then attaches the old body to a new list.

State and persistence: state is caller-owned list/hlist nodes and heads in memory. Deleted nodes remain reachable to old readers until grace-period cleanup.

Dependencies and integration points: depends on generic list APIs and `rcupdate.h`. It is used throughout networking, VFS, device, and core kernel tables needing lockless read traversal.

Risks and test signals: risks include immediate free after deletion, mixing `list_del_rcu()` with bidirectional traversal, missing reader lock, hlist `pprev` poisoning surprises, unsafe empty-then-first patterns, and writer-writer races. Test lockdep RCU-list checks, concurrent add/delete/traverse, splice with active readers, replace/swap heads, hlist tail insertion, and SRCU-protected traversals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rculist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rculist_bl.h -->
# sources/distributed-fs/ceph-client/include/linux/rculist_bl.h

Purpose: supplies RCU traversal and mutation helpers for bit-lock hash lists (`hlist_bl`), whose head pointer stores a lock bit in the low address bit.

Important APIs and types: `hlist_bl_first_rcu()` and `hlist_bl_next_rcu()` expose RCU pointers. `hlist_bl_set_first_rcu()` publishes a first node while preserving the lock bit. `hlist_bl_first_rcu_dereference()` masks the lock bit after checked dereference. Mutators include `hlist_bl_del_rcu()` and `hlist_bl_add_head_rcu()`. Traversal macros include `hlist_bl_for_each_entry_rcu()` and continue variant.

Control flow: writers hold the bucket bit-lock, add or delete nodes, and publish first-node changes with RCU assignment because readers may traverse locklessly. Readers dereference the first node with lock-aware checks, mask out the lock bit, and continue through RCU next pointers.

State and persistence: state is caller-owned `hlist_bl_head`/node memory with low-bit lock encoding. Deleted nodes must not be freed until readers drain.

Dependencies and integration points: depends on `list_bl.h` and RCU. It is used by hash tables needing compact per-bucket locking plus RCU read-side lookup.

Risks and test signals: risks include losing or misinterpreting the lock bit, unaligned node pointers, freeing nodes too early, traversing without RCU protection, and writer updates without the bit-lock. Test bucket lock/unlock with concurrent lookups, add/delete races, lock-bit masking, hash table resize/teardown, and debug list checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rculist_bl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rculist_nulls.h -->
# sources/distributed-fs/ceph-client/include/linux/rculist_nulls.h

Purpose: provides RCU helpers for nulls-terminated hash lists, where the end marker encodes bucket identity so lockless readers can detect races with node movement or table changes.

Important APIs and types: helpers expose first/next/pprev RCU pointers, delete with or without reinitialization, add head/tail, add fake node, replace with or without old-node initialization, and traverse through `hlist_nulls_for_each_entry_rcu()` or safe variant. Traversal includes a compiler barrier so restarted loops reread the first element.

Control flow: writers serialize updates, publish head/next changes with RCU assignment, and preserve nulls markers at list ends. Readers traverse under RCU until `is_a_nulls(pos)` is true; higher-level lookup code can inspect the marker to decide whether a restart is needed.

State and persistence: state is caller-owned nulls hlist nodes and heads in memory. Removed nodes remain valid until grace-period cleanup.

Dependencies and integration points: depends on `list_nulls.h` and RCU. It is commonly used by networking hash tables where entries can move between buckets during lockless lookup.

Risks and test signals: risks include wrong nulls marker after table changes, missing traversal barrier, early free, replacing unhashed nodes, tail insertion marker corruption, and lookup loops that fail to restart on marker mismatch. Test concurrent rehash/move/delete/lookup, marker mismatch restart logic, fake-node deletion, replace-init behavior, and lockdep RCU coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rculist_nulls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rcupdate.h -->
# sources/distributed-fs/ceph-client/include/linux/rcupdate.h

Purpose: defines the central Read-Copy Update API surface: read-side lock/unlock variants, callback and grace-period primitives, pointer publication/dereference macros, lockdep/debug checks, Tasks RCU hooks, NOCB controls, RCU head helpers, and deferred freeing helpers.

Important APIs and types: exported primitives include `call_rcu()`, `synchronize_rcu()`, `get_completed_synchronize_rcu()`, `call_rcu_hurry()`, Tasks RCU variants, `rcu_init()`, NOCB offload controls, and stall/sysrq helpers. Read-side APIs include `rcu_read_lock/unlock()`, `_bh`, `_sched`, notrace, and migration-disabling variants. Pointer APIs include `rcu_assign_pointer()`, `RCU_INIT_POINTER()`, `RCU_POINTER_INITIALIZER()`, `rcu_dereference*()`, `rcu_dereference_protected()`, `rcu_replace_pointer()`, `unrcu_pointer()`, and `rcu_pointer_handoff()`. Debug helpers include lockdep maps, `RCU_LOCKDEP_WARN()`, assertion macros, sleep checks, `rcu_head_init()`, and `rcu_head_after_call_rcu()`. Deferred free helpers include `kfree_rcu()`, `kvfree_rcu()`, and might-sleep one-argument variants.

Control flow: writers initialize data, publish pointers with release ordering, remove or replace pointers under writer synchronization, and defer freeing with `call_rcu()`/`kfree_rcu()` or wait with `synchronize_rcu()`. Readers enter an RCU read-side critical section, dereference protected pointers with dependency/lockdep checks, optionally hand off via refcounting, and exit. BH and sched variants add softirq/preemption constraints; modern vanilla RCU grace periods also account for preempt-disabled and IRQ/BH-disabled regions.

State and persistence: RCU global and per-CPU state is implemented in included TREE/TINY RCU headers and source files. `rcu_head` callbacks are embedded in caller objects. No persistence exists, but object lifetime is extended until grace periods complete.

Dependencies and integration points: depends on compiler annotations, atomics, irq/preempt tracking, scheduler state, bottom halves, lockdep, context tracking, TREE/TINY RCU implementations, slab/vmalloc freeing, and optional Tasks/NOCB/stall configs. It is a foundational synchronization contract used across the kernel.

Risks and test signals: risks include using `RCU_INIT_POINTER()` where publication ordering is required, dereferencing outside an RCU or update-side lock, blocking illegally in non-preemptible read sections, freeing objects before grace period, callback/module unload without barriers, `kfree_rcu()` offset limits, and config-specific semantics. Test RCU torture, lockdep/prove-RCU builds, Tasks RCU torture, NOCB offload/deoffload, callback flood and barriers, pointer replacement under readers, idle/offline CPU cases, and static analysis for `__rcu` sparse annotations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rcupdate.h -->
