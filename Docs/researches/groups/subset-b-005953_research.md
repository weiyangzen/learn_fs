# subset-b-005953 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/rdmavt_qp.h -->
# sources/distributed-fs/ceph-client/include/rdma/rdmavt_qp.h

Purpose: Defines the rdmavt queue pair core data model used by software RDMA transports. It covers QP send/receive state, SWQE/RWQE rings, ACK queues, multicast tracking, QPN allocation maps, retry/RNR timers, and helper routines used by RC/UC/UD processing.

Important APIs/types/functions: `struct rvt_qp` is the central state object, embedding `struct ib_qp`, AH attributes, send queue, receive queue, PSNs, MSN/SSN counters, retry counters, locks, timers, and flexible receive SGEs. `struct rvt_swqe`, `struct rvt_rq`, `struct rvt_krwq`, `struct rvt_ack_entry`, `struct rvt_qpn_table`, and multicast structs describe the queue and namespace machinery. Inline helpers include `rvt_lookup_qpn()`, `rvt_get_swqe_ptr()`, `rvt_get_rwqe_ptr()`, `rvt_qp_complete_swqe()`, `rvt_recv_cq()`, `rvt_send_cq()`, credit checks, timer modifiers, and refcount helpers. External hooks include `rvt_get_rwqe()`, `rvt_error_qp()`, `rvt_copy_sge()`, `rvt_rc_error()`, iterator functions, and MR cleanup.

Control flow and state: Posting and completion revolve around ring indices (`s_head`, `s_tail`, `s_cur`, `s_acked`, `s_last`) and receive head/tail queues. `s_flags` encodes wait, timer, credit, ACK, and send gating states; `r_flags` and `r_aflags` track receive-side replay and response conditions. `rvt_qp_complete_swqe()` unreserves reserved WQEs before advancing `s_last` with release ordering, then optionally emits a CQE according to signaled-completion rules. `rvt_lookup_qpn()` uses RCU and a QPN hash table, while QP 0/1 are port-special. Retry timers must be called with `s_lock` held.

Dependencies and integration: Depends on RDMA core verbs, rdmavt CQ/MR/AH/SGL types, Linux timers, atomics, RCU, vmalloc, spinlocks, wait queues, and low-level rdmavt driver private data. It is consumed by rdmavt providers such as hfi1/qib and by RC/UC/UD send/receive engines.

Risks and test signals: High risk areas are lock ordering between `r_rq.lock` and `s_lock`, ring wrap calculations for flexible WQE sizes, release/acquire ordering around `s_last`, timer races, AH attribute lifetime on UD WQEs, RCU lookup lifetime, and CQ full error transitions. Test signals include post-send/post-recv stress, CQ overflow paths, RNR/retry timer behavior, PSN wrap/retry, QPN allocation collisions, multicast attach/detach, and KASAN/KCSAN coverage under parallel traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/rdmavt_qp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/restrack.h -->
# sources/distributed-fs/ceph-client/include/rdma/restrack.h

Purpose: Declares RDMA resource tracking metadata used to expose kernel and user RDMA resources through nldev/netlink and to coordinate resource lifetime.

Important APIs/types/functions: `enum rdma_restrack_type` names tracked objects such as PD, CQ, QP, CM_ID, MR, CTX, COUNTER, SRQ, and DMAH. `struct rdma_restrack_entry` stores validity, no-track state, kref/completion, owner task or kernel name, resource type, user/kernel ownership, and exported ID. APIs include `rdma_restrack_count()`, `rdma_restrack_get()`, `rdma_restrack_put()`, `rdma_restrack_get_byid()`, `rdma_restrack_no_track()`, `rdma_restrack_is_tracked()`, and netlink driver-attribute emitters.

Control flow and state: Entries are filled during add and may be concurrently observed until delete completes. The kref plus completion protect object destruction while netlink dump or lookup users hold references. `no_track` suppresses database exposure but leaves the resource usable internally. `user` distinguishes process-owned objects from kernel-created objects.

Dependencies and integration: Depends on `ib_device`, netlink SKBs, Linux kref/completion/task/xarray, and UAPI RDMA netlink identifiers. Drivers integrate by embedding an entry in RDMA objects and publishing optional driver-specific attributes.

Risks and test signals: Risks include leaking task references, marking objects untracked without review, exposing stale IDs, and missing get/put pairs during nldev dumps. Tests should cover resource create/destroy races while dumping `rdma resource`, no-track resources, driver detail attributes, and module unload with active references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/restrack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/rw.h -->
# sources/distributed-fs/ceph-client/include/rdma/rw.h

Purpose: Defines the RDMA READ/WRITE context abstraction that maps block or scatterlist I/O into send work requests, optionally using memory registration or signature offload.

Important APIs/types/functions: `struct rdma_rw_ctx` records operation count and mapping type, with variants for a single SGE, multiple SGEs, IOVA-based bvec mapping, or a registration context containing RDMA WR, REG WR, invalidate WR, MR, and SG table. APIs include `rdma_rw_ctx_init()`, `rdma_rw_ctx_destroy()`, bvec variants, signature variants, `rdma_rw_ctx_wrs()`, `rdma_rw_ctx_post()`, MR sizing helpers, QP initialization, MR pool initialization, and cleanup.

Control flow and state: Callers initialize a context from SG/bvec input, obtain or post the generated WR chain, then destroy the context to unmap DMA and release MRs. The `type` field selects which union branch is valid; `nr_ops` excludes MR management WRs. Signature contexts additionally include protection SG lists and `ib_sig_attrs`.

Dependencies and integration: Integrates RDMA core verbs, RDMA CM, MR pools, DMA mapping, scatterlists, bio vectors, and block/storage clients such as NVMe/RDMA or SCSI RDMA transports.

Risks and test signals: Risks include mismatched init/destroy direction or SG counts, leaking MRs, invalid DMA unmap lengths, WR chain ordering with local invalidation, and underestimating send WR needs. Tests should cover single-SGE, multi-SGE, bvec IOVA, registration-backed transfer, signature offload, bidirectional error unwind, and QP attr sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/rw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/signature.h -->
# sources/distributed-fs/ceph-client/include/rdma/signature.h

Purpose: Provides RDMA signature/T10-DIF capability and attribute types for protection information handover between memory and wire domains.

Important APIs/types/functions: Capability enums advertise T10 DIF types and guard algorithms. `struct ib_t10_dif_domain` describes DIF interval, guard seed/type, application tag, reference tag, remap and escape behavior, and check mask. `struct ib_sig_domain` wraps the signature type, `struct ib_sig_attrs` describes memory and wire domains plus check mask and metadata length, and `struct ib_sig_err` reports guard/ref/app tag failures.

Control flow and state: This header carries configuration only; providers consume attributes when building registered MRs or signature RDMA operations. Error records identify the failed field, expected/actual values, offset, and key.

Dependencies and integration: Used by RDMA verbs providers and `rdma_rw_ctx_signature_init()`. It aligns with T10 PI/DIF and storage transports that need end-to-end data protection.

Risks and test signals: Main risks are mismatched memory/wire domains, incorrect interval or tag remap semantics, and incomplete check masks. Test signals include guard CRC and checksum cases, type 1/2/3 DIF, reference tag rollover/remap, escape tag behavior, and injected signature errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/signature.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/tid_rdma_defs.h -->
# sources/distributed-fs/ceph-client/include/rdma/tid_rdma_defs.h

Purpose: Defines on-wire packet layouts and opcodes for Intel TID RDMA extensions carried under the InfiniBand opcode space.

Important APIs/types/functions: Packet structs cover TID RDMA read request/response, write request/response/data, resync, and ACK. Each includes KDETH words and fields such as RETH, AETH, TID flow PSN/QP, verbs PSN, and verbs QP. `IB_OPCODE_TID_RDMA` and enum entries create specific opcodes via `IB_OPCODE()`. `IB_WR_TID_RDMA_WRITE` and `IB_WR_TID_RDMA_READ` map to reserved verbs work request opcodes.

Control flow and state: This is a format contract. Drivers encode/decode TID flow and verbs flow state across request, response, data, resync, and ACK messages. The structs mix little-endian KDETH fields and big-endian IB fields, so callers must preserve byte ordering.

Dependencies and integration: Depends on `rdma/ib_pack.h`; used by hfi1/rdmavt style drivers implementing TID RDMA acceleration.

Risks and test signals: Risks include struct layout drift, endian mistakes, opcode collisions, and mismatched TID/verbs PSN tracking. Tests should include packet encode/decode golden vectors, sparse endian checking, write/read ACK sequencing, resync recovery, and interop with non-TID paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/tid_rdma_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/uverbs_ioctl.h -->
# sources/distributed-fs/ceph-client/include/rdma/uverbs_ioctl.h

Purpose: Defines the RDMA uverbs ioctl description DSL, radix-tree key encoding, parsed attribute bundle, and helper accessors for safely moving data and object references between userspace and RDMA drivers.

Important APIs/types/functions: `struct uverbs_attr_spec`, `uverbs_attr_def`, `uverbs_method_def`, `uverbs_object_def`, and `uapi_definition` describe objects, methods, write commands, attributes, support predicates, and chained definitions. Macros such as `DECLARE_UVERBS_OBJECT`, `DECLARE_UVERBS_WRITE`, `UAPI_DEF_*`, `UVERBS_ATTR_PTR_IN/OUT`, `UVERBS_ATTR_IDR`, `UVERBS_ATTR_FD`, `UVERBS_ATTR_ENUM_IN`, and `UVERBS_ATTR_UHW` build compile-time API tables. `uapi_key_*` helpers compress object/method/attr IDs. Runtime helpers include `uverbs_attr_get()`, object and length accessors, `uverbs_copy_from()`, `uverbs_copy_from_or_zero()`, allocation helpers, flag/const getters, and `ib_copy_validate_udata_in*()`.

Control flow and state: The parser validates mandatory attributes, object access mode, user pointer sizes, extension zeroing, and driver udata. Parsed data is stored in `struct uverbs_attr_bundle`, whose header carries `ib_udata`, user file, context, current uobject, and an attr-present bitmap. Object attributes refer to looked-up `ib_uobject`s; pointer attributes may be inline or user pointers. Compatibility helpers zero-pad or reject non-zero extension bytes depending on the declared ABI shape.

Dependencies and integration: Depends on uverbs object types, RDMA UAPI ioctl IDs, userspace copy helpers, `ib_uverbs_file`, `ib_ucontext`, and `ib_device_ops` feature detection. Driver method handlers receive `struct uverbs_attr_bundle`.

Risks and test signals: Risks include key-space overflow, wrong namespace/core ID encoding, missing mandatory attributes, insufficient zero-trailing checks, copying less/more than declared, stale uobject access mode, and disabled-user-access stubs returning `-EINVAL`. Tests should cover every attr type, old/new struct compatibility, invalid comp masks, object create/destroy lifetimes, driver UHW passthrough, and fuzzed ioctl payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/uverbs_ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/uverbs_named_ioctl.h -->
# sources/distributed-fs/ceph-client/include/rdma/uverbs_named_ioctl.h

Purpose: Provides naming macros that turn uverbs object/method declarations into module-scoped static symbols using `UVERBS_MODULE_NAME`.

Important APIs/types/functions: `UVERBS_METHOD()`, `UVERBS_HANDLER()`, and `UVERBS_OBJECT()` paste module names into generated symbols. `DECLARE_UVERBS_NAMED_METHOD`, `DECLARE_UVERBS_NAMED_METHOD_DESTROY`, `DECLARE_UVERBS_NAMED_OBJECT`, `DECLARE_UVERBS_GLOBAL_METHODS`, `ADD_UVERBS_METHODS`, and `ADD_UVERBS_ATTRIBUTES_SIMPLE` create uverbs definition tables.

Control flow and state: This header has no runtime state. It builds arrays of attribute pointers and method pointers, then wraps them into `uverbs_method_def` and `uverbs_object_def`. Destroy methods can use the shared `uverbs_destroy_def_handler`.

Dependencies and integration: Depends on `rdma/uverbs_ioctl.h` and must be included only after defining `UVERBS_MODULE_NAME`. Drivers use it to add named driver-specific object trees or attributes to the common uverbs API.

Risks and test signals: Risks include symbol collisions, forgetting `UVERBS_MODULE_NAME`, handler naming mismatches, and accidentally declaring methods without handlers. Build coverage is the main test signal; runtime ioctl smoke tests should verify that added methods and attributes are visible and parse correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/uverbs_named_ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/uverbs_std_types.h -->
# sources/distributed-fs/ceph-client/include/rdma/uverbs_std_types.h

Purpose: Supplies standard uverbs object lookup/allocation/destroy helpers and flow object support for write-based and ioctl-based RDMA user APIs.

Important APIs/types/functions: Macros `uobj_get_read()`, `uobj_get_write()`, `uobj_get_destroy()`, `uobj_perform_destroy()`, `uobj_alloc()`, and `uobj_get_obj_read()` wrap lookup against a uverbs API object. `uobj_put_*()`, `uobj_alloc_abort()`, and `uobj_finalize_uobj_create()` handle lifetime completion. `struct uverbs_api_object` records type attributes, type class, disabled state, and object ID. Flow helpers include `ib_uflow_resources`, `ib_uflow_object`, `flow_resources_alloc/add/free()`, `uverbs_flow_action_fill_action()`, and `ib_set_flow()`.

Control flow and state: IDR/FD lookups are done with explicit read/write/destroy modes and must be paired with the matching put. Allocation starts through core uobject APIs, initializes driver object pointers, then commits or aborts. Flow resources track counters and action collections associated with an `ib_flow`.

Dependencies and integration: Depends on uverbs type classes, ioctl bundles, RDMA user ioctl verbs, `ib_uobject`, `ib_flow`, `ib_qp`, and `ib_device`.

Risks and test signals: Risks include wrong ID type for legacy write API, missing put on error paths, committing an uninitialized object, usecount leaks on QPs, and flow resource cleanup mismatches. Tests should cover read/write/destroy lookup modes, create abort paths, default destroy handler paths, flow creation with counters/actions, and object disable behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/uverbs_std_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/uverbs_types.h -->
# sources/distributed-fs/ceph-client/include/rdma/uverbs_types.h

Purpose: Defines the core uverbs object type classes, user file state, lookup modes, and allocation macros for IDR-backed and FD-backed RDMA userspace objects.

Important APIs/types/functions: `enum rdma_lookup_mode` distinguishes read, write, and destroy lookups. `struct uverbs_obj_type_class` defines callbacks for allocation, lookup, destroy, handle removal, and object swapping. `struct uverbs_obj_type`, `uverbs_obj_idr_type`, and `uverbs_obj_fd_type` specialize object storage. `struct ib_uverbs_file` owns context, async file, object lists, hw-destroy synchronization, mmap state, IDR xarray, and disassociation locking. Functions include lookup/allocation/commit/abort/assign, kref get/put, object locking, and FD release.

Control flow and state: Valid lifecycles are documented as allocate-begin/commit/abort, lookup-get/put, and destroy lookup/remove/put sequences. `hw_destroy_rwsem` coordinates hardware object teardown with object-list traversal. `ucontext_lock` protects context access, while the object list and xarray map user handles to `ib_uobject`s.

Dependencies and integration: Depends on RDMA verbs, Linux krefs, mutexes, rwsems, xarray, file operations, and uverbs API objects. It is the substrate used by `uverbs_ioctl.h` and `uverbs_std_types.h`.

Risks and test signals: Risks include violating documented lifecycle order, detaching objects concurrently with driver calls, incorrect lookup lock mode, FD close races, and disassociation cleanup. Tests should include parallel object lookup/destroy, FD object release, driver unload while userspace holds handles, context cleanup, and lockdep coverage of `hw_destroy_rwsem`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/uverbs_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rv/automata.h -->
# sources/distributed-fs/ceph-client/include/rv/automata.h

Purpose: Provides generic accessors for deterministic automata generated by the kernel RV tooling, parameterized by `MONITOR_NAME`.

Important APIs/types/functions: Macro aliases derive `RV_AUTOMATON_NAME`, `EVENT_MAX`, `STATE_MAX`, `events`, and `states` from the generated monitor name. Helpers return state names, event names, initial state, next state, and final-state status from the generated automaton tables.

Control flow and state: The helper layer is read-only. `model_get_next_state()` bounds-checks current state and event before indexing the transition table and returns `INVALID_STATE` for invalid input.

Dependencies and integration: Must be included with an rvgen-generated model header defining `MONITOR_NAME`, enums, `INVALID_STATE`, and automaton tables. Used by DA and HA monitor templates.

Risks and test signals: Risks are generated model/header mismatches, invalid enum ranges, and missing `MONITOR_NAME`. Tests should compile generated monitors, validate transition table dimensions, and exercise invalid state/event handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rv/automata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rv/da_monitor.h -->
# sources/distributed-fs/ceph-client/include/rv/da_monitor.h

Purpose: Implements deterministic automata runtime-monitor templates for global, per-CPU, per-task, and per-object Linux runtime verification monitors.

Important APIs/types/functions: Defines `rv_this`, hook macros for HA extensions, `da_monitor_reset/start/enabled/handling_event`, monitor storage for each `RV_MON_TYPE`, trace/error helpers, and event entry points such as `da_handle_event()`, `da_handle_start_event()`, and `da_handle_start_run_event()`. Per-object mode uses `struct da_monitor_storage`, an RCU hash table, and helpers for create/get/destroy/fill storage.

Control flow and state: A monitor starts in the model initial state and ignores events until monitoring is enabled. Event handling reads `curr_state`, computes the next state, atomically updates with `try_cmpxchg`, invokes extension hooks, traces transitions, and resets on invalid transitions or too many racing retries. Per-task monitors allocate task RV slots; per-object monitors allocate hash entries and free them with RCU.

Dependencies and integration: Depends on generated automata, Linux RV core, tracepoints generated per monitor, task RV storage, RCU, hashtables, delayed work context assumptions, and optional HA hooks.

Risks and test signals: Risks include racing event updates, unsafe allocation in event context, per-object lifetime leaks, task slot exhaustion, reset-hook ordering, and tracepoint signature mismatch. Tests should compile each monitor type, run concurrent event streams, force invalid transitions, exercise per-object create/destroy under RCU, and verify trace/error emission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rv/da_monitor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rv/ha_monitor.h -->
# sources/distributed-fs/ceph-client/include/rv/ha_monitor.h

Purpose: Extends deterministic RV monitors with hybrid automata environment variables, clock constraints, invariant timers, and environment-aware reactions.

Important APIs/types/functions: Includes DA monitor after installing HA hooks. Important helpers include `ha_monitor_init_env()`, `ha_monitor_reset_env()`, `ha_monitor_handle_constraint()`, `ha_get_env_string()`, clock helpers for ns and jiffies, invariant conversion helpers, timer setup/start/cancel for timer wheel and hrtimer modes, and trace/reaction helpers.

Control flow and state: HA state overlays `struct ha_monitor` on `struct da_monitor`; a static assertion requires `da_mon` at offset zero. Initialization resets stored environment values and sets up timers. Each DA transition invokes `ha_verify_constraint()` with cached time; failure emits reaction and trace data and rejects the transition. Timers can fire without an event, report the current environment, and reset the DA monitor. Environment storage uses `ENV_INVALID_VALUE` and changes representation between guard reset timestamps and invariant expiration timestamps.

Dependencies and integration: Depends on generated monitor-provided `ha_get_env()` and `ha_verify_constraint()`, RV reactors, seq buffers, Linux timers/hrtimers, and DA monitor types. Timer behavior varies by `HA_TIMER_TYPE`, `HA_CLK_NS`, and monitor scope.

Risks and test signals: Risks include invalid env index use, mixing guard and invariant representations, timer callback racing with transition handling, per-CPU timer affinity mistakes, and missing generated HA callbacks. Tests should cover constraint pass/fail, timer expiry, ns/jiffy clocks, invariant conversion, monitor reset cancellation, and reactor/trace output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rv/ha_monitor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rv/instrumentation.h -->
# sources/distributed-fs/ceph-client/include/rv/instrumentation.h

Purpose: Provides small tracepoint attach/detach macros for generated RV monitor instrumentation.

Important APIs/types/functions: `rv_attach_trace_probe(monitor, tp, rv_handler)` type-checks a trace callback and registers it, warning on failure. `rv_detach_trace_probe()` unregisters the callback.

Control flow and state: The macros bind monitor handlers to static tracepoints. Attach uses the tracepoint-generated `check_trace_callback_type_*` and `register_trace_*`; detach uses `unregister_trace_*`.

Dependencies and integration: Depends on Linux ftrace tracepoint APIs and generated trace event symbols. Used by generated DA/LTL monitor code during init/destroy.

Risks and test signals: Risks are handler signature drift, attach failure ignored beyond warning, and missing detach on module unload. Tests should build with tracepoint type checks, enable/disable monitors repeatedly, and inspect warning paths for failed registrations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rv/instrumentation.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rv/ltl_monitor.h -->
# sources/distributed-fs/ceph-client/include/rv/ltl_monitor.h

Purpose: Implements a generated LTL monitor runtime over per-task RV storage, including atom tracking, Büchi-state validation, trace output, and violation reaction.

Important APIs/types/functions: Defines a module-specific `rv_monitor`, allocates `ltl_monitor_slot`, initializes per-task `struct ltl_monitor`, and provides `ltl_atom_set()`, `ltl_atom_update()`, `ltl_atom_pulse()`, `ltl_validate()`, `ltl_trace_event()`, and task-newtask handling. Generated code must provide atom fetch/init, atom names, start logic, next-state calculation, and trace events.

Control flow and state: Init allocates a task monitor slot, attaches `task_newtask`, initializes all existing process threads and idle tasks, and marks atoms initially unknown. Atom updates clear unknown bits, refresh atoms, start the monitor once all atoms are known, compute possible next states from all active BA states, copy next states into the monitor, and react if no valid state remains.

Dependencies and integration: Depends on Linux RV task slots, tasklist traversal, scheduler/task tracepoints, seq buffers, generated LTL monitor helpers, and RV reactors.

Risks and test signals: Risks include task slot leaks, missing new-task initialization, atom unknown-state bugs, bitmap size mismatches, and trace buffer truncation. Tests should cover monitor load/unload, task creation, atom pulse semantics, violation traces, concurrent task updates, and generated model boundary sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rv/ltl_monitor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/fc/fc_encaps.h -->
# sources/distributed-fs/ceph-client/include/scsi/fc/fc_encaps.h

Purpose: Defines Fibre Channel frame encapsulation constants and SOF/EOF helpers based on RFC 3643.

Important APIs/types/functions: `struct fc_encaps_hdr` describes the FCIP-style encapsulation header with protocol/version complements, protocol data, length/flags, timestamp, CRC, and SOF. Enums define SOF, EOF, and FC classes. Helpers include `fc_sof_needs_ack()`, `fc_sof_normal()`, `fc_sof_class()`, and `fc_sof_is_init()`.

Control flow and state: This is a stateless wire-format header. Helpers derive class and ACK requirements from SOF byte encodings and convert initial SOF to normal SOF.

Dependencies and integration: Used by FCoE/libfc frame handling and FC frame allocation. Relies on FC payload size definitions from FC headers included elsewhere.

Risks and test signals: Risks include malformed macro definitions for redundant SOF/EOF encoding, incorrect frame length accounting, and class derivation errors. Tests should validate header size, SOF/EOF golden encodings, class helper results, and min/max encapsulated frame lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/fc/fc_encaps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/fc/fc_fc2.h -->
# sources/distributed-fs/ceph-client/include/scsi/fc/fc_fc2.h

Purpose: Defines FC-2 exchange and sequence status wire structures and status flags.

Important APIs/types/functions: `struct fc_ssb` models the packed Sequence Status Block with sequence ID, count range, status flags, error count, frame header CS_CTL/OX_ID, and RX_ID. `struct fc_esb` models the Exchange Status Block with exchange IDs, fabric IDs, exchange status, service params, and sequence status array. Macros define expected sizes and bit flags such as responder, active, abnormal, retransmission, timeout, and error policy.

Control flow and state: No runtime logic is present; these are packed protocol records consumed by FC exchange recovery and diagnostics.

Dependencies and integration: Used by libfc exchange manager, REC/SRR recovery, and FC-FS protocol code.

Risks and test signals: Risks include packed layout mismatches, endian conversion mistakes, and incorrect status-bit interpretation during recovery. Tests should assert `FC_SSB_SIZE`/`FC_ESB_SIZE`, parse known SSB/ESB samples, and exercise exchange recovery state decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/fc/fc_fc2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/fc/fc_fcoe.h -->
# sources/distributed-fs/ceph-client/include/scsi/fc/fc_fcoe.h

Purpose: Defines Fibre Channel over Ethernet frame, trailer, MAC mapping, and link-error status structures.

Important APIs/types/functions: Constants include default FC-MAP OUI, non-FIP FLOGI MAC, version, header lengths, and minimum frame sizes. `struct fcoe_hdr` contains version/reserved/SOF fields. `struct fcoe_crc_eof` stores CRC and EOF trailer. `struct fcoe_fc_els_lesb` records FCoE link error counters. `fc_fcoe_set_mac()` writes OUI plus FC destination ID into a MAC address.

Control flow and state: Stateless helpers encode/decode FCoE header version and map FC IDs to Ethernet MAC addresses.

Dependencies and integration: Used by FCoE low-level drivers, libfc frame handling, and FCoE sysfs LESB reporting.

Risks and test signals: Risks include version nibble mistakes, MAC mapping errors, trailer packing mismatch, and host/network-endian counter display confusion. Tests should cover MAC generation, header/trailer lengths, version macros, and LESB counter export.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/fc/fc_fcoe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/fc/fc_fcp.h -->
# sources/distributed-fs/ceph-client/include/scsi/fc/fc_fcp.h

Purpose: Defines Fibre Channel Protocol for SCSI command, transfer-ready, response, task-management, and SRR payloads.

Important APIs/types/functions: `struct fcp_cmnd` and `fcp_cmnd32` encode LUN, task attributes, task-management flags, CDB, and data length. `struct fcp_txrdy` carries relative offset and burst length. `struct fcp_resp`, `fcp_resp_ext`, and response-info structs describe status, residuals, sense length, response length, and optional bidirectional residuals. `struct fcp_srr` defines Sequence Retransmission Request. Macros define command flags, task attributes, TM flags, response flags, response codes, and FC-4 feature bits.

Control flow and state: These wire records drive SCSI-over-FC command submission and completion. Consumers inspect read/write bits, residual flags, sense/response lengths, and task-management responses to complete `scsi_cmnd`s or trigger recovery.

Dependencies and integration: Depends on SCSI LUN definitions and is used by libfc FCP packet logic, FC target/initiator paths, and discovery feature reporting.

Risks and test signals: Risks include accepting non-standard short responses incorrectly, CDB additional-length mistakes, residual over/underflow handling, and malformed sense/response length parsing. Tests should cover 16/32-byte CDBs, task management commands, residual flags, sense data extraction, SRR recovery, and feature registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/fc/fc_fcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/fc/fc_fip.h -->
# sources/distributed-fs/ceph-client/include/scsi/fc/fc_fip.h

Purpose: Defines FCoE Initialization Protocol headers, opcodes, subcodes, flags, multicast MACs, timing constants, and descriptors for fabric, VLAN, VN2VN, and encapsulated ELS/ILS exchanges.

Important APIs/types/functions: `struct fip_header` is the common packet header. Descriptor types include priority, MAC, FC-MAP, WWN/name, fabric, FCoE size, encapsulated frame, VN ID, keep-alive, VLAN, FC-4 features, and vendor descriptors. Enums define discovery, link-service, control, VLAN, VN2VN subcodes, and flags such as FPMA/SPMA, FCF/FDF, availability, solicited, and F-port.

Control flow and state: This header is format-only. FIP controllers use the constants to discover FCFs, negotiate VLANs, maintain keep-alives, process VN2VN probes/claims/beacons, and carry FLOGI/FDISC/LOGO/ELP payloads.

Dependencies and integration: Depends on FC name-server types and Ethernet address lengths. Used by fcoe controller code and sysfs FCF device representation.

Risks and test signals: Risks include descriptor length unit mistakes, packed layout/alignment errors, subcode/opcode confusion, malformed descriptor tolerance, and keep-alive timing bugs. Tests should parse/build FIP discovery, VLAN notification, VN2VN claim, FLOGI encapsulation, and descriptor fuzz cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/fc/fc_fip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/fc/fc_ms.h -->
# sources/distributed-fs/ceph-client/include/scsi/fc/fc_ms.h

Purpose: Defines Fibre Channel Management Service FDMI request codes, attribute identifiers/lengths, and packed request payloads for registering HBA and port attributes.

Important APIs/types/functions: Enums cover FDMI requests and HBA/port attribute types. Length macros document fixed attribute sizes. Structures include HBA identifiers, port names, variable-length attribute entries, attribute lists, registered port lists, RHBA/RHAT/RPRT/RPA, and deregistration payloads.

Control flow and state: No runtime logic is present. libfc builds these packed payloads during FDMI registration/deregistration against the management server.

Dependencies and integration: Depends on Linux types and FC-GS management service conventions. Integrated from libfc local-port states such as RHBA, RPA, DHBA, and DPRT.

Risks and test signals: Risks include variable-length attribute packing errors, wrong attribute length constants, unaligned big-endian fields, and incomplete deregistration payloads. Tests should validate FDMI request buffers, attribute count/length calculations, and management-server interop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/fc/fc_ms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/fc_frame.h -->
# sources/distributed-fs/ceph-client/include/scsi/fc_frame.h

Purpose: Defines the libfc frame wrapper around `sk_buff`, receive metadata in `skb->cb`, FC ID endian helpers, frame allocation/free helpers, header/payload accessors, CRC checks, and FC header filling.

Important APIs/types/functions: `struct fc_frame` embeds an skb. `struct fcoe_rcv_info` stores local port, sequence, FCP packet, CRC, max payload, SOF/EOF, flags, encapsulation, and granted MAC. Macros expose frame fields. Helpers include `ntoh24()`, `hton24()`, `fc_frame_init()`, `fc_frame_alloc()`, `fc_frame_free()`, header/payload getters, SID/DID getters, class/rctl/cmd checks, CRC check declaration, leak check, `__fc_fill_fc_hdr()`, and `fc_fill_fc_hdr()`.

Control flow and state: Frames are allocated with FC headroom/tailroom and initialized lazily for performance; callers must eventually set header, length, SOF, and EOF. Payload access validates minimum length. Header fill writes r_ctl, DID/SID, type, F_CTL, and parameter offset.

Dependencies and integration: Depends on skb, scatterlist, SCSI command, FC protocol headers, Ethernet headers, and libfc exchange/FCP layers.

Risks and test signals: Risks include `skb->cb` size overflow, insufficient frame length checks, non-linear skb assumptions, CRC unchecked flags, and 24-bit FC ID conversion mistakes. Tests should cover allocation with unaligned payload sizes, payload bounds, header fill golden values, CRC validation, and leak detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/fc_frame.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/fcoe_sysfs.h -->
# sources/distributed-fs/ceph-client/include/scsi/fcoe_sysfs.h

Purpose: Declares sysfs-facing FCoE controller and FCF device models plus driver callbacks for exposing link-error counters, mode/enabled state, selected FCF, and VLAN.

Important APIs/types/functions: `struct fcoe_sysfs_function_template` contains get/set callbacks. `struct fcoe_ctlr_device` embeds a `struct device`, callback template, FCF list, workqueues, mutex, dev-loss timeout, mode, enabled state, and LESB counters. `struct fcoe_fcf_device` represents a discovered FCF with device, peer list, delete/devloss work, state, fabric/switch names, FC map, VFID, MAC, priority, FKA period, selected flag, and VLAN. Add/delete/setup/teardown APIs manage devices.

Control flow and state: Controller and FCF devices are registered under sysfs and updated by FCoE control-plane code. Workqueues process deletion and dev-loss events. Inline helpers map `struct device` back to controller/FCF and private data.

Dependencies and integration: Depends on Linux device model, workqueues, mutexes, Ethernet addresses, and FCoE LESB structures. Used by FCoE transport and management tooling.

Risks and test signals: Risks include device lifetime races, devloss delayed-work ordering, stale sysfs attributes, missing parent linkage, and host-order counter assumptions. Tests should cover add/delete, sysfs read/write callbacks, FCF devloss, mode/enabled transitions, and teardown with pending work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/fcoe_sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/iscsi_if.h -->
# sources/distributed-fs/ceph-client/include/scsi/iscsi_if.h

Purpose: Defines the iSCSI kernel/userspace netlink ABI for session, connection, transport endpoint, discovery, host, interface, CHAP, flashnode, ping, path, and statistics operations.

Important APIs/types/functions: `enum iscsi_uevent_e` defines user-to-kernel commands and kernel-to-user events. `struct iscsi_uevent` is the aligned netlink message with input and response unions. Additional records include parameter info, interface parameter info, path updates, flashnode parameter info, stats, CHAP records, and offload host stats. Enums define target discovery, host events, parameter classes, network/interface/session/host/flashnode params, connection states, errors, discovery parents, port speed/state, and ping status. Capability and stop-connection flags describe transport behavior.

Control flow and state: Userspace sends `ISCSI_UEVENT_*` requests with object IDs, handles, lengths, and parameter identifiers; the kernel replies with return codes or events such as session create, PDU receive, connection error, path request, link-down, login state, host event, or ping completion. Variable payloads follow the fixed event for params, paths, stats, CHAP, or host events.

Dependencies and integration: Depends on `iscsi_proto.h`, IPv4/IPv6 address types, netlink multicast groups, and open-iscsi userspace. It is shared by software and offload iSCSI transports.

Risks and test signals: Risks include ABI size/alignment breakage, mismatched variable payload lengths, pointer-handle truncation, enum drift with userspace, secret exposure in CHAP records, and flashnode/offload feature incompatibilities. Tests should include netlink ABI size checks, create/bind/start/stop/destroy flows, param set/get, path update, CHAP CRUD, ping completion, stats dumps, and compatibility with existing open-iscsi tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/iscsi_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/iscsi_proto.h -->
# sources/distributed-fs/ceph-client/include/scsi/iscsi_proto.h

Purpose: Defines RFC 3720 iSCSI wire protocol constants, serial-number arithmetic, 24-bit length helpers, initiator tag helpers, and all fixed 48-byte PDU header structures.

Important APIs/types/functions: Structures cover generic headers, AHS headers, SCSI command/response, async events, NOP, task management, R2T, data out/in, text, login, logout, SNACK, and reject PDUs. Macros define opcodes, flags, status codes, login stages/status, logout reasons/responses, SNACK types, reject reasons, limits for text key/value pairs, default negotiated lengths, and iSCSI name length. Inline helpers implement RFC1982 serial comparisons and ITT build/extract.

Control flow and state: This is a protocol contract used by initiator and target code to parse and construct PDUs. Command sequencing relies on CmdSN/StatSN/DataSN serial arithmetic; login progresses through security negotiation, operational parameter negotiation, and full feature phase; data movement uses R2T/DataSN/offset fields and residual flags.

Dependencies and integration: Depends on Linux types and SCSI LUN/CDB definitions. Used by `iscsi_if.h`, libiscsi, iscsi_tcp, offload transports, and target implementations.

Risks and test signals: Risks include endian and 24-bit length mistakes, PDU struct size drift, incorrect serial arithmetic at wrap, invalid login stage transitions, and malformed AHS handling. Tests should include PDU size/layout assertions, encode/decode golden vectors, CmdSN/StatSN wrap tests, login negotiation, reject handling, and fuzzed PDU headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/iscsi_proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/iser.h -->
# sources/distributed-fs/ceph-client/include/scsi/iser.h

Purpose: Defines iSER connection-manager and control PDU headers used to carry iSCSI over RDMA capabilities and RDMA steering keys.

Important APIs/types/functions: Capability flags describe ZBVA and Send-with-Invalidate support or use. Opcodes identify iSCSI control, iSER hello, and hello reply messages. `struct iser_cm_hdr` carries negotiation flags. `struct iser_ctrl` carries opcode/read-write-valid flags, write/read STags, and virtual addresses.

Control flow and state: During connection setup peers exchange CM headers to negotiate optional behavior. For iSCSI control PDUs, `iser_ctrl` indicates whether write/read RDMA buffers are valid and supplies remote keys and virtual addresses.

Dependencies and integration: Used by iSER initiator/target RDMA transports alongside iSCSI protocol headers and RDMA memory registration.

Risks and test signals: Risks include packed layout mismatch, wrong flag polarity between supported and used bits, endian errors for STags/VAs, and invalid key lifetime. Tests should cover CM negotiation, control PDU encode/decode, read/write steering combinations, and invalidation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/iser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/libfc.h -->
# sources/distributed-fs/ceph-client/include/scsi/libfc.h

Purpose: Declares the libfc Fibre Channel stack interface, state machines, local/remote port models, FCP packet state, exchange/sequence objects, discovery context, provider hooks, and exported layer entry points.

Important APIs/types/functions: State enums cover local-port login/FDMI/SCR/ready/logout/reset and remote-port login/PRLI/RTV/ready/delete. `struct fc_rport_priv` tracks remote-port identifiers, state, retries, timers, mutex, callbacks, PRLI/provider data, and RCU lifetime. `struct fc_fcp_pkt` represents one SCSI command with locks, timers, transfer status, FCP command, DDP/XID state, sequence pointers, recovery retry, and completion. `struct fc_exch` models an exchange with lock, refcount, IDs, sequence, response callback, timeout work, and state flags. `struct libfc_function_template` defines lower-level driver hooks for frame send, ELS/CT send, DDP, LESB, exchange reset, port ID updates, rport events, FCP send/cleanup/abort, and discovery. `struct fc_lport` is the main local-port object with SCSI host, rports, discovery, vports, template, link/state/capability fields, stats, mutex, and provider slots.

Control flow and state: libfc layers compose local-port login, discovery, remote-port login, FCP I/O, ELS/CT, and exchange management. State transitions reset retry counters via `fc_lport_state_enter()`. Exchanges own sequence callbacks and delayed timeout work; FCP packets map SCSI commands to FC exchanges and handle recovery. Discovery maintains pending/requested state and discovered rport lists. Per-CPU stats are allocated/freed from the lport.

Dependencies and integration: Depends on SCSI transport, FC transport, BSG, FC protocol headers, FC frames, timers, percpu stats, refcounts, workqueues, and lower-level FCoE/FC drivers. Exported functions initialize/destroy layers, handle link up/down, queue SCSI commands, run error handlers, send ELS/CT, manage exchanges, and expose host stats.

Risks and test signals: Risks include exchange refcount and timeout races, lock ordering between FCP packet lock and host lock, rport RCU lifetime, link-down cleanup with active I/O, DDP setup/done mismatch, discovery retry loops, and provider registration lifetime. Tests should cover fabric login/logoff, link flap, rport discovery/login/logout, SCSI queue/error handlers, exchange timeout/abort, DDP paths, vport creation, FDMI registration, and per-CPU stats aggregation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/libfc.h -->
