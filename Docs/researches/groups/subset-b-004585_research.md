# Research: subset-b-004585

This grouped report covers Netronome NFP ABM qdisc offload, NFP eBPF offload, and common control-message files. Each source file section is delimited for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/abm/main.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/abm/main.h

## Purpose
This header defines the ABM app's shared model for queue-management and RED/GRED qdisc offload on NFP NICs. It provides app-level capability/configuration state, per-link qdisc tracking state, statistics formats, action enums, helper predicates, and prototypes used by ABM control, qdisc, classifier, and priority-map code.

## Important APIs, Types, And Functions
- `struct nfp_abm` holds firmware capability data such as `red_support`, `num_prios`, `num_bands`, supported action bitmask, threshold/action arrays, DSCP mask, devlink eswitch mode, and runtime symbols for queue levels and stats.
- `enum nfp_abm_q_action` describes firmware actions for congestion thresholds: mark/drop, mark/queue, drop, queue, and noqueue.
- `struct nfp_alink_stats` and `struct nfp_alink_xstats` model queue counters read from firmware and exposed back to TC qdisc stats.
- `enum nfp_qdisc_type` and `struct nfp_qdisc` represent tracked Linux qdisc objects, including MQ children and RED/GRED per-band parameters, current stats, and previous reported stats.
- `struct nfp_abm_link` ties an ABM app to one data vNIC, its PCIe queue base/count, DSCP/default-band policy, root qdisc, and radix tree of qdiscs.
- Inline helpers `nfp_abm_has_prio()`, `nfp_abm_has_drop()`, and `nfp_abm_has_mark()` centralize capability checks.
- Exported prototypes connect this header to qdisc setup, control-memory access, queue action/level programming, stats reads, queue manager enable/disable, and priority-map updates.

## Control Flow
The header is declarative, but it shapes runtime flow: TC qdisc setup code records qdiscs in `nfp_abm_link.qdiscs`, marks offload candidates, and uses control helpers to program thresholds/actions into firmware. Stats reads populate `struct nfp_alink_stats`/`xstats`, with previous snapshots retained in `struct nfp_qdisc` so later TC stat dumps can report deltas. Per-link priority and DSCP state guide RED versus GRED eligibility and band selection.

## State And Persistence
All state is in kernel memory plus firmware-visible queue configuration. `thresholds`, `threshold_undef`, and `actions` mirror firmware settings; `root_qdisc`, `qdiscs`, qdisc `use_cnt`, `offload_mark`, and `offloaded` represent Linux qdisc hierarchy state. No disk persistence exists. Hardware/firmware state persists only until app reset, queue-manager disable, or explicit reprogramming.

## Dependencies And Integration Points
The header depends on Linux `devlink`, packet classifier/scheduler APIs, radix trees, lists, and NFP app/netdev forward declarations. It is consumed by ABM qdisc code, ABM control code, repr classifier setup, devlink eswitch handling, and NFP app lifecycle code.

## Risks And Edge Cases
- `NFP_QDISC_UNTRACKED` is a sentinel pointer value, so child-pointer users must always test through `nfp_abm_qdisc_child_valid()`.
- `MAX_DPs` bounds GRED bands, while firmware `num_bands` drives loops; capability parsing must ensure these remain compatible.
- Queue indexes combine link `queue_base`, per-link `total_queues`, and global `NFP_NET_MAX_RX_RINGS`; mistakes can program another link's thresholds.
- Stats are snapshot/delta based, so missed initialization or offload-stop transitions can produce negative-looking deltas after unsigned subtraction.
- The structs are shared between TC callbacks, app cleanup, and firmware control paths under RTNL or app-level serialization assumptions not expressed in the header.

## Test Signals
Useful signals include TC RED/GRED/MQ offload success, offload rejection messages for unsupported actions or band counts, correct queue thresholds/actions in firmware, stable qdisc refcounts on graft/destroy/unregister, accurate qdisc stats deltas, DSCP priority-map behavior, and clean app teardown with empty qdisc trees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/abm/main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/abm/qdisc.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/abm/qdisc.c

## Purpose
This file implements TC qdisc tracking and offload programming for the NFP ABM app. It supports root/MQ/RED/GRED setup callbacks, maintains a local qdisc hierarchy, compiles eligible RED/GRED leaves into firmware queue levels/actions, reads firmware queue stats, and translates hardware counters back into Linux qdisc statistics.

## Important APIs, Types, And Functions
- Entry points: `nfp_abm_qdisc_offload_update()`, `nfp_abm_setup_root()`, `nfp_abm_setup_tc_red()`, `nfp_abm_setup_tc_mq()`, and `nfp_abm_setup_tc_gred()`.
- Qdisc tree helpers: `nfp_abm_qdisc_alloc()`, `nfp_abm_qdisc_free()`, `nfp_abm_qdisc_find()`, `nfp_abm_qdisc_replace()`, `nfp_abm_qdisc_destroy()`, `nfp_abm_qdisc_graft()`, and `nfp_abm_qdisc_unlink_children()`.
- Offload compiler: `nfp_abm_offload_compile_mq()` walks MQ children and `nfp_abm_offload_compile_red()` validates RED/GRED leaves and programs `nfp_abm_ctrl_set_q_lvl()` and `nfp_abm_ctrl_set_q_act()`.
- Parameter checks: `nfp_abm_red_check_params()` and `nfp_abm_gred_check_params()` enforce firmware-supported ECN/drop action, harddrop absence, min/max equality, threshold bounds, default band, and band count.
- Stats path: `nfp_abm_stats_update()`, `nfp_abm_stats_update_mq()`, `nfp_abm_stats_update_red()`, `nfp_abm_stats_init()`, `nfp_abm_stats_calculate()`, and `nfp_abm_stats_red_calculate()`.

## Control Flow
TC setup first creates or finds qdisc records by major handle in `alink->qdiscs`. Root setup adjusts the root use count and calls `nfp_abm_qdisc_offload_update()`. MQ creation creates a child table sized to `alink->total_queues`; MQ graft links per-queue children and increments child `use_cnt`. RED/GRED replace records parameters and updates offload only when attached.

`nfp_abm_qdisc_offload_update()` clears firmware threshold-defined bits for this link, clears all qdisc `offload_mark`s, recompiles the current root MQ tree, flips `offloaded` state, stops stale offloads, resets unconfigured thresholds to `NFP_ABM_LVL_INFINITY`, and forces a stats refresh. A plain RED qdisc is offloadable only as a single attached leaf without priority bands or children. GRED is offloadable when parameters are valid and the qdisc has one attachment. MQ is the root fanout that maps child RED/GRED qdiscs to hardware queues.

Stats are rate-limited by `NFP_ABM_STATS_REFRESH_IVAL`. Firmware counters are read only for offloaded RED/GRED children. TC stats commands compute deltas from previous snapshots and update the previous snapshots after reporting. MQ stats are synthesized by summing child RED/GRED band counters because Linux core aggregates MQ child stats differently.

## State And Persistence
Persistent storage is not used. Runtime state lives in the `nfp_abm_link` qdisc radix tree and `struct nfp_qdisc` instances: hierarchy child pointers, use counts, parameter validity, offload status, thresholds/actions, and stats snapshots. Firmware-visible state includes queue levels, queue actions, and stats counters accessed through ABM control helpers. On offload stop, backlog counters are reset after they can be reported back through TC.

## Dependencies And Integration Points
The file integrates Linux RTNL/TC qdisc offload APIs (`tc_red_qopt_offload`, `tc_gred_qopt_offload`, `tc_mq_qopt_offload`, root qdisc offload), generic qdisc stats helpers, Netronome app/netdev/port structures, firmware control helpers declared in `abm/main.h`, and `nfp_port.tc_offload_cnt` accounting.

## Risks And Edge Cases
- MQ destruction during netdev unregister is special-cased because MQ does not always notify child destruction cleanly.
- Child `use_cnt` correctness depends on every graft, root change, destroy, and unregister path being balanced.
- The qdisc radix tree key uses `TC_H_MAJ(handle)`, so duplicate major handles are impossible and handle misuse can collide.
- Parameter rejection leaves qdisc records present but `params_ok == false`; later graft/root updates must keep rejecting offload while retaining software TC behavior.
- Firmware programming calls in `nfp_abm_offload_compile_red()` do not abort on individual set failures, so test logs are important to catch partial programming.
- Stats are rate-limited and delta-based; rapid TC stat polling or offload transitions can hide short-lived firmware counter changes.

## Test Signals
Exercise RED and GRED offload with ECN and drop modes, unsupported harddrop/min-max/WRED/GRIO cases, MQ grafting across multiple queues, root qdisc replacement, netdev unregister cleanup, repeated stats dumps, offload stop/restart preserving backlog deltas, firmware threshold reset to infinity for unconfigured queues, and `tc_offload_cnt` returning to zero after teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/abm/qdisc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/cmsg.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/cmsg.c

## Purpose
This file implements BPF app control-message operations over the common NFP control channel. It allocates/free firmware map tables, performs map lookup/update/delete/get-first/get-next operations, manages a short-lived multi-entry map cache, computes control-message MTU requirements, and dispatches firmware-originated BPF events.

## Important APIs, Types, And Functions
- Map lifecycle: `nfp_bpf_ctrl_alloc_map()` sends `NFP_CCM_TYPE_BPF_MAP_ALLOC` and returns a firmware table id; `nfp_bpf_ctrl_free_map()` sends `NFP_CCM_TYPE_BPF_MAP_FREE` and logs leak risks on failure.
- Entry operations: `nfp_bpf_ctrl_update_entry()`, `nfp_bpf_ctrl_del_entry()`, `nfp_bpf_ctrl_lookup_entry()`, `nfp_bpf_ctrl_getfirst_entry()`, and `nfp_bpf_ctrl_getnext_entry()` all use `nfp_bpf_ctrl_entry_op()`.
- Cache helpers: `nfp_bpf_ctrl_op_cache_get()` handles lookup/getnext hits and invalidation blockers; `nfp_bpf_ctrl_op_cache_put()` installs or releases cached replies with generation checks.
- Message sizing: `nfp_bpf_cmsg_map_req_size()`, `nfp_bpf_cmsg_map_reply_size()`, `nfp_bpf_ctrl_cmsg_min_mtu()`, `nfp_bpf_ctrl_cmsg_mtu()`, and `nfp_bpf_ctrl_cmsg_cache_cnt()`.
- Receive path: `nfp_bpf_ctrl_msg_rx()` handles skb control messages, while `nfp_bpf_ctrl_msg_rx_raw()` accepts raw event buffers.

## Control Flow
Requests allocate a control skb sized for the fixed header plus key/value arrays, fill big-endian firmware fields, and call `nfp_ccm_communicate()` with the corresponding `enum nfp_ccm_type`. Allocation replies are fixed-size and include a table id. Entry replies are variable-size, so `nfp_bpf_ctrl_entry_op()` validates minimum length, firmware status, reply count, and final expected length before copying returned key/value bytes.

The map cache is intentionally tiny and time-bound. Lookup and getnext can satisfy from an skb cached by getfirst/getnext. Update and delete increment `cache_blockers` before issuing firmware I/O, then invalidate by bumping `cache_gen` on completion. Fill operations install the reply only if no blocker ran and the generation still matches. Firmware BPF event messages bypass CCM reply matching and are forwarded to `nfp_bpf_event_output()`.

## State And Persistence
State is in memory only. `struct nfp_bpf_map` owns cache fields (`cache`, `cache_to`, `cache_gen`, `cache_blockers`) protected by `cache_lock`. Firmware persists map contents in device-managed tables identified by `tid`; the driver mirrors only table ids and caches short-lived replies. No filesystem persistence exists.

## Dependencies And Integration Points
The file depends on `ccm.h` for request/reply transport, `fw.h` for BPF control-message ABIs, `main.h` for BPF app/map state, Linux skb/timekeeping/bitops APIs, and `nfp_app_ctrl_msg_alloc()`/`nfp_ccm_communicate()` for transport. It is called by BPF map device ops in `offload.c` and by the app control-message receive hooks in `main.c`.

## Risks And Edge Cases
- ABI v2 uses fixed 64-byte key/value slots; ABI v3 uses firmware-reported max key/value sizes, so MTU sizing must match parsed capabilities.
- `flags` are truncated to firmware's 32-bit field and rejected if high bits are set.
- Multi-entry cache correctness relies on blocker/generation ordering around concurrent update/delete and lookup/getnext operations.
- Variable-length replies must be exact; short or overlong replies are treated as I/O errors.
- `nfp_bpf_ctrl_free_map()` can only warn on allocation/I/O errors, because firmware map leaks may be unrecoverable after host state is gone.

## Test Signals
Test map allocation/free for supported and unsupported map shapes, update/delete invalidating lookup/getnext cache, getfirst/getnext multi-entry replies with ABI v3 MTU sizing, firmware error-code translation to Linux errno, malformed or short control replies, BPF event delivery, and cleanup with no cached skb leaks or cache blocker warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/cmsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/fw.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/fw.h

## Purpose
This header defines the firmware-facing BPF ABI structures and constants used by the NFP BPF app. It covers BPF capability TLVs, stable firmware encodings for selected verifier register types, BPF map control-message payloads, firmware return codes, fixed ABI v2 map element slot sizes, and asynchronous BPF event messages.

## Important APIs, Types, And Functions
- Capability types: `enum bpf_cap_tlv_type` includes helper functions, adjust-head, maps, random, queue-select, adjust-tail, ABI version, and multi-entry control-message support.
- Capability payloads: `struct nfp_bpf_cap_tlv_func`, `struct nfp_bpf_cap_tlv_adjust_head`, and `struct nfp_bpf_cap_tlv_maps`.
- Register-type ABI constants: `NFP_BPF_SCALAR_VALUE`, `NFP_BPF_MAP_VALUE`, `NFP_BPF_STACK`, and `NFP_BPF_PACKET_DATA` decouple firmware ABI from kernel enum churn.
- Map control messages: `cmsg_req_map_alloc_tbl`, `cmsg_reply_map_alloc_tbl`, `cmsg_req_map_free_tbl`, `cmsg_req_map_op`, and `cmsg_reply_map_op`.
- Event message: `struct cmsg_bpf_event` carries CPU id, map id/pointer, data size, packet size, and payload bytes.

## Control Flow
The header is consumed by app startup to parse `_abi_bpf_capabilities`, by verifier checks to gate helpers/features, by control-message code to serialize map requests, and by event-output code to decode firmware-generated perf events. Firmware return codes in `enum nfp_bpf_cmsg_status` are translated to host errnos by `cmsg.c`.

## State And Persistence
The header defines ABI layout, not storage. Runtime parsed capability state is stored in `struct nfp_app_bpf`; firmware map state is addressed by table ids returned in map allocation replies. Endianness is explicit in control messages (`__be32`/`__be64`) and capability TLVs are read from little-endian firmware memory with MMIO accessors.

## Dependencies And Integration Points
It includes Linux bitops/types and `../ccm.h` for the common control-message header. It is shared by BPF `main.c`, `cmsg.c`, `offload.c`, `verifier.c`, and `jit.c`, and by firmware that must emit exactly matching TLVs and control-message replies.

## Risks And Edge Cases
- These structs are firmware ABI; field size, order, and endianness changes break compatibility.
- The comment notes kernel `enum bpf_reg_type` is not uABI, so `BUILD_BUG_ON()` checks in verifier code are needed to catch drift for event-output pointer types.
- ABI v2 fixed key/value longword sizes can waste MTU or truncate if map validation is wrong; ABI v3 relies on parsed max sizes.
- Event messages include separate packet and data payload lengths; callers must validate combined size to avoid overrun.

## Test Signals
Validate capability TLV parsing for every known type, ABI version fallback and rejection, map control-message serialization against firmware, firmware return-code coverage, event-output decoding with valid and malformed lengths, and compile-time checks that stable NFP pointer-type constants still match kernel verifier constants where required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/jit.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/jit.c

## Purpose
This file is the NFP eBPF JIT compiler. It translates verified eBPF programs for TC direct-action and XDP into NFP microcode instructions, performs NFP-specific optimizations, emits helper/subprogram/stack handling, fixes branches and relocations, and produces per-vNIC relocated ustore images with ECC.

## Important APIs, Types, And Functions
- Public entry points: `nfp_bpf_jit_prepare()` records branch and subprogram metadata, `nfp_bpf_jit()` optimizes and translates a program, `nfp_bpf_supported_opcode()` exposes opcode support to the verifier, and `nfp_bpf_relo_for_vnic()` creates a relocated image for one vNIC.
- Low-level emitters: `emit_alu()`, `emit_shf()`, `emit_immed()`, `emit_cmd()`, `emit_br_relo()`, `emit_br_bit_relo()`, CSR helpers, and wrappers like `wrp_immed()`, `wrp_mov()`, and `wrp_zext()`.
- Translation callbacks: `instr_cb[256]` maps supported eBPF opcodes to callbacks for ALU64/ALU32, shifts, endian conversion, packet loads, memory loads/stores, atomics, jumps, calls, and exits.
- Memory paths: `mem_ldx()`, `mem_stx()`, `mem_op_stack()`, `data_ld_host_order*()`, `nfp_cpp_memcpy()`, and packet-cache helpers implement stack, packet, context, and map-value accesses.
- Helper/subprogram support: `adjust_head()`, `adjust_tail()`, `map_call_stack_common()`, `nfp_get_prandom_u32()`, `nfp_perf_event_output()`, `bpf_to_bpf_call()`, prologue/epilogue helpers, and callee-register save/restore routines.
- Optimization passes: `nfp_bpf_opt_reg_init()`, `nfp_bpf_opt_neg_add_sub()`, `nfp_bpf_opt_ld_mask()`, `nfp_bpf_opt_ld_shift()`, `nfp_bpf_opt_ldst_gather()`, and `nfp_bpf_opt_pkt_cache()`.

## Control Flow
Preparation walks the metadata list and records jump destinations; pseudo calls mark subprogram starts. `nfp_bpf_jit()` replaces map pseudo pointers with firmware table ids or neutral map ids, runs optimization passes, and calls `nfp_translate()`. Translation emits an intro that derives packet length, then walks instruction metadata in order, sets each instruction's output offset, emits subprogram prologues when needed, skips optimized instructions, invokes the opcode callback, emits TC/XDP outro code and optional callee-register subroutines, pads for the ustore prefetch window, and fixes relative branches.

The generated program uses pairs of NFP GPRs for 64-bit BPF registers. Stack is modeled in local memory with `stack_reg()`/LM pointer setup. Packet accesses use packet vector pointer/length with explicit bounds checks for classic loads and cached/gathered CPP reads for repeated packet loads. Map values use 40-bit addressing and atomic add commands. Helper calls are emitted as relocated branches to firmware helper addresses, with return addresses loaded through agreed registers.

Relocation is two-stage. Translation leaves `OP_RELO_TYPE` markers in branch/immediate instructions for relative branches, helper calls, normal/abort exits, next-packet target, and callee save/restore routines. `nfp_bpf_relo_for_vnic()` copies the generic image, applies the vNIC `start_off` and `tgt_done`, replaces helper relocations with parsed firmware helper addresses, clears relocation bits, and calculates ustore ECC.

## State And Persistence
The compiler mutates `struct nfp_prog`: instruction metadata flags, generated `prog`, length/allocation fields, target offsets, stack size/depth, subprogram info, map record ids, and error status. No disk state is written. Firmware-visible persistence occurs later when `offload.c` DMA-loads the relocated image and asks firmware to install it.

## Dependencies And Integration Points
The JIT depends on `nfp_asm.h` instruction encodings, NFP CSR/register conventions, BPF verifier metadata captured in `main.h`, firmware capabilities/helper addresses in `struct nfp_app_bpf`, Linux reciprocal division helpers, packet-classifier constants, and NFP netdev configuration offsets. It is invoked from BPF offload ops in `offload.c` after verifier preparation/finalization.

## Risks And Edge Cases
- Verifier hooks must reject cases the JIT cannot encode, such as unsupported pointer types, variable map offsets, non-constant divides, oversized stack, unsupported helpers, or unsafe atomics.
- Branch fixup assumes each translated block ends in an expected branch; optimized-out jump targets or unexpected delay-slot lengths produce hard translation failures.
- NFP branch delay slots and LM pointer update nops are timing-sensitive; changing emitted instruction counts can break offset assertions.
- Map-value atomics require endian-aware initialization and use-map tracking to avoid mixing host-endian values with firmware atomic counters.
- Packet-cache and load/store gather optimizations rely on pointer id/offset stability and no jumps into the middle of optimized sequences.
- `nfp_bpf_relo_for_vnic()` must clear relocation bits before ECC calculation; stale relocation markers would corrupt hardware instructions.

## Test Signals
Use verifier/JIT selftests for every supported opcode class, TC and XDP return mapping, packet bounds aborts, helper calls, adjust_head/tail success and failure, BPF-to-BPF calls with and without callee-saved registers, map lookup/update/delete and atomics, packet cache/gathered memcpy optimization cases, live reload relocation, program-size/stack-limit rejection, ustore validity/ECC checks, and hardware packet forwarding with expected TC/XDP actions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/jit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/main.c

## Purpose
This file registers and implements the NFP eBPF app type. It owns BPF app initialization/cleanup, firmware capability parsing, vNIC BPF capability checks, TC cls_bpf and XDP offload entry points, netdev BPF offload device registration, control-channel MTU setup, and MTU-change validation while BPF offload is active.

## Important APIs, Types, And Functions
- App descriptor: `app_bpf` wires `.init`, `.clean`, `.start`, `.check_mtu`, `.extra_cap`, `.ndo_init`, `.ndo_uninit`, `.vnic_alloc`, `.vnic_free`, `.ctrl_msg_rx`, `.ctrl_msg_rx_raw`, `.setup_tc`, `.bpf`, and `.xdp_offload`.
- Capability checks: `nfp_net_ebpf_capable()` validates little-endian host, netdev BPF control capability, app ABI version, and per-vNIC ABI register match.
- Offload entry points: `nfp_bpf_xdp_offload()` for XDP and `nfp_bpf_setup_tc_block_cb()`/`nfp_bpf_setup_tc()` for TC cls_bpf direct-action offload.
- Capability parsing: `nfp_bpf_parse_capabilities()` reads `_abi_bpf_capabilities`; typed parsers fill helper addresses, adjust-head limits, map limits, ABI version, random, queue-select, adjust-tail, and multi-entry cmsg support.
- Lifecycle: `nfp_bpf_init()`, `nfp_bpf_start()`, `nfp_bpf_clean()`, `nfp_bpf_vnic_alloc()`, `nfp_bpf_vnic_free()`, `nfp_bpf_ndo_init()`, and `nfp_bpf_ndo_uninit()`.

## Control Flow
App init allocates `struct nfp_app_bpf`, initializes CCM and neutral-map rhashtable state, defaults ABI version to 2, parses firmware capability TLVs, chooses cmsg key/value sizes from ABI version, may raise `app->ctrl_mtu` for ABI v3 multi-entry messages, and creates a kernel BPF offload device. Start verifies the control channel MTU can hold at least one map operation and computes cache entry count if firmware supports multi-entry cmsgs.

Each vNIC allocation verifies ETH table/vNIC count consistency, delegates normal NIC allocation, and records BPF program start and done targets from vNIC config space. TC setup accepts only block callbacks for cls_bpf, chain 0, ETH_P_ALL, direct-action with no legacy actions, and capable firmware. XDP offload blocks conflicts between TC and XDP use of the single firmware BPF slot. MTU changes are rejected when active BPF programs may access packet bytes beyond the firmware inline split boundary.

## State And Persistence
State is runtime-only in `struct nfp_app_bpf` and per-vNIC `struct nfp_bpf_vnic`: parsed firmware capabilities, helper addresses, map resource counters, neutral-map table, control-message sizes, active TC program pointer, program start offset, and next-packet target. No disk persistence exists. Firmware state is affected indirectly when BPF programs are loaded/unloaded by `offload.c`.

## Dependencies And Integration Points
The file integrates with NFP app registration, netdev priv state, ETH table metadata, NFP runtime symbols, BPF offload core, TC flow block callbacks, XDP offload hooks, CCM receive paths, and netdev MTU validation. It uses `fw.h` ABI structures and `main.h` shared BPF state/prototypes.

## Risks And Edge Cases
- eBPF offload is disabled on big-endian hosts.
- Firmware ABI mismatch between global capabilities and vNIC config register disables BPF even if the app loaded.
- TC and XDP share one firmware BPF slot; attempts to load both must fail cleanly.
- Capability TLV parsing maps device memory and must reject truncated or overrun records while releasing CPP areas.
- `nfp_bpf_setup_tc_block_cb()` updates `tc_offload_cnt` as a boolean, so concurrent or unexpected multiple TC programs would not be represented.
- MTU rejection is conservative and depends on verifier-provided `max_pkt_offset`.

## Test Signals
Validate app probe with and without `_abi_bpf_capabilities`, ABI v2/v3 setup, helper/map capability parsing, BPF extra capability string, TC cls_bpf attach/detach and rejection paths, XDP attach/detach and TC conflict handling, MTU changes under active programs, BPF offload device netdev register/unregister, vNIC allocation with ETH table mismatch, and cleanup warnings for leaked maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/main.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/main.h

## Purpose
This header defines the shared internal model for NFP eBPF offload. It contains app private state, map private state, neutral-map records, JIT instruction metadata, program compilation state, per-vNIC state, register/relocation conventions, opcode classification helpers, and prototypes linking the BPF app, verifier, JIT, control-message, and offload code.

## Important APIs, Types, And Functions
- `struct nfp_app_bpf` stores CCM transport, BPF offload device, cmsg sizing/cache count, map list/resource counters, neutral-map rhashtable, ABI version, parsed capabilities, helper addresses, and feature booleans.
- `struct nfp_bpf_map` attaches firmware table id, cache state, and per-4-byte use tracking to an offloaded map.
- `struct nfp_bpf_neutral_map` tracks maps that are legal to reference by id for event output without being NFP-offloaded maps.
- `struct nfp_insn_meta` wraps each BPF instruction with verifier pointer/range state, optimization flags, jump/call metadata, packet-cache/gather metadata, and generated-code offset.
- `struct nfp_prog` stores the full compilation unit: generated image, stack/subprogram info, relocation targets, map records, instruction list, and translation error state.
- Register/relocation definitions include `enum nfp_relo_type`, static register ids, packet-vector accessors, `STACK_FRAME_ALIGN`, and instruction flags such as `FLAG_INSN_DO_ZEXT`.
- Inline classifiers such as `is_mbpf_load()`, `is_mbpf_store()`, `is_mbpf_atomic()`, `is_mbpf_helper_call()`, and `is_mbpf_pseudo_call()` keep verifier and JIT opcode logic aligned.

## Control Flow
The header's structures carry a BPF program through offload lifecycle. `offload.c` allocates `struct nfp_prog` and populates `nfp_insn_meta`; `verifier.c` updates metadata during kernel verifier callbacks; `jit.c` uses that metadata to optimize, translate, and relocate machine code; `offload.c` then loads the image into firmware. Map device ops use `struct nfp_bpf_map` and control-message prototypes; event output uses neutral-map records.

## State And Persistence
All state is volatile kernel memory. `nfp_app_bpf` persists for the app lifetime, `nfp_bpf_vnic` for vNIC lifetime, `nfp_bpf_map` for map lifetime, and `nfp_prog`/`nfp_insn_meta` for program offload lifetime. Firmware-visible state is referenced by helper addresses, table ids, and loaded code offsets but is not stored in this header.

## Dependencies And Integration Points
The header includes Linux BPF verifier/offload, rhashtable, skb, waitqueue, bitfield, and NFP assembly/CCM/FW headers. It is the central contract among `main.c`, `cmsg.c`, `offload.c`, `verifier.c`, and `jit.c`, and it exposes `nfp_bpf_dev_ops`, `nfp_ndo_bpf()`, and `nfp_net_bpf_offload()` to app/netdev integration.

## Risks And Edge Cases
- Metadata unions reuse storage for pointer, jump, call, and ALU range information; users must only read fields relevant to the instruction class.
- `FLAG_INSN_SKIP_MASK` coordinates verifier and JIT optimizations; branch destinations into skipped instructions are invalid.
- Stack and subprogram accounting depend on verifier-populated call metadata and fixed NFP stack-frame alignment.
- Map use tracking is per 4-byte word, so unaligned or mixed-size accesses can mark multiple words and reject conflicting atomic/read use.
- Relocation marker bits temporarily occupy instruction bits and must be cleared before firmware load.

## Test Signals
Compile coverage across all BPF source files, verifier/JIT tests for every opcode helper classifier, map cache/use tracking, neutral-map event output, subprogram stack metadata, relocation target generation, zero-extension flags, and teardown warnings for non-empty map lists or resource counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/offload.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/offload.c

## Purpose
This file connects the Linux BPF offload core to NFP firmware. It prepares and destroys per-program compiler state, translates verified BPF to NFP instructions, manages offloaded maps and neutral map references, implements map device ops with firmware control messages, handles async perf-event output, checks MTU/program/stack limits, and loads/unloads BPF programs into vNIC firmware state.

## Important APIs, Types, And Functions
- Program offload ops: `nfp_bpf_verifier_prep()`, `nfp_bpf_translate()`, and `nfp_bpf_destroy()` are exported through `nfp_bpf_dev_ops`.
- Program metadata: `nfp_prog_prepare()` builds the instruction metadata list; `nfp_prog_free()` tears it down.
- Neutral map tracking: `nfp_map_ptrs_record()`, `nfp_map_ptr_record()`, and `nfp_map_ptrs_forget()` hold references to offload-neutral maps used by programs.
- Map device ops: `nfp_bpf_map_alloc()`, `nfp_bpf_map_free()`, `nfp_bpf_map_lookup_entry()`, `nfp_bpf_map_update_entry()`, `nfp_bpf_map_get_next_key()`, and `nfp_bpf_map_delete_elem()`.
- Firmware program load: `nfp_bpf_offload_check_mtu()`, `nfp_net_bpf_load()`, `nfp_net_bpf_start()`, `nfp_net_bpf_stop()`, and `nfp_net_bpf_offload()`.
- Event output: `nfp_bpf_event_output()` maps firmware events back to host perf-event maps.

## Control Flow
When BPF offload begins, prepare allocates `struct nfp_prog`, attaches it to `prog->aux->offload->dev_priv`, copies eBPF instructions into metadata, and records jump/subprogram metadata. Translate rejects failed verifier optimizations, allocates a maximum-size image based on vNIC config, calls `nfp_bpf_jit()`, exposes the JIT image to BPF core, and records neutral maps. Destroy frees the image, releases neutral-map references after RCU synchronization if needed, and frees metadata.

Map allocation validates firmware map capabilities, flags, NUMA node, map type, resource limits, key/value sizes, and element size. It allocates NFP private map state, asks firmware for a table id, installs device ops, increments app resource counters, and links the map. Free reverses the firmware and host state, warns on outstanding cache blockers, and releases cached skbs.

Program load checks packet boundary, stack size, and program length, obtains a per-vNIC relocated/ECC image from the JIT, DMA maps it, writes firmware BPF size/address registers, and triggers `NFP_NET_CFG_UPDATE_BPF`. Starting/stopping toggles `NFP_NET_CFG_CTRL_BPF` through a generic reconfig. Live reload requires firmware relocation capability.

## State And Persistence
Runtime state includes per-program generated image and map records, per-map firmware table id/cache/use map, app map counters/list, neutral-map rhashtable records with refcounts, and vNIC BPF control bit. Firmware persists loaded program image and map table contents until unload, map free, or device reset. No disk persistence exists.

## Dependencies And Integration Points
The file depends on Linux BPF offload core, BPF map APIs, netdev/PCI/DMA APIs, TC action headers, NFP netdev control registers/reconfig, CCM map operations from `cmsg.c`, JIT/verifier hooks from `main.h`, and firmware ABIs from `fw.h`.

## Risks And Edge Cases
- `nfp_bpf_translate()` returns without freeing `nfp_prog->prog` on JIT error; later destroy must run or memory can remain attached to failed offload state.
- Map value endian conversion is necessary for atomic counters; mixed read/atomic or non-zero initialization paths are rejected or marked by verifier/offload code.
- Neutral-map references require RCU synchronization before `bpf_map_put()` and free, because event output looks them up under RCU.
- Live reload is refused unless firmware advertises relocation capability; otherwise active BPF control state would be overwritten unsafely.
- Firmware free-map failures can leak device-side maps even though host state is being destroyed.
- Async event output cannot report lost/rejected events synchronously to the BPF program.

## Test Signals
Validate BPF offload prepare/translate/destroy, map allocation limit failures, map endian behavior with atomics, neutral perf-event map references, event delivery to perf rings, DMA load/unload and reconfig errors, live reload with/without firmware relocation capability, MTU/stack/program length rejection, map delete rejection for arrays, and cleanup warnings for cache blockers or leaked map counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/offload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/verifier.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/verifier.c

## Purpose
This file implements NFP-specific BPF verifier hooks. It rejects programs the NFP JIT/firmware cannot support, records verifier-derived metadata needed by translation, validates helper calls and pointer usage, tracks map-value access semantics for endian-safe atomics, computes subprogram stack usage, and mirrors verifier optimizations into JIT metadata.

## Important APIs, Types, And Functions
- Verifier hooks: `nfp_verify_insn()` runs per instruction, and `nfp_bpf_finalize()` runs after kernel verifier completion.
- Metadata navigation: `nfp_bpf_goto_meta()` efficiently moves through the metadata list by instruction index.
- Helper checks: `nfp_bpf_check_helper_call()`, `nfp_record_adjust_head()`, `nfp_bpf_stack_arg_ok()`, and `nfp_bpf_map_call_ok()`.
- Pointer and memory checks: `nfp_bpf_check_ptr()`, `nfp_bpf_check_store()`, `nfp_bpf_check_atomic()`, `nfp_bpf_check_stack_access()`, and `nfp_bpf_map_mark_used()`.
- ALU constraints: `nfp_bpf_check_alu()` records operand ranges and rejects unsupported multiplication/division ranges.
- Finalization/optimization hooks: `nfp_assign_subprog_idx_and_regs()`, `nfp_bpf_get_stack_usage()`, `nfp_bpf_insn_flag_zext()`, `nfp_bpf_opt_replace_insn()`, and `nfp_bpf_opt_remove_insns()`.

## Control Flow
For each verifier instruction callback, the driver locates the matching `nfp_insn_meta`, checks opcode support with the JIT callback table, rejects extended register numbers, and dispatches by instruction class. Helper calls are gated by firmware capability and argument shape. Loads/stores/atomics validate pointer types and record pointer state for translation. ALU operations store min/max source and destination ranges so the JIT can choose multiplication/division/shift sequences.

Finalize allocates subprogram metadata, assigns subprogram indexes and callee-save needs, imports kernel stack depths, accounts for return address and saved R6-R9 registers, computes max call-chain stack usage, verifies firmware stack limit, and copies zero-extension flags from verifier aux data. Replacement/removal hooks allow only verifier optimizations that the JIT can mirror, such as conditional jump hard-wiring and instruction removal flags.

## State And Persistence
The file mutates only per-program and per-map runtime metadata: instruction flags, pointer states, helper argument snapshots, ALU ranges, map use-map words, `adjust_head_location`, subprogram stack info, and computed `stack_size`. No hardware or disk state is changed directly.

## Dependencies And Integration Points
It depends on the Linux BPF verifier environment, verifier register/stack state, TC/XDP constants, NFP firmware capability state, BPF map offload state from `offload.c`, and the JIT metadata/layout in `main.h`. Its results are consumed directly by `jit.c`.

## Risks And Edge Cases
- The JIT trusts verifier metadata; accepting an unsupported pointer type, variable stack offset, unsupported helper argument, or unsafe map use can lead to bad firmware code generation.
- `nfp_bpf_map_update_value_ok()` depends on stack argument checks running first and on kernel stack-state semantics for zero initialization.
- Atomic map counters cannot be safely used after non-zero host-endian initialization; the code rejects those conflicts but only at tracked word granularity.
- Event output supports only `BPF_F_CURRENT_CPU` and warns that return codes/loss/reordering differ for offload.
- Subprogram stack walking assumes kernel verifier has prevented recursion and that recorded pseudo-call destinations are correct.
- `nfp_assign_subprog_idx_and_regs()` return value is ignored in finalize, so inconsistency would need later failures or logs to surface.

## Test Signals
Run BPF verifier/offload tests for unsupported opcodes, helper gating, adjust_head/tail capabilities, map helper stack arguments, event_output restrictions, pointer type changes across paths, stack access alignment/variable offsets, ALU64 multiplication/division range rejection, map atomic conflicts, subprogram stack accounting, verifier instruction replacement/removal, and JIT translation of finalized metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/verifier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/ccm.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/ccm.c

## Purpose
This file implements the common control-message request/reply transport used by NFP apps such as BPF. It allocates unique message tags, sends control skbs, waits for matching firmware replies, validates reply type/size, queues received replies, and handles tag cleanup on success, timeout, and interruption.

## Important APIs, Types, And Functions
- Tag management: `nfp_ccm_alloc_tag()`, `nfp_ccm_free_tag()`, and `nfp_ccm_all_tags_busy()` maintain a bounded in-flight tag window.
- Reply matching: `__nfp_ccm_reply()`, `nfp_ccm_reply()`, and `nfp_ccm_reply_drop_tag()` search the reply queue for a matching tag and free tag state.
- Wait path: `nfp_ccm_wait_reply()` spins briefly, then waits up to five seconds on `ccm->wq`, and finally drops the tag if no reply is found.
- Public transport: `nfp_ccm_communicate()` fills `struct nfp_ccm_hdr`, transmits via `__nfp_app_ctrl_tx()`, waits for reply, and validates reply type and optional fixed size.
- Receive/lifecycle: `nfp_ccm_rx()` queues valid replies and wakes waiters; `nfp_ccm_init()` and `nfp_ccm_clean()` initialize/check state.

## Control Flow
Callers pass a prepared skb to `nfp_ccm_communicate()`. Under the app control lock, CCM allocates a tag, writes ABI version/type/tag into the message header, transmits on the app control channel, and unlocks. It then polls briefly for low-latency replies before sleeping on the waitqueue. Receive-side code validates minimum header length, checks the tag is currently allocated, queues the skb on `ccm->replies`, and wakes all waiters. The waiter removes the matching skb, validates it is the reply type for the request and optionally the exact size, then returns ownership to the caller.

## State And Persistence
State is volatile in `struct nfp_ccm`: tag bitmap, next/last tag cursors, reply skb queue, waitqueue, and app pointer. No disk or hardware state is persisted here beyond messages transmitted to firmware. Tags are deliberately not reused too quickly after timeouts by limiting the in-flight window to `U16_MAX / 4`.

## Dependencies And Integration Points
The file depends on Linux bitops, skb queues, waitqueues, udelay/jiffies behavior, NFP app control locking/transmit functions, and NFP netdev warning logging. BPF map operations and other app protocols use it through `nfp_ccm_communicate()` and deliver replies through app control receive hooks.

## Risks And Edge Cases
- Late firmware replies after timeout are dropped because their tag has been freed; a future request could otherwise match stale replies if tag reuse were too aggressive.
- `nfp_ccm_wait_reply()` logs `err == ERESTARTSYS`, but `wait_event_interruptible_timeout()` returns negative `-ERESTARTSYS`, so that comparison appears sign-sensitive.
- All reply queue operations rely on `nfp_ctrl_lock(app->ctrl)` serialization; receive and send paths must use the same lock.
- `nfp_ccm_clean()` only warns if replies remain queued; callers must ensure no in-flight requests during app teardown.
- A wrong reply type or size is converted to `-EIO` after freeing the skb.

## Test Signals
Exercise successful request/reply, wrong type/size, short receive skb, unknown tag receive, timeout, interrupted wait, tag-window exhaustion, late reply after timeout, concurrent map operations, and app cleanup with no queued replies or busy tags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/ccm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/ccm.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/ccm.h

## Purpose
This header defines the common NFP control-message ABI and transport state. It enumerates firmware message types for BPF maps/events and crypto operations, defines the shared control-message header and TLV constants, provides inline accessors for skb type/tag fields, declares `struct nfp_ccm`, and exposes CCM transport and mailbox helper APIs.

## Important APIs, Types, And Functions
- `enum nfp_ccm_type` assigns request ids for BPF map alloc/free/lookup/update/delete/getnext/getfirst, BPF events, and crypto reset/add/delete/update/resync.
- `NFP_CCM_ABI_VERSION`, `NFP_CCM_TYPE_REPLY_BIT`, and `__NFP_CCM_REPLY()` define the request/reply ABI convention.
- `struct nfp_ccm_hdr` is the firmware header containing type, version, and big-endian tag, also viewable as a raw 32-bit word.
- Inline helpers `nfp_ccm_get_type()`, `__nfp_ccm_get_tag()`, and `nfp_ccm_get_tag()` decode skb headers.
- `enum nfp_ccm_mbox_tlv_type` and `NFP_NET_MBOX_TLV_*` define mailbox TLV framing constants used by mailbox-backed CCM paths.
- `struct nfp_ccm` stores app pointer, tag allocator bitmap/cursors, reply queue, and waitqueue.
- Prototypes expose skb-based CCM and mailbox-backed communication helpers.

## Control Flow
The header's ABI is used by callers that allocate an skb with room for `struct nfp_ccm_hdr`, fill request-specific payload after the header, and call `nfp_ccm_communicate()` or mailbox variants. Firmware replies set the reply bit in the type and echo the tag; receive handlers use the inline helpers to route the skb to the matching waiter or event path.

## State And Persistence
No storage is defined beyond `struct nfp_ccm` instances embedded in app or netdev private state. Tags and reply queues are runtime-only. Firmware message type ids and header layout are persistent ABI contracts between driver and firmware.

## Dependencies And Integration Points
It includes Linux bitmap, skb, and waitqueue headers and forward-declares `struct nfp_app` and `struct nfp_net`. BPF control messages include this header through `fw.h`; app control receive code calls `nfp_ccm_rx()`; mailbox helpers integrate CCM with NFP netdev mailbox transport.

## Risks And Edge Cases
- Type ids are ABI values; changing or reordering the enum breaks firmware compatibility.
- `struct nfp_ccm_hdr` relies on exact byte layout and big-endian tag encoding.
- The tag bitmap has `U16_MAX + 1` bits, so cursor wraparound behavior must match unsigned 16-bit arithmetic in the implementation.
- Mailbox TLV declarations here are only framing constants; callers must still validate actual mailbox sizes and maximum reply lengths.

## Test Signals
Build users of skb and mailbox CCM paths, verify request/reply type ids against firmware, test tag encode/decode, BPF map operations over CCM, BPF event messages bypassing reply matching, mailbox TLV parsing for supported/unsupported message types, and cleanup with empty reply queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/ccm.h -->
