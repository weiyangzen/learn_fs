# Research: subset-b-004597

Grouped research for QED context, debug HSI, and DCBX files. Each section preserves the original source path for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_cxt.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_cxt.c

## Purpose

`qed_cxt.c` implements the QED driver's context manager for connection IDs, task IDs, ILT layout/allocation, searcher free-list memory, timer/search/parser/DQ/CDU/QM runtime initialization, and protocol-specific resource sizing. It is central to PF bring-up because the firmware and hardware blocks need a consistent view of where CDUC connection contexts, CDUT task contexts, QM/TM/SRC/TSDM memory, and VF regions live in ILT space.

## Important APIs, Types, and Functions

- Context sizing unions: `conn_context`, `type0_task_context`, and `type1_task_context` define the maximum-sized per-protocol context payloads used by `CONN_CXT_SIZE()`, `TYPE0_TASK_CXT_SIZE()`, and `TYPE1_TASK_CXT_SIZE()`.
- Resource counters: `qed_cxt_cdu_iids()`, `qed_cxt_src_iids()`, `qed_cxt_tm_iids()`, and `qed_cxt_qm_iids()` aggregate PF/VF CID and TID counts from `p_hwfn->p_cxt_mngr->conn_cfg`.
- ILT layout: `qed_cxt_cfg_ilt_compute()` is the major layout pass. It resets block descriptors, computes client first/last lines, block sizes, PF/VF spans, dynamic RoCE CDUC skip lines, SRC/TM/TSDM sizing, and rejects configurations exceeding `RESC_NUM(p_hwfn, QED_ILT)`.
- Allocation/free: `qed_cxt_mngr_alloc()`, `qed_cxt_tables_alloc()`, and `qed_cxt_mngr_free()` allocate the manager, ILT shadow DMA pages, SRC T2 pages, and CID bitmaps, and unwind them on failure.
- Hardware initialization: `qed_cxt_hw_init_common()` programs CDU common and parser common settings; `qed_cxt_hw_init_pf()` sequences QM, CM, DQ, CDU PF, ILT, SRC, TM, and parser PF runtime-register initialization.
- CID lifecycle: `_qed_cxt_acquire_cid()`, `qed_cxt_acquire_cid()`, `_qed_cxt_release_cid()`, `qed_cxt_release_cid()`, `qed_cxt_get_cid_info()`, and `qed_cxt_test_cid_acquired()` manage per-protocol PF/VF CID bitmaps and return context pointers.
- Protocol sizing: `qed_cxt_set_pf_params()` maps the active PCI personality to CORE, ETH, RDMA, FCoE, iSCSI, or NVMe/TCP CID/TID requirements. `qed_rdma_set_pf_params()` has special RoCE/iWARP behavior and SRQ/XRC-SRQ sizing.
- Dynamic ILT: `qed_cxt_dynamic_ilt_alloc()` lazily allocates RoCE-oriented CDUC, CDUT, TSDM SRQ, and XRC SRQ pages and writes the wide-bus PSWRQ2 ILT entry via DMAE. `qed_cxt_free_proto_ilt()` frees protocol-related dynamic ranges.
- Task helpers: `qed_cxt_get_tid_mem_info()` and `qed_cxt_get_task_ctx()` expose task working/forced-load memory for storage personalities. Page count helpers report CDUT work/init pages for PF/VF.

## Control Flow

Initialization is staged. First `qed_cxt_mngr_alloc()` creates the manager, initializes ILT client register offsets and default 64K ILT page sizes, computes context/task sizes, captures SR-IOV VF counts, initializes the dynamic allocation mutex, and attaches the manager to `p_hwfn`. Then `qed_cxt_set_pf_params()` fills protocol resource counts from personality-specific PF parameters. `qed_cxt_cfg_ilt_compute()` converts those counts into client block layout and total ILT line usage. `qed_cxt_tables_alloc()` allocates memory backing for non-dynamic ILT lines, SRC T2 pages, and CID acquisition maps.

During PF hardware initialization, `qed_cxt_hw_init_common()` stores CDU common sizing and parser-common settings into runtime arrays. `qed_cxt_hw_init_pf()` calls the per-block initialization functions in dependency order: QM gets resource totals, DQ gets cumulative protocol CID ranges, CDU gets CDUT segment offsets, ILT gets bounds and physical entries, SRC gets T2 free-list registers, TM gets PF/VF timer-memory descriptors, and parser gets FCoE task limits when applicable.

Runtime CID acquisition scans the correct PF or VF bitmap for the first clear bit, marks it, and returns `start_cid + rel_cid`. Release verifies the CID belongs to an acquired protocol range before clearing the bit. CID info lookup repeats the verification, computes the CDUC ILT line and offset, and fails if the line is not allocated, which matters for dynamic RoCE allocation.

Dynamic ILT allocation is serialized by `p_cxt_mngr->mutex`. It selects the ILT client/block and element size from `enum qed_cxt_elem_type`, computes the ILT line from `iid`, allocates one DMA page if absent, patches RoCE task TDIF ref-tag masks for task pages, records the shadow descriptor, writes the hardware ILT entry through DMAE, and updates parser RDMA search state for connection contexts.

## State and Persistence Behavior

All durable-in-driver state is attached to `struct qed_cxt_mngr` under `p_hwfn->p_cxt_mngr`. It persists for the hardware function lifetime and includes protocol resource configuration, ILT client layout, task type sizes, VF counts, CID acquisition bitmaps, the ILT shadow descriptor array, the SRC T2 DMA free-list metadata, SRQ/XRC counts, ARFS counts, and cached page counters/context sizes. Hardware-visible state is written through runtime-register storage macros, direct GRC writes, or DMAE writes; it must be recreated on device initialization and is freed on manager teardown. CID bitmap contents are reset by `qed_cxt_mngr_setup()` but not persisted across reload.

## Dependencies and Integration Points

The file depends on QED hardware and firmware interface headers (`qed_hsi.h`, `qed_reg_addr.h`, `qed_init_ops.h`), core device state (`qed.h`, `qed_dev_api.h`, `qed_hw.h`), SR-IOV metadata (`qed_sriov.h`), RDMA parameters (`qed_rdma.h`), Linux DMA allocation, bitmaps, mutexes, and logging. It integrates with QM initialization/reconfiguration (`qed_qm_pf_rt_init`, `qed_qm_pf_mem_size`, `qed_get_cm_pq_idx`), parser RDMA/FCoE settings, DMAE, PTT acquisition, and slowpath updates that need CID/task context pointers.

## Risks and Edge Cases

- ILT arithmetic is sensitive to resource counts, alignment, and per-page element sizes. A bad count can overrun `RESC_NUM(QED_ILT)` or misprogram first/last lines.
- Several paths assume only one protocol owns a TID segment. `qed_cxt_tid_seg_info()` returns the first segment with a nonzero count.
- Dynamic RoCE allocation intentionally leaves some ILT shadow lines absent at initial allocation. Callers of `qed_cxt_get_cid_info()` must tolerate `-EINVAL` until pages are allocated.
- `qed_cxt_free_ilt_range()` iterates `i < shadow_end_line`; boundary correctness is important for freeing the last page in a range.
- DQ register programming is manually cumulative for protocol indexes 0 through 5 and then mirrors values to 6 and 7, so protocol enum changes would need careful updates.
- SRC T2 setup assumes entries per page is a power of two and builds a DMA-address linked list consumed by hardware.
- Dynamic allocation holds a mutex while acquiring PTT and allocating DMA memory, so failure handling and release paths must remain balanced.

## Test Signals

Useful signals are kernel build coverage for QED with Ethernet, RDMA, FCoE, iSCSI, NVMe/TCP, SR-IOV, and DCB combinations; boot/probe logs with `QED_MSG_ILT` and `QED_MSG_CXT`; resource-limit tests that intentionally exceed ILT lines and verify `-EINVAL`; CID acquire/release exhaustion tests; RDMA workloads that trigger dynamic ILT allocation and teardown; storage offload tests that use task memory helpers; and device reload/SR-IOV enable-disable cycles that exercise allocation unwind and bitmap reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_cxt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_cxt.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_cxt.h

## Purpose

`qed_cxt.h` declares the context manager's public and internal contract: context lookup structures, TID memory views, dynamic ILT element types, exported initialization/allocation/CID APIs, ILT block layout structures, CID maps, SRC T2 metadata, and the top-level `struct qed_cxt_mngr` stored on each hardware function.

## Important APIs, Types, and Functions

- `struct qed_cxt_info` is an in/out lookup object containing the requested `iid`, resolved protocol `type`, and returned context pointer.
- `struct qed_tid_mem` returns storage-offload task memory geometry: task size, TIDs per block, page waste, and up to `MAX_TID_BLOCKS` block pointers.
- `enum qed_cxt_elem_type` identifies dynamic allocation targets: connection context, SRQ, task, and XRC SRQ.
- Public lifecycle APIs include `qed_cxt_mngr_alloc()`, `qed_cxt_tables_alloc()`, `qed_cxt_mngr_setup()`, and `qed_cxt_mngr_free()`.
- Hardware init APIs include `qed_cxt_cfg_ilt_compute()`, `qed_cxt_cfg_ilt_compute_excess()`, `qed_cxt_hw_init_common()`, `qed_cxt_hw_init_pf()`, `qed_qm_init_pf()`, and `qed_qm_reconf()`.
- Runtime APIs include CID acquire/release for PF and VF queues, protocol CID/TID count getters, dynamic ILT allocation/free, task context lookup, CDUT page count helpers, ILT page-size lookup, and total SRQ count lookup.
- Internal layout structures `qed_tid_seg`, `qed_conn_type_cfg`, `qed_ilt_cli_blk`, and `qed_ilt_client_cfg` model protocol resource counts and ILT client block boundaries.
- `struct qed_cxt_mngr` is the persistent owner of protocol config, ILT clients, task sizes, VF metadata, acquired CID bitmaps, ILT shadow, dynamic allocation mutex, SRC T2 metadata, SRQ counts, ARFS count, and cached size/page counters.

## Control Flow

The header defines the state graph used by `qed_cxt.c`: callers allocate a manager, set PF parameters, compute ILT layout, allocate tables, initialize hardware, and then acquire/release CIDs or dynamically allocate ILT entries as protocols run. Storage and RDMA call sites use the helper APIs to discover task memory, context pointers, and resource counts without knowing ILT client internals.

## State and Persistence Behavior

`struct qed_cxt_mngr` is a long-lived in-memory object, not a serialized artifact. It persists for the active `qed_hwfn` lifetime and is the only owner of allocated ILT/SRC/CID state. Its register values and DMA addresses are mirrored into hardware during init, but the structure itself is rebuilt on driver reload.

## Dependencies and Integration Points

The header depends on Linux types/slab, QED public interface types, hardware status/interface structures from `qed_hsi.h`, and core device definitions from `qed.h`. It is consumed by QED core initialization, slowpath, protocol offloads, RDMA, storage offloads, SR-IOV code, and DCBX/QM paths that need context or queue-manager resource counts.

## Risks and Edge Cases

- Constants such as `MAX_CONN_TYPES`, `TASK_SEGMENTS`, `ILT_CLI_PF_BLOCKS`, and CDUT block index macros must stay aligned with firmware protocol IDs and hardware register expectations.
- `struct qed_tid_mem` has a fixed `MAX_TID_BLOCKS`; callers rely on implementation-side line counts not exceeding it.
- The manager exposes many fields directly to implementation files, so layout changes are cross-cutting and can affect allocation, hardware programming, and teardown.
- `dynamic_line_offset` is present in `qed_ilt_cli_blk` but not central in the observed implementation; future users need to distinguish it from `dynamic_line_cnt`.

## Test Signals

Build coverage is the main signal for declaration consistency. Runtime validation comes from probe initialization across personalities, SR-IOV configurations, RDMA dynamic allocation, CID lifecycle tests, and any users of `qed_cxt_get_task_ctx()`/`qed_cxt_get_tid_mem_info()` successfully consuming the exposed memory geometry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_cxt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_dbg_hsi.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_dbg_hsi.h

## Purpose

`qed_dbg_hsi.h` defines the QED debug tools hardware/software interface. It is mostly an ABI/schema header for firmware-generated debug arrays, GRC dumps, idle checks, attention parsing, MCP traces, debug bus capture, register FIFOs, IGU FIFOs, protection override dumps, and firmware assert dumps.

## Important APIs, Types, and Functions

- Hardware block and buffer identity enums: `enum block_id`, `enum bin_dbg_buffer_type`, `enum dbg_attn_type`, `enum dbg_bus_clients`, `enum dbg_bus_constraint_ops`, `enum dbg_bus_states`, `enum dbg_bus_storm_modes`, `enum dbg_bus_targets`, `enum dbg_grc_params`, `enum dbg_status`, `enum dbg_storms`, and `enum ilt_clients`.
- Packed/bitfield schemas: attention mappings/results, mode headers, dump register/memory descriptors, idle-check rules/results, reset registers, debug bus line/block/storm data, GRC parameter data, MCP trace metadata, and per-hardware-function `struct dbg_tools_data`.
- Debug dump APIs: `qed_dbg_grc_get_dump_buf_size()`, `qed_dbg_grc_dump()`, idle-check, MCP trace, register FIFO, IGU FIFO, protection override, firmware assert, and attention read/print functions.
- User/parser APIs: `qed_dbg_user_set_bin_ptr()`, `qed_dbg_alloc_user_data()`, `qed_dbg_get_status_str()`, result buffer size calculators, result printers, MCP trace metadata setters/free functions, and attention parsing.
- Utility hardware access declarations: `qed_read_regs()` and `qed_read_fw_info()`.

## Control Flow

This file does not implement algorithms; it declares the data contract used by debug implementation files. Typical control flow is: set debug binary pointers, configure optional GRC parameters, ask for a dump buffer size, allocate a caller buffer, collect a raw dump through a `qed_dbg_*_dump()` routine using a PTT window, and optionally parse/print the raw dump through a corresponding `qed_print_*_results()` function.

## State and Persistence Behavior

State is represented by caller-owned buffers and by `struct dbg_tools_data` attached to each hardware function by implementation code. It tracks configured GRC params, debug bus state, idle-check buffer sizing, mode enable arrays, block reset state, chip/hardware topology, DMAE usage, pretend/split parameters, and register read counts. MCP trace parsing also owns optional allocated metadata through `struct mcp_trace_meta`.

## Dependencies and Integration Points

The header depends on Linux primitive types, I/O helpers, bitops, delay, kernel, list, and slab headers. It also references QED core objects (`struct qed_hwfn`, `struct qed_ptt`, `struct fw_info`) that are defined elsewhere. It is shared by debug collection code, ethtool/devlink-style diagnostic paths, firmware dump consumers, and context code via `enum ilt_clients`.

## Risks and Edge Cases

- Many structures encode bitfields with explicit masks/shifts; firmware tooling, hardware register definitions, and parser code must agree exactly.
- The enum ordering is part of the implicit ABI for firmware-generated debug arrays. Reordering breaks binary buffer interpretation.
- Public dump functions return `enum dbg_status`, not Linux `errno`, so callers need correct status translation.
- Buffer sizing is two-phase; callers must honor returned dword or byte sizes to avoid `DBG_STATUS_DUMP_BUF_TOO_SMALL` or parse failures.
- Some debug functions may halt/resume MCP, access wide-bus registers, or rely on block reset state; diagnostic paths should be careful during error recovery.

## Test Signals

Validation includes compiling all debug implementations against this header, collecting GRC/idle/MCP/FIFO/assert dumps on supported chips, parsing dumps with expected status strings, exercising invalid buffer sizes and invalid parameters, and confirming firmware debug bundle version compatibility through `qed_dbg_set_bin_ptr()`/`qed_dbg_user_set_bin_ptr()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_dbg_hsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_dcbx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_dcbx.c

## Purpose

`qed_dcbx.c` implements Data Center Bridging Exchange handling for QED PFs. It reads LLDP/DCBX MIBs from MCP public memory, parses operational/local/remote DCBX features, updates protocol traffic-class/priority state, triggers QM and firmware PF updates after negotiation changes, exposes DCBX state to protocol callbacks, and implements the Linux DCB netlink operations when `CONFIG_DCB` is enabled.

## Important APIs, Types, and Functions

- TLV classifiers: `qed_dcbx_*_tlv()` helpers identify ETH default, iSCSI, FCoE, RoCE, and RoCEv2 application TLVs from MFW app entries, including IEEE selector compatibility for older MFW values.
- Protocol result updates: `qed_dcbx_set_params()` and `qed_dcbx_update_app_info()` fill `struct qed_dcbx_results` per protocol, set offload TC for matching personalities, set VLAN0 behavior, and configure UFP/RoCE EDPM doorbell priority overrides.
- MIB parsing: `qed_dcbx_process_tlv()` parses app priority entries, falls back for missing ETH TLVs, and applies defaults. `qed_dcbx_process_mib_info()` updates active TC count, OOO TC, PF ID, enabled state, and cached results.
- MIB reading: `qed_dcbx_copy_mib()` retries until prefix/suffix sequence numbers match; `qed_dcbx_read_*_mib()` functions map each MIB type to MCP public memory offsets; `qed_dcbx_read_mib()` dispatches by `enum qed_mib_read_type`.
- Query/export helpers: `qed_dcbx_get_*_params()` populate `struct qed_dcbx_get` views for operational, local, remote, and LLDP data. `qed_dcbx_get_priority_tc()` maps a priority to the operational ETS TC.
- Event entry point: `qed_dcbx_mib_update_event()` is the core update path. For operational changes it reads the MIB, processes results, reconfigures QM, sends a PF update ramrod, updates RoCE DPM behavior, programs NIG EDPM TC enablement, refreshes cached get-data, and emits an AEN callback.
- Allocation and PF update: `qed_dcbx_info_alloc()`, `qed_dcbx_info_free()`, and `qed_dcbx_set_pf_update_params()` own the per-HWFN DCBX state and copy negotiated protocol data into slowpath ramrod payloads.
- `CONFIG_DCB` configuration path: `qed_dcbx_get_config_params()` and `qed_dcbx_config_params()` manage cached set parameters, local-admin MIB writes, and MCP `DRV_MSG_CODE_SET_DCBX` commits.
- DCB netlink operations: `qed_dcbnl_ops_pass` binds get/set callbacks for state, PFC, ETS, app entries, DCBX mode, CEE peer data, IEEE PFC/ETS/app data, and feature flags.

## Control Flow

For asynchronous firmware updates, `qed_dcbx_mib_update_event()` reads the requested MIB. Operational updates then parse app/ETS/PFC data into protocol results, reconfigure queue manager TCs through `qed_qm_reconf()`, notify firmware via `qed_sp_pf_update()`, adjust RoCE DPM if applicable, program NIG EDPM TC bits, refresh the cached `qed_dcbx_get` view, and notify upper-layer callbacks with `dcbx_aen`.

For user configuration under `CONFIG_DCB`, dcbnl setters call `qed_dcbx_get_config_params()` to get a mutable cached config derived from current operational data, set override flags and fields, acquire a PTT, and call `qed_dcbx_config_params(..., hw_commit=false)` to cache changes. `setall` later calls the same function with `hw_commit=true`, which builds a local-admin MIB, writes it to MCP public memory, and sends the MCP SET_DCBX command.

For dcbnl getters, callbacks allocate a temporary `qed_dcbx_get`, query the relevant MIB through PTT-protected reads, validate operational state/mode when necessary, translate QED internal params into Linux DCB/CEE/IEEE structures, and free the temporary buffer.

## State and Persistence Behavior

Per-HWFN DCBX state lives in `p_hwfn->p_dcbx_info`, allocated by `qed_dcbx_info_alloc()`. It caches local and remote LLDP parameters, local-admin config, operational and remote DCBX MIBs, negotiated `results`, pending set parameters, and the last `get` snapshot. Hardware/firmware state persists in MCP public memory and device registers; the driver-side cache is rebuilt on reload and refreshed by MIB reads. Pending dcbnl changes can remain cached in `p_dcbx_info->set` until committed by `setall`.

## Dependencies and Integration Points

The file integrates with MCP public memory (`qed_memcpy_from/to`, `qed_mcp_cmd`, `public_port` offsets), PTT/GRC access, QM reconfiguration, slowpath PF update ramrods, RoCE DPM policy, SR-IOV/VF restrictions, multi-function flags, Linux DCB netlink structures, and upper-layer common callbacks. It depends heavily on MFW bitfield macros from `qed_hsi.h` and public QED Ethernet interface types when `CONFIG_DCB` is enabled.

## Risks and Edge Cases

- `qed_dcbx_copy_mib()` retries up to 100 times for stable sequence numbers; repeated instability returns `-EIO`.
- `qed_dcbx_process_tlv()` uses `ffs(priority_map) - 1` and rejects empty priority maps. Some dcbnl setters store either priority numbers or priority bitmaps depending on CEE versus IEEE paths, so translations must stay consistent.
- Operational DCBX disabled state causes many getters to return no data or defaults.
- DCBX configuration is blocked for VFs in query paths.
- The local-admin write starts from operational features and applies override flags; missing override flags intentionally preserve negotiated/current data.
- `qed_dcbnl_setstate()` and many setters cache changes with `hw_commit=false`, so userspace must call the commit path (`setall`) to push to firmware.
- App table capacity is limited to `DCBX_CONFIG_MAX_APP_PROTOCOL`; setters return `-EBUSY` if no empty slot exists.
- IEEE-only getters/setters reject non-IEEE operational modes.

## Test Signals

Strong signals include kernel build with and without `CONFIG_DCB`, LLDP/DCBX negotiation tests against IEEE and CEE peers, MIB sequence retry/failure injection, dcbtool/lldptool/iproute2 DCB getter/setter coverage, `setall` commit verification through MCP-visible local-admin MIB changes, QM TC changes after operational updates, PF update ramrod payload inspection, RoCE DPM behavior after priority changes, and VF rejection tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_dcbx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_dcbx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_dcbx.h

## Purpose

`qed_dcbx.h` declares the QED DCBX state model and public APIs used by the driver core, MCP event path, PF update path, and optional DCB netlink support. It defines MIB read selectors, protocol result data, configuration override flags, metadata for application protocol matching, and the per-HWFN DCBX cache.

## Important APIs, Types, and Functions

- `enum qed_mib_read_type` identifies operational, remote, local, remote LLDP, and local LLDP MIB reads.
- `struct qed_dcbx_app_data` stores per-protocol enable/update/priority/TC/VLAN0 behavior used for PF update ramrods.
- `struct qed_dcbx_set` stores pending/admin configuration, including override flags for state, PFC, ETS, APP, and DSCP config.
- `struct qed_dcbx_results` stores negotiated state for all `DCBX_MAX_PROTOCOL_TYPE` protocols plus PF ID and enabled state.
- `struct qed_dcbx_info` is the driver cache for LLDP local/remote data, local admin MIB, operational/remote MIBs, negotiated results, pending set data, last get data, and capability.
- `struct qed_dcbx_mib_meta_data` packages MIB target pointers, size, and MCP public memory address for copy helpers.
- Public APIs include `qed_dcbx_mib_update_event()`, allocation/free helpers, PF update copy helper, `qed_dcbx_get_priority_tc()`, and `CONFIG_DCB` get/config functions. `qed_dcbnl_ops_pass` exports the DCB netlink ops table to the Ethernet layer.

## Control Flow

Consumers allocate `p_dcbx_info`, handle MCP MIB events with `qed_dcbx_mib_update_event()`, use cached negotiated results to fill PF update ramrods, and query priority-to-TC mappings for packet/offload behavior. When DCB netlink is enabled, userspace-facing operations call the declared config functions to read current settings, stage overrides, and commit local-admin MIB updates.

## State and Persistence Behavior

The header's main state object, `struct qed_dcbx_info`, is transient driver memory. It mirrors firmware/MCP MIB data and pending admin settings but does not itself persist across device reload. Firmware-visible persistence is handled by writing local-admin DCBX MIBs and issuing MCP commands in the implementation.

## Dependencies and Integration Points

The header depends on QED core, HSI, hardware access, MCP public-memory definitions, and register addresses. It exposes data consumed by slowpath ramrods (`pf_update_ramrod_data`), protocol-specific offload code, and Linux DCB netlink integration through `struct qed_eth_dcbnl_ops`.

## Risks and Edge Cases

- Override flags define which parts of a staged config are meaningful; callers must set them correctly or changes will not be included in local-admin MIB generation.
- `DCBX_CONFIG_MAX_APP_PROTOCOL` bounds app-entry arrays in the QED config view.
- `qed_dcbx_get_config_params()` and `qed_dcbx_config_params()` only exist under `CONFIG_DCB`, so non-DCB builds must avoid those symbols.
- `qed_dcbx_get_priority_tc()` depends on a valid operational snapshot and falls back to `QED_DCBX_DEFAULT_TC` in implementation when unavailable.

## Test Signals

Compile with `CONFIG_DCB=y` and disabled, run MCP DCBX MIB update paths, verify PF update ramrod data matches `qed_dcbx_results`, exercise DCB netlink get/set operations, and validate priority-to-TC lookups before and after operational MIB changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_dcbx.h -->
