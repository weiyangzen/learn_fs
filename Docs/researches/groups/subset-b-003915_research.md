# Research: subset-b-003915

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_sp.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_sp.c

Purpose: implements the BNG RoCE slow-path device-attribute query path. The file sends firmware command queue requests through `struct bng_re_rcfw`, decodes the `QUERY_FUNC` side-buffer response, records firmware version data, and exposes a single public entry point, `bng_re_get_dev_attr()`, used by higher-level resource and verbs setup to discover device limits.

Important APIs and functions: `bng_re_get_dev_attr()` prepares `CMDQ_BASE_OPCODE_QUERY_FUNC`, allocates a coherent side buffer for `struct creq_query_func_resp_sb`, sends the command with `bng_re_rcfw_send_message()`, and fills `rcfw->res->dattr`. `bng_re_query_version()` is a private helper around `CMDQ_BASE_OPCODE_QUERY_VERSION` and stores four firmware version bytes. `bng_re_is_atomic_cap()` checks PCIe device control 2 for `PCI_EXP_DEVCTL2_ATOMIC_REQ` and feeds the `is_atomic` advertised capability.

Control flow: the top-level query allocates DMA-coherent response memory, sets `req.resp_size`, submits the command, then normalizes firmware values into driver-visible attributes. It adjusts `max_qp` to include QP1, caps outgoing and initiating RDMA atomics at `BNG_RE_MAX_OUT_RD_ATOM`, limits variable-WQE depth and SGE counts to `BNG_VAR_MAX_WQE` and `BNG_VAR_MAX_SGE`, doubles hardware GID capacity for kernel GID-table accounting up to `BNG_RE_NUM_GIDS_SUPPORTED`, optionally adds extended SRQ capacity when `_is_max_srq_ext_supported()` is set, copies TQM allocation requests out of little-endian packed words, queries firmware version, and always frees the side buffer on exit.

State and persistence: this file does not persist state to disk. Runtime state is stored in `struct bng_re_dev_attr` owned by the RCFW resource object. The coherent side buffer exists only for the command duration. Attribute fields are cached after query and become the contract for later resource sizing, feature exposure, and verbs validation.

Dependencies and integration points: depends on PCI helpers, DMA allocation, generated firmware command structures from `bng_fw.h`, RCFW helpers from `bng_fw`/`bng_res`, and TLV-aware command accessors included via `bng_tlv.h`. It integrates with the device bring-up path that has already initialized `rcfw->pdev`, `rcfw->res`, and `rcfw->res->dattr`.

Risks: firmware values are trusted after basic capping; an unexpected side-buffer layout or endian mismatch would corrupt advertised limits. The TQM copy path treats a little-endian word as four bytes after conversion, so tests should catch host-endian assumptions. `bng_re_query_version()` silently leaves version bytes unchanged on failure. If the PCI atomic bit is absent, atomic verbs are disabled even if firmware reports support.

Test signals: exercise successful and failed `QUERY_FUNC` and `QUERY_VERSION` responses, DMA allocation failure, max-limit capping for QP/SRQ/GID/SGE values, PCIe atomic-capability variation, and attribute consumers that reject requests above the populated limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_sp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_sp.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_sp.h

Purpose: declares the BNG RoCE slow-path device-attribute data model and the query entry point used to populate it. It is the public header for `bng_sp.c`.

Important APIs and types: `struct bng_re_dev_attr` stores firmware version, GID count, QP/CQ/MR/MW/PD/AH/SRQ limits, max inline data, TQM allocation requests, atomic capability, firmware capability flags, and maximum DPI count. Constants include `FW_VER_ARR_LEN`, `BNG_RE_NUM_GIDS_SUPPORTED`, `BNG_RE_MAX_OUT_RD_ATOM`, `BNG_VAR_MAX_WQE`, and `BNG_VAR_MAX_SGE`. `bng_re_get_dev_attr(struct bng_re_rcfw *rcfw)` is the exported query function.

Control flow and integration: the header has no executable control flow, but it defines the shape that firmware query results are normalized into. Resource initialization and verbs/device-query code are expected to read this struct after `bng_re_get_dev_attr()` succeeds.

State and persistence: `struct bng_re_dev_attr` is an in-memory cache of hardware and firmware limits. It is not self-synchronized, reference-counted, or persisted; lifecycle is owned by the enclosing resource object.

Dependencies: includes `bng_fw.h` for firmware constants such as `BNG_MAX_TQM_ALLOC_REQ`. It relies on Linux integer and bool types being available through included driver headers.

Risks: because this header centralizes advertised limits, any mismatch with firmware response decoding can cascade into bad queue sizes, invalid MR limits, or unsupported capability exposure. The `max_mrw` field is declared but not populated in the associated implementation in this subset.

Test signals: compile checks for all consumers of the struct, device-query tests that compare populated attributes with firmware limits, and ABI/feature tests around max GID, max SRQ, atomic enablement, variable WQE, and max DPI behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_sp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_tlv.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_tlv.h

Purpose: provides TLV encapsulation helpers for BNG RoCE command queue messages. It lets common command-preparation code read and write `struct cmdq_base` fields whether the command is sent directly or wrapped behind a RoCE TLV header.

Important APIs and types: `struct roce_tlv` embeds a firmware `struct tlv`, stores `total_size` in 16-byte chunks, and pads to 16-byte alignment. `TLV_SIZE` and `TLV_BYTES` define the aligned header size. `HAS_TLV_HEADER()` tests the command discriminator for `CMD_DISCR_TLV_ENCAP`; `GET_TLV_DATA()` returns the payload following the TLV header. Inline accessors cover opcode, cookie, response address, response size, command size, and flags.

Control flow: every accessor checks whether the passed request appears TLV-encapsulated and whether the buffer is larger than the TLV header. If true, it casts the payload after `TLV_BYTES` to `struct cmdq_base`; otherwise it accesses the base request directly. The command-size getter is special: for TLV messages it returns the outer `roce_tlv.total_size`, while the setter writes the inner base `cmd_size`.

State and persistence: this header stores no state. It performs direct in-place mutation of command buffers supplied by callers, so the lifetime and validity of those buffers are external.

Dependencies and integration points: includes generated HSI definitions from `bng_roce_hsi.h` and depends on little-endian helpers for `cmd_discr`. It integrates with RCFW command builders such as `bng_re_rcfw_cmd_prep()` and `bng_re_fill_cmdqmsg()` that need generic base-field access.

Risks: all helpers assume the supplied `size` accurately describes the backing buffer. Incorrect sizes can cause fields to be written into the outer TLV header or skipped. The pointer arithmetic in `GET_TLV_DATA()` relies on byte-addressing and alignment; malformed TLV commands can still be misinterpreted if their discriminator is set but their payload is shorter than expected.

Test signals: unit-style command-buffer tests for direct and TLV-wrapped commands, verification that opcode/cookie/response fields are set in the right location, malformed short-TLV tests, and command submission tests that confirm firmware accepts both encapsulated and non-encapsulated requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_tlv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/Kconfig

Purpose: defines the kernel configuration symbol for the Broadcom NetXtreme-E RoCE driver.

Important APIs and build contract: `config INFINIBAND_BNXT_RE` is a tristate option with prompt `Broadcom Netxtreme HCA support`. It depends on `64BIT`, `INET`, `DCB`, and the Broadcom Ethernet driver symbol `BNXT`. The help text documents that the module name is `bnxt_re` and that it supports Broadcom NetXtreme-E 10/25/40/50 Gb RoCE HCAs.

Control flow: Kconfig selection controls whether the Makefile builds `bnxt_re.o` built-in, as a module, or not at all. No runtime code is present.

State and persistence: the selected symbol persists in kernel build configuration files such as `.config`; it does not create driver runtime state itself.

Dependencies and integration points: ties the RDMA driver to networking prerequisites and the underlying Broadcom Ethernet device support. The `DCB` and `INET` dependencies reflect RoCE’s Ethernet/IP and data-center-bridging integration points.

Risks: missing or too-weak dependencies can produce build failures or runtime feature gaps. Overly strict dependencies can hide the driver on valid platforms. The option is limited to 64-bit builds.

Test signals: Kconfig resolution tests across built-in/module combinations, allmodconfig/allnoconfig builds, dependency-disabled builds that verify the option disappears, and module-load tests confirming the built artifact is named `bnxt_re`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/Makefile -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/Makefile

Purpose: builds the Broadcom `bnxt_re` RDMA driver object and supplies include paths for shared Broadcom Ethernet headers.

Important build entries: `ccflags-y` adds `drivers/net/ethernet/broadcom/bnxt` to the include path. `obj-$(CONFIG_INFINIBAND_BNXT_RE) += bnxt_re.o` connects the object to the Kconfig symbol. `bnxt_re-y` links `main.o`, `ib_verbs.o`, `qplib_res.o`, `qplib_rcfw.o`, `qplib_sp.o`, `qplib_fp.o`, `hw_counters.o`, `debugfs.o`, and `uapi.o`.

Control flow: no runtime control flow exists. Build control flows from Kbuild expansion of `CONFIG_INFINIBAND_BNXT_RE` into object inclusion.

State and persistence: this file affects build artifacts only. It does not create persistent runtime state.

Dependencies and integration points: integrates with kernel Kbuild, RDMA-core driver build conventions, and the sibling Broadcom Ethernet driver headers. The object list shows the driver’s major subsystems: main device binding, verbs, firmware/resource libraries, stats, debugfs, and user ABI.

Risks: omitting a subsystem object causes link failures or missing callback implementations. The Broadcom include path can hide unintended header dependencies. Object ordering is normally not significant for Kbuild linking but can matter for initcall or symbol expectations if changed carelessly.

Test signals: incremental and clean kernel builds with `CONFIG_INFINIBAND_BNXT_RE=y` and `m`, compile with the underlying `BNXT` driver enabled, and link checks for all exported verbs, debugfs, stats, and uapi symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/bnxt_re.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/bnxt_re.h

Purpose: central private header for the Broadcom NetXtreme-C/E RoCE driver. It defines the main device object, resource limits, recovery flags, GSI state, notification queue bookkeeping, doorbell pacing state, debugfs pointers, and cross-file prototypes.

Important APIs and types: `struct bnxt_re_dev` embeds `struct ib_device` and links the RDMA device to `net_device`, auxiliary device, `bnxt_en_dev`, chip context, RCFW channel, qplib resources, device attributes, privileged DPI, CQs/QPs/SRQs hashes, GSI context, statistics, DCB workqueue, congestion-control and CQ-coalescing debugfs state, and RoCE mirror state. Supporting types include `bnxt_re_ring_attr`, `bnxt_re_gsi_context`, `bnxt_re_sqp_entries`, `bnxt_re_nq_record`, `bnxt_re_pacing`, and `bnxt_re_en_dev_info`.

Control flow and integration: executable logic is limited to small inline helpers. `bnxt_re_chip_gen_p7()` classifies chips, `rdev_to_dev()` returns a device pointer, `bnxt_re_set_pacing_dev_state()` mirrors error-detach state into pacing data, and `bnxt_re_read_context_allowed()` gates firmware context reads on chip generation and HWRM interface version. Function prototypes connect to `main`, HWRM VNIC setup, hardware counters, and pacing alert handling.

State and persistence: all state is runtime kernel memory. The main `bnxt_re_dev` structure is the persistence point across RDMA object lifetimes: flags track registration, channel/resource allocation, detach/error state, and stats availability; lists and hashes retain live objects; atomic counters track resource use; debugfs dentries expose selected fields while the device is registered.

Dependencies: includes RDMA uverbs definitions, `hw_counters.h`, Linux hashtable support, and Broadcom Ethernet/chip constants through transitive qplib headers. It is consumed by nearly every `bnxt_re` implementation file.

Risks: this header is a high-blast-radius coupling point. Incorrect flag use can break recovery or detach paths. Resource counters and hash/list updates must remain balanced with object create/destroy paths. Debugfs pointers require careful cleanup ordering. Chip-generation predicates affect context sizes, doorbell FIFO depth, and supported firmware operations.

Test signals: full driver build, probe/remove/recovery testing, resource create/destroy leak checks, debugfs add/remove under device detach, chip-generation matrix testing for P5/P7 versus older devices, and KASAN/lockdep around QP list, CQ/SRQ hashes, and pacing locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/bnxt_re.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/debugfs.c

Purpose: implements debugfs support for `bnxt_re`, including per-device directories, per-QP inspection files, resource/pacing info, congestion-control tunables, and CQ coalescing tunables.

Important APIs and functions: module-level `bnxt_re_register_debugfs()` and `bnxt_re_unregister_debugfs()` create/remove `/sys/kernel/debug/bnxt_re`. Per-device lifecycle is handled by `bnxt_re_debugfs_add_pdev()` and `bnxt_re_debugfs_rem_pdev()`. Per-QP entries are added and removed with `bnxt_re_debug_add_qpinfo()` and `bnxt_re_debug_rem_qpinfo()`. `info_show()` reports resource watermarks and doorbell pacing counters. `bnxt_re_cc_config_get()`/`bnxt_re_cc_config_set()` query and modify firmware congestion-control parameters. `cq_coal_cfg_show()`/`cq_coal_cfg_write()` expose CQ interrupt coalescing knobs when supported.

Control flow: device debugfs creation builds the PCI-device directory, `QPs`, `cc_config`, the `info` file, and optional `cq_coal_cfg`. QP creation adds a read-only file named by QPN; reading it formats transport type, state, MTU, timeout, remote QPN, and rate-limit status. CC reads issue `bnxt_qplib_query_cc_param()`, map an offset to a field, and return the value; writes parse a u32, fill one modified field and mask, then call `bnxt_qplib_modify_cc()`. CQ coalescing writes validate ranges before mutating `rdev->cq_coalescing`.

State and persistence: debugfs entries are ephemeral and removed on driver/device teardown. Some writes modify persistent runtime device state: CC writes program firmware state, while CQ coalescing writes update `rdev->cq_coalescing` used by future or active CQ handling. Allocated parameter arrays live in `rdev->cc_config_params` and `rdev->cq_coal_cfg_params`.

Dependencies and integration points: depends on Linux debugfs, seq_file, user-copy parsing, qplib SP firmware calls, qplib FP constants, `bnxt_re` device state, and `ib_verbs.h` QP structures. It is integrated from QP create/destroy paths and main device registration/removal.

Risks: debugfs write handlers are privileged but still need strict range checking. `bnxt_re_debugfs_add_pdev()` allocates `cc_config_params` but does not explicitly guard allocation failure before indexing. CC parameter name arrays and `BNXT_RE_CC_PARAM_GEN0` must stay in sync. Cleanup must handle optional CQ coalescing directories and partially initialized devices. QP debug reads allocate a formatted buffer and reject short user buffers with `-ENOSPC`, which differs from normal partial-read behavior.

Test signals: mount-debugfs inspection, per-QP file creation/removal during QP churn, read/write tests for every CC and CQ coalescing file including invalid values, firmware error injection for CC query/modify, remove paths after partial initialization, and lockdep/KASAN during concurrent QP destroy and debugfs reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/debugfs.h

Purpose: declares the debugfs interface and small state containers used by `debugfs.c`.

Important APIs and types: exported functions cover QP file add/remove, per-device debugfs add/remove, and global debugfs root registration/unregistration. `struct bnxt_re_cc_param` binds a debugfs file to a device, offset, generation/extension selector, and dentry. `struct bnxt_re_dbg_cc_config_params` contains the gen0 CC parameter array. `struct bnxt_re_cq_coal_param` and `struct bnxt_re_dbg_cq_coal_params` perform the same role for CQ coalescing. `enum bnxt_re_cq_coal_types` indexes the coalescing fields.

Control flow and integration: no executable control flow beyond macros. The constants `CC_CONFIG_GEN_EXT()`, `CC_CONFIG_GEN0_EXT0`, and `BNXT_RE_CC_PARAM_GEN0` define how debugfs maps files to firmware modify masks.

State and persistence: the structs are runtime-only allocations hanging off `struct bnxt_re_dev`. They persist as long as the device debugfs tree exists and are freed during debugfs removal.

Dependencies: relies on forward-declared driver types from including translation units, debugfs `struct dentry`, and `bnxt_re_dev`.

Risks: enum order must match the string table and switch statements in `debugfs.c`. `BNXT_RE_CC_PARAM_GEN0` must match `bnxt_re_cc_gen0_name[]` and the supported firmware mask mapping. Any mismatch can expose the wrong knob or write the wrong firmware field.

Test signals: compile-time coverage through `debugfs.c`, runtime enumeration of expected file names, and write/read validation that each offset controls the intended firmware or CQ coalescing field.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/hw_counters.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/hw_counters.c

Purpose: maps Broadcom hardware, firmware, and qplib RoCE statistics into RDMA-core hardware stats and Performance Management Agent MAD counters.

Important APIs and functions: `bnxt_re_ib_alloc_hw_port_stats()` allocates RDMA stats descriptors. `bnxt_re_ib_get_hw_stats()` fills standard and extended RDMA counters. `bnxt_re_assign_pma_port_counters()` and `bnxt_re_assign_pma_port_ext_counters()` populate PMA MAD response payloads. Helpers `bnxt_re_copy_err_stats()`, `bnxt_re_copy_ext_stats()`, and `bnxt_re_get_ext_stat()` translate qplib structures into RDMA stats indices.

Control flow: stats allocation chooses standard versus extended counter count based on chip generation. Stats retrieval first copies L2 hardware DMA stats from `rdev->qplib_ctx.stats.dma`, then, if `BNXT_RE_FLAG_ISSUE_ROCE_STATS` is set, queries firmware RoCE error counters and optional extended stats. Query failures clear the issue flag to avoid repeated failing firmware requests. PMA assignment chooses between L2 DMA stats and RoCE-only extended stats depending on chip generation and VF status, then writes big-endian PMA fields.

State and persistence: hardware counters are read from DMA-backed qplib stats memory and firmware query results are cached in `rdev->stats.rstat.errs` and `rdev->stats.rstat.ext_stat`. RDMA stats values are snapshots supplied to callers and are not persisted by this file.

Dependencies and integration points: depends on RDMA MAD/PMA structures, `rdma_hw_stats`, qplib SP functions (`bnxt_qplib_get_roce_stats()`, `bnxt_qplib_qext_stat()`), qplib chip-generation predicates, and driver flags from `bnxt_re.h`. `ib_verbs.c` calls the PMA assignment functions from `bnxt_re_process_mad()`.

Risks: counter units differ: PMA data counters are in 32-bit words, so byte counters are divided by four. Standard PMA counters truncate to 32 or 16 bits. Extended stats availability varies by capability flags, chip generation, and VF mode. Clearing `BNXT_RE_FLAG_ISSUE_ROCE_STATS` on one query failure can hide later-recovering firmware stats.

Test signals: RDMA sysfs/hw_stats reads on P5/P7 and older chips, PF versus VF PMA counter validation, firmware error injection for RoCE and extended stat queries, endian/unit checks for MAD responses, and traffic tests that increment send, receive, CNP/ECN, atomic/read/write, and error counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/hw_counters.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/hw_counters.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/hw_counters.h

Purpose: declares the counter index ABI and in-driver statistics containers for `bnxt_re`.

Important APIs and types: `enum bnxt_re_hw_stats` defines RDMA stats array indices from basic packet/byte counters through RoCE transport errors, responder errors, request/response CQE rollups, opcode counters, RoCE-only packet/byte counters, out-of-buffer, CNP, and ECN counters. `BNXT_RE_NUM_STD_COUNTERS` marks the older standard counter boundary and `BNXT_RE_NUM_EXT_COUNTERS` is the full enum count. `struct bnxt_re_res_cntrs` tracks atomic live resource counts and watermarks. `struct bnxt_re_rstat` caches qplib error and extended stats. `struct bnxt_re_stats` aggregates RoCE stats, resource counters, and doorbell pacing counters.

Control flow and integration: no executable control flow. Function prototypes expose RDMA-core callbacks for allocating and filling port hardware stats.

State and persistence: all structs are runtime fields, normally embedded in `struct bnxt_re_dev`. Atomic counters represent live object counts; watermarks retain high-water values for the life of the device instance and are displayed through debugfs.

Dependencies: requires qplib stat structure definitions and RDMA `struct ib_device`/`struct rdma_hw_stats` through including files. It is included by `bnxt_re.h` and implemented by `hw_counters.c`.

Risks: enum ordering must remain synchronized with `bnxt_re_stat_descs[]` and every assignment in `hw_counters.c`. Adding a counter in the middle changes all later indices. Resource counters must be incremented/decremented consistently in verbs object lifecycle paths to keep debugfs reporting meaningful.

Test signals: compile-time array designated initializer coverage, RDMA stats descriptor count validation, resource churn tests for PD/QP/CQ/SRQ/MR/MW/AH counts and watermarks, and counter-index compatibility checks with user tooling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/hw_counters.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/ib_verbs.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/ib_verbs.c

Purpose: implements the RDMA verbs provider for Broadcom `bnxt_re`. It translates RDMA-core object operations into qplib firmware/resource operations for device and port queries, GID/PKEY handling, PD/AH/SRQ/QP/CQ/MR/MW lifecycle, send/receive posting, CQ polling and notification, ucontext mmap, RoCE mirror flows, and PMA MAD handling.

Important APIs and functions: device/port entry points include `bnxt_re_query_device()`, `bnxt_re_modify_device()`, `bnxt_re_query_port()`, `bnxt_re_get_port_immutable()`, and `bnxt_re_query_fw_str()`. Addressing APIs include `bnxt_re_add_gid()`, `bnxt_re_del_gid()`, `bnxt_re_query_gid()`, `bnxt_re_create_ah()`, `bnxt_re_destroy_ah()`, and `bnxt_re_query_ah()`. Object lifecycle is handled by `bnxt_re_alloc_pd()`, `bnxt_re_dealloc_pd()`, `bnxt_re_create_srq()`, `bnxt_re_destroy_srq()`, `bnxt_re_create_qp()`, `bnxt_re_destroy_qp()`, `bnxt_re_create_cq()`, `bnxt_re_create_user_cq()`, `bnxt_re_destroy_cq()`, and `bnxt_re_resize_cq()`. Data path entry points are `bnxt_re_post_send()`, `bnxt_re_post_recv()`, `bnxt_re_post_srq_recv()`, `bnxt_re_poll_cq()`, and `bnxt_re_req_notify_cq()`. Memory APIs include `bnxt_re_get_dma_mr()`, `bnxt_re_alloc_mr()`, `bnxt_re_reg_user_mr()`, `bnxt_re_reg_user_mr_dmabuf()`, `bnxt_re_dereg_mr()`, `bnxt_re_alloc_mw()`, and `bnxt_re_dealloc_mw()`. User ABI support is in `bnxt_re_alloc_ucontext()`, `bnxt_re_dealloc_ucontext()`, `bnxt_re_mmap_entry_insert()`, `bnxt_re_mmap()`, and `bnxt_re_mmap_free()`.

Control flow: query paths copy cached qplib device attributes into RDMA-core structures and expose optional capabilities such as atomics, packet pacing, variable WQE mode, MSN table mode, and rate limits. Creation paths validate user data and limits, initialize qplib state, pin user memory when needed, allocate hardware queues, call qplib create commands, return udata responses, update resource counters/watermarks, and register debugfs entries. Destroy paths reverse firmware objects, qplib resources, umem pins, mmap entries, hashes, lists, NQ load, debugfs entries, and counters. Modify/query QP paths translate IB state, MTU, access flags, AV/GRH data, rate limits, PSNs, retry timers, and caps to and from firmware fields.

State and persistence: persistent runtime state lives in the driver objects declared in `ib_verbs.h`: PDs keep qplib PDs and optional fence MR/MW data; QPs keep qplib queues, CQ links, umems, locks, GSI header state, and debugfs dentries; CQs keep qplib CQ state, optional user umem, resize state, lock, CQL scratch array, and toggle-page mapping; SRQs keep qplib SRQ state, user umem, lock, and toggle page; MRs/MWs keep qplib MRW state and pinned memory. Device-level lists, hashes, GSI context, resource counters, and RoCE mirror state are updated here. No disk persistence exists.

Dependencies and integration points: heavily depends on RDMA core verbs, uverbs, mmap, umem, MAD/PMA, address/GID helpers, network and VLAN helpers, qplib resource/firmware/fast-path APIs, `debugfs.c` QP hooks, `hw_counters.c` PMA helpers, and HWRM VNIC helpers from main driver code. Doorbell pages and shared pages are exposed to userspace through RDMA mmap entries.

High-risk implementation areas: GSI/QP1 handling for older chips creates a shadow QP and shadow AH, rewrites QP1 send headers, loops raw QP packets through the shadow QP, and reconstructs completions from `sqp_tbl`; this is sensitive to packet layout, VLAN metadata, loopback offsets, and table indices. CQ resize for userspace defers final umem replacement until poll time. User mmap offsets and toggle pages must be removed exactly once. Error unwinds in create paths must balance qplib resources, umem pins, debugfs, list insertion, and counters. Legacy fence-MR/MW and phantom WQE handling affects ordering for memory operations. Some comparisons use qplib type values against IB QP constants, so chip/type translation tests matter.

Test signals: full RDMA verbs smoke tests with `ibv_devinfo`, `rping`, RC read/write/atomic, UD send/recv, GSI MAD traffic, user and kernel CQs, SRQ threshold changes, CQ resize, MR registration/deregistration including dmabuf, fast-reg MR, MW bind/dealloc, ucontext mmap of UC/WC doorbells and shared pages, QP state transitions and invalid masks, packet pacing rate-limit modify, RoCE v1/v2 IPv4/IPv6 and VLAN completions, device removal while objects exist, and fault injection for every qplib create/modify/destroy path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/ib_verbs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/ib_verbs.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/ib_verbs.h

Purpose: declares the private RDMA object wrappers and verbs callbacks implemented by `ib_verbs.c`.

Important APIs and types: wrapper structs embed RDMA-core objects and qplib state: `bnxt_re_pd`, `bnxt_re_ah`, `bnxt_re_srq`, `bnxt_re_qp`, `bnxt_re_cq`, `bnxt_re_mr`, `bnxt_re_mw`, `bnxt_re_ucontext`, `bnxt_re_user_mmap_entry`, `bnxt_re_dbr_obj`, and `bnxt_re_flow`. `bnxt_re_fence_data` stores the legacy fence MR/MW and bind WQE. `bnxt_re_gid_ctx` records hardware SGID index and refcount. Inline helpers compute send/receive WQE sizes, initialize queue depth according to user context capabilities, detect variable-WQE support, and convert zero-based port IDs to IB port numbers.

Control flow and integration: no major executable control flow exists in the header, but the prototypes define the driver's verbs surface: device/port query, GID/PKEY, PD/AH/SRQ/QP/CQ/MR/MW/ucontext/mmap/flow/MAD operations, CQ lock helpers, and mmap-entry insertion. RDMA-core operation tables in other driver files bind to these functions.

State and persistence: the wrapper structs define all long-lived per-object runtime state. Locks protect QP SQ/RQ, CQ polling, SRQ posting, and shared user page writes. User objects retain umem pointers and mmap entries until destroy/dealloc. GSI QPs retain packet header and send PSN state. No structure is persisted outside kernel memory.

Dependencies: depends on RDMA-core types, qplib queue/MR/CQ/SRQ/QP structures through included compilation units, and ABI constants used in user responses. It is included by debugfs and verbs implementation files.

Risks: object layout is central to `container_of()` conversions; changing embedded member names or lifetimes breaks many callbacks. The inline `bnxt_re_init_depth()` rounds depths unless userspace opted out, so queue sizing must stay aligned with ABI expectations. Variable-WQE capability depends on either user context masks or chip mode; mismatches can corrupt queue layout. Locking comments document intended protection and should remain accurate.

Test signals: compile coverage of all callback prototypes, uverbs ABI tests for user context capability masks and mmap entries, queue-depth tests with and without power-of-two rounding disabled, variable versus static WQE QP creation, lockdep around SQ/RQ/CQ/SRQ paths, and object lifecycle tests validating every wrapper is freed after its corresponding destroy callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/ib_verbs.h -->
