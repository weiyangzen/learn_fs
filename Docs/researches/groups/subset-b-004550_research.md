# Research Group subset-b-004550

Grouped source research for Mellanox mlx5 direct steering HWS/SWS send, table, vport, action, command, debug, definer, domain, firmware helper, and ICM allocator files.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/send.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/send.c

Purpose: implements the HWS send engine that posts GTA table-access WQEs to mlx5 SQ/CQ rings, drains dependent WQEs, polls completions, advances rule status, and provides a firmware command fallback for WQE generation.

Important APIs/functions: `mlx5hws_send_queues_open/close`, `mlx5hws_send_queue_poll`, `mlx5hws_send_queue_action`, `mlx5hws_send_ste`, `mlx5hws_send_stes_fw`, `mlx5hws_send_engine_post_start/req_wqe/end`, `mlx5hws_send_add_new_dep_wqe`, `mlx5hws_send_all_dep_wqe`, and `mlx5hws_send_engine_flush_queue`. Static helpers allocate/open SQ/CQ objects, ring doorbells, retry collision RTC writes, decode CQEs, and update rule resize state.

Control flow: callers reserve WQEBBs through the post controller, fill GTA control/data, finalize a WQE control segment, and optionally ring the UAR doorbell. `mlx5hws_send_ste()` emits RTC1 then RTC0, preserving notify/fence semantics so the last hardware WQE signals completion. CQ polling walks unsignaled WQEs up to the completed counter, synthesizes success for earlier WQEs, parses the signaled CQE, updates `wr_priv`, and reports either into the caller result array or the internal completion list.

State/persistence: queue state lives in `mlx5hws_send_engine`, `send_sq`, `send_cq`, `wr_priv`, and `completed`. Rule state is mutated through `pending_wqes`, `status`, `rtc_0/rtc_1`, resize info, and action STE cleanup. SQ/CQ objects, work queues, doorbell records, and DMA-backed buffers are kernel/device resources created at queue-open time and destroyed on close. No disk persistence is present.

Dependencies/integration: depends on mlx5 core command and work-queue APIs, `internal.h`, clock timestamp selection, rule helpers, context capability flags, and HWS command `mlx5hws_cmd_generate_wqe`. It is integrated by the HWS rule path and context queue lifecycle; BWC queues add extra locks and queue slots.

Risks: ring arithmetic assumes power-of-two queue sizes and enough `MAX_WQES_PER_RULE` slots; completion handling must keep `pending_wqes`, `used_id`, and retry IDs consistent or rules leak/complete incorrectly. Doorbell ordering relies on DMA/write barriers. Firmware fallback cannot hardware-fence, so it drains synchronously before fenced writes. Error CQE logging intentionally prints only once per engine, which can hide later distinct failures.

Test signals: exercise create/update/delete rule flows with one and two RTCs, retry RTC path, dependent WQE drain, queue full/empty accounting, CQ error decoding, resize move failure/success, firmware WQE fallback, and teardown during device internal error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/send.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/send.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/send.h

Purpose: declares the HWS send-engine wire formats, queue/ring data structures, posting attributes, dependent-WQE records, and public send queue APIs.

Important APIs/types: defines `MAX_WQES_PER_RULE`, WQE opcode/opmod/GTA enums, `mlx5hws_wqe_ctrl_seg`, `mlx5hws_wqe_gta_ctrl_seg`, STE/argument GTA data segments, `mlx5hws_send_ring_cq`, `mlx5hws_send_ring_sq`, `mlx5hws_send_engine`, `mlx5hws_send_engine_post_attr`, and `mlx5hws_send_ste_attr`. Inline helpers expose empty/full/error checks, used-entry accounting, and generated completions.

Control flow/state: the header describes the contract used by `send.c`: callers build posts with `post_start`, one or more `post_req_wqe` buffers, then `post_end`; STE callers fill `mlx5hws_send_ste_attr` so the implementation can target RTC0/RTC1 and retry RTCs. `wr_priv` links posted WQEs back to rules and user data for CQ polling.

Dependencies/integration: types are consumed by HWS rule, action, and queue-management code through `internal.h`. The WQE fields are big-endian hardware layouts, so consumers must use conversion helpers before posting.

Risks: structure layout mirrors hardware PRM expectations; accidental padding/field changes or inconsistent WQE length constants can corrupt device commands. `mlx5hws_send_engine_gen_comp()` is a ring without overflow checks, relying on queue accounting.

Test signals: compile-time layout coverage, posting/polling integration tests, queue accounting around generated completions, and dual-RTC rule cases validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/send.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/table.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/table.c

Purpose: manages HWS flow-table objects, default FDB miss behavior, table creation/destruction, and chaining one table's miss path to another table or matcher RTC.

Important APIs/functions: `mlx5hws_table_create`, `mlx5hws_table_destroy`, `mlx5hws_table_get_id`, `mlx5hws_table_create_default_ft`, `mlx5hws_table_destroy_default_ft`, `mlx5hws_table_connect_to_miss_table`, `mlx5hws_table_update_connected_miss_tables`, `mlx5hws_table_ft_set_default_next_ft`, `mlx5hws_table_ft_set_next_rtc`, and `mlx5hws_table_ft_set_next_ft`.

Control flow: create validates HWS support and table type, creates a firmware flow table under `ctx->ctrl_lock`, obtains default STCs, initializes matcher/default-miss lists, and links into the context table list. FDB tables create/reference a shared default miss table that forwards to the eswitch-manager vport. Miss-table connection chooses the source table's last FT, then either sets a GOTO table miss action or connects the last FT directly to the first matcher RTCs in the destination table.

State/persistence: `mlx5hws_table` stores firmware table IDs, type, UID, level, matcher list, context list node, and default-miss relationship. The shared `ctx->common_res.default_miss` is refcounted. State is in-memory plus firmware flow table objects; no persistent storage.

Dependencies/integration: relies on HWS command wrappers, action default STC management, context capabilities (`ignore_flow_level_rtc_valid`, FDB levels), matcher RTC IDs, and Linux lists/mutexes.

Risks: miss-chain correctness depends on list ordering and lock discipline. Destroy refuses tables with matchers or incoming default-miss users, but misuse can leave firmware miss actions pointing at destroyed tables. FDB default miss refcounting assumes create/destroy paths remain paired.

Test signals: table create/destroy under empty and busy conditions, FDB default miss refcount reuse, connect/disconnect to empty and populated destination tables, matcher insertion order changes, and capability-disabled default miss support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/table.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/table.h

Purpose: defines HWS table and default-miss relationship structures plus flow-table helper prototypes.

Important APIs/types: `struct mlx5hws_default_miss` records a table's miss target and reverse list of source tables. `struct mlx5hws_table` stores context, firmware FT id/type, logical type/level/uid, matcher list, context list node, and default-miss metadata. Inline helpers map HWS table types to firmware flow-table types.

Control flow/state: the header establishes the state consumed by `table.c` and matcher code. `mlx5hws_table_get_fw_ft_type()` currently accepts only FDB tables and returns `FS_FT_FDB`; resource FW type helper distinguishes FDB RX/TX mirror cases.

Dependencies/integration: included through HWS internal headers, depends on `mlx5hws_context`, table type enums, mlx5 flow-table constants, and Linux `list_head`.

Risks: only FDB is supported here; adding NIC table types requires updating the inline type mappers and table creation logic together. Default-miss list ownership is manual and must remain synchronized with firmware miss actions.

Test signals: compile/build coverage for all callers, FDB table creation, invalid table type rejection, and default-miss list membership after connect/destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/vport.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/vport.c

Purpose: provides HWS vport GVMI lookup and caching for eswitch-manager contexts.

Important APIs/functions: `mlx5hws_vport_init_vports`, `mlx5hws_vport_uninit_vports`, and `mlx5hws_vport_get_gvmi`. Static helpers add a queried GVMI to an xarray and detect whether a vport is the eswitch manager PF/ECPF.

Control flow: initialization is a no-op outside eswitch manager mode; otherwise it initializes `vport_gvmi_xa`, queries the manager GVMI, and records uplink GVMI as zero. Lookup returns cached manager/uplink values for special vports or lazily queries other vports via `mlx5hws_cmd_query_gvmi`, inserts an `xa_mk_value`, and reloads to handle races/`-EBUSY`.

State/persistence: state is `ctx->vports.vport_gvmi_xa`, `esw_manager_gvmi`, and `uplink_gvmi`. It caches firmware query results in memory until context uninit destroys the xarray.

Dependencies/integration: depends on HWS command GVMI query, context capability flags (`eswitch_manager`, `is_ecpf`), mlx5 vport constants, and Linux xarray APIs. Consumers are vport/action paths needing hardware GVMI values.

Risks: no explicit locking surrounds xarray lookup/insert; the code tolerates insert races with reload, but callers must not use after uninit. Query failures are normalized to `-EINVAL` in the add path, losing original firmware error detail.

Test signals: manager PF and ECPF lookups, uplink lookup, dynamic VF/SF lookup, concurrent first lookup of one vport, non-eswitch-manager rejection, and teardown after cached entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/vport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/vport.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/vport.h

Purpose: declares the small HWS vport GVMI cache API.

Important APIs: `mlx5hws_vport_init_vports()` initializes per-context vport cache state, `mlx5hws_vport_uninit_vports()` tears it down, and `mlx5hws_vport_get_gvmi()` returns a GVMI for a vport.

Control flow/state: callers are expected to initialize once during context setup, query as vport destinations are used, and uninitialize during context teardown. The actual state fields live in the context and are implemented in `vport.c`.

Dependencies/integration: requires `struct mlx5hws_context` and kernel integer types from the HWS internal include chain.

Risks: the header does not expose locking or lifetime requirements; misuse before init or after uninit can race the implementation's xarray.

Test signals: build coverage and context lifecycle tests that call init/get/uninit in expected order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/vport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_action.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_action.c

Purpose: implements SWS direct-rule action construction, validation, conversion to STE action attributes, firmware helper destinations, packet reformat/modify-header actions, VLAN/ASO/range actions, and action destruction.

Important APIs/functions: `mlx5dr_actions_build_ste_arr`, `mlx5dr_action_create_drop`, `mlx5dr_action_create_dest_table`, `mlx5dr_action_create_dest_flow_fw_table`, `mlx5dr_action_create_dest_match_range`, `mlx5dr_action_create_mult_dest_tbl`, `mlx5dr_action_create_flow_counter`, `mlx5dr_action_create_tag`, `mlx5dr_action_create_flow_sampler`, `mlx5dr_action_create_packet_reformat`, `mlx5dr_action_create_pop_vlan`, `mlx5dr_action_create_push_vlan`, `mlx5dr_action_create_modify_header`, `mlx5dr_action_create_dest_vport`, `mlx5dr_action_create_aso`, `mlx5dr_action_get_pkt_reformat_id`, and `mlx5dr_action_destroy`.

Control flow: action arrays are validated against a domain/nic-direction state machine (`next_action_state`) that enforces legal ordering and terminal/nonterminal constraints. `mlx5dr_actions_build_ste_arr()` scans the action list, fills `mlx5dr_ste_actions_attr`, resolves destination ICM addresses, applies capability workarounds such as TTL checksum recalculation, and calls RX/TX STE action builders. Constructors allocate the typed action payload after `struct mlx5dr_action`, obtain firmware objects or DR resources as needed, and increment domain/table/action refcounts.

State/persistence: actions are refcounted kernel objects. Some own firmware packet reformat IDs, modify-header ICM allocations, match definers, multidestination firmware tables, or references to tables/domains/vports. Modify-header conversion stores HW action lists and may use single-action optimization or pattern/argument resources.

Dependencies/integration: depends on `dr_types.h`, `dr_ste.h`, command wrappers, domain vport/csum helpers, definer manager, argument/pattern managers, ICM pools, firmware helper table creation, and mlx5 capabilities. Rule creation consumes these actions to build STE arrays.

Risks: the state machine is dense and domain-specific; missing an action transition can accept invalid hardware programming or reject valid flows. Resource ownership is split by action type, making destroy-path parity critical. TTL modification uses hardware workaround logic that depends on destination type and vport helper tables. Modify-header conversion must respect field limitations, L3/L4 incompatibilities, and paired-action hazards.

Test signals: legal/illegal action order matrices for NIC RX/TX and FDB RX/TX, action destructor leak checks, modify-header SET/ADD/COPY conversion including TTL-last behavior, reformat parameter validation, multidestination with vport reformat, range hit/miss tables, and capability-disabled VLAN/encap/pop/push paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_action.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_arg.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_arg.c

Purpose: manages pools of header-modify argument objects for pattern/argument modify-header support.

Important APIs/functions/types: `mlx5dr_arg_mgr_create`, `mlx5dr_arg_mgr_destroy`, `mlx5dr_arg_get_obj`, `mlx5dr_arg_put_obj`, and `mlx5dr_arg_get_obj_id`; internal `dr_arg_pool` tracks one chunk-size class with a mutex and free list.

Control flow: manager creation builds pools for supported chunk sizes if the domain supports pattern arguments. A get request maps number of actions to a chunk size, obtains a free object from the matching pool, allocating a firmware modify-header-argument object range if the free list is empty, writes action data via `mlx5dr_send_postsend_args`, and returns the object. Put returns it to the pool list.

State/persistence: each `mlx5dr_arg_obj` records firmware object id, offset, and log chunk size. Pools cache unused argument slots in memory; firmware general objects persist until pool destroy frees only the first slot of each allocated range with `obj_offset == 0`.

Dependencies/integration: depends on domain capabilities for argument granularity/max allocation, command create/destroy helpers, send-post path for writing argument data, and Linux lists/mutexes.

Risks: object range destruction assumes the first slot is present in the free list at destroy; leaked/in-use args during manager destruction would leak firmware objects or skip destroy. Error normalization sometimes returns `-EAGAIN`/`-ENOMEM` rather than original command status. Pool sizing must track hardware granularity caps.

Test signals: allocation for 1/2/3/4 chunk-size classes, free-list exhaustion and refill, write failure rollback, unsupported large action count, manager create on unsupported domains, and destroy with all objects returned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_arg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_buddy.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_buddy.c

Purpose: implements a bitmap buddy allocator used by the SWS ICM pool for suballocating chunks inside a larger device-memory region.

Important APIs/functions: `mlx5dr_buddy_init`, `mlx5dr_buddy_cleanup`, `mlx5dr_buddy_alloc_mem`, and `mlx5dr_buddy_free_mem`. Internal `dr_buddy_find_free_seg()` scans free bitmaps from requested order upward.

Control flow: init allocates one bitmap per order, marks the single largest block free, and tracks free counts. Allocation finds the smallest available higher/equal order, clears it, splits down to the requested order by marking sibling blocks free, and returns a segment index in entry units. Free coalesces upward while the sibling bit is free, then marks the merged segment free.

State/persistence: state is in-memory bitmaps and `num_free` arrays within `mlx5dr_icm_buddy_mem`; it models ownership of already-created ICM memory but does not itself create hardware resources.

Dependencies/integration: used by `dr_icm_pool.c`; depends on Linux bitmap helpers and list node membership managed by the pool.

Risks: caller must serialize access; the allocator itself has no lock. Incorrect order/segment pairs on free can corrupt bitmaps. `mlx5dr_buddy_cleanup()` removes `list_node`, so callers must ensure the node is linked or list deletion is valid.

Test signals: allocate/free each order, split and coalesce back to max order, exhaustion behavior, repeated randomized alloc/free under pool lock, and cleanup after partial init failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_buddy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_cmd.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_cmd.c

Purpose: wraps mlx5 firmware command mailbox construction for SWS steering capabilities, flow tables/groups/FTEs, vport context, reformat/modify-header objects, definers, samplers, GIDs, and sync-steering.

Important APIs/functions: query helpers (`mlx5dr_cmd_query_device`, `mlx5dr_cmd_query_esw_caps`, `mlx5dr_cmd_query_esw_vport_context`, `mlx5dr_cmd_query_gvmi`, `mlx5dr_cmd_query_flow_table`, `mlx5dr_cmd_query_flow_sampler`, `mlx5dr_cmd_query_gid`), object helpers (`mlx5dr_cmd_create_flow_table`, `destroy_flow_table`, `create_empty_flow_group`, `destroy_flow_group`, `alloc/dealloc_modify_header`, `create/destroy_reformat_ctx`, `create/destroy_definer`, `create/destroy_modify_header_arg`), FTE helpers (`mlx5dr_cmd_set_fte`, `set_fte_modify_and_vport`, `del_flow_table_entry`), and `mlx5dr_cmd_sync_steering`.

Control flow: each function creates stack or kvzalloc command buffers, fills PRM fields with `MLX5_SET/GET`, executes via `mlx5_cmd_exec*`, copies returned IDs/addresses into DR structs, and frees temporary buffers. `mlx5dr_cmd_set_fte()` builds variable-size destination arrays, handles extended destination format when multiple forwarding destinations include encapsulation, encodes counters separately, and fills match values/action metadata.

State/persistence: this file owns no long-lived state; it creates, modifies, queries, or destroys firmware/device objects on behalf of higher layers. Returned IDs become persistent firmware resources until destroy helpers are called.

Dependencies/integration: depends on mlx5 command interface, capability macros, eswitch/vport helpers, flow-table PRM layouts, and DR command data structures. It is the low-level bridge used by action, domain, definer, firmware helper, and ICM argument code.

Risks: mailbox layouts are sensitive to table type, destination type, opmod, and variable-length sizing. Extended-destination support must match firmware caps or FTE creation fails. Some destroy helpers ignore command errors, which can hide firmware cleanup failures. `sync_steering` intentionally no-ops during internal error state.

Test signals: command-buffer field validation with firmware simulators, capability-query matrix across NIC/FDB devices, FTE creation with counters/vports/uplink/flow tables/samplers/extended encap, reformat and definer lifecycle, and destroy paths after partial create failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_dbg.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_dbg.c

Purpose: exposes SWS steering state through debugfs as a CSV-like dump of domains, capabilities, send rings, tables, matchers, rules, STE hardware bytes, and actions.

Important APIs/functions: public list hooks `mlx5dr_dbg_tbl_add/del` and `mlx5dr_dbg_rule_add/del`, lifecycle `mlx5dr_dbg_init_dump` and `mlx5dr_dbg_uninit_dump`, plus seq-file callbacks generated by `DEFINE_SEQ_ATTRIBUTE(dr_dump)`. Static dump helpers format each object family and action type into record IDs.

Control flow: init creates `steering/fdb/dmn_%p` debugfs entries only for FDB domains and initializes debug lists/mutex. On read, `dr_dump_start()` prevents concurrent dumps with an atomic state, lazily allocates 64 MiB buffers, locks the domain/debug list, walks domain->tables->matchers->rules, appends formatted records, and then seq iteration streams buffer list entries. Stop frees buffers at end-of-read and releases the state.

State/persistence: debug state lives in `dmn->dump_info` plus debug list nodes embedded in tables/rules. Dump data is transient per read. Debugfs entries persist for the domain lifetime.

Dependencies/integration: depends on debugfs, seq_file, Linux version macros, hex conversion, domain/table/matcher/rule/action internals, ICM address helpers, and action argument helpers.

Risks: dump generation can allocate large buffers and walks live steering objects; lock coverage must prevent mutation races without deadlocking with normal rule/table paths. Some pointer-derived IDs are truncated to 32 bits for readability and are not stable across boots. Dump state reset must handle early errors or debugfs reads can remain blocked.

Test signals: debugfs read with empty and populated FDB domain, unsupported NIC domain init behavior, concurrent read rejection, table/rule add/del list consistency, dumping all action types, and memory cleanup after interrupted/failed dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_dbg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_dbg.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_dbg.h

Purpose: declares debug dump constants, transient buffer structures, domain debugfs state, and public debug list/lifecycle hooks for SWS steering.

Important APIs/types: `MLX5DR_DEBUG_DUMP_BUFF_SIZE`, `MLX5DR_DEBUG_DUMP_BUFF_LENGTH`, dump state enum, `mlx5dr_dbg_dump_buff`, `mlx5dr_dbg_dump_data`, `mlx5dr_dbg_dump_info`, and function prototypes for init/uninit and table/rule add/delete.

Control flow/state: `mlx5dr_dbg_dump_info` is embedded in the domain and stores mutex-protected debug lists, debugfs dentries, current dump buffer data, and atomic dump state. The .c file allocates/frees buffers and populates list nodes.

Dependencies/integration: requires `struct mlx5dr_domain`, `struct mlx5dr_table`, `struct mlx5dr_rule`, Linux list/dentry/mutex/atomic definitions through DR includes.

Risks: buffer size is large by design; increasing it affects memory pressure. The header exposes list-management functions but not lifetime constraints, so callers must pair add/del with object lifecycle.

Test signals: compile coverage, FDB debugfs lifecycle, add/del calls during table/rule create/destroy, and repeated read/free cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_dbg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_definer.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_definer.c

Purpose: caches firmware match definer objects by selector/mask tuple and provides refcounted get/put operations.

Important APIs/functions/types: `mlx5dr_definer_get`, `mlx5dr_definer_put`, and internal `dr_definer_object` containing firmware id, format id, DW/byte selectors, match mask, and refcount.

Control flow: get scans the domain xarray for an identical definer. On miss, it allocates a new object, creates the firmware definer, rejects IDs beyond the 8-bit STE encoding limit, copies selectors/mask, sets refcount, and inserts it by ID into `dmn->definers_xa`. On hit, it increments the refcount. Put loads by ID, logs if missing, and destroys/erases the object when the refcount reaches zero.

State/persistence: definers are firmware general objects cached in `dmn->definers_xa` for the domain lifetime or until the last user releases them. No disk persistence.

Dependencies/integration: used by range action creation and any code needing SELECT definers. Depends on command create/destroy helpers, DR STE match-tag size, xarray, and refcount APIs.

Risks: find and insert are not locally locked; callers need domain-level synchronization to avoid duplicate creation races. Firmware definer IDs greater than 255 are unusable by STE format and cause cleanup. Put with a stale/missing ID only logs, so caller lifecycle bugs may leak references elsewhere.

Test signals: duplicate get returns same ID and increments refcount, put destroys only after final release, selector/mask mismatch creates distinct objects, high firmware ID rejection, and concurrent get race coverage under expected locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_definer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_domain.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_domain.c

Purpose: owns SWS domain creation/destruction, capability discovery, vport capability caching, memory/send resources, checksum-recalculation helper table cache, modify-header pattern/argument resources, and peer-domain mapping.

Important APIs/functions: `mlx5dr_domain_create`, `mlx5dr_domain_destroy`, `mlx5dr_domain_is_support_ptrn_arg`, `mlx5dr_domain_get_recalc_cs_ft_addr`, `mlx5dr_domain_get_vport_cap`, and `mlx5dr_domain_set_peer`. Static helpers initialize caps, ICM pools, send ring, PD/UAR, vport caps, checksum table xarray, and modify-header resources.

Control flow: create allocates and initializes the domain, queries device/FDB capabilities, checks SW steering support for the requested domain type, sets max chunk sizes, allocates PD/UAR/memory pools/send ring/pattern-arg managers, initializes checksum table cache and debugfs, then returns. Destroy requires refcount 1, syncs steering, removes debugfs, destroys cached checksum FTs, send/memory resources, caps/xarrays, mutexes, and the domain.

State/persistence: domain state includes capabilities, RX/TX default/drop ICM addresses, vport cap xarray, definer xarray, peer-domain xarray, ICM pools, kmem caches, send ring, PD, UAR, pattern/argument managers, checksum-recalc FW table cache, debugfs state, and refcount. Firmware/device resources persist only for the domain lifetime.

Dependencies/integration: depends on command wrappers, ICM pool, send ring, STE context selection, FW helper tables, debug dump, eswitch/vport data, and mlx5 core PD/UAR APIs. Higher-level tables/rules/actions all hang from a domain.

Risks: partial init unwinding is complex and must mirror init order. `dr_domain_caps_uninit()` always clears FDB vport xarray, so caps init failure paths must ensure it was initialized. Cached vport and checksum helper entries can be created lazily and must not race teardown. Peer domain replacement adjusts refcounts under domain lock.

Test signals: create/destroy for NIC RX/TX/FDB across capability combinations, partial failure injection for each resource stage, vport cap lazy query and `-EBUSY` race, checksum FT cache creation, peer mapping refcount updates, and destroy while references remain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_domain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_fw.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_fw.c

Purpose: builds and tears down small firmware-owned flow tables used as helpers by SWS actions, specifically checksum-recalculation tables and multidestination forwarding tables.

Important APIs/functions: `mlx5dr_fw_create_recalc_cs_ft`, `mlx5dr_fw_destroy_recalc_cs_ft`, `mlx5dr_fw_create_md_tbl`, and `mlx5dr_fw_destroy_md_tbl`.

Control flow: checksum-recalc creation allocates a terminal FDB flow table near max level, creates an empty group, allocates a modify-header action that adds zero to IPv4 TTL to trigger checksum recalculation, inserts an FTE forwarding to a vport, and returns IDs plus RX ICM address. Multidest creation allocates an FDB table at an allowed multipath level, creates a group, programs an FTE forwarding to the supplied destination array, and returns table/group IDs. Destroy paths delete the FTE, group, table, and modify-header resources in reverse order.

State/persistence: returned structs/IDs represent firmware flow tables, groups, entries, and modify-header contexts. The domain caches checksum tables in `dr_domain.c`; multidest actions retain their table/group IDs until action destroy.

Dependencies/integration: depends on `dr_cmd.c` command wrappers, domain capabilities, action multidestination construction, and TTL workaround logic from `dr_action.c`.

Risks: helper tables consume firmware flow-table levels and resources; failures must unwind all created objects. Destroy helpers assume IDs were fully initialized. The TTL workaround is specific to FDB RX checksum recalculation behavior and must stay aligned with action selection logic.

Test signals: create/destroy checksum table per vport, injected failures after table/group/modify-header/FTE creation, multidest with and without reformat, ignore-flow-level propagation, and action destroy releasing multidest tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_icm_pool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_icm_pool.c

Purpose: manages SWS ICM device-memory pools for STEs, modify actions, and modify-header patterns, including device-memory allocation, mkey registration, buddy suballocation, hot/free-after-sync handling, and STE software cache setup.

Important APIs/functions/types: `mlx5dr_icm_pool_create/destroy`, `mlx5dr_icm_alloc_chunk`, `mlx5dr_icm_free_chunk`, `mlx5dr_icm_pool_alloc_htbl/free_htbl`, address/key/size helpers (`get_chunk_mr_addr`, `get_chunk_rkey`, `get_chunk_icm_addr`, `get_chunk_byte_size`, `get_chunk_num_of_entries`), and internal `mlx5dr_icm_pool`, `mlx5dr_icm_mr`, and hot chunk records.

Control flow: pool creation sets max chunk size and hot-memory threshold by ICM type, creates a hot chunk array, and later lazily creates buddy memories. Buddy creation allocates SW ICM device memory, registers an mkey, initializes a buddy allocator, and for STE pools preallocates software STE, HW STE byte, and miss-list caches. Chunk allocation finds or creates a buddy with free space, allocates a chunk object, initializes STE cache pointers, and updates used memory. Free moves the segment into a hot array, frees the chunk object, and syncs steering plus returns hot segments to buddies when threshold is exceeded.

State/persistence: pools hold buddy memory lists, hot chunks awaiting hardware sync, mkeys, device-memory object IDs, ICM start addresses, and kmem caches. Hardware may keep reading freed chunks until `sync_steering` completes; hot memory models that delayed reclamation.

Dependencies/integration: depends on buddy allocator, mlx5 SW ICM allocation/deallocation, mkey creation/destruction, domain PD/caps, command sync, and STE/table code that consumes chunks.

Risks: hot chunk array sizing must cover threshold behavior; overflow would corrupt memory. Sync is required before reusing freed hardware-visible memory. Destroy clears hot chunks before destroying buddies, so outstanding users at destroy are unsafe. Alignment and entry-size calculations must match PRM for each ICM type.

Test signals: allocation/free for all ICM types and chunk sizes, threshold-triggered sync and buddy destruction, address/rkey helper correctness, partial failure of DM/mkey/buddy/STE cache allocation, randomized buddy reuse, and destroy with no outstanding chunks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_icm_pool.c -->
